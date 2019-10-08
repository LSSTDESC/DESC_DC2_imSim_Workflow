#!/bin/bash -l
#COBALT -A LSSTsky
#COBALT -q R.LSSTsky
#COBALT -n 1
#COBALT -t 15:45:00
#COBALT -M avillarreal@anl.gov

module unload trackdeps
umask 0057
aprun -n 1 -d 64 -j 1 singularity exec -H /lus/theta-fs0/projects/LSSTsky/Run2.1.1i -B /projects/LSSTsky:/projects/LSSTsky:rw /projects/LSSTsky/Run2.1.1i/run-test20190924/alcf_run2.0i_Run2.1.1i-20190924test.sif /projects/LSSTsky/Run2.1.1i/ALCF_1.2i/docker_run.sh python /projects/LSSTsky/Run2.1.1i/ALCF_1.2i/scripts/run_imsim.py --workdir /projects/LSSTsky/Run2.1.1i/run-test20190924/run/outputs/00445379to00497969/00479028/ --outdir /projects/LSSTsky/Run2.1.1i/run-test20190924/run/outputs/00445379to00497969/00479028/ --file_id 479028 --processes 64 --bundle_lists /projects/LSSTsky/Run2.1.1i/run-test20190924/parsl-auto-bundles.json --node_id node0 --visit_index 0 --ckpt_archive_dir /projects/LSSTsky/Run2.1.1i/run-test20190924/run/outputs/00445379to00497969/00479028/agn_ckpts/ --config /projects/LSSTsky/Run2.1.1i/ALCF_1.2i/parsl_imsim_configs
