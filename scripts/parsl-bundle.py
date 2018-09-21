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

# We need to define the max number of threads and max number of instances per node for this. We choose
# the fiducial values from Theta. Note that the max_instances_node is a non-trivial calculation.
# We assume 10 GB memory per imSim call + 1 GB per thread + 5 GB floating for sharp increases.
# This may vary depending on your version of imSim and architecture.

max_threads_node = 32
max_instances_node = 1

print("parsl-initial-bundle: Bundling first pass...")
bundle_list_a = jbu.determine_bundles(worklist_a, max_threads_node, max_instances_node)

# This bundle list can be saved and used for your workflow of choice!
with open(bundles, 'w') as fp:
    json.dump(bundle_list_a, fp)

print("parsl-initial-bundle: Checking job success...")

jbu.check_job_success(bundles, outpath, restartpath)

print("parsl-initial-bundle: Determining remaining jobs...")
worklist_new = jbu.determine_remaining_jobs("/projects/LSSTADSP_DESC/Run2.0i-parsl/ALCF_1.2i/empty-worklist.json", restartpath)

print("parsl-initial-bundle: Bundling second pass...")

bundle_list_new = jbu.determine_bundles(worklist_new, max_threads_node, max_instances_node)

with open(bundles, 'w') as fp:
    json.dump(bundle_list_new, fp)

print("parsl-initial-bundle: Done")

sys.exit(0)

