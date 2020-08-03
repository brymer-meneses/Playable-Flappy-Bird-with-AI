import pygame
import random
import os
import time
import neat

pygame.font.init()

# Background Images
BG_IMG = pygame.transform.scale2x(
    pygame.image.load(os.path.join('imgs', 'background.png')))
BASE_IMG = pygame.transform.scale2x(
    pygame.image.load(os.path.join('imgs', 'base.png')))


# List object that contains bird animation from 1 - 3
BIRD_IMGS = [
    pygame.transform.scale2x(pygame.image.load(
        os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(
        os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(
        os.path.join('imgs', 'bird3.png'))),
]

# Pipe Inage
PIPE_IMG = pygame.transform.scale2x(
    pygame.image.load(os.path.join('imgs', 'pipe.png')))


# Window Configuration
WIN_WIDTH = 700
WIN_HEIGHT = 700

# MAIN WINDOW
window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))


STAT_FONT = pygame.font.SysFont("comicsansms", 40)
machine_learning = False
bird_jump = False
GEN = 0


class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VELOCITY = 20
    ANIMATION_TIME = 5

    # Default Bird Property

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.velocity = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    # Make the bird jump
    def jump(self):
        self.velocity = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1

        # displacement (y direction)= vt + 1/2 (a t^2) - Kinematic Equation
        # v (inital velocity) = self.velocity
        # t (time) = tick_count
        # a (acceleration due to gravity) = 3

        displacement = self.velocity * \
            self.tick_count + (1.5*self.tick_count**2)

        if displacement >= 16:
            displacement = 16  # maintains the distance travelled by the bird

        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VELOCITY

    def draw(self, window):
        self.img_count += 1  # Animates the bird

        # if the img_count < 5 show the first flappy bird photo
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]

        # if the img_count < 10 (5*2) show the second flappy bird photo
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]

        # if the img_count < 10 (5*2) show the third flappy bird photo
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]

        # if the img_count < 15 (5*3) show the second flappy bird photo
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]

        # if the img_count < 20 (5*4) show the first flappy bird photo
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # if the img_count = 20 (5*4) + 1 show the first flappy bird photo
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0  # reset the img_count

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(
            center=self.img.get_rect(topleft=(int(self.x), int(self.y))).center)
        window.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Base:
    VELOCITY = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VELOCITY  # makes the first image move
        self.x2 -= self.VELOCITY  # makes the second image move

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, window):
        window.blit(self.IMG, (self.x1, self.y))
        window.blit(self.IMG, (self.x2, self.y))


class Pipe:

    GAP = 160
    VELOCITY = 5

    def __init__(self, x):

        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):

        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):

        self.x -= self.VELOCITY

    def draw(self, window):

        window.blit(self.PIPE_TOP, (self.x, self.top))
        window.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):

        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True
        return False


def draw(window, base, bird, pipes, score, gen):

    # Draws Background
    window.blit(BG_IMG, (0, 0))
    window.blit(BG_IMG, (440, 0))

    # Draws Base

    # Draws Bird
    global machine_learning

    for pipe in pipes:
        pipe.draw(window)

    if machine_learning == False:
        bird.draw(window)
    else:

        text = STAT_FONT.render("Gen: " + str(gen), 1, (255, 255, 255))
        window.blit(text, (10, 10))

        for x in bird:
            x.draw(window)

    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    window.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    base.draw(window)

    pygame.display.update()


def player_mode():
    global bird_jump
    gen = 0
    # Necessary commands for the loop
    quit = False

    clock = pygame.time.Clock()
    score = 0

    # Game Commands

    bird = Bird(230, 300)  # Summons bird
    base = Base(620)  # Summons base

    bird_jump = True  # initial jump

    pipes = [Pipe(800)]

    while not quit:
        
        add_pipe = False
        reset = False

        # Assigns framerate
        clock.tick(30)

        for event in pygame.event.get():

            # Tests for quit
            if event.type == pygame.QUIT:
                quit = True

            # Tests for bird jumping
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:

                    
                    bird_jump = True

                if event.key == pygame.K_h:
                    start_loop()
                    quit = True

        # Start of the Game
        bird.move()

        
        if bird_jump == True:
            

            bird.jump()
            bird_jump = False

        for pipe in pipes:

            if not pipe.passed and pipe.x < bird.x + 100:

                pipe.passed = True
                add_pipe = True

            if pipe.collide(bird) or bird.y > 580:

                reset = True

            pipe.move()

        if add_pipe:
            score += 1
            pipes.append(Pipe(700))

        # if player hits a pipe
        if reset:
            start_loop()
            quit = True

        base.move()
        draw(window, base, bird, pipes, score, gen)


def ai_mode(genomes, config):

    global GEN
    GEN += 1
    nets = []
    ge = []
    birds = []
    
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 300))
        g.fitness = 0
        ge.append(g)

    # Necessary commands for the loop
    quit = False

    clock = pygame.time.Clock()
    score = 0
    base = Base(620)  # Summons base
    pipes = [Pipe(800)]

    while not quit:
        add_pipe = False

        # Assigns framerate
        clock.tick(30)

        for event in pygame.event.get():

            # Tests for quit
            if event.type == pygame.QUIT:
                quit = True
                pygame.quit()
                quit()

            # Tests for bird jumping
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    start_loop()
                    quit = True

        pipe_ind = 0

        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            quit = True
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[x].activate((
                bird.y,
                abs(bird.y - pipes[pipe_ind].height),
                abs(bird.y - pipes[pipe_ind].bottom)
            ))

            if output[0] > 0.5:
                bird.jump()

        rem = []

        for pipe in pipes:
            for x, bird in enumerate(birds):
                

                if pipe.collide(bird):
                    ge[x]. fitness -= 1

                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:

                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe) 

            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(700))

        

        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 630 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
        
        
        

        base.move()
        draw(window, base, birds, pipes, score, GEN)

        

def start_loop():

    quit = False
    gen = 0

    base = Base(620)
    bird = Bird(230, 300)
    pipes = []
    score = 0

    clock = pygame.time.Clock()
    while not quit:

        clock.tick(30)
        for event in pygame.event.get():

            # Tests for quit
            if event.type == pygame.QUIT:
                quit = True

            # Tests for bird jumping
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:

                    player_mode()
                    quit = True

                if event.key == pygame.K_a:

                    global machine_learning
                    machine_learning = True

                    run(config_path)
                    quit = True

        base.move()
        draw(window, base, bird, pipes, score, gen)


def run(config_path):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    p = neat.Population(config)

    
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(ai_mode, 200)


if __name__ == "__main__":

    config_path = os.path.join("config-feedforward.txt")


start_loop()
