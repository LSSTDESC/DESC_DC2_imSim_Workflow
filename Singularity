Bootstrap: docker
From: avillarreal/alcf_run2.0i:latest

%environment
   /DC2/ALCF_1.2i/docker_run.sh

%runscript
   exec python /DC2/ALCF_1.2i/scripts/run_imsim.py "$@"

