from __future__ import division, print_function

import itertools

import numpy as np
import pygame

from space_env.spacecraft.dynamics import Spacecraft, Obstacle
from space_env.spacecraft.control import ControlledSpacecraft, MDPSpacecraft
from space_env.spacecraft.behavior import IDMSpacecraft, LinearSpacecraft

class VehicleGraphics(object):
    RED = (255, 100, 100)
    GREEN = (50, 200, 0)
    BLUE = (100, 200, 255)
    YELLOW = (200, 200, 0)
    BLACK = (60, 60, 60)
    PURPLE = (200, 0, 150)
    DEFAULT_COLOR = YELLOW
    EGO_COLOR = GREEN

    @classmethod
    def display(cls, spacecraft, surface, transparent=False, offscreen=False):
        """
            Display a spacecraft on a pygame surface.

            The spacecraft is represented as a colored rotated rectangle.

        :param spacecraft: the spacecraft to be drawn
        :param surface: the surface to draw the spacecraft on
        :param transparent: whether the spacecraft should be drawn slightly transparent
        :param offscreen: whether the rendering should be done offscreen or not
        """
        v = spacecraft
        s = pygame.Surface((surface.pix(v.LENGTH), surface.pix(v.LENGTH)), pygame.SRCALPHA)  # per-pixel alpha
        rect = (0, surface.pix(v.LENGTH) / 2 - surface.pix(v.WIDTH) / 2, surface.pix(v.LENGTH), surface.pix(v.WIDTH))
        pygame.draw.rect(s, cls.get_color(v, transparent), rect, 0)
        pygame.draw.rect(s, cls.BLACK, rect, 1)
        if not offscreen:  # convert_alpha throws errors in offscreen mode TODO() Explain why
            s = pygame.Surface.convert_alpha(s)
        h = v.heading if abs(v.heading) > 2 * np.pi / 180 else 0
        sr = pygame.transform.rotate(s, -h * 180 / np.pi)
        surface.blit(sr, (surface.pos2pix(v.position[0] - v.LENGTH / 2, v.position[1] - v.LENGTH / 2)))

    @classmethod
    def display_trajectory(cls, states, surface, offscreen=False):
        """
            Display the whole trajectory of a spacecraft on a pygame surface.

        :param states: the list of spacecraft states within the trajectory to be displayed
        :param surface: the surface to draw the spacecraft future states on
        :param offscreen: whether the rendering should be done offscreen or not
        """
        for spacecraft in states:
            cls.display(spacecraft, surface, transparent=True, offscreen=offscreen)

    @classmethod
    def display_history(cls, spacecraft, surface, frequency=3, duration=2, simulation=15, offscreen=False):
        """
            Display the whole trajectory of a spacecraft on a pygame surface.

        :param spacecraft: the spacecraft states within the trajectory to be displayed
        :param surface: the surface to draw the spacecraft future states on
        :param frequency: frequency of displayed positions in history
        :param duration: length of displayed history
        :param simulation: simulation frequency
        :param offscreen: whether the rendering should be done offscreen or not
        """

        for v in itertools.islice(spacecraft.history,
                                  None,
                                  int(simulation * duration),
                                  int(simulation / frequency)):
            cls.display(v, surface, transparent=True, offscreen=offscreen)

    @classmethod
    def get_color(cls, spacecraft, transparent=False):
        color = cls.DEFAULT_COLOR
        if getattr(spacecraft, "color", None):
            color = spacecraft.color
        elif spacecraft.crashed:
            color = cls.RED
        elif isinstance(spacecraft, LinearSpacecraft):
            color = cls.YELLOW
        elif isinstance(spacecraft, IDMSpacecraft):
            color = cls.BLUE
        elif isinstance(spacecraft, MDPSpacecraft):
            color = cls.EGO_COLOR
        elif isinstance(spacecraft, Obstacle):
            color = cls.GREEN
        if transparent:
            color = (color[0], color[1], color[2], 30)
        return color

    @classmethod
    def handle_event(cls, spacecraft, event):
        """
            Handle a pygame event depending on the spacecraft type

        :param spacecraft: the spacecraft receiving the event
        :param event: the pygame event
        """
        if isinstance(spacecraft, ControlledSpacecraft):
            cls.control_event(spacecraft, event)
        elif isinstance(spacecraft, Spacecraft):
            cls.dynamics_event(spacecraft, event)

    @classmethod
    def control_event(cls, spacecraft, event):
        """
            Map the pygame keyboard events to control decisions

        :param spacecraft: the spacecraft receiving the event
        :param event: the pygame event
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                spacecraft.act("FASTER")
            if event.key == pygame.K_LEFT:
                spacecraft.act("SLOWER")
            if event.key == pygame.K_DOWN:
                spacecraft.act("RIGHT")
            if event.key == pygame.K_UP:
                spacecraft.act("LEFT")

    @classmethod
    def dynamics_event(cls, spacecraft, event):
        """
            Map the pygame keyboard events to dynamics actuation

        :param spacecraft: the spacecraft receiving the event
        :param event: the pygame event
        """
        action = spacecraft.action.copy()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                action['steering'] = 45 * np.pi / 180
            if event.key == pygame.K_LEFT:
                action['steering'] = -45 * np.pi / 180
            if event.key == pygame.K_DOWN:
                action['acceleration'] = -6
            if event.key == pygame.K_UP:
                action['acceleration'] = 5
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                action['steering'] = 0
            if event.key == pygame.K_LEFT:
                action['steering'] = 0
            if event.key == pygame.K_DOWN:
                action['acceleration'] = 0
            if event.key == pygame.K_UP:
                action['acceleration'] = 0
        if action != spacecraft.action:
            spacecraft.act(action)