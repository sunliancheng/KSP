import math
import time

from krpc import Client

from dev.spaceCraft.SpaceCraft import SpaceCraft
from dev.spaceCraft.SpaceCraftConfig import SpaceCraftConfig


class SingleStageRocket(SpaceCraft):

    def set_up_config(self):
        # Pre-launch setup
        self.vessel.control.sas = self.config.sas
        self.vessel.control.rcs = self.config.rcs
        self.vessel.control.throttle = self.config.throttle
        self.vessel.auto_pilot.target_pitch_and_heading(self.config.pitch, self.config.heading)

    # how can we define a single stage rocket?
    # 1. an engine, a separator, fuel

    def __init__(self, conn: Client, config: SpaceCraftConfig):
        super().__init__(conn, config)
        # Set up streams for telemetry
        self.ut = self.connection.add_stream(getattr, self.connection.space_center, 'ut')
        self.altitude = self.connection.add_stream(getattr, self.vessel.flight(), 'mean_altitude')
        self.apoapsis = self.connection.add_stream(getattr, self.vessel.orbit, 'apoapsis_altitude')

    def launch(self):
        self.set_up_config()

        self.vessel.auto_pilot.engage()
        time.sleep(1)
        self.vessel.control.activate_next_stage()

        while True:
            # Gravity turn
            if self.config.kerbin_turn_start_altitude < self.altitude() < self.config.kerbin_turn_end_altitude:
                frac = ((self.altitude() - self.config.kerbin_turn_start_altitude) /
                        (self.config.kerbin_turn_end_altitude - self.config.kerbin_turn_start_altitude))
                new_turn_angle = frac * 90
                if abs(new_turn_angle - self.config.turn_angle) > 0.5:
                    self.config.turn_angle = new_turn_angle
                    self.vessel.auto_pilot.target_pitch_and_heading(90 - self.config.turn_angle, 90)

            # Decrease throttle when approaching target apoapsis
            if self.apoapsis() > self.config.target_altitude * 0.9:
                self.logger.info('Approaching target apoapsis')
                break

        # Disable engines when target apoapsis is reached
        self.vessel.control.throttle = 0.25
        while self.apoapsis() < self.config.target_altitude:
            pass
        self.logger.info('Target apoapsis reached')
        self.vessel.control.throttle = 0.0

        # Wait until out of atmosphere
        self.logger.info('Coasting out of atmosphere')
        while self.altitude() < self.config.kerbin_atmosphere_altitude:
            pass

        # Plan circularization burn (using vis-viva equation)
        self.logger.info('Planning circularization burn')
        mu = self.vessel.orbit.body.gravitational_parameter
        r = self.vessel.orbit.apoapsis
        a1 = self.vessel.orbit.semi_major_axis
        a2 = r
        v1 = math.sqrt(mu * ((2. / r) - (1. / a1)))
        v2 = math.sqrt(mu * ((2. / r) - (1. / a2)))
        delta_v = v2 - v1
        node = self.vessel.control.add_node(
            self.ut() + self.vessel.orbit.time_to_apoapsis, prograde=delta_v)

        # Calculate burn time (using rocket equation)
        F = self.vessel.available_thrust
        Isp = self.vessel.specific_impulse * 9.82
        m0 = self.vessel.mass
        m1 = m0 / math.exp(delta_v / Isp)
        flow_rate = F / Isp
        burn_time = (m0 - m1) / flow_rate

        # Orientate ship
        self.logger.info('Orientating ship for circularization burn')
        self.vessel.auto_pilot.reference_frame = node.reference_frame
        self.vessel.auto_pilot.target_direction = (0, 1, 0)
        self.vessel.auto_pilot.wait()

        # Wait until burn
        self.logger.info('Waiting until circularization burn')
        burn_ut = self.ut() + self.vessel.orbit.time_to_apoapsis - (burn_time / 2.)
        lead_time = 5
        self.connection.space_center.warp_to(burn_ut - lead_time)

        # Execute burn
        self.logger.info('Ready to execute burn')
        time_to_apoapsis = self.connection.add_stream(getattr, self.vessel.orbit, 'time_to_apoapsis')
        while time_to_apoapsis() - (burn_time / 2.) > 0:
            pass

        self.logger.info('Executing burn')
        self.vessel.control.throttle = 1.0
        time.sleep(burn_time - 0.1)
        self.logger.info('Fine tuning')
        self.vessel.control.throttle = 0.05
        remaining_burn = self.connection.add_stream(node.remaining_burn_vector, node.reference_frame)
        while remaining_burn()[1] > 0:
            pass
        self.vessel.control.throttle = 0.0
        node.remove()

        self.logger.info('Launch complete')
        while self.current_stage_engine_has_fuel():
            time.sleep(0.2)

        self.logger.info('Run out of fuel')
