#!/usr/bin/env python3
print("parsl-initial-bundle: start")
import glob
import json
import sys
import os

import instcat_trimmer as ict
import job_bundling_utils as jbu


inst_cat_root = sys.argv[1]

worklist = sys.argv[2]
bundles = sys.argv[3]

outpath = sys.argv[4]

restartpath = sys.argv[5]

# With all the work to be done found, we then want to determine some initial bundling scheme.
# To do this, we call on the job_bundling_utils module. Let's read in that json file.
with open(worklist) as fp:
    worklist_a = json.load(fp)

# we now define key characteristics of the imSim version + architecture.
mem_per_thread = 2      # the amount of memory a given sensor thread is expected to max out at
mem_per_instance = 10   # the amount of shared memory an imSim container is expected to have

mem_per_node = 96-5     # the available memory on a compute node to target for use, minus some leeway
threads_per_node = 68*4 # the number of available threads to be used on a given node

print("parsl-initial-bundle: Bundling first pass...")
bundle_list_a = jbu.determine_bundles(worklist_a, mem_per_thread, mem_per_instance, mem_per_node, threads_per_node)

# This bundle list can be saved and used for your workflow of choice!
with open(bundles, 'w') as fp:
    json.dump(bundle_list_a, fp)

print("parsl-initial-bundle: Checking job success...")

jbu.check_job_success(bundles, outpath, restartpath)

print("parsl-initial-bundle: Determining remaining jobs...")
worklist_new = jbu.determine_remaining_jobs("/projects/LSSTADSP_DESC/Run2.0i-parsl/ALCF_1.2i/empty-worklist.json", restartpath)

print("parsl-initial-bundle: Bundling second pass...")

bundle_list_new = jbu.determine_bundles(worklist_new, mem_per_thread, mem_per_instance, mem_per_node, threads_per_node)

with open(bundles, 'w') as fp:
    json.dump(bundle_list_new, fp)

print("parsl-initial-bundle: Done")

sys.exit(0)

