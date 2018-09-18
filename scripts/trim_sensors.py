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

    def trim_sensors(self, instcat):
        obs_md, _, _ \
            = desc.imsim.parsePhoSimInstanceFile(instcat, (), numRows=50)

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
    instcat = '/global/cscratch1/sd/desc/DC2/Run2.0i/instCat/z-WFD/0002188_test/instCat/phosim_cat_2188.txt'
    sensors = run20_region.trim_sensors(instcat)
    print(len(sensors))
    print(sensors)
