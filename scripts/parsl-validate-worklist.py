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
# 4. If the required instance catalog does NOT exist, copy it over.
# 5. Output a new worklist which is utilizing the runtime_root directory structure for analysis.

with open(worklistpath) as fp: oldworklist = json.load(fp)

longterm_instcats = [item[0] for item in oldworklist]
longterm_root = os.path.commonprefix(longterm_instcats)

runtime_instcats = [os.path.join(runtime_root, '/'.join(instcat.split('/')[-3:])) for instcat in longterm_instcats]

sensors = [item[1] for item in oldworklist]
numobjs = [item[2] for item in oldworklist]

# So now we have both old and new directory structures. We now want to check that files exist and copy over those that
# do not. The best way to do this is probably with an rsync command between each directory pair. For now, prototype
# the comparison. We might as well make the new worklist at the same time at the same time.
new_worklist = [ [runtime_instcats[i], sensors[i], numobjs[i]] for i in range(len(runtime_instcats))]
with open(newworklistpath, 'w') as fp: json.dump(new_worklist, fp)

for longterm_instcat, runtime_instcat in zip(longterm_instcats, runtime_instcats):
    first_path = longterm_instcat.split('phosim')[0]
    second_path = runtime_instcat.split('phosim')[0]
    print('first: ', first_path)
    print('second: ', second_path)
    #subprocess.call(["rsync", "-avzh", "--ignore-existing", first_path, second_path])

sys.exit(0)
