#!/bin/bash -ex

# requires parsl source checkout in $(pwd)/parsl/

module load python/3.6-anaconda-4.4

# delete old conda environment

rm -rf ~/.conda/envs/parsl-imsim-nov2018

conda create -n parsl-imsim-nov2018 -y
source activate parsl-imsim-nov2018

conda install mpi4py -y

pushd parsl
pip install .
popd
