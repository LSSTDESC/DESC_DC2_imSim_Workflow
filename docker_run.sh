#!/bin/bash

cd /home/lsst/DC2
source /opt/lsst/software/stack/loadLSST.bash
setup lsst_sims
setup -r sims_photUtils -j
setup -r sims_skybrightness -j
setup -r sims_GalSimInterface -j
setup -r imSim -j
setup -r obs_lsstCam -j

echo docker_run.sh: will run command: "$@" >&2

$@
