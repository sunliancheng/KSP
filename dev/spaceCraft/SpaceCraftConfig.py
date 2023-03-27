from dev.configs.kerbin.KerbinGeneralConfig import KerbinGeneralConfig


class SpaceCraftConfig(KerbinGeneralConfig):
    pitch: float = 90.0
    heading: float = 90.0
    throttle: float = 1.0
    target_orbit_altitude = 150000
    sas: bool = False
    rcs: bool = False

    srbs_separated = False
    turn_angle = 0
