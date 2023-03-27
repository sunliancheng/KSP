from abc import abstractmethod

from krpc import Client

from dev.MetaClass.MetaClass import MetaClass
from dev.spaceCraft.SpaceCraftConfig import SpaceCraftConfig


class SpaceCraft(MetaClass):
    def __init__(self, conn: Client, config: SpaceCraftConfig):
        super().__init__()
        self.connection = conn
        self.vessel = self.connection.space_center.active_vessel
        self.config = config
        self.apoapsis = self.connection.add_stream(getattr, self.vessel.orbit, 'apoapsis_altitude')
        self.periapsis = self.connection.add_stream(getattr, self.vessel.orbit, 'periapsis_altitude')

    # A vessel can have multiple engines
    # We care about whether the most bottom one has fuel or not
    def current_stage_engine_has_fuel(self) -> bool:
        size = len(self.vessel.parts.engines)
        return self.vessel.parts.engines[size - 1].has_fuel

    @abstractmethod
    def set_up_config(self):
        pass

    @abstractmethod
    def launch(self):
        self.set_up_config()
        pass

    # use this function to calculate how accurate the orbit is compared with the given target orbit
    def calculate_orbit_diff(self):
        apoapsis_diff = str(
            abs(self.apoapsis() - self.config.target_orbit_altitude) / self.config.target_orbit_altitude)
        periapsis_diff = str(
            abs(self.periapsis() - self.config.target_orbit_altitude) / self.config.target_orbit_altitude)
        self.logger.info('target_altitude = ' + str(self.config.target_orbit_altitude) + '; apoapsis = ' + str(
            self.apoapsis()) + '; apoapsis_diff = ' + apoapsis_diff + '; periapsis_diff = ' + periapsis_diff + '; periapsis = ' + str(
            self.periapsis()))
