import numpy as np
import json
import sys
import glob
import os

def determine_bundles(sample, max_threads_node=64, max_instances_node=10):
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

    thread_counts = [len(item[1]) for item in sample]

    bundle_list = dict()
    bin_counter = 0

    for i in range(0, len(thread_counts)):
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
            for j in range(0, len(open_bins)):
                if found_fit == 0:
                    if open_bins[j]+thread_counts[idx] <= max_threads_node:
                        if num_fit[j]+1 < max_instances_node:
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
    if listofrestarts:
        for restart in listofrestarts:
            with open(restart) as json_input:
                restart_data = json.load(json_input)
            for node in restart_data.keys():
                for visit, sensors, numobjs in restart_data[node]:
                    key = str(visit)
                    if key in temp_sensors:
                        for sensor, numobj in zip(sensors, numobjs):
                            if numobj:
                                temp_sensors[key].append(sensor)
                                temp_numobjs[key].append(numobj)
                    else:
                        temp_sensors[key] = []
                        temp_numobjs[key] = [] 
                        for sensor, numobj in zip(sensors, numobjs):
                            if numobj:
                                temp_sensors[key].append(sensor)
                                temp_numobjs[key].append(numobj)
    remaining_work = [[key, temp_sensors[key], temp_numobjs[key]] for key in temp_sensors.keys()]
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
        for visit, sensors, numobjs in input_data[node]:
            # This line in particular may need changing depending on how we set up our output directory
            # structure.
            searchstring = visit.split('/')[-2]
            searchpath = os.path.join(outpath,searchstring)
            files = glob.glob(searchpath+'/*')
            for i in range(len(sensors)):
                sensor_nums = [str(s) for s in sensors[i] if s.isdigit()]
                fits_sensorstr='R'+sensor_nums[0]+sensor_nums[1]+'_S'+sensor_nums[2]+sensor_nums[3]
                ckpt_sensorstr='R_'+sensor_nums[0]+'_'+sensor_nums[1]+'_S_'+sensor_nums[2]+'_'+sensor_nums[3]
                matchingfits = [s for s in files if fits_sensorstr in s]
                check_fits = [s for s in matchingfits if '.fits' in s]
                matchingckpt = [s for s in files if ckpt_sensorstr in s]
                check_ckpt = [s for s in matchingckpt if '.ckpt' in s]

                if check_fits:
                    sensors[i] = []
                    numobjs[i] = []
                else:
                    # TODO: add code to recalculate number of remaining objects using the
                    # sqlite objects made for the sensors.
                    pass

    outfilename = (infile.split('/')[-1]).split('.')[0]
    with open(restartpath+outfilename+'_restart.json', 'w') as outfile:
        json.dump(input_data, outfile)
    return

