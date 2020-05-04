import numpy as np
import math
import json
import sys
import glob

def determine_bundles(sample, mem_per_thread=2, mem_per_instance=10, max_mem_node=180, max_threads_node=64):
    """Given a sample which is a series of three tuple of
    [instcat, [listofsensors], [listofnumobjs]], calculate
    a semi-optimal bundling onto a given node architecture.
    Args:
       sample (list): list of lists as above.
       max_threads_node (int): number of hardware threads on a single node.
       max_instances_node (int): number of imsim instances to start, based
          on hardware limitations.

    Returns:
       bundle_list (dict): a semi-optimal bundling of the above data,
          with each key corresponding to a hardware node.
    """
    example = sample[0]
    print("example is: {} - expecting len(item[1]) to be a thread count".format(example))

    thread_counts = [len(item[1]) for item in sample]

    # quick loop to determine given an input mem_per_thread and mem_per_instance,
    # what the actual max threads are. If this is SMALLER than input max_threads,
    # this is corrected.
    mem=max_mem_node-mem_per_instance
    tmp = int(math.floor(mem / mem_per_thread))
    max_threads_node = min(tmp, max_threads_node)

    bundle_list = dict()
    bin_counter = 0

    # first loop. Fill each node to the absolute max number
    # of threads.
    for i in range(0, len(thread_counts)):
        print("determine_bundles: bin {}".format(bin_counter))
        print("thread_counts[i] = {}, max_threads_node = {}".format(thread_counts[i], max_threads_node))
        while thread_counts[i] >= max_threads_node:
            thread_counts[i] += -1*max_threads_node
            temp_sensor = []
            temp_num = []
            for tempi in range(max_threads_node):
                temp_sensor.append((sample[i])[1].pop())
                temp_num.append((sample[i])[2].pop())
            nodedict = 'node'+str(bin_counter)
            bundle_list[nodedict]=[((sample[i])[0],temp_sensor,temp_num)]
            bin_counter += 1

    print("determine_bundles: bundle list bin_count is {}".format(bin_counter))

    # adjust so we don't look into already "full" bins.
    bin_adjust = bin_counter
    bin_counter = 0
    open_bins = []
    num_fit = []

    # sort arrays by largest number of remaining threads to smallest.
    sort_idx = np.array(thread_counts).argsort()[::-1]
    for idx in sort_idx:
        found_fit = 0
        if (open_bins and thread_counts[idx]>0):
            if found_fit == 0:
                for j in range(0, len(open_bins)):
                    # this time, for each j we want to do the same thing, but now we will allow a
                    # variable SLICE to be added. Calculate instance memory the same...
                    instancecount = num_fit[j]+1
                    # amount of remaining memory AFTER added one new instance.
                    memremaining = max_mem_node - mem_per_thread*open_bins[j] - mem_per_instance*instancecount
                    sliceint = 0
                    # then calcluating the size of a slice that can fit in the box
                    thread_counter = open_bins[j]
                    if memremaining >= mem_per_thread and thread_counter < max_threads_node:
                        while (memremaining >= mem_per_thread) and (thread_counter < max_threads_node) and (sliceint < thread_counts[idx]):
                            memremaining = memremaining - mem_per_thread
                            sliceint += 1
                            thread_counter += 1
                    # if the number of remaining threads exceeds the allowed slice size, we just fit the slice
                    # size in.
                    if found_fit == 6 and thread_counts[idx] > sliceint and sliceint!=0:
                        if open_bins[j]+sliceint <= max_threads_node:
                            open_bins[j]+=sliceint
                            num_fit[j]+=1
                            temp_sensor = []
                            temp_num = []
                            for tempi in range(sliceint):
                                temp_sensor.append((sample[idx])[1].pop())
                                temp_num.append((sample[idx])[2].pop())
                            nodedict = 'node'+str(j+bin_adjust)
                            bundle_list[nodedict].append(((sample[idx])[0], temp_sensor, temp_num))
                            thread_counts[idx]+=-sliceint
                    # if the number of remaining threads is smaller than the allowed slice size, we fit the
                    # whole piece in.
                    if found_fit == 6 and thread_counts[idx] <= sliceint and sliceint!=0:
                        threadcount = open_bins[j]+thread_counts[idx]
                        threadcount_test = threadcount <= max_threads_node
                        memcount = threadcount*mem_per_thread + (num_fit[j]+1)*mem_per_instance
                        memcount_test = memcount <= max_mem_node
                        if threadcount_test == True and memcount_test == True:
                            open_bins[j]+=thread_counts[idx]
                            num_fit[j]+=1
                            temp_sensor = []
                            temp_num = []
                            for tempi in range(thread_counts[idx]):
                                temp_sensor.append((sample[idx])[1].pop())
                                temp_num.append((sample[idx])[2].pop())
                            nodedict = 'node'+str(j+bin_adjust)
                            bundle_list[nodedict].append(((sample[idx])[0], temp_sensor, temp_num))
                            found_fit = 1
        # if we found no fit yet, stuff it in a box and call it a day.
        if (found_fit == 0 and thread_counts[idx]>0):
            open_bins.append(thread_counts[idx])
            num_fit.append(1)
            temp_sensor = []
            temp_num = []
            for tempi in range(thread_counts[idx]):
                temp_sensor.append((sample[idx])[1].pop())
                temp_num.append((sample[idx])[2].pop())
            nodedict = 'node'+str(bin_counter+bin_adjust)
            bundle_list[nodedict] = [((sample[idx])[0], temp_sensor, temp_num)]
            bin_counter+=1

    return bundle_list

