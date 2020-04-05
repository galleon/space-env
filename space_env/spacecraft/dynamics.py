import jax.numpy as np
from collections import deque

from space_env.logger import Loggable

class Spacecraft(Loggable):
    """
       A moving object in space and its dynamics

       The state of the object is propagated depending on its sterring and acceleration  actions
       The spacecraft has a triangle shape
    """

    COLLISION_ENABLED = True

    """ Maximum reachable velocity [m/s] """
    MAX_VELOCITY = 70
    """ spacecraft length [m] """
    LENGTH = 9.0
    """ spacecraft width [m] """
    WIDTH = 4.0
    """ Range for random initial velocities [m/s] """
    DEFAULT_VELOCITIES = [50, 60]
 
    def __init__(self, space, position, heading=0, velocity=0):
        sefl.space = space
        self.position = np.array(position).astype('float')
        self.heading = heading
        self.velocity = velocity
        self.action = {'steering': 0, 'acceleration': 0}
        self.crashed = False
        self.log = []
        self.history = deque(maxlen=30)

    def step(self, dt):
        """
            Propagate the object state given its actions.

            Integrate a model with a 1st-order response on the steering wheel dynamics.
            If the object is crashed, the actions are overridden with erratic steering and braking until complete stop.

        :param dt: timestep of integration of the model [s]
        """
        if self.crashed:
            self.action['steering'] = 0
            self.action['acceleration'] = -1.0*self.velocity
        self.action['steering'] = float(self.action['steering'])
        self.action['acceleration'] = float(self.action['acceleration'])
        if self.velocity > self.MAX_VELOCITY:
            self.action['acceleration'] = min(self.action['acceleration'], 1.0*(self.MAX_VELOCITY - self.velocity))
        elif self.velocity < -self.MAX_VELOCITY:
            self.action['acceleration'] = max(self.action['acceleration'], 1.0*(self.MAX_VELOCITY - self.velocity))

        v = self.velocity * np.array([np.cos(self.heading), np.sin(self.heading)])
        self.position += v * dt
        self.heading += self.velocity * np.tan(self.action['steering']) / self.LENGTH * dt
        self.velocity += self.action['acceleration'] * dt

        if self.road:
            self.lane_index = self.road.network.get_closest_lane_index(self.position)
            self.lane = self.road.network.get_lane(self.lane_index)
            if self.road.record_history:
                self.history.appendleft(self.create_from(self))        

    def check_collision(self, other):
        """
            Check for collision with another spacecraft.

        :param other: the other spacecraft
        """
        if not self.COLLISIONS_ENABLED or not other.COLLISIONS_ENABLED or self.crashed or other is self:
            return

        # Fast spherical pre-check
        if np.linalg.norm(other.position - self.position) > self.LENGTH:
            return

        # Accurate rectangular check

        # Accurate rectangular check
        print("Not implemented")
        if utils.triangles_intersect((self.position , 0.9*self.LENGTH , 0.9*self.WIDTH, self.heading),
                                     (other.position, 0.9*other.LENGTH, 0.9*other.WIDTH, other.heading)):
            self.velocity = other.velocity = min([self.velocity, other.velocity], key=abs)
            self.crashed = other.crashed = True

class Obstacle(Spacecraft):
    """
        A motionless obstacle at a given position.
    """

    def __init__(self, road, position, heading=0):
        super(Obstacle, self).__init__(road, position, velocity=0, heading=heading)
        self.target_velocity = 0
        self.LENGTH = self.WIDTH