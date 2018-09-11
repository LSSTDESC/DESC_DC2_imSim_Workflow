
import glob
import time
import pathlib
import json

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
def generate_bundles(singularity_img_path: str, inst_cat_root: str, work_and_out_base, work_json: str, bundle_json: str):
    return "singularity exec -B {},{} {} /home/benc/desc2.0i/ALCF_1.2i/scripts/parsl-initial-bundle.py {} {} {}".format(inst_cat_root, work_and_out_base, singularity_img_path, inst_cat_root, work_json, bundle_json)

# bundle_future = generate_bundles(configuration.singularity_img, configuration.inst_cat_root, configuration.bundle_lists + ".work.json", configuration.bundle_lists)


@bash_app(executors=['submit-node'])
def cache_singularity_image(local_file, url):
    return "singularity build {} {}".format(local_file, url)


@bash_app(executors=['worker-nodes'])
def run_imsim_in_singularity_fake(nthreads: int, work_and_out_base: str, singularity_img_path: str, inst_cat_root: str, bundle_lists: str, nodeid: str, bundle, stdout=None, stderr=None):
    return "echo start a bash task; sleep 20s ; echo this is stdout ; (echo this is stderr >&2 ) ; false"

@bash_app(executors=['worker-nodes'])
def run_imsim_in_singularity(nthreads: int, work_and_out_base: str, singularity_img_path: str, inst_cat_root: str, bundle_lists: str, nodeid: str, bundle, stdout=None, stderr=None):

    import os
    import re

    run = bundle[0]
    inst_cat_path = run[0]
    sensor_count = len(run[1]) # TODO: use instead of nthreads

    (inst_cat_dir1, phosim_txt_fn) = os.path.split(inst_cat_path)
    (inst_cat_path_trimmed, instcat_const) = os.path.split(inst_cat_dir1)

    stuff_b = inst_cat_path_trimmed.replace(inst_cat_root, "outputs/", 1)
    pathbase = "{}/run/{}/".format(work_and_out_base, stuff_b)
    outdir = pathbase + "out/"
    workdir = pathbase + "work/"
    visit_index = 0

    # filename in phosim_txt_fn will look like: phosim_cat_1909355.txt
    # extract the numeric part of that
    (checkpoint_file_id, subs) = re.subn("[^0-9]","", phosim_txt_fn)

    return "echo BENC: info pre singularity; date ;  echo BENC sensor count is {} ; echo BENC id; id ; echo BENC HOME = $HOME; echo BENC hostnaee ; hostname ; echo BENC ls ~ ; ls ~ ; echo BENC launch singularity ; singularity run -B {},{} {} --workdir {} --outdir {} --low_fidelity --file_id {} --processes {} --bundle_lists {} --node_id {} --visit_index {}".format(sensor_count, inst_cat_root, work_and_out_base, singularity_img_path, outdir, workdir, checkpoint_file_id, nthreads, bundle_lists, nodeid, visit_index)

def trickle_submit(bundle_lists, task_info):

  logger.info("trickle_submit has bundle {}".format(task_info))

  (nodename, catalogs) = task_info

  logger.info("trickle_submit: submitting for bundle nodename {}".format(nodename))
  logger.info("trickle_submit: submitting (parts of) {} instance catalogs".format(len(catalogs)))

  workdir = "{}/node_logs/{}/".format(configuration.work_and_out_path, nodename)

  pathlib.Path(workdir).mkdir(parents=True, exist_ok=True) 

  logger.info("app stdout/stderr logging: will create path {} for task stdout/err".format(workdir))
  ot = workdir + "task-stdout.txt"
  er = workdir + "task-stderr.txt"

  future = run_imsim(64, configuration.work_and_out_path, configuration.singularity_img, configuration.inst_cat_root, bundle_lists, nodename, catalogs, stdout=ot, stderr=er)
  logger.info("launched a run for bundle nodename {}".format(nodename))

  return future


#logger.info("listing instance catalogs")
# This glob came from Jim Chiang
#instance_catalogs = glob.glob('{}/DC2-R1*/0*/instCat/phosim_cat*.txt'.format(configuration.inst_cat_root))
#logger.info("there are {} instance catalogs to process".format(len(instance_catalogs)))

logger.info("caching singularity image")

if (not configuration.fake) and configuration.singularity_download:
  singularity_future = cache_singularity_image(configuration.singularity_img, configuration.singularity_url)

  singularity_future.result()


logger.info("generating bundles")

bundle_future = generate_bundles(configuration.singularity_img, configuration.inst_cat_root, configuration.work_and_out_path, configuration.original_work_list, configuration.bundle_lists)
bundle_future.result()

logger.info("loading bundles")

with open(configuration.bundle_lists) as fp:
  bundles = json.load(fp)
logger.info("Loaded {} bundles".format(len(bundles)))



if configuration.fake:
    run_imsim = run_imsim_in_singularity_fake
else:
    run_imsim = run_imsim_in_singularity

logger.info("Starting up trickle-in loop")


todo_tasks = bundles
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
    task_info = todo_tasks.popitem()
    logger.info("popped task_info is: {}".format(task_info))
    f = trickle_submit(configuration.bundle_lists, task_info)
    submitted_futures.append(f)

  logger.info("trickle loop: end iteration")
  time.sleep(configuration.trickle_loop_seconds)




logger.info("end of parsl-driver")

