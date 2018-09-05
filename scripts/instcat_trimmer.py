import desc.imsim as imsim
import json
import os.path

def get_object_entries(visit_object, chip_name):
    """Pulls the number of objects on the chip and returns a list of them.
       Returns an empty list if under the minimum set by the instance
       catalog.

       Args:
          visit_object (InstCatTrimmer object): instantiation of the InstCatTrimmer class.
          chip_name (str): imSim name of the sensor to operate on.

       Returns:
          object_list (list): list containing num of objects to simulate on a given
             chip.
    """
    return visit_object.get_object_entries(chip_name)

def determine_sensor_jobs(instcat_file):
    """Determines which sensors in a given visit need imSim work and returns both the
       list of chips you want to simulate on and the number of objects on each chip.

       Args:
          instcat_file (str): The path to a given instcat file.

       Returns:
          visit_work (list): a list of lists containing the instance catalog string,
             a list of sensors, and a list of objects on each sensor.
    """
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

    visit_object = imsim.trim.InstCatTrimmer(instcat_file)

    object_lists = {chip_name: get_object_entries(visit_object, chip_name) for chip_name in chip_list}
    job_list = [chip_name for chip_name in object_lists if object_lists[chip_name]]
    num_obj_list = [len(object_lists[chip_name]) for chip_name in object_lists if object_lists[chip_name]]

    return [instcat_file, job_list, num_obj_list]

def determine_instcat_work(instcat_list, outfile):
    """Determine how many sensors each visit will take and the number of
       objects to simulate. Then output a single json file containing a list of all
       the work to be done.

       Args:
          instcat_list (list): a list of paths to all instance catalogs.
          outfile (str): path and name of where you want the master list to be written.
    """

    instcat_list = [os.path.abspath(instcat_file) for instcat_file in instcat_list]
    work_data = [determine_sensor_jobs(instcat_file) for instcat_file in instcat_list]

    with open(outfile, 'w') as fp:
        json.dump(work_data, outfile)

    return
