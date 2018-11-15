#! /usr/bin/env python

import sys
import os
import os.path
import json

import galsim
import desc.imsim

# phosim style
#all_sensor_list = ['R01_S00', 'R01_S01', 'R01_S02', 'R01_S10', 'R01_S11', 'R01_S12', 'R01_S20', 'R01_S21', 'R01_S22', 'R02_S00', 'R02_S01', 'R02_S02', 'R02_S10', 'R02_S11', 'R02_S12', 'R02_S20', 'R02_S21', 'R02_S22', 'R03_S00', 'R03_S01', 'R03_S02', 'R03_S10', 'R03_S11', 'R03_S12', 'R03_S20', 'R03_S21', 'R03_S22', 'R10_S00', 'R10_S01', 'R10_S02', 'R10_S10', 'R10_S11', 'R10_S12', 'R10_S20', 'R10_S21', 'R10_S22', 'R11_S00', 'R11_S01', 'R11_S02', 'R11_S10', 'R11_S11', 'R11_S12', 'R11_S20', 'R11_S21', 'R11_S22', 'R12_S00', 'R12_S01', 'R12_S02', 'R12_S10', 'R12_S11', 'R12_S12', 'R12_S20', 'R12_S21', 'R12_S22', 'R13_S00', 'R13_S01', 'R13_S02', 'R13_S10', 'R13_S11', 'R13_S12', 'R13_S20', 'R13_S21', 'R13_S22', 'R14_S00', 'R14_S01', 'R14_S02', 'R14_S10', 'R14_S11', 'R14_S12', 'R14_S20', 'R14_S21', 'R14_S22', 'R20_S00', 'R20_S01', 'R20_S02', 'R20_S10', 'R20_S11', 'R20_S12', 'R20_S20', 'R20_S21', 'R20_S22', 'R21_S00', 'R21_S01', 'R21_S02', 'R21_S10', 'R21_S11', 'R21_S12', 'R21_S20', 'R21_S21', 'R21_S22', 'R22_S00', 'R22_S01', 'R22_S02', 'R22_S10', 'R22_S11', 'R22_S12', 'R22_S20', 'R22_S21', 'R22_S22', 'R23_S00', 'R23_S01', 'R23_S02', 'R23_S10', 'R23_S11', 'R23_S12', 'R23_S20', 'R23_S21', 'R23_S22', 'R24_S00', 'R24_S01', 'R24_S02', 'R24_S10', 'R24_S11', 'R24_S12', 'R24_S20', 'R24_S21', 'R24_S22', 'R30_S00', 'R30_S01', 'R30_S02', 'R30_S10', 'R30_S11', 'R30_S12', 'R30_S20', 'R30_S21', 'R30_S22', 'R31_S00', 'R31_S01', 'R31_S02', 'R31_S10', 'R31_S11', 'R31_S12', 'R31_S20', 'R31_S21', 'R31_S22', 'R32_S00', 'R32_S01', 'R32_S02', 'R32_S10', 'R32_S11', 'R32_S12', 'R32_S20', 'R32_S21', 'R32_S22', 'R33_S00', 'R33_S01', 'R33_S02', 'R33_S10', 'R33_S11', 'R33_S12', 'R33_S20', 'R33_S21', 'R33_S22', 'R34_S00', 'R34_S01', 'R34_S02', 'R34_S10', 'R34_S11', 'R34_S12', 'R34_S20', 'R34_S21', 'R34_S22', 'R41_S00', 'R41_S01', 'R41_S02', 'R41_S10', 'R41_S11', 'R41_S12', 'R41_S20', 'R41_S21', 'R41_S22', 'R42_S00', 'R42_S01', 'R42_S02', 'R42_S10', 'R42_S11', 'R42_S12', 'R42_S20', 'R42_S21', 'R42_S22', 'R43_S00', 'R43_S01', 'R43_S02', 'R43_S10', 'R43_S11', 'R43_S12', 'R43_S20', 'R43_S21', 'R43_S22']

