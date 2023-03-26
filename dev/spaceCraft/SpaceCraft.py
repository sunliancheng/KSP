from abc import ABC, abstractmethod

from krpc import Client


class SpaceCraft(ABC):
    def __init__(self, conn: Client):
        super().__init__()
        self.connection = conn
        self.vessel = self.connection.space_center.active_vessel

    # A vessel can have multiple engines
    # We care about whether the most bottom one has fuel or not
    def current_stage_engine_has_fuel(self) -> bool:
        size = len(self.vessel.parts.engines)
        return self.vessel.parts.engines[size - 1].has_fuel

    @abstractmethod
    def launch(self):
        pass
