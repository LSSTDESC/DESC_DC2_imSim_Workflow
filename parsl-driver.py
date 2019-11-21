import collections
import glob
import time
import pathlib
import json

import parsl
from parsl.app.app import bash_app

import logging

from functools import partial

logger = logging.getLogger("parsl.appworkflow")

parsl.set_stream_logger()
parsl.set_stream_logger(__name__)

logger.info("No-op log message to test log configuration")
logger.info("Parsl version is {}".format(parsl.__version__))
logger.info("Parsl file is {}".format(parsl.__file__))
# import configuration after setting parsl logging, because interesting
# construction happens during the configuration

import configuration

parsl.load(configuration.parsl_config)

# given a commandline, wrap it so that we'll invoke
# shifter appropriately (so that we don't need to
# hardcode shifter / singularity command lines all
# over the place.
def shifter_wrapper(img, cmd):
  wrapped_cmd = "shifter --image={} /global/cscratch1/sd/descim/Run2.2i/DESC_DC2_imSim_Workflow/docker_run.sh python {}".format(img, cmd)
  return wrapped_cmd

def singularity_wrapper(img, inst_cat_root, work_and_out_path, cmd):
  wrapped_cmd = "singularity exec -H /lus/theta-fs0/projects/LSSTADSP_DESC/Run2.1i -B {},{},/projects/LSSTADSP_DESC {} /projects/LSSTADSP_DESC/Run2.1i/DESC_DC2_imSim_Workflow/docker_run.sh python {}".format(inst_cat_root, work_and_out_path, img, cmd)
  return wrapped_cmd


@bash_app(executors=['submit-node'])
def validate_transfer(wrap, inst_cat_root: str, tarball_json: str):
    base = "/global/cscratch1/sd/descim/Run2.2i/DESC_DC2_imSim_Workflow/scripts/parsl-validate-transfer.py {} {}".format(inst_cat_root, tarball_json)
    c = wrap(base)
    logger.debug("validate_transfer command is: {}".format(c))
    return c   

@bash_app(executors=['submit-node'])
def generate_worklist(wrap, inst_cat_root: str, work_json: str, bundle_json: str):
    base = "/global/cscratch1/sd/descim/Run2.2i/DESC_DC2_imSim_Workflow/scripts/parsl-initial-worklist.py {} {} {}".format(inst_cat_root, work_json, bundle_json)
    c = wrap(base)
    logger.debug("generate_worklist command is: {}".format(c))
    return c

@bash_app(executors=['submit-node'])
def generate_bundles(wrap, inst_cat_root: str, work_and_out_base, work_json: str, bundle_json: str, bundler_restart_path: str):
    c = wrap("/global/cscratch1/sd/descim/Run2.2i/DESC_DC2_imSim_Workflow/scripts/parsl-bundle.py {} {} {} {} {}".format(inst_cat_root, work_json, bundle_json, work_and_out_base + "/run/outputs/", bundler_restart_path))
    logger.debug("generate_bundles command is: {}".format(c))
    return c

@bash_app(executors=['submit-node'])
def archive_completed(wrap, runtime_root: str, work_json: str, longterm_root: str):
    c = wrap("/global/cscratch1/sd/descim/Run2.2i/DESC_DC2_imSim_Workflow/scripts/parsl-move-completed.py {} {} {}".format(runtime_root, longterm_root, work_json))
    logger.debug("archive_completed command is: {}".format(c))
    return c

@bash_app(executors=['submit-node'])
def cache_singularity_image(local_file, url):
    return "singularity build {} {}".format(local_file, url)

@bash_app(executors=['submit-node'])
def cache_shifter_image(image_tag):
    return "shifterimg -v pull {}".format(image_tag)

@bash_app(executors=['worker-nodes'])
def run_imsim_in_singularity_fake(wrap, nthreads: int, work_and_out_base: str, inst_cat_root: str, bundle_lists: str, nodeid: str, imsim_config: str, bundle, stdout=None, stderr=None):
    return "echo start a bash task; sleep 20s ; echo this is stdout ; (echo this is stderr >&2 ) ; false"