# imsim style
all_sensor_list = ['R:0,1 S:0,0', 'R:0,1 S:0,1', 'R:0,1 S:0,2', 'R:0,1 S:1,0', 'R:0,1 S:1,1', 'R:0,1 S:1,2', 'R:0,1 S:2,0', 'R:0,1 S:2,1', 'R:0,1 S:2,2', 'R:0,2 S:0,0', 'R:0,2 S:0,1', 'R:0,2 S:0,2', 'R:0,2 S:1,0', 'R:0,2 S:1,1', 'R:0,2 S:1,2', 'R:0,2 S:2,0', 'R:0,2 S:2,1', 'R:0,2 S:2,2', 'R:0,3 S:0,0', 'R:0,3 S:0,1', 'R:0,3 S:0,2', 'R:0,3 S:1,0', 'R:0,3 S:1,1', 'R:0,3 S:1,2', 'R:0,3 S:2,0', 'R:0,3 S:2,1', 'R:0,3 S:2,2', 'R:1,0 S:0,0', 'R:1,0 S:0,1', 'R:1,0 S:0,2', 'R:1,0 S:1,0', 'R:1,0 S:1,1', 'R:1,0 S:1,2', 'R:1,0 S:2,0', 'R:1,0 S:2,1', 'R:1,0 S:2,2', 'R:1,1 S:0,0', 'R:1,1 S:0,1', 'R:1,1 S:0,2', 'R:1,1 S:1,0', 'R:1,1 S:1,1', 'R:1,1 S:1,2', 'R:1,1 S:2,0', 'R:1,1 S:2,1', 'R:1,1 S:2,2', 'R:1,2 S:0,0', 'R:1,2 S:0,1', 'R:1,2 S:0,2', 'R:1,2 S:1,0', 'R:1,2 S:1,1', 'R:1,2 S:1,2', 'R:1,2 S:2,0', 'R:1,2 S:2,1', 'R:1,2 S:2,2', 'R:1,3 S:0,0', 'R:1,3 S:0,1', 'R:1,3 S:0,2', 'R:1,3 S:1,0', 'R:1,3 S:1,1', 'R:1,3 S:1,2', 'R:1,3 S:2,0', 'R:1,3 S:2,1', 'R:1,3 S:2,2', 'R:1,4 S:0,0', 'R:1,4 S:0,1', 'R:1,4 S:0,2', 'R:1,4 S:1,0', 'R:1,4 S:1,1', 'R:1,4 S:1,2', 'R:1,4 S:2,0', 'R:1,4 S:2,1', 'R:1,4 S:2,2', 'R:2,0 S:0,0', 'R:2,0 S:0,1', 'R:2,0 S:0,2', 'R:2,0 S:1,0', 'R:2,0 S:1,1', 'R:2,0 S:1,2', 'R:2,0 S:2,0', 'R:2,0 S:2,1', 'R:2,0 S:2,2', 'R:2,1 S:0,0', 'R:2,1 S:0,1', 'R:2,1 S:0,2', 'R:2,1 S:1,0', 'R:2,1 S:1,1', 'R:2,1 S:1,2', 'R:2,1 S:2,0', 'R:2,1 S:2,1', 'R:2,1 S:2,2', 'R:2,2 S:0,0', 'R:2,2 S:0,1', 'R:2,2 S:0,2', 'R:2,2 S:1,0', 'R:2,2 S:1,1', 'R:2,2 S:1,2', 'R:2,2 S:2,0', 'R:2,2 S:2,1', 'R:2,2 S:2,2', 'R:2,3 S:0,0', 'R:2,3 S:0,1', 'R:2,3 S:0,2', 'R:2,3 S:1,0', 'R:2,3 S:1,1', 'R:2,3 S:1,2', 'R:2,3 S:2,0', 'R:2,3 S:2,1', 'R:2,3 S:2,2', 'R:2,4 S:0,0', 'R:2,4 S:0,1', 'R:2,4 S:0,2', 'R:2,4 S:1,0', 'R:2,4 S:1,1', 'R:2,4 S:1,2', 'R:2,4 S:2,0', 'R:2,4 S:2,1', 'R:2,4 S:2,2', 'R:3,0 S:0,0', 'R:3,0 S:0,1', 'R:3,0 S:0,2', 'R:3,0 S:1,0', 'R:3,0 S:1,1', 'R:3,0 S:1,2', 'R:3,0 S:2,0', 'R:3,0 S:2,1', 'R:3,0 S:2,2', 'R:3,1 S:0,0', 'R:3,1 S:0,1', 'R:3,1 S:0,2', 'R:3,1 S:1,0', 'R:3,1 S:1,1', 'R:3,1 S:1,2', 'R:3,1 S:2,0', 'R:3,1 S:2,1', 'R:3,1 S:2,2', 'R:3,2 S:0,0', 'R:3,2 S:0,1', 'R:3,2 S:0,2', 'R:3,2 S:1,0', 'R:3,2 S:1,1', 'R:3,2 S:1,2', 'R:3,2 S:2,0', 'R:3,2 S:2,1', 'R:3,2 S:2,2', 'R:3,3 S:0,0', 'R:3,3 S:0,1', 'R:3,3 S:0,2', 'R:3,3 S:1,0', 'R:3,3 S:1,1', 'R:3,3 S:1,2', 'R:3,3 S:2,0', 'R:3,3 S:2,1', 'R:3,3 S:2,2', 'R:3,4 S:0,0', 'R:3,4 S:0,1', 'R:3,4 S:0,2', 'R:3,4 S:1,0', 'R:3,4 S:1,1', 'R:3,4 S:1,2', 'R:3,4 S:2,0', 'R:3,4 S:2,1', 'R:3,4 S:2,2', 'R:4,1 S:0,0', 'R:4,1 S:0,1', 'R:4,1 S:0,2', 'R:4,1 S:1,0', 'R:4,1 S:1,1', 'R:4,1 S:1,2', 'R:4,1 S:2,0', 'R:4,1 S:2,1', 'R:4,1 S:2,2', 'R:4,2 S:0,0', 'R:4,2 S:0,1', 'R:4,2 S:0,2', 'R:4,2 S:1,0', 'R:4,2 S:1,1', 'R:4,2 S:1,2', 'R:4,2 S:2,0', 'R:4,2 S:2,1', 'R:4,2 S:2,2', 'R:4,3 S:0,0', 'R:4,3 S:0,1', 'R:4,3 S:0,2', 'R:4,3 S:1,0', 'R:4,3 S:1,1', 'R:4,3 S:1,2', 'R:4,3 S:2,0', 'R:4,3 S:2,1', 'R:4,3 S:2,2']

