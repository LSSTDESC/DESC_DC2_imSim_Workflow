#!/bin/bash

cd /home/lsst/DC2
source /opt/lsst/software/stack/loadLSST.bash
setup lsst_sims
setup -r sims_GalSimInterface -j
setup -r imSim -j
setup -r obs_lsstCam -j
cd GalSim
setup -r . -j
cd ..

echo docker_run.sh: will run command: "$@" >&2

$@
