from libsubmit.providers import CobaltProvider
from libsubmit.launchers import SimpleLauncher

from parsl.config import Config
from parsl.executors.mpix import MPIExecutor



IP = "10.236.1.193"
JOB_URL = "tcp://{}:50005".format(IP)
RESULT_URL = "tcp://{}:50006".format(IP)

launch_cmd='which python3; \
aprun -b -cc depth -j 1 -d 64 -n $(($COBALT_PARTSIZE * {tasks_per_node})) -N {tasks_per_node} \
python3 /home/benc/desc2.0i/parsl/parsl/executors/mpix/fabric.py -d --task_url={task_url} --result_url={result_url}'

overrides="""module load intelpython35/2017.0.035                                                                                                                                                                              
source activate theta_intel_test1 
module swap cray-mpich cray-mpich-abi                                                                                                                                                                                                          
export LD_LIBRARY_PATH=${CRAY_LD_LIBRARY_PATH}:$LD_LIBRARY_PATH                                                                                                                                                                                
                                                                                                                                                                                                                                               
ulimit -c unlimited                                                                                                                                                                                                                            
                                                                                                                                                                                                                                               
export OMP_NUM_THREADS=1"""



config = Config(
    executors=[
        MPIExecutor(
            label="parsl-mpi-executor",
            jobs_q_url=JOB_URL,
            results_q_url=RESULT_URL,
            launch_cmd=launch_cmd,
            provider=CobaltProvider(
                queue="debug-flat-quad",
                # queue="default",                                                                                                                                                                                                             
                launcher=SimpleLauncher(),
                walltime="00:58:00",
                nodes_per_block=2, # this should scale up to 802 in real life, or up to 8 or 16 in debug queue
                                   # note at present, 1 is required to run the rank 0 controller, not any app tasks
                tasks_per_node=1,
                init_blocks=1,
                max_blocks=1,
                overrides=overrides,
                account="LSSTADSP_DESC",
                cmd_timeout=60
            ),
        )
    ],
    strategy=None,
)
