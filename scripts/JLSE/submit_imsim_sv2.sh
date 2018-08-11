#! /bin/bash

image=$1
prefix=$2

ic[0]=/home/apope/imsim/ALCF_1.2i/testing/DC2-R1-2p-WFD-u/000018/instCat/phosim_cat_200739.txt
ic[1]=/home/apope/imsim/ALCF_1.2i/testing/DC2-R1-2p-WFD-g/000027/instCat/phosim_cat_185783.txt
ic[2]=/home/apope/imsim/ALCF_1.2i/testing/DC2-R1-2p-WFD-r/000094/instCat/phosim_cat_219976.txt
ic[3]=/home/apope/imsim/ALCF_1.2i/testing/DC2-R1-2p-WFD-i/000057/instCat/phosim_cat_204595.txt
ic[4]=/home/apope/imsim/ALCF_1.2i/testing/DC2-R1-2p-WFD-z/000025/instCat/phosim_cat_32678.txt
ic[5]=/home/apope/imsim/ALCF_1.2i/testing/DC2-R1-2p-WFD-y/000077/instCat/phosim_cat_191127.txt

./imsim/reset_intel_pstate.sh

mkdir -p ${prefix}

for i in `seq 0 5`;
do
    time singularity run $image ${ic[$filter]} ${prefix}/${i}/work ${prefix}/${i}/fits 1 1 1 1> ${prefix}/stdout.${i}.txt 2> ${prefix}/stderr.${i}.txt &
done

wait
