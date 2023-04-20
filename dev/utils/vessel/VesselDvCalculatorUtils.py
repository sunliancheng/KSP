import math

from krpc.services.spacecenter import Orbit

from dev.metaClass.MetaClass import MetaClass


def get_apoapsis_circularize_dv(orbit: Orbit):
    gp = orbit.body.gravitational_parameter
    r = orbit.apoapsis
    a = orbit.semi_major_axis
    v1 = math.sqrt(gp * ((2.0 / r) - (1.0 / a)))
    v2 = math.sqrt(gp * ((2.0 / r) - (1.0 / r)))
    return v2 - v1


class VesselDvCalculatorUtils(MetaClass):
    pass
