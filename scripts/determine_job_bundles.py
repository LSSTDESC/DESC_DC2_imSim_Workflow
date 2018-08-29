# Standard section importing imsim and preparing parsl for use.
import desc.imsim as imsim
import numpy as np
import sys
import os.path
import json

# set this way for being used in Parsl in the future.
def get_object_entries(visit_object, chip_name):
    """Get the number of objects on the chip and return a list of
       them. If under a minimum set by the instance catalog, return
       an empty list.
       INPUT: visit_object (InstCatTrimmer object), chip_name (string)
       OUTPUT: object_list (list)
    """
    object_list = visit_object.get_object_entries(chip_name)
    return object_list

def determine_sensor_jobs(instcat_file):
    """Determine which sensors in a given visit need imSim work done
       and return the list of chips that you want to sim on.
       INPUT: instcat_file (string)
       OUTPUT: job_list, num_obj_list
    """

    # we'll need a list of all 189 chips here, to loop over later.
    chip_list = ['R:0,1 S:0,0', 'R:0,1 S:0,1', 'R:0,1 S:0,2', 'R:0,1 S:1,0', 'R:0,1 S:1,1', 'R:0,1 S:1,2',
                 'R:0,1 S:2,0', 'R:0,1 S:2,1', 'R:0,1 S:2,2', 'R:0,2 S:0,0', 'R:0,2 S:0,1', 'R:0,2 S:0,2',
                 'R:0,2 S:1,0', 'R:0,2 S:1,1', 'R:0,2 S:1,2', 'R:0,2 S:2,0', 'R:0,2 S:2,1', 'R:0,2 S:2,2',
                 'R:0,3 S:0,0', 'R:0,3 S:0,1', 'R:0,3 S:0,2', 'R:0,3 S:1,0', 'R:0,3 S:1,1', 'R:0,3 S:1,2',
                 'R:0,3 S:2,0', 'R:0,3 S:2,1', 'R:0,3 S:2,2', 'R:1,0 S:0,0', 'R:1,0 S:0,1', 'R:1,0 S:0,2',
                 'R:1,0 S:1,0', 'R:1,0 S:1,1', 'R:1,0 S:1,2', 'R:1,0 S:2,0', 'R:1,0 S:2,1', 'R:1,0 S:2,2',
                 'R:1,1 S:0,0', 'R:1,1 S:0,1', 'R:1,1 S:0,2', 'R:1,1 S:1,0', 'R:1,1 S:1,1', 'R:1,1 S:1,2',
                 'R:1,1 S:2,0', 'R:1,1 S:2,1', 'R:1,1 S:2,2', 'R:1,2 S:0,0', 'R:1,2 S:0,1', 'R:1,2 S:0,2',
                 'R:1,2 S:1,0', 'R:1,2 S:1,1', 'R:1,2 S:1,2', 'R:1,2 S:2,0', 'R:1,2 S:2,1', 'R:1,2 S:2,2',
                 'R:1,3 S:0,0', 'R:1,3 S:0,1', 'R:1,3 S:0,2', 'R:1,3 S:1,0', 'R:1,3 S:1,1', 'R:1,3 S:1,2',
                 'R:1,3 S:2,0', 'R:1,3 S:2,1', 'R:1,3 S:2,2', 'R:1,4 S:0,0', 'R:1,4 S:0,1', 'R:1,4 S:0,2',
                 'R:1,4 S:1,0', 'R:1,4 S:1,1', 'R:1,4 S:1,2', 'R:1,4 S:2,0', 'R:1,4 S:2,1', 'R:1,4 S:2,2',
                 'R:2,0 S:0,0', 'R:2,0 S:0,1', 'R:2,0 S:0,2', 'R:2,0 S:1,0', 'R:2,0 S:1,1', 'R:2,0 S:1,2',
                 'R:2,0 S:2,0', 'R:2,0 S:2,1', 'R:2,0 S:2,2', 'R:2,1 S:0,0', 'R:2,1 S:0,1', 'R:2,1 S:0,2',
                 'R:2,1 S:1,0', 'R:2,1 S:1,1', 'R:2,1 S:1,2', 'R:2,1 S:2,0', 'R:2,1 S:2,1', 'R:2,1 S:2,2',
                 'R:2,2 S:0,0', 'R:2,2 S:0,1', 'R:2,2 S:0,2', 'R:2,2 S:1,0', 'R:2,2 S:1,1', 'R:2,2 S:1,2',
                 'R:2,2 S:2,0', 'R:2,2 S:2,1', 'R:2,2 S:2,2', 'R:2,3 S:0,0', 'R:2,3 S:0,1', 'R:2,3 S:0,2',
                 'R:2,3 S:1,0', 'R:2,3 S:1,1', 'R:2,3 S:1,2', 'R:2,3 S:2,0', 'R:2,3 S:2,1', 'R:2,3 S:2,2',
                 'R:2,4 S:0,0', 'R:2,4 S:0,1', 'R:2,4 S:0,2', 'R:2,4 S:1,0', 'R:2,4 S:1,1', 'R:2,4 S:1,2',
                 'R:2,4 S:2,0', 'R:2,4 S:2,1', 'R:2,4 S:2,2', 'R:3,0 S:0,0', 'R:3,0 S:0,1', 'R:3,0 S:0,2',
                 'R:3,0 S:1,0', 'R:3,0 S:1,1', 'R:3,0 S:1,2', 'R:3,0 S:2,0', 'R:3,0 S:2,1', 'R:3,0 S:2,2',
                 'R:3,1 S:0,0', 'R:3,1 S:0,1', 'R:3,1 S:0,2', 'R:3,1 S:1,0', 'R:3,1 S:1,1', 'R:3,1 S:1,2',
                 'R:3,1 S:2,0', 'R:3,1 S:2,1', 'R:3,1 S:2,2', 'R:3,2 S:0,0', 'R:3,2 S:0,1', 'R:3,2 S:0,2',
                 'R:3,2 S:1,0', 'R:3,2 S:1,1', 'R:3,2 S:1,2', 'R:3,2 S:2,0', 'R:3,2 S:2,1', 'R:3,2 S:2,2',
                 'R:3,3 S:0,0', 'R:3,3 S:0,1', 'R:3,3 S:0,2', 'R:3,3 S:1,0', 'R:3,3 S:1,1', 'R:3,3 S:1,2',
                 'R:3,3 S:2,0', 'R:3,3 S:2,1', 'R:3,3 S:2,2', 'R:3,4 S:0,0', 'R:3,4 S:0,1', 'R:3,4 S:0,2',
                 'R:3,4 S:1,0', 'R:3,4 S:1,1', 'R:3,4 S:1,2', 'R:3,4 S:2,0', 'R:3,4 S:2,1', 'R:3,4 S:2,2',
                 'R:4,1 S:0,0', 'R:4,1 S:0,1', 'R:4,1 S:0,2', 'R:4,1 S:1,0', 'R:4,1 S:1,1', 'R:4,1 S:1,2',
                 'R:4,1 S:2,0', 'R:4,1 S:2,1', 'R:4,1 S:2,2', 'R:4,2 S:0,0', 'R:4,2 S:0,1', 'R:4,2 S:0,2',
                 'R:4,2 S:1,0', 'R:4,2 S:1,1', 'R:4,2 S:1,2', 'R:4,2 S:2,0', 'R:4,2 S:2,1', 'R:4,2 S:2,2',
                 'R:4,3 S:0,0', 'R:4,3 S:0,1', 'R:4,3 S:0,2', 'R:4,3 S:1,0', 'R:4,3 S:1,1', 'R:4,3 S:1,2',
                 'R:4,3 S:2,0', 'R:4,3 S:2,1', 'R:4,3 S:2,2']

    # instantiate the InstCatTrimmer object.
    visit_object = imsim.trim.InstCatTrimmer(instcat_file)

    # Calculate number of objects to sim on each sensor.
    # We optimally want to prune the list so we don't pass empty around.
    object_lists = {chip_name: get_object_entries(visit_object, chip_name) for chip_name in chip_list}
    job_list = [chip_name for chip_name in object_lists if object_lists[chip_name]]
    num_obj_list = [len(object_lists) for chip_name in object_lists if object_lists[chip_name]]

    return job_list, num_obj_list

