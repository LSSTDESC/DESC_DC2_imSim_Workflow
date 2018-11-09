FROM lsstdesc/stack-sims:w_2018_35-sims_2_10_0-v2
ENV source /opt/lsst/software/stack/loadLSST.bash
ENV setup lsst_sims
ENV cd /DC2
ENV setup -r sims_GalSimInterface -j
ENV setup -r imSim -j
ENV setup -r obs_lsstCam -j
ENV setup -r sims_skybrightness -j
ENV setup -r sims_photUtils -j
ENV cd
RUN set +e
RUN source scl_source enable devtoolset-6
RUN set -e
RUN source /opt/lsst/software/stack/loadLSST.bash
RUN setup lsst_sims
RUN mkdir /DC2
RUN cd /DC2
RUN git clone https://github.com/lsst/sims_photUtils.git
RUN git clone https://github.com/lsst/sims_skybrightness.git
RUN git clone https://github.com/lsst/sims_GalSimInterface.git
RUN git clone https://github.com/LSSTDESC/imSim.git
RUN git clone https://github.com/lsst/obs_lsstCam.git
RUN setup -r sims_photUtils -j
RUN setup -r sims_skybrightness -j
RUN setup -r sims_GalSimInterface -j
RUN setup -r imSim -j
RUN setup -r obs_lsstCam -j
RUN cd sims_photUtils
RUN git checkout ba5b942a9359e7eceea918e8663e6225cfb49dfc
RUN set +e
RUN scons
RUN set -e
RUN cd ../sims_skybrightness
RUN git checkout fdd58c7eb0414e89f5c7fa12eccf8809acabcf92
RUN set +e
RUN scons
RUN set -e
RUN cd ../sims_GalSimInterface
RUN set +e
RUN scons
RUN set -e
RUN cd ../imSim
RUN git checkout dc2_run2.0_rc
RUN sed -i -e 's/_stepK/_getStepK/g' python/desc/imsim/atmPSF.py
RUN scons
RUN cd ../obs_lsstCam
RUN git checkout imsim-0.1.0
RUN scons
RUN cd ..
RUN git clone https://github.com/LSSTDESC/ALCF_1.2i.git
CMD exec python /DC2/ALCF_1.2i/scripts/run_imsim.py "$@"
