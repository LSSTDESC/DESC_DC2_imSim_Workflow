import sys
import glob
import os
import shutil

def copy_imsim_inputs(inPrefix, outPrefix):
    cwd = os.getcwd()
    os.chdir(inPrefix)
    dl = glob.glob('DC2-R1-2p-*-?/??????/instCat/')
    dl.sort()
    os.chdir(cwd)
    for d in dl:
        inDir = inPrefix + '/' + d
        outDir = outPrefix + '/' + d
        os.makedirs(outDir)
        icl = glob.glob(inDir + 'phosim_cat_*.txt')
        for ic in icl:
            shutil.copy(ic, outDir)
        shutil.copytree(inDir + 'Dynamic', outDir + 'Dynamic')
    return

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('USAGE: %s <inPrefix> <outPrefix>' % sys.argv[0])
        sys.exit(-1)
    inPrefix = sys.argv[1]
    outPrefix = sys.argv[2]
    copy_imsim_inputs(inPrefix, outPrefix)
