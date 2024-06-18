from snake import *

# in case we need to reload the library
from importlib import reload
reload(sys.modules['snake'])
from snake import *

# seed to initialize the RNG
seed = None
seed_rng(seed)

# snake parameters
cell_size = 30
box_size = 30
snake_speed = 15
periodic = True

# snake parameters
snake_speed = 15
periodic = True

actionMode = 3

stateMode = 'simple'
# stateMode = 'body_length'
# stateMode = 'tail_compass'

snake = Snake(actionMode, stateMode, cell_size, snake_speed=snake_speed, randomInitialBodyLength=True)

pi_star = None

# import numpy as np
# n_episodes = int(1e7)
# pi_star = np.load(f'policies/pi_{box_size}_{actionMode}_{stateMode}_{n_episodes:.0e}.npy', allow_pickle=True).item()

snake.play(pi_star)
