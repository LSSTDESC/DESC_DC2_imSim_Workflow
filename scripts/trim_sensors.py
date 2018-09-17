import warnings
import sqlite3
import numpy as np
from lsst.afw import cameraGeom
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from lsst.sims.coordUtils import getCornerRaDec
    from lsst.sims.catUtils.utils import ObservationMetaDataGenerator
    from lsst.sims.utils import getRotSkyPos
import desc.imsim

class Run20Region:
    def __init__(self, ra_mid=61.855, ne_corner=(71.46, -27.25),
                 dec_range=(-44.33, -27.25)):
        self._ra_mid = ra_mid
        ra0 = ne_corner[0]
        cos_dec0 = np.cos(np.radians(ne_corner[1]))
        self._dra_scale = np.abs(ra0 - self._ra_mid)*cos_dec0
        self._dec_range = dec_range

    def contains(self, ra, dec):
        if dec < min(self._dec_range) or dec > max(self._dec_range):
            return False
        dra = np.abs(self._dra_scale/np.cos(np.radians(dec)))
        if np.abs(ra - self._ra_mid) > dra:
            return False
        return True

    def trim_sensors(self, visit, opsim_db='/global/projecta/projectdirs/lsst/groups/SSim/DC2/minion_1016_desc_dithered_v4.db'):
        obs_gen = ObservationMetaDataGenerator(database=opsim_db,
                                               driver='sqlite')
        with sqlite3.connect(opsim_db) as conn:
            curs = conn.execute('''select descDitheredRA, descDitheredDec,
                                   descDitheredRotTelPos from summary
                                   where obshistid={}'''.format(visit))
            ra, dec, rottelpos = [np.degrees(x) for x in curs][0]

        # An ObservationMetaData object used to pass the pointing info to
        # the function in lsst.sims.coordUtils that provides the CCD
        # coordinates.
        obs_md = obs_gen.getObservationMetaData(obsHistID=visit,
                                                boundType='circle',
                                                boundLength=0.1)[0]
        obs_md.pointingRA = ra
        obs_md.pointingDec = dec
        obs_md.OpsimMetaData['rotTelPos'] = rottelpos

        # Convert the rotation angle of the sky relative to the
        # telescope to the sky angle relative to the camera.
        obs_md.rotSkyPos = getRotSkyPos(ra, dec, obs_md, rottelpos)

        camera = desc.imsim.get_obs_lsstSim_camera()

        sensors = []
        for det in list(camera):
            det_name = det.getName()
            if det.getType() != cameraGeom.SCIENCE:
                continue
            corners = np.array(getCornerRaDec(det_name, camera, obs_md))
            if any([run20_region.contains(*corner) for corner in corners]):
                sensors.append(det_name)
        return sensors

if __name__ == '__main__':
    visit = 2188
    run20_region = Run20Region()
    sensors = run20_region.trim_sensors(visit)
    print(len(sensors))
    print(sensors)
