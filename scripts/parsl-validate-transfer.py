#!/usr/bin/env python
print("parsl-validate-transfer: start")
import glob
import json
import sys
import os
import subprocess

runtime_root = sys.argv[1] # location of instance catalogs for runtime usage.

tarballpath = sys.argv[2] # a list of visits and sensors that has been pre-prepared. It should point to longterm_root.

# This script takes a list of files that should have been transferred and confirms their transfer.
# 1. Read in the tarball paths.
# 2. Determine where they SHOULD go.
# 3. Check if phosim files already exist.
# 4. IF Phosim files do not exist, transfer and unpack the tarball.
# 5. Clean up.

with open(tarballpath) as fp: longterm_tarballs = json.load(fp)	# this is a list of the tarballs to move.

#longterm_root = os.path.commonpath(longterm_tarballs)	# This is the common directory structure across them.
							# note this FAILS if it gets a single directory worth of tarballs.
longterm_root = os.path.dirname(os.path.dirname(longterm_tarballs[0])) # This might work better?

# This generates the paths to the expected directory to find files.
runtime_instcats = [runtime_root+tarball.split(longterm_root)[-1].split('.tar.gz')[0] for tarball in longterm_tarballs]
print(runtime_instcats)

# Now we need to walk the RUNTIME directories to attempt to see if they have the appropriate files.
for longterm_tarball, runtime_instcat in zip(longterm_tarballs, runtime_instcats):
    target_path = runtime_instcat+'/phosim*'
    phosim_file = glob.glob(target_path)
    # if there is not a phosim_file, we're going to have to rsync and untar some files.
    if not phosim_file:
        updirectory=os.path.dirname(runtime_instcat)+'/'
        tarpath=updirectory+longterm_tarball.split('/')[-1]
        subprocess.call(["rsync", "-avzh", "--ignore-existing", longterm_tarball, updirectory])
        subprocess.call(["tar", "zxvf", tarpath, "-C", updirectory])
        subprocess.call(["rm", tarpath])
        phosim_file = glob.glob(target_path)
print("parsl-validate-transfer: complete")

sys.exit(0)
