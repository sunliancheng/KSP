import math
import time
from typing import Callable

from krpc import Client
from krpc.services.spacecenter import Vessel, Node

from dev.configs.GeneralConfig import GeneralConfig
from dev.metaClass.MetaClass import MetaClass
from dev.utils.vessel import VesselDvCalculatorUtils


def get_burn_time(vessel: Vessel, dv: float):
    F = vessel.available_thrust
    Isp = vessel.specific_impulse * 9.82
    m0 = vessel.mass
    m1 = m0 / math.exp(dv / Isp)
    flow_rate = F / Isp
    return (m0 - m1) / flow_rate


class VesselControlUtils(MetaClass):
    def __init__(self):
        super().__init__()

    def execute_node(
            self,
            conn: Client,
            vessel: Vessel,
            node: Node,
            stop_condition: Callable[[float], None] | None = None,
    ):
        with conn.stream(getattr, node, "time_to") as time_to, conn.stream(
                getattr, node, "remaining_delta_v"
        ) as remaining_dv:
            self.logger.info("Orienting for burn.")
            vessel.auto_pilot.reference_frame = node.reference_frame
            vessel.auto_pilot.target_direction = (0, 1, 0)
            vessel.auto_pilot.disengage()
            vessel.auto_pilot.engage()
            vessel.auto_pilot.wait()

            self.logger.info("Waiting to start burn.")
            burn_time = get_burn_time(vessel, remaining_dv())
            if time_to() > burn_time / 2 + 2:
                burn_ut = conn.space_center.ut + time_to() - burn_time / 2
                conn.space_center.warp_to(burn_ut - 2)

            while time_to() > burn_time / 2:
                time.sleep(GeneralConfig.wait_sleep)

            self.logger.info("Executing node.")
            if burn_time > 0.5:
                vessel.control.throttle = 1

            if stop_condition:
                stop_condition(burn_time)
            else:
                time.sleep(burn_time - 0.3)
                vessel.control.throttle = 0.05
                prev_dv = remaining_dv()
                while remaining_dv() - prev_dv <= 0:
                    prev_dv = remaining_dv()
                    time.sleep(0.01)  # intentionally not using settings.wait_sleep

            node.remove()
            vessel.control.throttle = 0

    def circularize(self, client: Client, vessel: Vessel):
        dv = VesselDvCalculatorUtils.get_apoapsis_circularize_dv(vessel.orbit)
        node = vessel.control.add_node(
            client.space_center.ut + vessel.orbit.time_to_apoapsis, prograde=dv
        )
        self.execute_node(client, vessel, node)
