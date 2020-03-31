from gym.envs.registration import register

from space_env import utils
from space_env.env.common.abstract import AbstractEnv
from space_env.spacecraft.control import MDPSpacecraft

class SpaceEnv(AbstractEnv):
    """
       A flying environment

       The spacecraft is flying to reach is goal as quickly as possible and avoiding collision
    """

    COLLISION_REWARD = -100
    HIGH_VELOCITY_REWARD = 1
    REACH_GOAL_REWARD = 1

    def default_config(self):
        config = super().default_config()
        config.update({
            "observation":{
                "type": "Kinematics"
            }
            "duration": 40,
            "spacecrafts_count": 2,
            "collision_reward": self.COLLISION_REWARD
        }) 
        return config 

    def reset(self):
        self._create_space()
        self._create_spacecrafts()
        self.steps = 0
        return super(SpaceEnv, self).reset()

    def step(self, action):
        self.steps += 1
        return super(SpaceEnv, self).step(action)

    def _create_space(self):
        """
            Create a space
        """

    def _create_spacecrafts(self):
        """
            Create some random vehicles of a given type and add them in space
        """
        self.spacecraft = MPDSpacecraft.create_random(self.space, )
        self.space.spacecrafts.append(self.spacecraft)

        vehicles_type = utils.class_from_path(self.config["other_spacecrafts_type"])
        for _ in range(self.config["spacecrafts_count"]):
            self.road.spacecrafts.append(spacecrafts_type.create_random(self.space))

    def _reward(self, action):
        """
            The reward is defined to foster the flying at high speed 
            :param action: the last action performed
            :retur: the corresponding reward
        """
        action_reward = {0: 0}
        state_reward = self.config["collision_reward"] * self.spacecraft.crashed +\
                       self.COLLISION_REWARD
        return utils.remap()

    def _is_terminal(self):
        """
            The episode is over if the ego spacecraft crashed or the time is out.
        """
        return self.spacecraft.crashed or self.steps >= self.config["duration"]

    def _cost(self, action):
        """
            The cost signal is the occurrence of collision
        """
        return float(self.spacecraft.crashed)

register(
    id='space-v0',
    entry_point='space_env.envs:SpaceEnv',
)        