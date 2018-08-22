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

# Import determine job bundles...
sys.path.append('/mnt/scripts')
import determine_job_bundles as djb

nodelist = djb.determine_bundling(instcat_list_subset, '/mnt/scripts/outputs/bundle_list_subset'+str(subset_index)+'.json')
