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
   git clone https://github.com/lsst/sims_GalSimInterface.git
   git clone https://github.com/LSSTDESC/imSim.git
   setup -r sims_GalSimInterface -j
   setup -r imSim -j
   cd sims_GalSimInterface
   set +e
   scons
   set -e
   cd ../imSim
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
   cd
   export OMP_NUM_THREADS=1

%runscript
   exec python /DC2/ALCF_1.2i/scripts/run_imsim.py "$@"
