#! /bin/bash

prefix=$1
filter=$2
processes=$3
ckpt=$4

ic[0]=/home/apope/imsim/ALCF_1.2i/testing/DC2-R1-2p-WFD-u/000018/instCat/phosim_cat_200739.txt
ic[1]=/home/apope/imsim/ALCF_1.2i/testing/DC2-R1-2p-WFD-g/000027/instCat/phosim_cat_185783.txt
ic[2]=/home/apope/imsim/ALCF_1.2i/testing/DC2-R1-2p-WFD-r/000094/instCat/phosim_cat_219976.txt
ic[3]=/home/apope/imsim/ALCF_1.2i/testing/DC2-R1-2p-WFD-i/000057/instCat/phosim_cat_204595.txt
ic[4]=/home/apope/imsim/ALCF_1.2i/testing/DC2-R1-2p-WFD-z/000025/instCat/phosim_cat_32678.txt
ic[5]=/home/apope/imsim/ALCF_1.2i/testing/DC2-R1-2p-WFD-y/000077/instCat/phosim_cat_191127.txt

instcat=${ic[$filter]}
workdir=${prefix}/${filter}_${processes}

if [ $ckpt -eq 0 ]
then
    ckptflag=""
else
    ckptflag="--file_id test"
fi

mkdir -p ${workdir}
cd ${workdir}
OMP_NUM_THREADS=1 imsim.py --psf Atmospheric --create_centroid_file --processes ${processes} ${ckptflag} ${instcat} 1> stdout.txt 2> stderr.txt
