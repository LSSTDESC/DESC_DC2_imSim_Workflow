#! /bin/bash

image=$1
prefix=$2
filter=$3
processes=$4
ckpt=$5

./imsim/reset_intel_pstate.sh

time singularity exec $image ./run_imsim_fp.sh ${prefix} ${filter} ${processes} ${ckpt}
