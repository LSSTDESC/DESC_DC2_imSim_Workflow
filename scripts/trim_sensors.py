"""
Module to find the sensors that overlap the DC2 simulation region for a
given visit.
"""
import warnings
import numpy as np
from lsst.afw import cameraGeom
import lsst.sphgeom
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from lsst.sims.coordUtils import getCornerRaDec
import desc.imsim

class Run20Region:
    """
    Class to find sensors in a given visit that intersect the
    Run2.0 simulation region.
    """
    def __init__(self, ra_mid=61.855, ne_corner=(71.46, -27.25),
                 dec_range=(-44.33, -27.25)):
        self._ra_mid = ra_mid
        ra0 = ne_corner[0]
        cos_dec0 = np.cos(np.radians(ne_corner[1]))
        self._dra_scale = np.abs(ra0 - self._ra_mid)*cos_dec0
        self._dec_range = dec_range

        self.region_corners = []
        for dec in dec_range:
            dra = self._dra(dec)
            self.region_corners.extend([(ra_mid - dra, dec),
                                        (ra_mid + dra, dec)])
        self.region_polygon = self.get_convex_polygon(self.region_corners)

    @staticmethod
    def get_convex_polygon(corners):
        """
        Return a convex polygon for the specified list of region
        corner coordinates.  Coordinates should be in degrees.
        """
        vertices = []
        for corner in corners:
            lonlat = lsst.sphgeom.LonLat.fromDegrees(*corner)
            vertices.append(lsst.sphgeom.UnitVector3d(lonlat))
        return lsst.sphgeom.ConvexPolygon(vertices)

    def _dra(self, dec):
        return np.abs(self._dra_scale/np.cos(np.radians(dec)))

    def contains(self, ra, dec):
        if dec < min(self._dec_range) or dec > max(self._dec_range):
            return False
        if np.abs(ra - self._ra_mid) > self._dra(dec):
            return False
        return True

    def contains_region_corners(self, sensor_corners):
        det_polygon = self.get_convex_polygon(sensor_corners)
        return self.region_polygon.relate(det_polygon) != lsst.sphgeom.DISJOINT

    def trim_sensors(self, instcat):
        obs_md, _, _ \
            = desc.imsim.parsePhoSimInstanceFile(instcat, (), numRows=50)

        camera = desc.imsim.get_obs_lsstSim_camera()

        sensors = []
        for det in list(camera):
            if det.getType() != cameraGeom.SCIENCE:
                continue
            det_name = det.getName()
            corners = np.array(getCornerRaDec(det_name, camera, obs_md))
            if (any([self.contains(*corner) for corner in corners]) or
                self.contains_region_corners(corners)):
                sensors.append(det_name)
        return sensors

    def plot_boundary(self, color='blue', linestyle='--'):
        import matplotlib.pyplot as plt
        dec1 = np.linspace(-44.33, -27.25, 100)
        dec2 = dec1[-1::-1]
        ra1 = self._ra_mid - self._dra(dec1)
        ra2 = self._ra_mid + self._dra(dec2)
        ra = np.concatenate((ra1, ra2, ra1[:1]))
        dec = np.concatenate((dec1, dec2, dec1[:1]))
        plt.plot(ra, dec, color=color, linestyle=linestyle)

if __name__ == '__main__':
    run20_region = Run20Region()
    instcat = '/global/cscratch1/sd/desc/DC2/Run2.0i/instCat/z-WFD/0002188_test/instCat/phosim_cat_2188.txt'
    sensors = run20_region.trim_sensors(instcat)
    print(len(sensors))
    print(sensors)
