Bootstrap: docker
From: lsstdesc/stack-sims:w_2018_26-sims_2_9_0

%post
   set +e
   source scl_source enable devtoolset-6
   set -e
   source /opt/lsst/software/stack/loadLSST.bash
   setup lsst_sims
   mkdir /DC2
   cd /DC2
   git clone https://github.com/lsst/sims_skybrightness.git
   git clone https://github.com/lsst/sims_GalSimInterface.git
   git clone https://github.com/LSSTDESC/imSim.git
   git clone https://github.com/lsst/obs_lsstCam.git
   setup -r sims_skybrightness -j
   setup -r sims_GalSimInterface -j
   setup -r imSim -j
   setup -r obs_lsstCam -j
   cd sims_skybrightness
   git checkout fdd58c7eb0414e89f5c7fa12eccf8809acabcf92
   set +e
   scons
   set -e
   cd ../sims_GalSimInterface
   git checkout u/jchiang/uniqueId_as_string
   set +e
   scons
   set -e
   cd ../imSim
   git checkout v0.3.5-beta
   scons
   cd ../obs_lsstCam
   git checkout imsim-0.1.0
   scons
   cd ..
   git clone https://github.com/LSSTDESC/ALCF_1.2i.git
   #set +e
   #py.test
   #set -e

%environment
   source /opt/lsst/software/stack/loadLSST.bash
   setup lsst_sims
   cd /DC2
   setup -r sims_GalSimInterface -j
   setup -r imSim -j
   setup -r obs_lsstCam -j
   cd
   export OMP_NUM_THREADS=1

%runscript
   exec python /DC2/ALCF_1.2i/scripts/run_imsim.py "$@"

