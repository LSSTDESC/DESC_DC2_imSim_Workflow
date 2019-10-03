FROM lsstdesc/stack-sims:w_2019_37-sims_w_2019_37

USER root
RUN mkdir -p /DC2 &&\
  chown lsst /DC2
USER lsst
RUN set +e &&\
  source scl_source enable devtoolset-6 &&\
  set -e &&\ 
  source /opt/lsst/software/stack/loadLSST.bash &&\
  setup lsst_sims -t sims_w_2019_37 &&\
  setup -t DC2production throughputs &&\
  setup -t DC2production sims_skybrightness_data &&\
  cd /DC2 &&\
  git clone https://github.com/LSSTDESC/imSim.git &&\
  git clone https://github.com/LSSTDESC/ALCF_1.2i.git &&\
  git clone https://github.com/lsst/sims_GalSimInterface.git &&\
  setup -r imSim -j &&\
  setup -r sims_GalSimInterface -j &&\
  cd imSim &&\
  git checkout DC2-Run2.2i-rc &&\
  scons &&\
  cd ../sims_GalSimInterface &&\
  git checkout DC2-Run2.2i-rc &&\
  scons &&\
  cd ../ALCF_1.2i &&\
  git checkout production201903
ENTRYPOINT ["/DC2/ALCF_1.2i/docker_run.sh"]
CMD ["echo You must specify a command to run inside the LSST ALCF container"]

