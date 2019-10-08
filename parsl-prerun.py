import collections
import glob
import time
import pathlib
import json
import sys

import parsl
from parsl.app.app import bash_app

import logging

from functools import partial

logger = logging.getLogger("parsl.appworkflow")

parsl.set_stream_logger()
parsl.set_stream_logger(__name__)

logger.info("No-op log message to test log configuration")

# import configuration after setting parsl logging, because interesting
# construction happens during the configuration

import configuration

parsl.load(configuration.parsl_config)

# given a commandline, wrap it so that we'll invoke
# shifter appropriately (so that we don't need to
# hardcode shifter / singularity command lines all
# over the place.
def shifter_wrapper(img, cmd):
  wrapped_cmd = "shifter --entrypoint --image={} {}".format(img, cmd)
  return wrapped_cmd

def singularity_wrapper(img, inst_cat_root, work_and_out_path, cmd):
  wrapped_cmd = "singularity exec -B {},{},/projects/LSSTADSP_DESC {} /projects/LSSTADSP_DESC/Run2.1i/DESC_DC2_imSim_Workflow/docker_run.sh {}".format(inst_cat_root, work_and_out_path, img, cmd)
  return wrapped_cmd

@bash_app(executors=['submit-node'])
def validate_transfer(wrap, inst_cat_root: str, tarball_json: str):
    base = "/global/cscratch1/sd/desc/DC2/Run2.1.1i/DESC_DC2_imSim_Workflow/scripts/parsl-validate-transfer.py {} {}".format(inst_cat_root, tarball_json)
    c = wrap(base)
    logger.debug("validate_transfer command is: {}".format(c))
    return c   

@bash_app(executors=['submit-node'])
def generate_worklist(wrap, inst_cat_root: str, work_json: str, bundle_json: str):
    base = "/global/cscratch1/sd/desc/DC2/Run2.1.1i/DESC_DC2_imSim_Workflow/scripts/parsl-initial-worklist.py {} {} {}".format(inst_cat_root, work_json, bundle_json)
    c = wrap(base)
    logger.debug("generate_worklist command is: {}".format(c))
    return c


@bash_app(executors=['submit-node'])
def cache_singularity_image(local_file, url):
    return "singularity build {} {}".format(local_file, url)

@bash_app(executors=['submit-node'])
def cache_shifter_image(image_tag):
    return "shifterimg -v pull {}".format(image_tag)

if configuration.MACHINEMODE == "cori":
  container_wrapper = partial(shifter_wrapper, configuration.singularity_img)
elif configuration.MACHINEMODE == "theta":
  container_wrapper = partial(singularity_wrapper, configuration.singularity_img, configuration.inst_cat_root,
                            configuration.work_and_out_path)
elif configuration.MACHINEMODE == "theta_local":
  container_wrapper = partial(singularity_wrapper, configuration.singularity_img, configuration.inst_cat_root,
                            configuration.work_and_out_path)

logger.info("caching container image")

# first pull a shifter/singularity image as necessary.
if (not configuration.fake) and configuration.singularity_download:
  if configuration.MACHINEMODE == "theta":
    singularity_future = cache_singularity_image(configuration.singularity_img, configuration.singularity_url)
    singularity_future.result()
  elif configuration.MACHINEMODE == "cori":
    shifter_future = cache_shifter_image(configuration.singularity_img)
    shifter_future.result()

# this is unused in favor of globus transfers for speed. Globus hooks may be integrated
# if they ever fix this for collaborative accounts.
# then, transfer all desired files via a tarball list.
#if configuration.validate_transfer:
#  logger.info("validating transfer")
#  validate_future = validate_transfer(container_wrapper, configuration.inst_cat_root, configuration.tarball_list)
#  validate_future.result()

# then generate a worklist given all desired files have been transferred.
logger.info("generating worklist")
worklist_future = generate_worklist(container_wrapper, configuration.inst_cat_root, configuration.original_work_list, configuration.bundle_lists)
worklist_future.result()
