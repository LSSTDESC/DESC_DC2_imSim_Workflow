#! /usr/bin/env python

import sys
import os
import os.path

import galsim
import desc.imsim

def run_imsim(workdir, instcat, outdir, file_id, processes):
    cwd = os.getcwd()
    instcat = os.path.abspath(instcat)
    outdir = os.path.abspath(outdir)
    workdir = os.path.abspath(workdir)

    commands = desc.imsim.metadata_from_file(instcat)
    obs_md = desc.imsim.phosim_obs_metadata(commands)
    rng = galsim.UniformDeviate(commands['seed'])
    psf = desc.imsim.make_psf('Atmospheric', obs_md, rng=rng)

    os.chdir(workdir)

    image_simulator = desc.imsim.ImageSimulator(instcat, \
                                                psf, \
                                                outdir = outdir, \
                                                apply_sensor_model = True, \
                                                file_id = file_id, \
                                                log_level = 'INFO')
    image_simulator.run(processes=processes)

    os.chdir(cwd)

    return

if __name__=='__main__':
    if len(sys.argv) < 6:
        print('USAGE: %s <workdir> <instcat> <outdir> <file_id> <processes>' % sys.argv[0])
        sys.exit(-1)
    workdir = sys.argv[1]
    instcat = sys.argv[2]
    outdir = sys.argv[3]
    file_id = sys.argv[4]
    processes = int(sys.argv[5])
    run_imsim(workdir, instcat, outdir, file_id, processes)
