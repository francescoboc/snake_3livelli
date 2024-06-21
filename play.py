from snake import *

# in case we need to reload the library
from importlib import reload
reload(sys.modules['snake'])
from snake import *

# seed to initialize the RNG
seed_rng(seed=None)

# snake parameters
cell_size = 30
box_size = 30
snake_speed = 15
periodic = True

action_mode = 3
rand_init_body_length = True
rand_init_direction = True

# state_mode = 'simple'
# state_mode = 'body_length'
# state_mode = 'tail_compass'
# state_mode = 'com_compass'
state_mode = 'proximity'

snake = Snake(action_mode, state_mode, cell_size, box_size, snake_speed, periodic, rand_init_body_length, rand_init_direction)

pi_star = None

# # load a saved policy
# import numpy as np
# n_episodes = int(1e7)
# policy_folder = f'policies/{"periodic" if periodic else "non_periodic"}'
# pi_star = np.load(f'{policy_folder}/pi_{box_size}_{action_mode}_{state_mode}_{n_episodes:.0e}.npy', allow_pickle=True).item()

snake.play(pi_star)
