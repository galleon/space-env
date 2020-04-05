from __future__ import division, print_function, absolute_import

import os

import numpy as np
import pygame
from gym.spaces import Discrete

from space_env.space.graphics import SpaceSurface
from space_env.spacecraft.graphics import SpacecraftGraphics


class EnvViewer(object):
    """
        A viewer to render a highway driving environment.
    """
    SAVE_IMAGES = False

    def __init__(self, env, offscreen=False):
        self.env = env
        self.offscreen = offscreen

        pygame.init()
        pygame.display.set_caption("Space-env")
        panel_size = (self.env.config["screen_width"], self.env.config["screen_height"])

        # A display is not mandatory to draw things. Ignoring the display.set_mode()
        # instruction allows the drawing to be done on surfaces without
        # handling a screen display, useful for e.g. cloud computing
        if not self.offscreen:
            self.screen = pygame.display.set_mode([self.env.config["screen_width"], self.env.config["screen_height"]])
        self.sim_surface = SpaceSurface(panel_size, 0, pygame.Surface(panel_size))
        self.sim_surface.scaling = env.config.get("scaling", self.sim_surface.INITIAL_SCALING)
        self.sim_surface.centering_position = env.config.get("centering_position", self.sim_surface.INITIAL_CENTERING)
        self.clock = pygame.time.Clock()

        self.enabled = True
        if "SDL_VIDEODRIVER" in os.environ and os.environ["SDL_VIDEODRIVER"] == "dummy":
            self.enabled = False

        self.agent_display = None
        self.agent_surface = None
        self.spacecraft_trajectory = None
        self.frame = 0

    def set_agent_display(self, agent_display):
        """
            Set a display callback provided by an agent, so that they can render their behaviour on a dedicated
            agent surface, or even on the simulation surface.
        :param agent_display: a callback provided by the agent to display on surfaces
        """
        if self.agent_display is None:
            if self.env.config["screen_width"] > self.env.config["screen_height"]:
                self.screen = pygame.display.set_mode((self.env.config["screen_width"],
                                                       2 * self.env.config["screen_height"]))
            else:
                self.screen = pygame.display.set_mode((2 * self.env.config["screen_width"],
                                                       self.env.config["screen_height"]))
            self.agent_surface = pygame.Surface((self.env.config["screen_width"], self.env.config["screen_height"]))
        self.agent_display = agent_display

    def set_agent_action_sequence(self, actions):
        """
            Set the sequence of actions chosen by the agent, so that it can be displayed
        :param actions: list of action, following the env's action space specification
        """
        return
        if isinstance(self.env.action_space, Discrete):
            actions = [self.env.ACTIONS[a] for a in actions]
        if len(actions) > 1:
            self.spacecraft_trajectory = self.env.spacecraft.predict_trajectory(actions,
                                                                          1 / self.env.config["policy_frequency"],
                                                                          1 / 3 / self.env.config["policy_frequency"],
                                                                          1 / self.env.SIMULATION_FREQUENCY)

    def handle_events(self):
        """
            Handle pygame events by forwarding them to the display and environment vehicle.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.env.close()
            self.sim_surface.handle_event(event)
            if self.env.spacecraft:
                SpacecraftGraphics.handle_event(self.env.spacecraft, event)

    def display(self):
        """
            Display the space and spacecrafts on a pygame window.
        """
        if not self.enabled:
            return

        self.sim_surface.move_display_window_to(self.window_position())
        RoadGraphics.display(self.env.space, self.sim_surface)

        if self.vehicle_trajectory:
            SpacecraftGraphics.display_trajectory(
                self.spacecraft_trajectory,
                self.sim_surface,
                offscreen=self.offscreen)
        """
        RoadGraphics.display_traffic(
            self.env.space,
            self.sim_surface,
            simulation_frequency=self.env.SIMULATION_FREQUENCY,
            offscreen=self.offscreen)
        """

        if self.agent_display:
            self.agent_display(self.agent_surface, self.sim_surface)
            if self.env.config["screen_width"] > self.env.config["screen_height"]:
                self.screen.blit(self.agent_surface, (0, self.env.config["screen_height"]))
            else:
                self.screen.blit(self.agent_surface, (self.env.config["screen_width"], 0))

        if not self.offscreen:
            self.screen.blit(self.sim_surface, (0, 0))
            self.clock.tick(self.env.SIMULATION_FREQUENCY)
            pygame.display.flip()

        if self.SAVE_IMAGES:
            pygame.image.save(self.screen, "space-env_{}.png".format(self.frame))
            self.frame += 1

    def get_image(self):
        """
        :return: the rendered image as a rbg array
        """
        data = pygame.surfarray.array3d(self.sim_surface)
        return np.moveaxis(data, 0, 1)

    def window_position(self):
        """
        :return: the world position of the center of the displayed window.
        """
        if self.env.spacecraft:
            return self.env.spacecraft.position
        else:
            return np.array([0, 0])

    def close(self):
        """
            Close the pygame window.
        """
        pygame.quit()