def determine_remaining_jobs(infile, restartpath):
    """Given a json file of unstarted jobs and a path to restart json files,
       generate a combined list of jobs needing to be started or restarted.
       Args:
          infile (str): Path to a json file in the same format as the determine_bundles
             output.
          restartpath (str): The directory path to where restart json files can be found.
       
       Returns:
          remaining_work (list): A list of lists containing instance catalog paths,
             sensors to simulate, and remaining number of objects to simulate. This
             is the primary input of determine_bundles.
    """

    print("determine_remaining_jobs: will read run data from infile={}".format(infile))
    with open(infile) as json_input:
        run_data = json.load(json_input)

    temp_sensors = dict()
    temp_numobjs = dict()

    for node in run_data.keys():
        for visit, sensors, numobjs in run_data[node]:
            key = str(visit)
            if key in temp_sensors:
                for sensor, numobj in zip(sensors, numobjs):
                    temp_sensors[key].append(sensor)
                    temp_numobjs[key].append(numobj)
            else:
                temp_sensors[key] = sensors
                temp_numobjs[key] = numobjs

    listofrestarts = glob.glob(restartpath+'*.json')
    print("determine_remaining_jobs: Count of restart files: {}".format(len(listofrestarts)))
    if listofrestarts:
        for restart in listofrestarts:
            print("determine_remaining_jobs: processing restart file {}".format(restart))
            with open(restart) as json_input:
                restart_data = json.load(json_input)
            for node in restart_data.keys():
                print("determine_remaining_jobs: node {} = {}".format(node, restart_data[node]))
                for visit, sensors, numobjs in restart_data[node]:
                    key = str(visit)
                    if key in temp_sensors:
                        for sensor, numobj in zip(sensors, numobjs):
                   #         if numobj:
                                temp_sensors[key].append(sensor)
                                temp_numobjs[key].append(numobj)
                    else:
                        temp_sensors[key] = []
                        temp_numobjs[key] = [] 
                        for sensor, numobj in zip(sensors, numobjs):
                   #         if numobj:
                                temp_sensors[key].append(sensor)
                                temp_numobjs[key].append(numobj)
    remaining_work = [[key, temp_sensors[key], temp_numobjs[key]] for key in temp_sensors.keys()]
    print("determine_remaining_jobs: remaining_work has length {}".format(len(remaining_work)))
    print("determine_remaining_jobs:  {}".format(remaining_work))
    print("determine_remaining_jobs: first remaining_work entry is {}".format(remaining_work[0]))
    return remaining_work