def determine_bundling(instcat_list, outfile):
    """Determine how many sensors each visit takes and determines which
       jobs should be bundled together. Needs a list of instcat files,
       and hard codes some infrastucture based parameters. Return a dictionary
       where each key is a node ID and has an entry tuple that contains both the
       associated instance catalog and sensors to run. It also saves a json of the bundle_list.
 
       INPUT: instcat_list (list), outfile (file destination)
       OUTPUT: bundle_list (list)
    """
    # We're going to assume we can pass in a list of instcat files for now,
    # but we can probably think of some more clever way to parse over this
    # for a directory.

    instcat_list = [os.path.abspath(instcat_file) for instcat_file in instcat_list]

    # This is going to be filled with a list of chips that need to be run
    # for every single visit.
    visit_job_queue = [determine_sensor_jobs(instcat_file) for instcat_file in instcat_list]
    print(visit_job_queue)

    # Each entry should now be list of sensors that need to be run and this point.
    # Our new problem is now basically the bin packing problem. Pack each job together
    # in a minimal number of bins.

    # Start by getting the number of threads we will need for each visit.
    thread_counts = [len(job_queue[0]) for job_queue in visit_job_queue]

    # The trick here is now that we probably want to take the list, sort it
    # and then use FFD to fit them into bins. The trick is sorting, but maintaining
    # necessary information about the object. So we really want a sorted index.

    max_threads_node = 63 # hard coded for now, straightforward to add as parameter.
    bin_counter = 0

    # Instead open up Dict for storing our lists in.
    bundle_list = dict()

    # First; if the threads in a job are greater than the max number of threads/node,
    # we should give 64 threads a node of their own.

    for i in range(0, len(thread_counts)):
        while thread_counts[i] >= max_threads_node:
            thread_counts[i] += -1*max_threads_node
            temp_sensor = []
            temp_num = []
            for tempi in range(max_threads_node):
                temp_sensor.append((visit_job_queue[i])[0].pop())
                temp_num.append((visit_job_queue[i])[1].pop())

            nodedict='node'+str(bin_counter)
            bundle_list[nodedict]=[(instcat_list[i],temp_sensor,temp_num)]

            bin_counter += 1

    # adjust so we don't look into bins we've already stuffed full.
    bin_adjust = bin_counter
    bin_counter = 0
    open_bins = []
    num_fit = []
    max_fit = 10 # again, currently harded coded; keeps from running out of memory
                 # on a node due to too many visits.

    # Get sorted index of thread_counts to loop over.
    sort_idx = np.array(thread_counts).argsort()[::-1]

    # Go through items from largest to smallest.
    for idx in sort_idx:
        found_fit = 0
        if open_bins:
            for j in range(0, len(open_bins)):
                if found_fit == 0:
                    if open_bins[j]+thread_counts[idx] <= max_threads_node:
                        if num_fit[j]+1 < max_fit:
                            open_bins[j]+=thread_counts[idx]
                            num_fit[j]+=1
                            temp_sensor = []
                            temp_num = []
                            for tempi in range(thread_counts[idx]):
                                temp_sensor.append((visit_job_queue[idx])[0].pop())
                                temp_num.append((visit_job_queue[idx])[1].pop())
                            nodedict = 'node'+str(j+bin_adjust)
                            bundle_list[nodedict].append((instcat_list[idx], temp_sensor, temp_num))
                            found_fit = 1   
        if found_fit == 0:
            open_bins.append(thread_counts[idx])
            num_fit.append(1)
            temp_sensor = []
            temp_num = []
            for tempi in range(thread_counts[idx]):
                temp_sensor.append((visit_job_queue[idx])[0].pop())
                temp_num.append((visit_job_queue[idx])[1].pop())
            nodedict = 'node'+str(bin_counter+bin_adjust)
            bundle_list[nodedict] = [(instcat_list[idx], temp_sensor, temp_num)]
            bin_counter+=1

    # Note, this is NOT an optimal algorithm. There is likely to be some underpacked nodes,
    # as the algorithm does NOT split groups once they are below 64 threads to fit them into
    # boxes.

    with open(outfile, 'w') as fp:
        json.dump(bundle_list, fp)

    return bundle_list
