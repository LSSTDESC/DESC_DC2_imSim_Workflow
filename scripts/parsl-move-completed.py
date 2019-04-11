#!/usr/bin/env python
print("parsl-move-completed: start")
import glob
import json
import sys
import os
import subprocess

runtime_root = sys.argv[1] # the base path to where runtime outputs are being stored.
longterm_root= sys.argv[2] # the base path to where longterm file storage is being handled
worklistpath = str(sys.argv[3]) # a list of visits and sensors that have been operated on OR a flag string of WALK_ALL

# This script does the following:
#1. Determine which instance catalogs had jobs run.
#2. Scan those directories for output files - specifically fits and centroids.
#3. Sync those up with the longterm root directory to make sure that everything is in the right place.

if worklistpath == 'WALK_ALL':
    print('walking all possible output files!')
    output_paths = glob.glob(os.path.join(runtime_root,'*/*/'))
    longterm_paths = [os.path.join(longterm_root, '/'.join(output_path.split('/')[-3:])) for output_path in output_paths]
else:
    with open(worklistpath) as fp: worklist = json.load(fp)
    input_instcats = [str(item[0]) for item in worklist]
    output_paths = [os.path.join(runtime_root,'/'.join(input_instcat.split('/')[-3:-1]))+'/' for input_instcat in input_instcats]
    longterm_paths = [os.path.join(longterm_root, '/'.join(input_instcat.split('/')[-3:-1]))+'/' for input_instcat in input_instcats]

# Now - determine the actual outputs.
types_to_grab = ('*.fits', '*.txt.gz', '*.ckpt')

for output_path, longterm_path in zip(output_paths, longterm_paths):
    files_grabbed = []
    for grabext in types_to_grab:
        files_grabbed.extend(glob.glob(output_path+grabext))
    # and with the outputs determined, we now want to transfer them to long-term storage.
    # first we need to create the directory if it does not exist already.
    if not any('.ckpt' in file_grabbed for file_grabbed in files_grabbed):
        print('moving: {}'.format(files_grabbed))
        if not os.path.exists(longterm_path):
            os.makedirs(longterm_path)
        for file_grabbed in files_grabbed:
            subprocess.call(["rsync", "-azh", "--ignore-existing", file_grabbed, longterm_path]) 

print("parsl-move-completed: finished")
sys.exit(0)
