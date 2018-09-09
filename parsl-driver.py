
import glob
import time
import pathlib

import parsl
from parsl.app.app import bash_app

import logging


logger = logging.getLogger(__name__)

parsl.set_stream_logger()
parsl.set_stream_logger(__name__)

logger.info("No-op log message to test log configuration")

# import configuration after setting parsl logging, because interesting
# construction happens during the configuration

import configuration

parsl.load(configuration.parsl_config)

@bash_app(executors=['submit-node'])
def cache_singularity_image(local_file, url):
    return "singularity build {} {}".format(local_file, url)


@bash_app(executors=['worker-nodes'])
def run_imsim_in_singularity_fake(nthreads: int, work_and_out_base: str, singularity_img_path: str, inst_cat: str, inst_cat_root: str, stdout=None, stderr=None):
    return "echo start a bash task; sleep 20s ; echo this is stdout ; (echo this is stderr >&2 ) ; false"

@bash_app(executors=['worker-nodes'])
def run_imsim_in_singularity(nthreads: int, work_and_out_base: str, singularity_img_path: str, inst_cat: str, inst_cat_root: str, stdout=None, stderr=None):
    stuff_a = inst_cat.replace(inst_cat_root, "ICROOT", 1)
    stuff_b = stuff_a.replace("/", "_")
    pathbase = "{}/run/{}/".format(work_and_out_base, stuff_b)
    outdir = pathbase + "out/"
    workdir = pathbase + "work/"
    return "echo BENC: info pre singularity; date ; echo BENC id; id ; echo BENC HOME = $HOME; echo BENC hostnaee ; hostname ; echo BENC ls ~ ; ls ~ ; echo BENC launch singularity ; singularity run -B {},{} {} --instcat {} --workdir {} --outdir {} --low_fidelity --subset_size 300 --subset_index 0 --file_id ckpt --processes {}".format(inst_cat_root, work_and_out_base, singularity_img_path, inst_cat, outdir, workdir, nthreads)

def trickle_submit(task_info):

  instance_catalog = task_info
  logger.info("launching a run for instance catalog {}".format(instance_catalog))

  # TODO: factor this base 
  stuff_a = instance_catalog.replace(configuration.inst_cat_root, "ICROOT", 1)
  stuff_b = stuff_a.replace("/", "_")
  pathbase = "{}/run/{}/".format(configuration.work_and_out_path, stuff_b)
  outdir = pathbase + "out/"
  workdir = pathbase + "work/"

  pathlib.Path(workdir).mkdir(parents=True, exist_ok=True) 

  logger.info("app stdout/stderr logging: will create path {}".format(workdir))
  ot = workdir + "task-stdout.txt"
  er = workdir + "task-stderr.txt"
 
  future = run_imsim(63, configuration.work_and_out_path, configuration.singularity_img, instance_catalog, configuration.inst_cat_root, stdout=ot, stderr=er)
  logger.info("launched a run for instance catalog {}".format(instance_catalog))
  return future


logger.info("listing instance catalogs")
# This glob came from Jim Chiang
instance_catalogs = glob.glob('{}/DC2-R1*/0*/instCat/phosim_cat*.txt'.format(configuration.inst_cat_root))
logger.info("there are {} instance catalogs to process".format(len(instance_catalogs)))

logger.info("caching singularity image")


if (not configuration.fake) and configuration.singularity_download:
  singularity_future = cache_singularity_image(configuration.singularity_img, configuration.singularity_url)

  singularity_future.result()

if configuration.fake:
    run_imsim = run_imsim_in_singularity_fake
else:
    run_imsim = run_imsim_in_singularity

logger.info("Starting up trickle-in loop")


todo_tasks = instance_catalogs
submitted_futures = []
last_rebalance = time.time()

while len(todo_tasks) > 0 or len(submitted_futures) > 0:
  balance_ago = time.time() - last_rebalance
  logger.info("trickle loop: looping - {} tasks still to submit, {} futures to wait for, last rebalance was {} ago".format(len(todo_tasks), len(submitted_futures), round(balance_ago) ))

  if balance_ago > configuration.rebalance_seconds:
    logger.info("CALLBACK: rebalance")
    last_rebalance = time.time() # this will be roughly the time the rebalance finished, not configuration.rebalance_seconds after the last rebalance

  # check if any futures are finished, without blocking
  for f in submitted_futures:
    if f.done():
      logger.info("Future f is done")
      logger.info("CALLBACK: task done")
      submitted_futures.remove(f)

  while len(submitted_futures) < configuration.max_simultaneous_submit and len(todo_tasks) > 0:
    logger.info("There is capacity for a new task")
    task_info = todo_tasks.pop()
    f = trickle_submit(task_info)
    submitted_futures.append(f)

  logger.info("trickle loop: end iteration")
  time.sleep(configuration.trickle_loop_seconds)




logger.info("end of parsl-driver")

