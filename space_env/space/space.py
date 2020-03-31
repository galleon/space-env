import jax.numpy as np
import logging

from space_env.logger import Loggable
from space_env.spacecraft.dynamics import Obstacle

logger = logging.getLogger(__name__)

class Space(Loggable):
    """
        An area and a set of spacecrafts flying around
    """

    def __init__(self, spacecrafts=None, np_random=None, record_history=False):
        """
            New road.

        :param network: the road network describing the lanes
        :param spacecrafts: the spacecrafts driving on the road
        :param np.random.RandomState np_random: a random number generator for spacecraft behaviour
        :param record_history: whether the recent trajectories of spacecrafts should be recorded for display
        """
        self.spacecrafts = spacecrafts or []
        self.np_random = np_random if np_random else np.random.RandomState()
        self.record_history = record_history

    def close_spacecrafts_to(self, spacecraft, distance, count=None, sort=False, see_behind=True):
        spacecrafts = [v for v in self.spacecrafts
                    if np.linalg.norm(v.position - spacecraft.position) < distance
                    and v is not spacecraft
                    and (see_behind or -2*spacecraft.LENGTH < spacecraft.lane_distance_to(v))]
        if sort:
            spacecrafts = sorted(spacecrafts, key=lambda v: abs(spacecraft.lane_distance_to(v)))
        if count:
            spacecrafts = spacecrafts[:count]
        return spacecrafts

    def act(self):
        """
            Decide the actions of each entity.
        """
        for spacecraft in self.spacecrafts:
            spacecraft.act()

    def step(self, dt):
        """
            Step the dynamics of each entity on the road.

        :param dt: timestep [s]
        """
        for spacecraft in self.spacecrafts:
            spacecraft.step(dt)

        for spacecraft in self.spacecrafts:
            for other in self.spacecrafts:
                spacecraft.check_collision(other)

    def neighbour_spacecrafts(self, spacecraft):
        """
            Find the neighboring spacecrafts of a given spacecraft.
        :param spacecraft: the spacecraft whose neighbours must be found
        :return: its neighboring spacecraft
        """

        lane = self.network.get_lane(lane_index)
        s = self.network.get_lane(lane_index).local_coordinates(spacecraft.position)[0]
        s_front = s_rear = None
        v_front = v_rear = None
        for v in self.spacecrafts:
            if v is not spacecraft and True :

        return None

    def dump(self):
        """
            Dump the data of all entities in the space
        """
        for v in self.spacecrafts:
            if not isinstance(v, Obstacle):
                v.dump()

    def get_log(self):
        """
            Concatenate the logs of all entities on the road.
        :return: the concatenated log.
        """
        return pd.concat([v.get_log() for v in self.spacecrafts])

    def __repr__(self):
        return self.spacecrafts.__repr__()