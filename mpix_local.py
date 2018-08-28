from libsubmit.providers import CobaltProvider
from libsubmit.launchers import SimpleLauncher

from parsl.config import Config
from parsl.executors.mpix import MPIExecutor



IP = "10.236.1.193"
JOB_URL = "tcp://{}:50005".format(IP)
RESULT_URL = "tcp://{}:50006".format(IP)

config = Config(
    executors=[
        MPIExecutor(
            label="local_ipp",
            jobs_q_url=JOB_URL,
            results_q_url=RESULT_URL,
            launch_cmd='which python3; \
aprun -b -cc depth -j 1 -n $(($COBALT_PARTSIZE * {tasks_per_node})) -N {tasks_per_node} \
python3 /home/benc/.conda/envs/theta_intel_test1/bin/fabric.py -d --task_url={task_url} --result_url={result_url}',
            provider=CobaltProvider(
                queue="debug-flat-quad",
                # queue="default",                                                                                                                                                                                                             
                launcher=SimpleLauncher(),
                walltime="00:30:00",
                nodes_per_block=8,
                tasks_per_node=64,
                init_blocks=1,
                max_blocks=1,
                overrides="""module load intelpython35/2017.0.035                                                                                                                                                                              
source activate theta_intel_test1 
module swap cray-mpich cray-mpich-abi                                                                                                                                                                                                          
export LD_LIBRARY_PATH=${CRAY_LD_LIBRARY_PATH}:$LD_LIBRARY_PATH                                                                                                                                                                                
                                                                                                                                                                                                                                               
ulimit -c unlimited                                                                                                                                                                                                                            
                                                                                                                                                                                                                                               
export OMP_NUM_THREADS=16""",
                account="LSSTADSP_DESC",
                cmd_timeout=60
            ),
        )
    ],
    strategy=None,
)
