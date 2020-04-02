import jax.numpy as np
from space_env import utils

from space_env.spacecraft.dynamics import Spacecraft

class ControlledSpacecraft(Spacecraft):
    """
        A spacecraft piloted by two low-level controller, allowing high-level actions
        such as cruise control.

        - The longitudinal controller is a velocity controller;
        - The lateral controller is a heading controller cascaded with a lateral position controller.
    """

    TAU_A = 0.6  # [s]
    TAU_DS = 0.2  # [s]
    PURSUIT_TAU = 1.5*TAU_DS  # [s]
    KP_A = 1 / TAU_A
    KP_HEADING = 1 / TAU_DS
    KP_LATERAL = 1 / 0.5  # [1/s]
    MAX_STEERING_ANGLE = np.pi / 3  # [rad]

    DELTA_VELOCITY = 5  # [m/s]

    def __init__(self,
                 space,
                 position,
                 heading=0,
                 velocity=0,
                 target_lane_index=None,
                 target_velocity=None,
                 route=None):
        super(ControlledVehicle, self).__init__(space, position, heading, velocity)
        self.target_velocity = target_velocity or self.velocity
        self.route = route

    @classmethod
    def create_from(cls, spacecraft):
        """
            Create a new spacecraft from an existing one.
            The spacecraft dynamics and target dynamics are copied, other properties are default.

        :param spacecraft: a spacecraft
        :return: a new spacecraft at the same dynamical state
        """
        v = cls(spacecraft.space, spacecraft.position, heading=spacecraft.heading, velocity=spacecraft.velocity,
                target_lane_index=spacecraft.target_lane_index, target_velocity=spacecraft.target_velocity,
                route=spacecraft.route)
        return v

    def act(self, action=None):
        """
            Perform a high-level action to change the desired heading or velocity.

            - If a high-level action is provided, update the target velocity and heading;
            - then, perform longitudinal and lateral control.

        :param action: a high-level action
        """
        self.follow_road()
        if action == "FASTER":
            self.target_velocity += self.DELTA_VELOCITY
        elif action == "SLOWER":
            self.target_velocity -= self.DELTA_VELOCITY
        elif action == "RIGHT":
            _from, _to, _id = self.target_lane_index
            target_lane_index = _from, _to, np.clip(_id + 1, 0, len(self.road.network.graph[_from][_to]) - 1)
            if self.road.network.get_lane(target_lane_index).is_reachable_from(self.position):
                self.target_lane_index = target_lane_index
        elif action == "LEFT":
            _from, _to, _id = self.target_lane_index
            target_lane_index = _from, _to, np.clip(_id - 1, 0, len(self.road.network.graph[_from][_to]) - 1)
            if self.road.network.get_lane(target_lane_index).is_reachable_from(self.position):
                self.target_lane_index = target_lane_index

        action = {'steering': self.steering_control(self.target_lane_index),
                  'acceleration': self.velocity_control(self.target_velocity)}
        super(ControlledVehicle, self).act(action)