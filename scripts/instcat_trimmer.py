import json
import os.path
import sys
import trim_sensors
from progressdb import ProgressDB

def determine_instcat_work(instcat_list, outfile):
    """Determine how many sensors each visit will take and the number of
       objects to simulate. Then output a single json file containing a list of all
       the work to be done.

       Args:
          instcat_list (list): a list of paths to all instance catalogs.
          outfile (str): path and name of where you want the master list to be written.
    """
    #db = ProgressDB() # connect to the database in order to start storing information about work.
    run20_region = trim_sensors.Run20Region()
    #instcat_list = [os.path.abspath(instcat_file) for instcat_file in instcat_list]
    sensors_list = [run20_region.trim_sensors(instcat) for instcat in instcat_list]
    work_data = [ [instcat, sensors] for (instcat, sensors) in zip(instcat_list, sensors_list)]
    for work in work_data:
        # first we want to add the instance catalog number.
        visit_id = int(os.path.basename(os.path.normpath(work[0])).split('_')[-1].split('.txt')[0])
        #db.put_visit(visit_id)
        # and then for each sensor, we want to add it to the database.
        for sensor in work[1]:
            sensor_name = ''.join([s for s in sensor if s.isdigit()])
            #db.init_sensor_visit(visit_id, sensor_name, False)
        numobj = [0 for sensor in work[1] ]
        work.append(numobj)

    with open(outfile, 'w') as fp:
        json.dump(work_data, fp)

    return
