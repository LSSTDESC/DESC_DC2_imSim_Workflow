#FROM lsstdesc/stack-sims:w_2018_35-sims_2_10_0-v2
FROM lsstdesc/stack-sims:w_2018_26-sims_2_9_0
RUN set +e &&\
  source scl_source enable devtoolset-6 &&\
  set -e &&\ 
  source /opt/lsst/software/stack/loadLSST.bash &&\
  setup lsst_sims &&\
  cd /home/lsst &&\
  mkdir -p DC2 &&\
  cd DC2 &&\
  git clone https://github.com/lsst/sims_photUtils.git &&\
  git clone https://github.com/lsst/sims_skybrightness.git &&\
  git clone https://github.com/lsst/sims_GalSimInterface.git &&\
  git clone https://github.com/LSSTDESC/imSim.git &&\
  git clone https://github.com/lsst/obs_lsstCam.git &&\
  git clone https://github.com/LSSTDESC/ALCF_1.2i.git &&\
  setup -r sims_photUtils -j &&\
  setup -r sims_skybrightness -j &&\
  setup -r sims_GalSimInterface -j &&\
  setup -r imSim -j &&\
  setup -r obs_lsstCam -j &&\
  cd sims_photUtils &&\
  git checkout ba5b942a9359e7eceea918e8663e6225cfb49dfc &&\
  set +e &&\
  scons &&\
  set -e &&\
  cd ../sims_skybrightness &&\
  git checkout fdd58c7eb0414e89f5c7fa12eccf8809acabcf92 &&\
  set +e &&\
  scons &&\
  set -e &&\
  cd ../sims_GalSimInterface &&\
  git checkout u/jchiang/rmjarvis/simple_faint &&\
  set +e &&\
  scons || echo 'ignored failure' &&\
  set -e &&\
  cd ../imSim &&\
  git checkout dc2_run2.0_rc &&\
  scons &&\
  cd ../obs_lsstCam &&\
  git checkout imsim-0.1.0 &&\
  scons
COPY docker_run.sh /home/lsst/DC2/docker_run.sh
ENTRYPOINT ["/home/lsst/DC2/docker_run.sh"]
CMD ["-h"]
