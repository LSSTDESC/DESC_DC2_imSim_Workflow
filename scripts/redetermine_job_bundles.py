import numpy as np
import json
import sys
import glob

# Three system arguments input by default:
infile = sys.argv[1]   # /path/to/json/inputfile of all jobs you haven't started
restartpath = sys.argv[2] # /path/to/dir storing all your checkpointed job output
outfile = sys.argv[3]  # /path/to/json/outfile for all jobs to now start.


# hard coded hardware limitations
max_threads_node = 64
max_fit = 10 # again, currently harded coded; keeps from running out of memory
             # on a node due to too many visits.


####################################################
# Commented out section for different reading format
####################################################
# modification to read in a JSON file consisting of a dict with keys of instcat
# and list of sensors
#with open(infile) as json_input:
#    temp_data = json.load(json_input)
####################################################

# Read in JSON file containing tuples of (instcat, [list of sensors]) for each job.
with open(infile) as json_input:
    run_data = json.load(json_input)

#Preprocessing step to recombine any two with the same instance catalogs.
temp_sensors = dict()
temp_numobjs = dict()
for visit, sensors, numobj in run_data:
    key = str(visit)
    if key in temp_sensors:
        for sensor in sensors:
            temp_sensors[key].append(sensor)
            temp_numobjs[key].append(numobj)
    else:
        temp_sensors[key] = sensors
        temp_numobjs[key] = numobj


listofrestarts = glob.glob(restartpath+'*.json')

for restart in list of restarts:
    with open(restart) as json_input:
         restart_data = json.load(json_input)
    for visit, sensors, numobj in restart_data:
        key = str(visit)
        if key in temp_sensors:
            for sensor in sensors:
                temp_sensors[key].append(sensor)
                temp_numobjs[key].append(numobj)
        else:
            temp_sensors[key] = sensors
            temp_numobjs[key] = numobj

sample = []
for key in temp_sensors.keys():
    sample.append([key, temp_sensors[key], temp_numobjs[key]])

# This produces something that my pipeline can easily take.
thread_counts = [len(item[1]) for item in sample]

bundle_list = dict()

bin_counter = 0

for i in range(0, len(thread_counts)):
    while thread_counts[i] >= max_threads_node:
        thread_counts[i] += -1*max_threads_node
        temp = []
        for tempi in range(max_threads_node):
            temp.append((sample[i])[1].pop())
        nodedict = 'node'+str(bin_counter)
        bundle_list[nodedict]=[((sample[i])[0],temp)]
        bin_counter += 1

bin_adjust = bin_counter
bin_counter = 0
open_bins = []
num_fit = []
# Get sorted index of thread_counts to loop over.
sort_idx = np.array(thread_counts).argsort()[::-1]


for idx in sort_idx:
    found_fit = 0
    if (open_bins and thread_counts[idx]>0):
        for j in range(0, len(open_bins)):
            if found_fit == 0:
                if open_bins[j]+thread_counts[idx] <= max_threads_node:
                    if num_fit[j]+1 < max_fit:
                        open_bins[j]+=thread_counts[idx]
                        num_fit[j]+=1
                        temp = []
                        for tempi in range(thread_counts[idx]):
                            temp.append((sample[idx])[1].pop())
                        nodedict = 'node'+str(j+bin_adjust)
                        bundle_list[nodedict].append(((sample[idx])[0], temp))
                        found_fit = 1   
    if (found_fit == 0 and thread_counts[idx]>0):
        open_bins.append(thread_counts[idx])
        num_fit.append(1)
        temp = []
        for tempi in range(thread_counts[idx]):
            temp.append((sample[idx])[1].pop())
        nodedict = 'node'+str(bin_counter+bin_adjust)
        bundle_list[nodedict] = [((sample[idx])[0], temp)]
        bin_counter+=1

with open(outfile, 'w') as fp:
    json.dump(bundle_list, fp)

############################################
# Commented out alternative outfile format #
############################################
## prints one job bundle file per node
#nodenum = 0
#for key in bundle_list.keys():
#    temp_bundle = dict()
#    temp_bundle['node0']=bundle_list[key]
#    with open(sys.argv[2]+str(nodenum)+'.json', 'w') as fp:
#        json.dump(temp_bundle, fp)
#    nodenum+=1
############################################ 
