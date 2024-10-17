from snake import *

# in case we need to reload the library
from importlib import reload
reload(sys.modules['snake'])
from snake import *

# seed for the RNG
seed = 3710131613367855960

# game parameters
box_size = 18
snake_speed = 10
periodic = True
action_mode = 3
rand_init_body_length = True
rand_init_direction = False

# state mode
state_mode = 'simple'
# state_mode = 'proximity'

# visual and sound effects
show_state = False
show_actions = True
sound_effects = True
window_size = 900
cell_size = window_size//box_size

team_name = None
window_position = None
verbose = True
countdown_seconds = 0
color_scheme = 'green'

# create snake game object
snake = Snake(action_mode, state_mode, cell_size, box_size, snake_speed, periodic, 
        rand_init_body_length, rand_init_direction, show_state, show_actions,  
        sound_effects, team_name, window_position, verbose, countdown_seconds, 
        color_scheme, seed)

policy = None

# policy = load_user_policy('i carciofi.txt', 'test_turno/strategie')

# load a saved policy
n_episodes = int(1e7)
label = None
policy = load_policy(periodic, action_mode, state_mode, n_episodes, label=label)

snake.play(policy)
