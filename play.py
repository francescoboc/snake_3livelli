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
snake_speed = 100

# game parameters
periodic = True
action_mode = 3
rand_init_body_length = True
rand_init_direction = False

state_mode = 'simple'
# state_mode = 'proximity'

sound_effects = True
show_state_info = False

snake = Snake(action_mode, state_mode, cell_size, box_size, snake_speed, periodic, 
        rand_init_body_length, rand_init_direction, sound_effects, show_state_info)

pi_star = None

# load a saved policy
n_episodes = int(1e7)
pi_star = load_policy(periodic, box_size, action_mode, state_mode, n_episodes)

snake.play(pi_star)
