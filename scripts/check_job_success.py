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

# As part of this, we need to define a search directory. We can probably
# just grab this off the .json file with (or similar):
# searchpath = str('/'.join(instcat.split('/')[-4:-2]))

for node in input_data.keys():
    for instcat, sensors, num_objs in input_data[node]:
        searchstring = str('/'.join(instcat.split('/')[-4:-2]))
        files = glob.glob(outfilepath+'/'+searchstring+'/*')
        for i in range(len(sensors)):
            # something here to compare sensor name to files in the list
            # remove the sensor from the list if a .fits.gz exists and not
            # a .json

            # not the most elegant way to handle this, but a way to handle
            # this.
            sensor_nums = [str(s) for s in sensors[i] if s.isdigit()]
            gz_sensorstr = 'R'+sensor_nums[0]+sensor_nums[1]+'_S'+sensor_nums[2]+sensor_nums[3]
            ckpt_sensorstr = 'R_'+sensor_nums[0]+'_'+sensor_nums[1]+'_S_'+sensor_nums[2]+'_'+sensor_nums[3]            
            matchinggz = [s for s in files if gz_sensorstr in s]
            check_gz = [s for s in matchinggz if '.gz' in s]
            matchingckpt = [s for s in files if ckpt_sensorstr in s]
            check_ckpt = [s for s in matchingckpt if '.ckpt' in s]
            
            if check_gz and not check_ckpt:
                sensors[i] = []
                num_objs[i] = []
            else:
                # update the number of objects left in the sensor.
                pass

# strip last part of infile name
outfilename = (infile.split('/')[-1]).split('.')[0]

with open(restartpath+outfilename+'_restart.json', 'w') as outfile:
    json.dump(input_data, outfile)
