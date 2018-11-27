Bootstrap: docker
From: avillarreal/alcf_run2.0i:latest

%environment
   source /opt/lsst/software/stack/loadLSST.bash
   setup lsst_sims
   cd /DC2
   setup -r sims_GalSimInterface -j
   setup -r imSim -j
   setup -r obs_lsstCam -j
   setup -r obs_lsst -j
   cd GalSim
   setup -r . -j
   cd ..
   export OMP_NUM_THREADS=1

%runscript
   exec python /DC2/ALCF_1.2i/scripts/run_imsim.py "$@"

