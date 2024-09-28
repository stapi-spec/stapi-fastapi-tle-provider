from datetime import datetime

from shapely import Point
from tle_sat import FieldOfView, FootprintError, Pass, Satellite, TimeOfInterest


class TleDefinedSatellite:
    def __init__(self, tle: str) -> None:
        self.satellite = Satellite(tle)
        self.fov = FieldOfView(2, 2)

    def passes(self, start_time: datetime, end_time: datetime, lat: float, lon: float):
        toi = TimeOfInterest(start_time, end_time)
        target = Point(lon, lat, 0)

        passes = self.satellite.passes(toi, target)

        def geom(p: Pass):
            try:
                return self.satellite.footprint(p.t, p.view_angles, self.fov)
            except FootprintError:
                return target

        return [(p, geom(p)) for p in passes if p.view_angles.off_nadir <= 45]
