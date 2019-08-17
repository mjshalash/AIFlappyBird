import pygame
import neat
import time
import os
import random
pygame.font.init()

# Constants for Window Size
WIN_WIDTH = 500
WIN_HEIGHT = 800

# Load Images
# Load bird images and make 2x bigger
BIRD_IMGS = [
    pygame.transform.scale2x(pygame.image.load(
        os.path.join("imgs", "bird1.png"))),
    pygame.transform.scale2x(pygame.image.load(
        os.path.join("imgs", "bird2.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]

# Load pipe images and make 2x bigger
PIPE_IMG = pygame.transform.scale2x(
    pygame.image.load(os.path.join("imgs", "pipe.png")))

BASE_IMG = pygame.transform.scale2x(pygame.image.load(
    os.path.join("imgs", "base.png")))

BG_IMG = pygame.transform.scale2x(pygame.image.load(
    os.path.join("imgs", "bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)


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

    # Draw bird (simulates flapping)
    def draw(self, win):
        # How many times has the game loop run
        self.img_count += 1

        # Check what image to show based on image count
        # This simulates the flapping animation (up then down)
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # No flap if facing down
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        # Rotate image around center (found on Stack Overflow)
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(
            center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    # Collision handling
    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    # Gap between pipes
    GAP = 200
    # Pipes moving backwards (remember the bird isnt moving, everything else is)
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0  # Will be assigned randomly later

        # Keep track of where the top and bottom of pipe will be drawn
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    # Set gap
    def set_height(self):
        self.height = random.randrange(50, 450)
        # For top pipe, we need to do some math to set actual position
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    # Move pipes toward bird each frame
    def move(self):
        self.x -= self.VEL

    # Draw Pipes
    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    # Check collision with bird using masks (not just straight box colliders)
    def collide(self, bird, win):
        # Get pixels for bird
        bird_mask = bird.get_mask()

        # Create masks for top and bottom pipes
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        # Calculate how far the masks are from each other
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # Check if the masks collide
        # (Returns none if no collision)
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True

        return False


class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    # Move base backwards to simulate movement
    #
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, bird, pipes, base, score):
    # Draw background/environment
    win.blit(BG_IMG, (0, 0))

    # Draw pipes
    for pipe in pipes:
        pipe.draw(win)

    # Display score text
    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    # Draw Ground
    base.draw(win)

    # Start bird's movement/flapping
    bird.draw(win)
    pygame.display.update()


def main():
    # Create bird object at a certain position
    bird = Bird(230, 350)

    # Create Base with height
    base = Base(730)

    # Create list of multiple pipes
    pipes = [Pipe(600)]

    # Create pygame window
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    # Establish clock so we can control how quick the loop loops
    clock = pygame.time.Clock()

    score = 0

    # Boolean to control game running or not
    run = True

    # Will loop every frame
    while run:
        clock.tick(30)

        # Check for user events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Move bird forward
        # bird.move()

        add_pipe = False
        rem = []
        # Move pipes backward
        for pipe in pipes:
            # Check for bird collision
            if pipe.collide(bird, win):
                pass

            # If pipe completely off screen
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            # If pipe has been passed, generate new pipe
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

            pipe.move()

        # Add to score and add new pipes
        if add_pipe:
            score += 1
            pipes.append(Pipe(700))

        # Remove any old pipes
        for r in rem:
            pipes.remove(r)

        # Bird hits ground = game over
        if bird.y + bird.img.get_height() >= 730:
            pass

            # Draw the game window
        base.move()
        draw_window(win, bird, pipes, base, score)

    # If loop exits then quit game
    pygame.quit()
    quit()


main()
