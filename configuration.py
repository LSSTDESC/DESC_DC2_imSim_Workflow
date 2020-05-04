import os
import logging
from parsl.config import Config

from parsl.addresses import address_by_hostname

# for theta
#from parsl.executors.mpix import MPIExecutor
from parsl.providers import CobaltProvider
from parsl.launchers import SimpleLauncher
from parsl.executors.threads import ThreadPoolExecutor
from parsl.monitoring.monitoring import MonitoringHub

# for cori htc
from parsl.providers import LocalProvider
from parsl.providers import SlurmProvider
from parsl.launchers import SrunLauncher
from parsl.launchers import AprunLauncher
from parsl.executors import HighThroughputExecutor

# some configuration varies based on machine, and this
# will swtich.
# choose either "core" or "theta" or "theta_local"
MACHINEMODE="theta"

 # this should scale up to 802 in real life, or up to 8 or 16 in debug queue
 # note at present, 1 is required to run the rank 0 controller, not any app tasks
 # so the minimum value to make progress is 2

#COMPUTE_NODES=128
#THETA_QUEUE="default"
#WALLTIME="02:58:30"

#COMPUTE_NODES=2048
#THETA_QUEUE="R.LSSTADSP_DESC"
#WALLTIME="16:30:00"

#COMPUTE_NODES=8
#THETA_QUEUE="debug-flat-quad"
#WALLTIME="00:58:00"

#COMPUTE_NODES=256
#THETA_QUEUE="default"
#WALLTIME="05:50:00"

COMPUTE_NODES=128
THETA_QUEUE="regular"
CORI_QUEUE="regular" # or debug
WALLTIME="00:55:00"

ACCOUNT="LSSTADSP_DESC"


# /-terminated path to work and output base dir
work_and_out_path = "/projects/LSSTsky/Run3.0i/y1-ddf/"
#work_and_out_path = "/global/cscratch1/sd/descim/test/workpath/"

# singularity image containing the DESC_DC2_imSim_Workflow distro
#singularity_img = "benclifford/alcf_run2.0i:20181115e" # -- benc test
# singularity_img = "lsstdesc/dc2-imsim:Run2.2i-production-v1" # -- cori/shifter
singularity_img = work_and_out_path + "dc2-imsim_Run2.2i-production-v1.simg" # -- theta/singularity

#singularity_url = "shub://benclifford/DESC_DC2_imSim_Workflow"
singularity_url = "docker://lsstdesc/dc2-imsim:Run2.2i-production-v1"

# whether to download the singularity image or to
# use the local copy from (eg) a previous run
# probably should be set to True unless testing
# interactively:
singularity_download = False

# should we validate that the transfer was successful?
validate_transfer = False

# should we re-generate the initial worklist or assume that
# what is on disk in original_work_list is sufficient?
worklist_generate = False

# set to true to use fake short sleep instead of singularity
fake = False

#tarball_list = "/global/cscratch1/sd/desc/DC2/Run2.1i/run201903/firsttwoyears_tarballs.json"
imsim_config = "/projects/LSSTsky/Run3.0i/DESC_DC2_imSim_Workflow/parsl_imsim_configs"

archive_base = "/projects/LSSTsky/Run3.0i/DESC_DC2_imSim_Workflow/"

inst_cat_root = "/projects/LSSTsky/Run3.0i/y1-ddf/instCats"

# trickle-loop parameters
# submit 10% more jobs than we have nodes for so that there are
# at least some waiting to run
max_simultaneous_submit = COMPUTE_NODES * 1.1

rebalance_seconds = 60 * 60
#rebalance_seconds = 4 * 60 * 60

trickle_loop_seconds = 60

# the (expensive to generate) overall work list, which will include
# everything we think needs to have been done, whether it has or not
#original_work_list = "/projects/LSSTADSP_DESC/benc/backup_worklist_2.0_153.json"
# original_work_list = "/projects/LSSTADSP_DESC/benc/full_worklist.json"
original_work_list = work_and_out_path+"worklist-gen3.json"

# this is where (possibly auto-generated) bundle list will be stored
bundle_lists = work_and_out_path+"parsl-auto-bundles.json"

# a temp working directory for the bundler
bundler_restart_path = work_and_out_path+"bundler-restart-tmp/"

