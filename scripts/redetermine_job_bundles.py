import numpy as np
import json
import sys

# hard coded hardware limitations
max_threads_node = 64
max_fit = 5 # again, currently harded coded; keeps from running out of memory
             # on a node due to too many visits.

# takes two system arguments - input json and output json

# Read in JSON file containing tuples of (instcat, [list of sensors]) for each job.
with open(sys.argv[1]) as json_input:
    run_data = json.load(json_input)

# Preprocessing step to recombine any two with the same instance catalogs.
temp_data = dict()
for visit, sensors in run_data:
    key = str(visit)
    if key in temp_data:
        for sensor in sensors:
            temp_data[key].append(sensor)
    else:
        temp_data[key] = sensors

sample = []
for key in temp_data.keys():
    sample.append([key, temp_data[key]])

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
    if open_bins:
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

with open(sys.argv[2], 'w') as fp:
    json.dump(bundle_list, fp)

