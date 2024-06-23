import pygame
import random, sys, signal, time
from tqdm import tqdm
import numpy as np

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
def seed_rng(seed=None, verbose=True):
    if seed is None:
        seed = random.randrange(sys.maxsize)
    rng.seed(seed)
    if verbose:
        print(f'RNG seed = {seed}')
    return seed

# load a saved policy
def load_policy(periodic, box_size, action_mode, state_mode, n_episodes, verbose=True):
    if periodic: policy_folder = f'policies/periodic'
    else: policy_folder = f'policies/non_periodic'
    policy_name = f'pi_{box_size}_{action_mode}_{state_mode}_{n_episodes:.0e}'
    try: 
        pi_star = np.load(f'{policy_folder}/{policy_name}.npy', allow_pickle=True).item()
        if verbose:
            print(f'Policy {policy_name} loaded!')
    except:
        raise Exception(f'Policy {policy_name} not found!')
    return pi_star

# load a saved policy
def save_policy(periodic, box_size, action_mode, state_mode, n_episodes):
    if periodic: policy_folder = f'policies/periodic'
    else: policy_folder = f'policies/non_periodic'
    policy_name = f'pi_{box_size}_{action_mode}_{state_mode}_{n_episodes:.0e}'
    np.save(f'{policy_folder}/{policy_name}.npy', pi_star)
    print(f'Policy {policy_name} saved!')
    return pi_star