@bash_app(executors=['worker-nodes'])
def run_imsim_in_singularity(wrap, nthreads: int, work_and_out_base: str, inst_cat_root: str, bundle_lists: str, nodeid: str, imsim_config: str, bundle, stdout=None, stderr=None):

    import os
    import re
    prefix_cmd = "echo DEBUG: info pre singularity; date ; echo DEBUG: id; id ; echo DEBUG: HOME = $HOME; echo DEBUG: hostnaee ; hostname ; echo DEBUG: ls ~ ; ls ~ ; echo DEBUG: launching singularity blocks ; ulimit -Sv 120000000 ; "

    debugger_cmd = " (for i in $(seq 1 300); do echo DEBUGLOOP; date ; free -m ; ps ax -o command,pid,ppid,vsize,rss,%mem,size,%cpu ; echo END DEBUGLOOP ; sleep 1m ; done ) & "

    postfix_cmd = " echo waiting ; wait ; echo done waiting "

    body_cmd = ""

    for visit_index in range(0, len(bundle)):

      run = bundle[visit_index]
      inst_cat_path = run[0]
      sensor_count = len(run[1]) # TODO: use instead of nthreads

      (inst_cat_path_trimmed, phosim_txt_fn) = os.path.split(inst_cat_path)

      stuff_b = inst_cat_path_trimmed.replace(inst_cat_root, "outputs/", 1)
      pathbase = "{}/run/{}/".format(work_and_out_base, stuff_b)
      outdir = pathbase + ""   # just in case we want to separate these
      workdir = pathbase + ""
      ckpt_archive_dir = pathbase + "/agn_ckpts/"

      # filename in phosim_txt_fn will look like: phosim_cat_1909355.txt
      # extract the numeric part of that
      (checkpoint_file_id, subs) = re.subn("[^0-9]","", phosim_txt_fn)

      body_cmd += wrap("/global/cscratch1/sd/descim/Run2.2i/DESC_DC2_imSim_Workflow/scripts/run_imsim.py --workdir {} --outdir {} --file_id {} --processes {} --bundle_lists {} --node_id {} --visit_index {} --ckpt_archive_dir {} --config {} & ".format(outdir, workdir, checkpoint_file_id, sensor_count, bundle_lists, nodeid, visit_index, ckpt_archive_dir, imsim_config))

    whole_cmd = prefix_cmd + debugger_cmd + body_cmd + postfix_cmd
    print("whole_cmd: %{}".format(whole_cmd))
    return whole_cmd

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

  future = run_imsim(container_wrapper, 64, configuration.work_and_out_path, configuration.inst_cat_root, bundle_lists, nodename, configuration.imsim_config, catalogs, stdout=ot, stderr=er)
  logger.info("launched a run for bundle nodename {}".format(nodename))

  return future

if configuration.MACHINEMODE == "cori":
  container_wrapper = partial(shifter_wrapper, configuration.singularity_img)
elif configuration.MACHINEMODE == "theta":
  container_wrapper = partial(singularity_wrapper, configuration.singularity_img, configuration.inst_cat_root,
                            configuration.work_and_out_path)

logger.info("caching container image")

if (not configuration.fake) and configuration.singularity_download:
  if configuration.MACHINEMODE == "theta":
    singularity_future = cache_singularity_image(configuration.singularity_img, configuration.singularity_url)
    singularity_future.result()
  elif configuration.MACHINEMODE == "cori":
    shifter_future = cache_shifter_image(configuration.singularity_img)
    shifter_future.result()

# long enough now that this should be limited to pre-production if possible.
#if configuration.worklist_generate:
#  logger.info("generating worklist")
#  worklist_future = generate_worklist(container_wrapper, configuration.inst_cat_root, configuration.original_work_list, configuration.bundle_lists)
#  worklist_future.result()

logger.info("generating bundles")

pathlib.Path(configuration.bundler_restart_path).mkdir(parents=True, exist_ok=True) 

bundle_future = generate_bundles(container_wrapper, configuration.inst_cat_root, configuration.work_and_out_path, configuration.original_work_list, configuration.bundle_lists, configuration.bundler_restart_path)

bundle_future.result()

logger.info("Loading bundles from {}".format(configuration.bundle_lists))

with open(configuration.bundle_lists) as fp:
  bundles = json.load(fp)
logger.info("Loaded {} bundles".format(len(bundles)))



if configuration.fake:
    run_imsim = run_imsim_in_singularity_fake
else:
    run_imsim = run_imsim_in_singularity

logger.info("Starting up trickle-in loop")


todo_tasks = collections.OrderedDict(bundles)
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
    task_info = todo_tasks.popitem(last=False)
    logger.info("popped task_info is: {}".format(task_info))
    f = trickle_submit(configuration.bundle_lists, task_info)
    submitted_futures.append(f)

  logger.info("trickle loop: end iteration")
  time.sleep(configuration.trickle_loop_seconds)

#archive_future = archive_completed(container_wrapper, configuration.work_and_out_base+"run/outputs/", configuration.original_work_list, configuration.archive_base)
#archive_future.result()

logger.info("end of parsl-driver")

