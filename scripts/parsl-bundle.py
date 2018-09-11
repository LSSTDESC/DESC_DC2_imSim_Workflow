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

# With all the work to be done found, we then want to determine some initial bundling scheme.
# To do this, we call on the job_bundling_utils module. Let's read in that json file.
with open(worklist) as fp:
    worklist_a = json.load(fp)

# We need to define the max number of threads and max number of instances per node for this. We choose
# the fiducial values from Theta. Note that the max_instances_node is a non-trivial calculation.
# We assume 10 GB memory per imSim call + 1 GB per thread + 5 GB floating for sharp increases.
# This may vary depending on your version of imSim and architecture.

max_threads_node = 64
max_instances_node = 10
bundle_list_a = jbu.determine_bundles(worklist_a, max_threads_node, max_instances_node)

# This bundle list can be saved and used for your workflow of choice!
with open(bundles, 'w') as fp:
    json.dump(bundle_list_a, fp)


sys.exit(0)

# We want to be able to check if a job has outputs. Since we haven't started the job,
# this should fail all those tests. But we can test this with our utilities!

infile = '/mnt/scripts/bundle_worklist_a.json' # the path to our file to check
outpath = '/mnt/outputs/'                       # the path to out imSim outputs
restartpath = '/mnt/restarts/'                  # where we are putting all our restarts

# This checks for the existence of a gzipped file WHILE not having a checkpoint to measure
# success, for each sensor that has work to do. Otherwise, it returns that information into
# a new json file for restarting off of, in the requested restart path.
jbu.check_job_success(infile, outpath, restartpath)

# Let's make a new set of work to also do real quick.
instcat_list_b = ['/mnt/cwd/DC2-R1-2p-WFD-g/000003/instCat/phosim_cat_159492.txt',
                 '/mnt/cwd/DC2-R1-2p-WFD-g/000004/instCat/phosim_cat_159493.txt']
ict.determine_instcat_work(instcat_list_b, '/mnt/scripts/instcat_worklist_b.json')
with open('/mnt/scripts/instcat_worklist_b.json') as fp:
    worklist_b = json.load(fp)
bundle_list_b = jbu.determine_bundles(worklist_b, max_threads_node, max_instances_node)
with open('/mnt/scripts/bundle_worklist_b.json', 'w') as fp:
    json.dump(bundle_list_b, fp)

# And now let's combine THIS with our restart data to generate a new master bundling.
worklist_new = jbu.determine_remaining_jobs('/mnt/scripts/bundle_worklist_b.json', restartpath)
bundle_list_new = jbu.determine_bundles(worklist_new, max_threads_node, max_instances_node)

# And we can just save this new work list!
with open('/mnt/scripts/bundle_worklist_new.json', 'w') as fp:
    json.dump(bundle_list_new, fp)
