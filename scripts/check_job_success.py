import glob
import json
import sys

# This code ingests a json file of the same format as the initial
# bundling and searches the output directory path for each sensor
# to insure job completion. It does this by both searching for a
# .fits.gz file *AND* the absence of a .ckpt file.
# For any unstarted job or unfinished job, it then wraps it with
# the initial nodekey as work to be redone. For unfinished jobs,
# we will optimally attempt to modify the remaining number of
# objects to allow for some ETA information down the road.

# Step 1: Arguments are the input .json file, the directory to walk
# for outputs, and the directory to place restart information in.

infile = sys.argv[1]
outfilepath = sys.argv[2]
restartpath = sys.argv[3]

# Step 2: Read in the input.json.
with open(infile) as fp:
    input_data = json.load(fp)

# Step 3: For each key in the input.json, search the list for .fits.gz
# and .ckpt files.

for node in input_data.keys():
    for instcat, sensors, num_objs in input_data[key]:
        searchstring = str(visit)
        files = glob.glob(outfilepath+'*/'+searchstring+'/*')
        for i in range(len(sensors)):
            # something here to compare sensor name to files in the list
            # remove the sensor from the list if a .fits.gz exists and not
            # a .json
            
            # currently assuming giant dictionary, to do this. Might be
            # more clever solution with regex or the like to explore.
            matching = [s for s in files if sensordict[sensor[i]] in s]
            check_gz = [s for s in matching if '.gz' in s]
            check_ckpt = [s for s in matching if '.ckpt' in s]
            
            if check_gz and not check_ckpt:
                sensors[i] = []
                numobjs[i] = []
            else:
                # update the number of objects left in the sensor.

with open(restartpath+infile+'restart.json', 'w') as outfile:
    json.dump(input_data, outfile)

