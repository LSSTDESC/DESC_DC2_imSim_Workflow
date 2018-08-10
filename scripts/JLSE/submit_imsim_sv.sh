#! /bin/bash

image=$1
prefix=$2
ckpt=$3

./imsim/reset_intel_pstate.sh

time singularity exec $image ./run_imsim_sv.sh $prefix 0 $ckpt &
time singularity exec $image ./run_imsim_sv.sh $prefix 1 $ckpt &
time singularity exec $image ./run_imsim_sv.sh $prefix 2 $ckpt &
time singularity exec $image ./run_imsim_sv.sh $prefix 3 $ckpt &
time singularity exec $image ./run_imsim_sv.sh $prefix 4 $ckpt &
time singularity exec $image ./run_imsim_sv.sh $prefix 5 $ckpt &

wait
