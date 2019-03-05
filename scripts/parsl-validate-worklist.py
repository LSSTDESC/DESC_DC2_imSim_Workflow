#!/usr/bin/env python
print("parsl-validate-worklist: start")
import glob
import json
import sys
import os
import subprocess

runtime_root = sys.argv[1] # location of instance catalogs for runtime usage.

worklistpath = sys.argv[2] # a list of visits and sensors that has been pre-prepared. It should point to longterm_root.
newworklistpath = sys.argv[3] # a list of visits and sensors that will be output. It will point to runtime_root.

# this script takes an existing worklist linked to locations of the longterm root directory. It then does the
# following steps.
# 1. Read in the existing worklist.
# 2. Convert from the longterm_root directory to the runtime_root directory structure.
# 3. Check that all required instance catalogs exist in the runtime_root directory structure.
# 4. If the required instance catalog does NOT exist, copy over the corresponding tarball.
# 5. Untar the tarball. 
# 6. Output a new worklist which is utilizing the runtime_root directory structure for analysis.

with open(worklistpath) as fp: oldworklist = json.load(fp)

longterm_instcats = [item[0] for item in oldworklist]		# This is a list of the appropriate tarballs to move.
longterm_root = os.path.commonprefix(longterm_instcats)[:-2]	# This is the common directory structure across them.
# the dumb -2 here is to try to avoid losing the 00.

# This generates the paths to the expected directory to find files.
runtime_instcats = [runtime_root+instcat.split(longterm_root)[-1].split('.tar.gz')[0] for instcat in longterm_instcats]

# This stores these additional bits of information for generating a new worklist.
sensors = [item[1] for item in oldworklist]
numobjs = [item[2] for item in oldworklist]

new_instcats=[]
# Now we need to walk the RUNTIME directories to attempt to see if they have the appropriate files.
for longterm_instcat, runtime_instcat in zip(longterm_instcats, runtime_instcats):
    target_path = runtime_instcat+'/phosim*'
    phosim_file = glob.glob(target_path)
    # if there is not a phosim_file, we're going to have to rsync and untar some files.
    if not phosim_file:
        updirectory=os.path.dirname(runtime_instcat)+'/'
        tarpath=updirectory+longterm_instcat.split('/')[-1]
        #subprocess.call(["rsync", "-avzh", "--ignore-existing", longterm_instcat, updirectory])
        #subprocess.call(["tar", "-zvcf", tarpath, "-C", updirectory])
        #subprocess.call(["rm", tarpath])
        phosim_file = glob.glob(target_path)
    new_instcats.append(str(phosim_file))

# This creates a new worklist.
new_worklist = [ [new_instcats[i], sensors[i], numobjs[i]] for i in range(len(runtime_instcats))]
with open(newworklistpath, 'w') as fp: json.dump(new_worklist, fp)

sys.exit(0)
