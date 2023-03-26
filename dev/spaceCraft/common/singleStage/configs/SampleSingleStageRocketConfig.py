from dev.spaceCraft.SpaceCraftConfig import SpaceCraftConfig


class SampleSingleStageRocketConfig(SpaceCraftConfig):
    # we can override the value in parent config file
    target_altitude = 150000
