from dev.spaceCraft.SpaceCraftConfig import SpaceCraftConfig


class SampleSingleStageRocketConfig(SpaceCraftConfig):
    # we can override the value in parent config file
    target_orbit_altitude = 48500000
