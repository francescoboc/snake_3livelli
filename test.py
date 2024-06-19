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

action_mode = 3

# stateMode = 'simple'
# state_mode = 'body_length'
# state_mode = 'tail_compass'
state_mode = 'com_compass'

snake = Snake(action_mode, state_mode, cell_size, snake_speed=snake_speed, rand_init_body_length=True)

pi_star = None

# import numpy as np
# n_episodes = int(1e7)
# pi_star = np.load(f'policies/pi_{box_size}_{action_mode}_{state_mode}_{n_episodes:.0e}.npy', allow_pickle=True).item()

snake.play(pi_star)
