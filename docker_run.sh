#!/bin/bash

cd /DC2
source /opt/lsst/software/stack/loadLSST.bash
setup lsst_sims
setup -r imSim -j
setup -r sims_GalSimInterface -j
export OMP_NUM_THREADS=1

echo docker_run.sh: will run command: "$@" >&2

$@
