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


THETA_NODES=8
THETA_QUEUE="debug-flat-quad"
WALLTIME="00:58:00"

#THETA_NODES=128
#THETA_QUEUE="default"
#WALLTIME="00:30:00"

ACCOUNT="LSSTADSP_DESC"

# ip (or hostname, probably) of the submitting host
SUBMIT_HOST_IP = "10.236.1.193"

# parameters above are ones you're likely to want
# to change
# stuff below, probably not so much


JOB_URL = "tcp://{}:50005".format(SUBMIT_HOST_IP)
RESULT_URL = "tcp://{}:50006".format(SUBMIT_HOST_IP)

launch_cmd='which python3; \
aprun -b -cc depth -j 1 -d 64 -n $(($COBALT_PARTSIZE * {tasks_per_node})) -N {tasks_per_node} \
python3 /home/benc/desc2.0i/parsl/parsl/executors/mpix/fabric_singlethreaded.py -d --task_url={task_url} --result_url={result_url}'

overrides="""module load intelpython35/2017.0.035                                                                                                                                                                              
source activate theta_intel_test1 
module swap cray-mpich cray-mpich-abi                                                                                                                                                                                                          
export LD_LIBRARY_PATH=${CRAY_LD_LIBRARY_PATH}:$LD_LIBRARY_PATH                                                                                                                                                                                
                                                                                                                                                                                                                                               
ulimit -c unlimited                                                                                                                                                                                                                            
                                                                                                                                                                                                                                               
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