# all: size=189, index=0
# 'R:2,2 S:1,1': size=1, index=94
def sensor_subset(size, index):
    lo = index*size
    hi = (index+1)*size
    return all_sensor_list[lo:hi]

def get_sensor_list(bundle_lists, node_id, visit_index):
    with open(bundle_lists, 'r') as fd:
        bundles = json.load(fd)
    return bundles[node_id][visit_index]

def run_imsim(instcat, workdir, outdir, processes, low_fidelity,
              subset_size, subset_index, file_id=None, bundle_lists=None,
              node_id='node0', visit_index=0, log_level='INFO'):

    logger = desc.imsim.get_logger(log_level, 'run_imsim')

    cwd = os.getcwd()

    if bundle_lists is None:
        if instcat is None:
            raise RuntimeError("Either an instcat or bundle_lists file "
                               "must be provided.")
        sensor_list = sensor_subset(subset_size, subset_index)
    else:
        instcat, sensor_list, _ = get_sensor_list(bundle_lists, node_id,
                                               visit_index)

    logger.info(instcat)
    logger.info(sensor_list)
    instcat = os.path.abspath(instcat)
    outdir = os.path.abspath(outdir)
    workdir = os.path.abspath(workdir)

    os.makedirs(workdir, exist_ok=True)
    os.makedirs(outdir, exist_ok=True)

    commands = desc.imsim.metadata_from_file(instcat)
    obs_md = desc.imsim.phosim_obs_metadata(commands)
    seed = commands['seed']

    if low_fidelity:
        logger.info("running in low fidelity mode")
        psf = desc.imsim.make_psf('DoubleGaussian', obs_md)
        apply_sensor_model = False
    else:
        logger.info("running in high fidelity mode")
        rng = galsim.UniformDeviate(seed)
        psf = desc.imsim.make_psf('Atmospheric', obs_md, rng=rng)
        apply_sensor_model = True

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
    image_simulator.run(processes=processes, node_id=node_id)

    os.chdir(cwd)

    return

# SINGLE SENSOR OPTION?
if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--instcat', type=str, default=None,
                        help='Instance catalog file')
    parser.add_argument('--workdir', type=str, default='.',
                        help='working directory')
    parser.add_argument('--outdir', type=str, default='.',
                        help='output directory')
    parser.add_argument('--processes', type=int, default=1,
                        help='number of processes. Default: 1')
    parser.add_argument('--low_fidelity', default=False, action='store_true',
                        help='Run in low fidelity mode.')
    parser.add_argument('--subset_size', type=int, default=1,
                        help='subset size of full focalplane sensors '
                        'to simulate. Default: 1')
    parser.add_argument('--subset_index', type=int, default=94,
                        help='starting index of subset full focalplane '
                        'sensors to simulate. Default: 94')
    parser.add_argument('--file_id', type=str, default=None,
                        help='file_id to use for checkpoint files. '
                        'If None, then checkpointing will not be used.')
    parser.add_argument('--bundle_lists', type=str, default=None,
                        help='json file with visit/chip list bundles. '
                        'If not None, this overrides the instcat argument'
                        'and the --subset_* parameters')
    parser.add_argument('--node_id', type=str, default='node0',
                        help='Node ID of desired visit/sensors lists. '
                        'Default: node0')
    parser.add_argument('--visit_index', type=int, default=0,
                        help='Index of the visit/sensor list tuple in the '
                        'desired node bundle. Default: 0')
    parser.add_argument('--log_level', type=str, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'],
                        help='Logging level. Default: INFO')
    args = parser.parse_args()

    run_imsim(args.instcat, args.workdir, args.outdir, args.processes,
              args.low_fidelity, args.subset_size, args.subset_index,
              args.file_id, bundle_lists=args.bundle_lists,
              node_id=args.node_id, visit_index=args.visit_index,
              log_level=args.log_level)
