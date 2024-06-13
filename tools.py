import pygame
import numpy as np
import random, sys, signal, time
from tqdm import tqdm

# hack to prevent raising KeyboardInterrupt when stopping the script with ctrl-c
# https://stackoverflow.com/questions/7073268/remove-traceback-in-python-on-ctrl-c
signal.signal(signal.SIGINT, lambda x, y: sys.exit())

# colors
black = pygame.Color(15, 15, 15)
white = pygame.Color(255, 255, 255)
red = pygame.Color(245, 61, 5)
green = pygame.Color(141, 245, 5)
light_green = pygame.Color(225, 245, 5)
blue = pygame.Color(0, 0, 255)

# head directions, compass directions
head_dirs = ['UP', 'RIGHT', 'DOWN', 'LEFT']
compass_dirs =['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']

# font parameters for printing info on screen
font = 'arial'
font_size = 20

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