# ip (or hostname, probably) of the submitting host
SUBMIT_HOST_IP = "10.236.1.194"

# parameters above are ones you're likely to want
# to change
# stuff below, probably not so much


JOB_URL = "tcp://{}:50005".format(SUBMIT_HOST_IP)
RESULT_URL = "tcp://{}:50006".format(SUBMIT_HOST_IP)

launch_cmd='which python3; \
aprun -b -cc depth -j 1 -d 64 -n $(($COBALT_PARTSIZE * {tasks_per_node})) -N {tasks_per_node} \
python3 /projects/LSSTADSP_DESC/Run2.0i-parsl/parsl/parsl/executors/mpix/fabric_singlethreaded.py -d --task_url={task_url} --result_url={result_url}'

overrides="""module load intelpython35/2017.0.035                                                                                                                                                                              
source activate parsl_env
module swap cray-mpich cray-mpich-abi                                                                                                                                                                                                          
export LD_LIBRARY_PATH=${CRAY_LD_LIBRARY_PATH}:$LD_LIBRARY_PATH                                                                                                                                                                                
ulimit -c unlimited
ulimit -Sv 120000000

export SINGULARITY_HOME=/home/antoniov                                                                                                                                                                                                                     
export OMP_NUM_THREADS=1"""

aprun_overrides = """-cc depth -j 1 -d 64"""

theta_executor = HighThroughputExecutor(
            label='worker-nodes',
            address=address_by_hostname(),
            worker_debug=True,
            suppress_failure=False,
            poll_period = 5000,
            cores_per_worker = 256,
            heartbeat_period = 300,
            heartbeat_threshold = 1200,
            provider=LocalProvider(
                nodes_per_block = 128,
                init_blocks=1,
                min_blocks=1,
                max_blocks=1,
                launcher=AprunLauncher(overrides=aprun_overrides),
                walltime=WALLTIME
            ),
        )

cori_in_salloc_executor = HighThroughputExecutor(
            label='worker-nodes',
            address=address_by_hostname(),
            worker_debug=True,
            suppress_failure=True,
            poll_period = 5000,   
            cores_per_worker = 272,
            heartbeat_period = 300,
            heartbeat_threshold = 1200,
            provider=LocalProvider(
                nodes_per_block = 128,
                init_blocks=1,
                min_blocks=1,
                max_blocks=1,
                launcher=SrunLauncher(overrides='--slurmd-debug=verbose'),
                walltime=WALLTIME
            ),
        )


cori_queue_executor = HighThroughputExecutor(
            label='worker-nodes',
            address=address_by_hostname(),
            worker_debug=True,
            cores_per_worker = 272,
            heartbeat_period = 300,
            heartbeat_threshold = 1200,
            provider=SlurmProvider(
                CORI_QUEUE,
                nodes_per_block=COMPUTE_NODES,
                exclusive = True,
                init_blocks=1,
                min_blocks=1,
                max_blocks=1,
                scheduler_options="""#SBATCH --constraint=knl""",
                launcher=SrunLauncher(),
                cmd_timeout=60,
                walltime=WALLTIME
            ),
        )

local_executor = ThreadPoolExecutor(max_threads=2, label="submit-node")

if MACHINEMODE == "cori":
    parsl_config = Config(
        executors=[ cori_in_salloc_executor, local_executor ],
        run_dir="{}/runinfo/".format(work_and_out_path),
        monitoring=MonitoringHub(
            hub_address=address_by_hostname(),
            hub_port=55055,
            monitoring_debug=False,
            resource_monitoring_interval=10,
        )
    )
elif MACHINEMODE == "theta":
    parsl_config = Config(
        executors=[ theta_executor, local_executor ],
        run_dir="{}/runinfo/".format(work_and_out_path),
        monitoring=MonitoringHub(
            hub_address=address_by_hostname(),
            hub_port=55055,
            monitoring_debug=False,
            resource_monitoring_interval=3*60,
        )
    )
elif MACHINEMODE == "theta_local":
    parsl_config = Config(
        executors=[local_executor],
        run_dir="{}/runinfo/".format(work_and_out_path),
        monitoring=MonitoringHub(
            hub_address=address_by_hostname(),
            hub_port=55055,
            monitoring_debug=False,
            resource_monitoring_interval=3*60,
        )
    )
