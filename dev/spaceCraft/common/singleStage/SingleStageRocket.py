import math
import time

from krpc import Client

from dev.spaceCraft.SpaceCraft import SpaceCraft
from dev.spaceCraft.SpaceCraftConfig import SpaceCraftConfig


# TODO with infinite fuel, the larger altitude is, the greater orbit diff we get
# Currently, we don't consider the limited fuel
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
        self.periapsis = self.connection.add_stream(getattr, self.vessel.orbit, 'periapsis_altitude')

    def launch(self):
        self.set_up_config()
        self.vessel.auto_pilot.engage()
        time.sleep(1)
        self.logger.info('launch started...')
        self.vessel.control.activate_next_stage()

        while True:
            time.sleep(0.05)
            # Decrease throttle when approaching target apoapsis
            if self.apoapsis() > self.config.target_orbit_altitude * 0.95:
                self.vessel.control.throttle = 0.1
                if self.apoapsis() > self.config.target_orbit_altitude * 0.98:
                    self.logger.info(
                        'Approaching target apoapsis, apoapsis: ' + str(self.apoapsis()) + ', target_altitude: ' + str(
                            self.config.target_orbit_altitude))
                    break

            # Gravity turn
            if self.config.kerbin_turn_start_altitude < self.altitude() < self.config.kerbin_turn_end_altitude:
                frac = ((self.altitude() - self.config.kerbin_turn_start_altitude) /
                        (self.config.kerbin_turn_end_altitude - self.config.kerbin_turn_start_altitude))
                new_turn_angle = frac * 90
                if abs(new_turn_angle - self.config.turn_angle) > 0.5:
                    self.config.turn_angle = new_turn_angle
                    self.vessel.auto_pilot.target_pitch_and_heading(90 - self.config.turn_angle, 90)

        # Disable engines when target apoapsis is reached
        self.vessel.control.throttle = 0.05
        self.logger.info(
            'target altitude: ' + str(self.config.target_orbit_altitude) + '; apoapsis: ' + str(self.apoapsis()))
        # TODO we can polish this code by using treemap
        # which means, for our current self.apoapsis(), what strategy should we use
        # like a map<apoapsis, strategy>, a strategy is like: time.sleep(0.05) self.vessel.control.throttle = 1
        while True:
            if self.apoapsis() < self.config.target_orbit_altitude * 0.98:
                time.sleep(0.05)
                self.vessel.control.throttle = 1
            elif self.config.target_orbit_altitude * 0.98 <= self.apoapsis() < self.config.target_orbit_altitude * 0.997:
                time.sleep(0.01)
                self.vessel.control.throttle = 0.3
            elif self.config.target_orbit_altitude * 0.997 <= self.apoapsis() < self.config.target_orbit_altitude:
                time.sleep(0.01)
                self.vessel.control.throttle = 0.02
            else:
                time.sleep(0.01)
                self.vessel.control.throttle = 0.0
                break
        self.logger.info(
            'Target apoapsis reached; target altitude' + str(self.config.target_orbit_altitude) + '; apoapsis: ' + str(
                self.apoapsis()))

        # Wait until out of atmosphere
        self.logger.info('Coasting out of atmosphere')
        while self.altitude() < self.config.kerbin_atmosphere_altitude:
            time.sleep(0.05)

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
        Isp = self.vessel.specific_impulse * self.config.kerbin_g
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
            time.sleep(0.05)

        self.logger.info(
            'Executing burn; time to apoapsis: ' + str(time_to_apoapsis()) + '; burn time: ' + str(burn_time))
        self.vessel.control.throttle = 1.0
        while self.connection.add_stream(node.remaining_burn_vector, node.reference_frame)()[1] > 4.0:
            time.sleep(0.01)
        self.vessel.control.throttle = 0.01
        remaining_burn = self.connection.add_stream(node.remaining_burn_vector, node.reference_frame)
        self.logger.info(
            'Fine tuning; delta_V = ' + str(remaining_burn()[1]) + '; sleep time = ' + str(remaining_burn()[1] / 0.1))
        while remaining_burn()[1] > 0.02:
            time.sleep(0.01)
        self.vessel.control.throttle = 0.0
        self.logger.info("Shutdown Engine")
        node.remove()

        self.calculate_orbit_diff()
        self.logger.info('Launch complete')
