#!/usr/bin/env python
print("parsl-move-completed: start")
import glob
import json
import sys
import os
import subprocess

runtime_root = sys.argv[1] # the base path to where runtime outputs are being stored.
worklistpath = sys.argv[2] # a list of visits and sensors that have been operated on.
longterm_root= sys.argv[3] # the base path to where longterm file storage is being handled

# This script does the following:
#1. Determine which instance catalogs had jobs run.
#2. Scan those directories for output files - specifically fits and centroids.
#3. Sync those up with the longterm root directory to make sure that everything is in the right place.

with open(worklistpath) as fp: worklist = json.load(fp)

#input_instcats = [item[0] for item in worklist]	# This is a list of the instance catalogs that had work done.

# quick fix for testing
input_instcats = [str(item[0]) for item in worklist]

# let's convert those into the expected output paths.
output_paths = [os.path.join(runtime_root,'/'.join(input_instcat.split('/')[-3:-1]))+'/' for input_instcat in input_instcats]
longterm_paths = [os.path.join(longterm_root, '/'.join(input_instcat.split('/')[-3:-1]))+'/' for input_instcat in input_instcats]

# Now - determine the actual outputs.
types_to_grab = ('*.fits', '*.txt.gz')

for output_path, longterm_path in zip(output_paths, longterm_paths):
    files_grabbed = []
    for grabext in types_to_grab:
        files_grabbed.extend(glob.glob(output_path+grabext))
    # and with the outputs determined, we now want to transfer them to long-term storage.
    # first we need to create the directory if it does not exist already.
    if not os.path.exists(longterm_path):
        os.makedirs(longterm_path)
    for file_grabbed in files_grabbed:
        subprocess.call(["rsync", "-azh", "--ignore-existing", file_grabbed, longterm_path]) 

print("parsl-move-completed: finished")
sys.exit(0)
