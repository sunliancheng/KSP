import time

from krpc import Client

from dev.spaceCraft.SpaceCraft import SpaceCraft


class SingleStageRocket(SpaceCraft):

    # how can we define a single stage rocket?
    # 1. an engine, a separator, fuel

    def __init__(self, conn: Client):
        super().__init__(conn)
        pass

    def launch(self):
        self.vessel.auto_pilot.target_pitch_and_heading(90, 90)
        self.vessel.auto_pilot.engage()
        self.vessel.control.throttle = 1
        time.sleep(1)
        self.vessel.control.activate_next_stage()
        while self.current_stage_engine_has_fuel():
            time.sleep(0.2)
        print('Run out of fuel')
