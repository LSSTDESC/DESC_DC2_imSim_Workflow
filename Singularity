Bootstrap: docker
From: lsstdesc/stack-sims:w_2018_35-sims_2_10_0-v2

%post
   set +e
   source scl_source enable devtoolset-6
   set -e
   source /opt/lsst/software/stack/loadLSST.bash
   setup lsst_sims
   mkdir /DC2
   cd /DC2
   git clone https://github.com/lsst/sims_photUtils.git
   git clone https://github.com/lsst/sims_skybrightness.git
   git clone https://github.com/lsst/sims_GalSimInterface.git
   git clone https://github.com/LSSTDESC/imSim.git
   git clone https://github.com/lsst/obs_lsstCam.git
   git clone https://github.com/GalSim-developers/GalSim.git
   setup -r sims_photUtils -j
   setup -r sims_skybrightness -j
   setup -r sims_GalSimInterface -j
   setup -r imSim -j
   setup -r obs_lsstCam -j
   cd sims_photUtils
   git checkout ba5b942a9359e7eceea918e8663e6225cfb49dfc
   set +e
   scons
   set -e
   cd ../sims_skybrightness
   git checkout fdd58c7eb0414e89f5c7fa12eccf8809acabcf92
   set +e
   scons
   set -e
   cd ../sims_GalSimInterface
   set +e
   scons
   set -e
   cd ../imSim
   git checkout dc2_run2.0_rc
   sed -i -e 's/_stepK/_getStepK/g' python/desc/imsim/atmPSF.py
   scons
   cd ../obs_lsstCam
   git checkout imsim-0.1.0
   scons
   cd ../GalSim
   git checkout 3af1a30bdb3f2ac0d0abcc957b175d8d01dae79c
   pip install -r requirements.txt
   python setup.py install
   cd ..
   git clone https://github.com/LSSTDESC/ALCF_1.2i.git

%environment
   source /opt/lsst/software/stack/loadLSST.bash
   setup lsst_sims
   cd /DC2
   setup -r sims_GalSimInterface -j
   setup -r imSim -j
   setup -r obs_lsstCam -j
   setup -r sims_skybrightness -j
   setup -r sims_photUtils -j
   export OMP_NUM_THREADS=1

%runscript
   exec python /DC2/ALCF_1.2i/scripts/run_imsim.py "$@"

