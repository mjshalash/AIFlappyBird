import pygame
import neat
import time
import os
import random

# Constants for Window Size
WIN_WIDTH = 600
WIN_WIDTH = 800

# Load Images
# Load bird images and make 2x bigger
BIRD_IMGS = [
    pygame.transform.scale2x(pygame.image.load(
        os.path.join("imgs", "bird1.png"))),
    pygame.transform.scale2x(pygame.image.load(
        os.path.join("imgs", "bird2.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]

# Load pipe images and make 2x bigger
PIPE_IMG = [
    pygame.transform.scale2x(pygame.image.load(
        os.path.join("imgs", "pipe.png")))]

BASE_IMG = [
    pygame.transform.scale2x(pygame.image.load(
        os.path.join("imgs", "base.png")))]

BG_IMG = [
    pygame.transform.scale2x(pygame.image.load(
        os.path.join("imgs", "bg.png")))]


# Bird Class
class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0  # Represents how long we have been moving
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    # Controls bird jump on user press
    def jump(self):
        self.vel = -10.5

        # Reset tick_count on jump
        self.tick_count = 0
        self.height = self.y

    # Used to control bird moving forword
    # Will be called in a loop
    def move(self):
        self.tick_count += 1

        # Acceleration Physics equation to know how much we are moving up or down
        # and thus apply the arc affect to the jump
        # as tick count goes up, d decreases
        d = self.vel * self.tick_count + 1.5*self.tick_count**2

        # Set maximum "falling acceleration"
        if d >= 16:
            d = 16

        # Set maximum upward movement
        if d < 0:
            d -= 2

        # Create movement
        self.y = self.y + d

        # Establish tilt if acceleration is upwards or if above middle point
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        # If falling, turn bird 90 degress down
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    # Draw bird
    def draw(self, win):
        # How many times has the game loop run
        self.img_count += 1
