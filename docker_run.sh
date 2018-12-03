#!/bin/bash

cd /DC2
source /opt/lsst/software/stack/loadLSST.bash
setup lsst_sims
setup -r sims_GalSimInterface -j
setup -r imSim -j
setup -r obs_lsstCam -j
setup -r obs_lsst -j 
cd GalSim
setup -r . -j
cd ..
export OMP_NUM_THREADS=1

echo docker_run.sh: will run command: "$@" >&2

$@
