import argparse
from lsst.sims.GalSimInterface import (make_gs_interpreter,
                                       make_galsim_detector,
                                       LSSTCameraWrapper)
import desc.imsim

desc.imsim.read_config()

def render_checkpoint(instcat, checkpoint_file):
    RS_digits = [x for x in checkpoint_file.split('-')[-1] if x.isdigit()]
    det_name = 'R:{},{} S:{},{}'.format(*RS_digits)
    obs_md, phot_params, _ \
        = desc.imsim.parsePhoSimInstanceFile(instcat, [det_name], numRows=50,
                                             log_level='DEBUG')

    camera_wrapper = LSSTCameraWrapper()
    det = make_galsim_detector(camera_wrapper, det_name, phot_params, obs_md)
    gs_interpreter = make_gs_interpreter(obs_md, [det], None, None)
    gs_interpreter.checkpoint_file = checkpoint_file
    gs_interpreter.restore_checkpoint(camera_wrapper, phot_params, obs_md)

    visit = obs_md.OpsimMetaData['obshistID']
    name_root = 'lsst_a_{}'.format(visit)
    for name, gs_image in gs_interpreter.detectorImages.items():
        raw = desc.imsim.ImageSource.create_from_galsim_image(gs_image)
        outfile = '_'.join((name_root, name))
        raw.write_fits_file(outfile, compress=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('instcat', type=str, help='instance catalog')
    parser.add_argument('checkpoint_file', type=str, help='checkpoint file')
    args = parser.parse_args()

    render_checkpoint(args.instcat, args.checkpoint_file)
