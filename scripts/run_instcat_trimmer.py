import json
import sys
import os

# Change to Singularity working directory.
os.chdir('/mnt/cwd')

# Take subset index as argument
subset_index = sys.argv[1]

# Open up subset matching this.
with open('/mnt/scripts/outputs/instcat_list_subset'+str(subset_index)+'.json', 'r') as f:
    instcat_list_subset = json.load(f)

# Import instcat trimmer
sys.path.append('/mnt/scripts')
import instcat_trimmer as ict

ict.determine_instcat_work(instcat_list_subset, '/mnt/scripts/outputs/worklist_subset'+str(subset_index)+'.json')
