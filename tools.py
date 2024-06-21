import pygame
import random, sys, signal, time

# hack to prevent raising KeyboardInterrupt when stopping the script with ctrl-c
# https://stackoverflow.com/questions/7073268/remove-traceback-in-python-on-ctrl-c
signal.signal(signal.SIGINT, lambda x, y: sys.exit())

# create the random number generator object
rng = random.Random()

# colors
black = pygame.Color(15, 15, 15)
white = pygame.Color(255, 255, 255)
red = pygame.Color(245, 61, 5)
green = pygame.Color(14, 171, 0)
blue = pygame.Color(0, 0, 255)
yellow = pygame.Color(252, 252, 25)

# head directions, compass directions
head_dirs = ['UP', 'RIGHT', 'DOWN', 'LEFT']
compass_dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
compass_dirs_empty = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', '']

# proximity values
prox_values = ['', 'f', 'l', 'r', 'fl', 'fr', 'lr', 'flr']

# initial direction and size of the snake
init_direction = 'RIGHT' 
init_size = 4

# read keys pressed by the user
def read_keys():
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                return 'UP'
            if event.key == pygame.K_DOWN:
                return 'DOWN'
            if event.key == pygame.K_LEFT:
                return 'LEFT'
            if event.key == pygame.K_RIGHT:
                return 'RIGHT'
    return "NO_TURN"


# initialise the RNG with a given seed or a random one
def seed_rng(seed=None):
    if seed is None:
        seed = random.randrange(sys.maxsize)
    rng.seed(seed)
    print(f'RNG seed = {seed}')
