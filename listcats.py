#!/usr/bin/env python3

# this comes from slack chat between jim chiang and benc

import glob

def get_inst_cats():
    return glob.glob('/projects/LSSTADSP_DESC/ALCF_1.2i/inputs/DC2-R1*/0*/instCat/phosim_cat*.txt')

print("listcats: this many instance catalogs: ", len(get_inst_cats()))
