# Standard section importing imsim and preparing parsl for use.
import parsl
import desc.imsim
import numpy as np

from parsl.app.app import bash_app, python_app
from parsl.configs.local_threads import config

parsl.load(config)

@python_app
def get_object_entries(visit_object, chip_name):
    """Get the number of objects on the chip and return a list of
       them. If under a minimum set by the instance catalog, return
       an empty list.
       INPUT: visit_object (InstCatTrimmer object), chip_name (string)
       OUTPUT: object_list (list)
    """
    object_list = visit_object.get_object_entries(chip_name)
    # could probably write this as one line? Maybe bad coding style.
    return object_list

def determine_sensor_jobs(instcat_file):
    """Determine which sensors in a given visit need imSim work done
       and return the list of chips that you want to sim on.
       INPUT: instcat_file (string)
       OUTPUT: chip_sim_list (lists)
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

    # create an empty list to fill with lists.
    sensor_job_queue = []

    # list comprehension to generate the sensor job queue for a single visit.
    [sensor_job_queue.append(get_object_entries(visit_object, chip_name).result())
     for chip_name in chip_list]

    # We optimally want to prune the list so we don't pass empty around.
    chip_sim_list = []
    [chip_sim_list.append(chip_list[i] for i in range(0, len(chip_list)) if sensor_job_queue[i]]

    # Commented out code in case we want to pass aroudn the sensor job queue instead of
    # calculating it twice.
    #sensor_job_queue[:] = [item for item in sensor_job_queue if item]

    return chip_sim_list

def determine_bundling(instcat_list):
    """Determine how many sensors each visit takes and determines which
       jobs should be bundled together. Needs a list of instcat files,
       as well as information about the HPC infrastructure. Returns a list of
       chips to run on for each visit and an optimal bundling of them for
       distributing them across nodes, as well as the instance catalog.
 
       INPUT: instcat_list (list)
       OUTPUT: bundle_list (list)
    """
    # We're going to assume we can pass in a list of instcat files for now,
    # but we can probably think of some more clever way to parse over this
    # for a directory.

    # This is going to be filled with a list of chips that need to be run
    # for every single visit.
    visit_job_queue = []
    [visit_job_queue.append(determine_sensor_jobs(instcat_file))
     for instcat_file in instcat_list]

    # Each entry should now be list of sensors that need to be run and this point.
    # Our new problem is now basically the bin packing problem. Pack each job together
    # in a minimal number of bins.

    # Start by getting the number of threads we will need for each visit.
    thread_counts = []
    [thread_counts.append(sum(job_queue)) for job_queue in visit_job_queue]

    # The trick here is now that we probably want to take the list, sort it
    # and then use FFD to fit them into bins. The trick is sorting, but maintaining
    # necessary information about the object. So we really want a sorted index.

    max_threads_node = 63 # hard coded for now
    bin_counter = 0

    # open up a list to store our lists.
    bundle_list = [[] for thread_count in thread_counts]

    # First; if the threads in a job are greater than the max number of threads/node,
    # we should give 64 threads a node of their own.

    for i in range(0, len(thread_counts)):
        while thread_counts[i] >= max_threads_node:
            thread_counts[i] += -1*max_threads_node
            temp = []
            for tempi in range(max_threads_node):
                temp.append(visit_job_queue[i].pop())
            bundle_list[i].append([bin_counter,temp,instcat_list[i]])
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
        # If it fits in an existing bin, add it.
        if open_bins:
            for j in range(0, len(open_bins)):
                if open_bins[j]+thread_counts[idx] <= max_threads_node:
                    if num_fit[j]+1 < max_fit:
                        open_bins[j]+=thread_counts[idx]
                        num_fit[j]+=1
                        temp = []
                        for tempi in range(thread_counts[idx]):
                            temp.append(visit_job_queue[idx].pop())
                        bundle_list[idx].append([j+bin_adjust,temp,instcat_list[idx]])
                        found_fit = 1   
        # If it does not fit in an existing bin, add a new bin!
        if found_fit == 0:
            open_bins.append(thread_counts[idx])
            num_fit.append(1)
            temp = []
            for tempi in range(thread_counts[idx]):
                temp.append(visit_job_queue[idx].pop())
            bundle_list[idx].append([bin_counter+bin_adjust,temp,instcat_list[idx]])
            bin_counter+=1

    # Note, this is NOT an optimal algorithm. There is likely to be some underpacked nodes,
    # as the algorithm does NOT split groups once they are below 64 threads to fit them into
    # boxes.

    return bundle_list
