from libsubmit.providers import CobaltProvider
from libsubmit.launchers import SimpleLauncher

from parsl.config import Config
from parsl.executors.mpix import MPIExecutor
from parsl.executors.threads import ThreadPoolExecutor

 # this should scale up to 802 in real life, or up to 8 or 16 in debug queue
 # note at present, 1 is required to run the rank 0 controller, not any app tasks
 # so the minimum value to make progress is 2

#THETA_NODES=128
#THETA_QUEUE="default"
#WALLTIME="02:58:30"

#THETA_NODES=2048
#THETA_QUEUE="R.LSSTADSP_DESC"
#WALLTIME="16:30:00"

#THETA_NODES=8
#THETA_QUEUE="debug-flat-quad"
#WALLTIME="00:58:00"

#THETA_NODES=256
#THETA_QUEUE="default"
#WALLTIME="05:50:00"

THETA_NODES=2048
THETA_QUEUE="R.LSSTADSP_DESC"
WALLTIME="47:28:00"

ACCOUNT="LSSTADSP_DESC"


# /-terminated path to work and output base dir
work_and_out_path = "/projects/LSSTADSP_DESC/benc/"

# singularity image containing the ALCF_1.2i distro
singularity_img = work_and_out_path + "ALCF_1.2.simg"

#singularity_url = "shub://benclifford/ALCF_1.2i"
singularity_url = "shub://LSSTDESC/ALCF_1.2i:latest"

# whether to download the singularity image or to
# use the local copy from (eg) a previous run
# probably should be set to True unless testing
# interactively
singularity_download = True

# should we re-generate the initial worklist or assume that
# what is on disk in original_work_list is sufficient?
worklist_generate = False

# set to true to use fake short sleep instead of singularity
fake = False


inst_cat_root = "/projects/LSSTADSP_DESC/Run2.0i_fixed/fixed_dust_180917/"
# inst_cat_root = "/projects/LSSTADSP_DESC/Run2.0i_fixed/fixed_dust_new/"
# inst_cat_root = "/projects/LSSTADSP_DESC/ALCF_1.2i/inputs/"
# inst_cat_root = "/projects/LSSTADSP_DESC/benc/2.0i_sample/inputs/"


# trickle-loop parameters
# submit 10% more jobs than we have nodes for so that there are
# at least some waiting to run
max_simultaneous_submit = THETA_NODES * 1.1

rebalance_seconds = 3 * 60
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

mpi_executor = MPIExecutor(
            label="worker-nodes",
            jobs_q_url=JOB_URL,
            results_q_url=RESULT_URL,
            launch_cmd=launch_cmd,
            provider=CobaltProvider(
                queue=THETA_QUEUE,
                launcher=SimpleLauncher(),
                walltime=WALLTIME,
                nodes_per_block=THETA_NODES,
                tasks_per_node=1,
                init_blocks=1,
                max_blocks=1,
                overrides=overrides,
                account=ACCOUNT,
                cmd_timeout=60
            ),
        )

local_executor = ThreadPoolExecutor(max_threads=2, label="submit-node")

parsl_config = Config(
    executors=[ mpi_executor, local_executor ],
    strategy=None,
)
