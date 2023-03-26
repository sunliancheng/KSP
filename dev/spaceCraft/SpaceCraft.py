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