def check_job_success(infile, outpath, restartpath):
    """Take an input json file in the determine_bundles format and walk over output
       directories in standard ordering in order to determine if a job exited complete
       or needs to be put back into the job queue. It then outputs the remaining work
       as a json file to the restart path, with an additional _restart flag.

       Args:
          infile (str): path to an input json file in determine_bundles format.
          outpath (str): path to start of imSim outputs - specifically, the level
             at which things break into multiple bands. Note this structure assumes
             checkpoint files are written to output directories.
          restartpath (str): path to a directory to store restart files in. Should be
             a seperate restart directory if dividing along multiple workflows, as the
             remaining work finder will pull the entire directory based on .json endings.
      
       Returns:
          Writes a json file to the restart path.
    """
    with open(infile) as fp:
        input_data = json.load(fp)

    for node in input_data.keys():
        print("check_job_success: before check, node {}, input_data[node] = {}".format(node, input_data[node]))
        for visit, sensors, numobjs in input_data[node]:
            # This line in particular may need changing depending on how we set up our output directory
            # structure.
            print("Checking for completed work: node {}, visit {}".format(node, visit))
            searchstring = str('/'.join(visit.split('/')[-2:-1])+'/')
            pat = outpath+searchstring+'*'
            files = glob.glob(pat)
            print("Checking for completed work: node {}, visit {}: glob {} found {} names".format(node, visit, pat, len(files)))
            for i in range(len(sensors)):
                print("Checking for completed work: node {}, visit {}, sensor index = {}".format(node, visit, i))
                sensor_nums = [str(s) for s in sensors[i] if s.isdigit()]
                gz_sensorstr='R'+sensor_nums[0]+sensor_nums[1]+'_S'+sensor_nums[2]+sensor_nums[3]
                ckpt_sensorstr='R'+sensor_nums[0]+sensor_nums[1]+'_S'+sensor_nums[2]+sensor_nums[3]
                matchinggz = [s for s in files if gz_sensorstr in s]
                check_gz = [s for s in matchinggz if '.fits' in s]
                matchingckpt = [s for s in files if ckpt_sensorstr in s]
                check_ckpt = [s for s in matchingckpt if '.ckpt' in s]

                if check_gz and not check_ckpt:
                    #print("Found completed work: node {}, visit {}, sensor index = {}".format(node, visit, i))
                    sensors[i] = []
                    numobjs[i] = []
                else:
                    # TODO: add code to recalculate number of remaining objects using the
                    # sqlite objects made for the sensors.
                    pass
        print("check_job_success: after check, node {}, input_data[node] = {}".format(node, input_data[node]))

    emptynode_list = []
    for node in input_data.keys():
        indexint = 0
        emptyvisit_list = []
        for visit, sensors, numobjs in input_data[node]:
            sensors = [sens for sens in sensors if sens != []]
            numobjs = [nums for nums in numobjs if nums != []]
            if len(sensors) == 0: emptyvisit_list.append(indexint)
            (input_data[node][indexint])[1] = sensors
            (input_data[node][indexint])[2] = numobjs
            indexint += 1
        if emptyvisit_list:
           for index in sorted(emptyvisit_list, reverse=True):
               del input_data[node][index]
        if not input_data[node]: emptynode_list.append(node)
    for node in emptynode_list:
        del input_data[node]

    outfilename = (infile.split('/')[-1]).split('.')[0]
    fn = restartpath+outfilename+'_restart.json'
    print("Writing restart path file: {}".format(fn))
    print("Restart path file will have {} entries".format(len(input_data)))
    with open(fn, 'w') as outfile:
        json.dump(input_data, outfile)
    return

