import gym
from gym import spaces
from gym.utils import seeding


class AbstractEnv(gym.Env):
    """
    A generic environment for various tasks.
    The environment contains a space populated with spacecrafts, and a controlled ego-vehicle that can change direction
        and velocity. The action space is fixed, but the observation space and reward function must be defined in the
        environment implementations.
    """
    metadata = {'render.modes': ['human', 'rgb_array']}

    ACTIONS = {0:' LEFT',
               1: 'IDLE',
               2: 'RIGHT',
               3: 'FASTER',
               4: 'SLOWER'}

    ACTIONS_INDEXES = {v: k  for k, v in ACTIONS.items()}

    SIMULATION_FREQUENCY = 15

    PERCEPTION_DISTANCE = 6.0

    def __init__(self, config=None):
        self.config = self.defaulf_config()
        if config:
            self.config.update(config)

        # Seeding
        self.np_random = None
        self.seed()

        # Scene
        self.space = None
        self.spacecraft = None

        # Spaces
        self.observation = None
        self.action_space = None
        self.observation_space = None
        self.define_spaces()

        # Running
        self.time = 0  # Simulation time
        self.steps = 0  # Actions performed
        self.done = False

        # Rendering
        self.viewer = None
        self.automatic_rendering_callback = None
        self.should_update_rendering = True
        self.rendering_mode = 'human'
        self.offscreen = self.config.get("offscreen_rendering", False)
        self.enable_auto_render = False

        self.reset()

    @classmethod
    def default_config(cls):
        """
            Default environment configuration.

            Can be overloaded in environment implementations, or by calling configure().
        :return: a configuration dict
        """
        return {
            "observation": {
                "type": "TimeToCollision"
            },
            "policy_frequency": 1,  # [Hz]
            "other_spacecrafts_type": "space_env.spacecraft.behavior.IDMspacecraft",
            "screen_width": 600,  # [px]
            "screen_height": 600,  # [px]
            "centering_position": [0.3, 0.5],
            "show_trajectories": False
        }

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def configure(self, config):
        if config:
            self.config.update(config)

    def define_spaces(self):
        self.action_space = spaces.Discrete(len(self.ACTIONS))

        if "observation" not in self.config:
            raise ValueError("The observation configuration must be defined")
        self.observation = observation_factory(self, self.config["observation"])
        self.observation_space = self.observation.space()

    def _reward(self, action):
        """
            Return the reward associated with performing a given action and ending up in the current state.

        :param action: the last action performed
        :return: the reward
        """
        raise NotImplementedError

    def _is_terminal(self):
        """
            Check whether the current state is a terminal state
        :return:is the state terminal
        """
        raise NotImplementedError

    def _cost(self, action):
        """
            A constraint metric, for budgeted MDP.

            If a constraint is defined, it must be used with an alternate reward that doesn't contain it
            as a penalty.
        :param action: the last action performed
        :return: the constraint signal, the alternate (constraint-free) reward
        """
        raise NotImplementedError

    def reset(self):
        """
            Reset the environment to it's initial configuration
        :return: the observation of the reset state
        """
        self.time = 0
        self.done = False
        self.define_spaces()
        return self.observation.observe()

    def step(self, action):
        """
            Perform an action and step the environment dynamics.

            The action is executed by the ego-spacecraft, and all other spacecrafts perform their default
            behaviour for several simulation timesteps until the next decision making step.
        :param int action: the action performed by the ego-spacecraft
        :return: a tuple (observation, reward, terminal, info)
        """
        if self.space is None or self.spacecraft is None:
            raise NotImplementedError("The spacecraft must be initialized in the environment implementation")

        self._simulate(action)

        obs = self.observation.observe()
        reward = self._reward(action)
        terminal = self._is_terminal()

        info = {
            "velocity": self.spacecraft.velocity,
            "crashed": self.spacecraft.crashed,
            "action": action,
        }
        try:
            info["cost"] = self._cost(action)
        except NotImplementedError:
            pass

        return obs, reward, terminal, info

    def _simulate(self, action=None):
        """
            Perform several steps of simulation with constant action
        """
        for k in range(int(self.SIMULATION_FREQUENCY // self.config["policy_frequency"])):
            if action is not None and \
                    self.time % int(self.SIMULATION_FREQUENCY // self.config["policy_frequency"]) == 0:
                # Forward action to the spacecraft
                self.spacecraft.act(self.ACTIONS[action])

            self.space.act()
            self.space.step(1 / self.SIMULATION_FREQUENCY)
            self.time += 1

            # Automatically render intermediate simulation steps if a viewer has been launched
            # Ignored if the rendering is done offscreen
            self._automatic_rendering()

            # Stop at terminal states
            if self.done or self._is_terminal():
                break
        self.enable_auto_render = False

    def render(self, mode='human'):
        """
            Render the environment.

            Create a viewer if none exists, and use it to render an image.
        :param mode: the rendering mode
        """
        self.rendering_mode = mode

        if self.viewer is None:
            self.viewer = EnvViewer(self, offscreen=self.offscreen)

        self.enable_auto_render = not self.offscreen

        # If the frame has already been rendered, do nothing
        if self.should_update_rendering:
            self.viewer.display()

        if mode == 'rgb_array':
            image = self.viewer.get_image()
            if not self.viewer.offscreen:
                self.viewer.handle_events()
            self.viewer.handle_events()
            return image
        elif mode == 'human':
            if not self.viewer.offscreen:
                self.viewer.handle_events()
        self.should_update_rendering = False

    def close(self):
        """
            Close the environment.

            Will close the environment viewer if it exists.
        """
        self.done = True
        if self.viewer is not None:
            self.viewer.close()
        self.viewer = None

    def get_available_actions(self):
        """
            Get the list of currently available actions.

        :return: the list of available actions
        """
        actions = [self.ACTIONS_INDEXES['IDLE']]

        # Shall we also restrict LEFT & RIGHT actions ?

        if self.spacecraft.velocity_index < self.spacecraft.SPEED_COUNT - 1:
            actions.append(self.ACTIONS_INDEXES['FASTER'])
        if self.spacecraft.velocity_index > 0:
            actions.append(self.ACTIONS_INDEXES['SLOWER'])
        return actions

    def _automatic_rendering(self):
        """
            Automatically render the intermediate frames while an action is still ongoing.
            This allows to render the whole video and not only single steps corresponding to agent decision-making.

            If a callback has been set, use it to perform the rendering. This is useful for the environment wrappers
            such as video-recording monitor that need to access these intermediate renderings.
        """
        if self.viewer is not None and self.enable_auto_render:
            self.should_update_rendering = True

            if self.automatic_rendering_callback:
                self.automatic_rendering_callback()
            else:
                self.render(self.rendering_mode)

    def simplify(self):
        """
            Return a simplified copy of the environment where distant spacecrafts have been removed from the space.

            This is meant to lower the policy computational load while preserving the optimal actions set.

        :return: a simplified environment state
        """
        state_copy = copy.deepcopy(self)
        state_copy.space.spacecrafts = [state_copy.spacecraft] + state_copy.space.close_spacecrafts_to(
            state_copy.spacecraft, self.PERCEPTION_DISTANCE)

        return state_copy

    def randomize_behaviour(self):
        env_copy = copy.deepcopy(self)
        for v in env_copy.space.spacecrafts:
            if isinstance(v, IDMspacecraft):
                v.randomize_behavior()
        return env_copy

    def to_finite_mdp(self):
        return finite_mdp(self, time_quantization=1/self.config["policy_frequency"])

    def __deepcopy__(self, memo):
        """
            Perform a deep copy but without copying the environment viewer.
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k not in ['viewer', 'automatic_rendering_callback']:
                setattr(result, k, copy.deepcopy(v, memo))
            else:
                setattr(result, k, None)
        return result