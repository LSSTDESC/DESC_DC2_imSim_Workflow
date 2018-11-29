FROM lsstdesc/stack-sims:w_2018_39-sims_2_11_1-v2

USER root
RUN mkdir -p /DC2 &&\
  chown lsst /DC2
USER lsst
RUN set +e &&\
  source scl_source enable devtoolset-6 &&\
  set -e &&\ 
  source /opt/lsst/software/stack/loadLSST.bash &&\
  setup lsst_sims &&\
  cd /DC2 &&\
  git clone https://github.com/lsst/sims_GalSimInterface.git &&\
  git clone https://github.com/LSSTDESC/imSim.git &&\
  git clone https://github.com/lsst/obs_lsstCam.git &&\
  git clone https://github.com/lsst/obs_lsst.git &&\
  git clone https://github.com/LSSTDESC/ALCF_1.2i.git &&\
  git clone https://github.com/GalSim-developers/GalSim.git &&\
  setup -r sims_GalSimInterface -j &&\
  setup -r imSim -j &&\
  setup -r obs_lsstCam -j &&\
  cd obs_lsst &&\
  eups declare -r . obs_lsst -t current &&\
  setup -r . -j &&\
  scons &&\
  cd ../sims_GalSimInterface &&\
  git checkout master &&\
  set +e &&\
  scons || echo 'ignored failure' &&\
  set -e &&\
  cd ../imSim &&\
  git checkout master &&\
  scons &&\
  cd ../obs_lsstCam &&\
  git checkout imsim-0.1.0 &&\
  scons &&\
  cd ../GalSim &&\
  git checkout master &&\
  eups declare -r . galsim -t current &&\
  setup -r . -j &&\
  set +e &&\
  scons -Q WITH_UPS=True EIGEN_DIR=/opt/lsst/software/stack/stack/miniconda3-4.5.4-fcd27eb/Linux64/eigen/3.3.4.lsst1/include &&\
  set -e
ENTRYPOINT ["/DC2/ALCF_1.2i/docker_run.sh"]
CMD ["echo You must specify a command to run inside the LSST ALCF container"]
