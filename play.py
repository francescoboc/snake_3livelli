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

state_mode = 'simple'
# state_mode = 'body_length'
# state_mode = 'tail_compass'
# state_mode = 'com_compass'
# state_mode = 'proximity'

rand_init_body_length = False
rand_init_direction = False

snake = Snake(action_mode, state_mode, cell_size, box_size, snake_speed, periodic, rand_init_body_length, rand_init_direction)

pi_star = None

# load a saved policy
n_episodes = int(1e7)
pi_star = load_policy(periodic, box_size, action_mode, state_mode, n_episodes)

snake.play(pi_star)
