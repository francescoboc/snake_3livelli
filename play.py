from snake import *
from multiplayer_tools import calculate_size_and_positions

# seed for the RNG
seed = None
# seed = 995566
# seed = 87654678
# seed = 987656
# seed = 45678
# seed = 5678654567
# seed = 99494949
# seed = 883838
# seed = 1122589732720105482

# # prox
# seed = 4667075490782767144

# game parameters
box_size = 20
snake_speed = 10
periodic = True
action_mode = 3
rand_init_body_length = False
rand_init_direction = False

# state mode
# state_mode = 'simple'
state_mode = 'proximity'

# visual and sound effects
show_state = False
show_actions = True
sound_effects = False
window_size = 900

team_name = None
verbose = True
countdown_seconds = 0
color_scheme = 'green'

window_position = calculate_size_and_positions(1, box_size)
cell_size = window_size//box_size

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
# label = 'demo'
# policy = load_policy(periodic, action_mode, state_mode, n_episodes, label=label)

snake.play(policy)
