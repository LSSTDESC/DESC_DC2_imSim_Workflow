#! /usr/bin/env python

import sys
import os
import os.path

import galsim
import desc.imsim

def run_imsim(instcat, workdir, outdir, processes, fidelity, single_sensor, file_id=None):
    cwd = os.getcwd()

    instcat = os.path.abspath(instcat)
    outdir = os.path.abspath(outdir)
    workdir = os.path.abspath(workdir)

    os.makedirs(workdir)
    os.makedirs(outdir)

    log_level = 'INFO'
    commands = desc.imsim.metadata_from_file(instcat)
    obs_md = desc.imsim.phosim_obs_metadata(commands)
    seed = commands['seed']

    if fidelity > 0:
        rng = galsim.UniformDeviate(seed)
        psf = desc.imsim.make_psf('Atmospheric', obs_md, rng=rng)
        apply_sensor_model = True
    else:
        psf = desc.imsim.make_psf('DoubleGaussian', obs_md)
        apply_sensor_model = False

    if single_sensor > 0:
        sensor_list = 'R:2,2 S:1,1'
        processes = 1
    else:
        sensor_list = None

    os.chdir(workdir)

    image_simulator \
        = desc.imsim.ImageSimulator(instcat, psf, 
                                    seed=seed, 
                                    outdir=outdir, 
                                    sensor_list=sensor_list, 
                                    apply_sensor_model=apply_sensor_model, 
                                    create_centroid_file=True, 
                                    file_id=file_id, 
                                    log_level=log_level)
    image_simulator.run(processes=processes)

    os.chdir(cwd)

    return

# SINGLE SENSOR OPTION?
if __name__=='__main__':
    if len(sys.argv) < 7:
        print('USAGE: %s <instcat> <workdir> <outdir> <processes> <high_fidelity_q> <single_sensor_q> [file_id]' % sys.argv[0])
        sys.exit(-1)
    instcat = sys.argv[1]
    workdir = sys.argv[2]
    outdir = sys.argv[3]
    processes = int(sys.argv[4])
    fidelity = int(sys.argv[5])
    single_sensor = int(sys.argv[6])
    if len(sys.argv) > 7:
        file_id = sys.argv[7]
    else:
        file_id = None
    run_imsim(instcat, workdir, outdir, processes, fidelity, single_sensor, file_id)
