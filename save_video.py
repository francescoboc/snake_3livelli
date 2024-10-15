from snake import *

# in case we need to reload the library
from importlib import reload
reload(sys.modules['snake'])
from snake import *

# seed for the RNG
seed = 7773300

# game parameters
box_size = 20
snake_speed = 50
periodic = True
action_mode = 3
rand_init_body_length = False
rand_init_direction = False

# state mode
state_mode = 'simple'
# state_mode = 'proximity'

# visual and sound effects
show_compass = True
sound_effects = True
show_state_info = False
window_size = 900
cell_size = window_size//box_size

# load a saved policy
n_episodes = int(1e6)

policy = load_policy(periodic, action_mode, state_mode, n_episodes, label='demo')

team_name = f'AI | {n_episodes} partite'
window_position = None
verbose = False
countdown_seconds = 0
color_scheme = 'grey'

# create snake game object
snake = Snake(action_mode, state_mode, cell_size, box_size, snake_speed, periodic, 
        rand_init_body_length, rand_init_direction, show_compass, sound_effects, 
        show_state_info, team_name, window_position, verbose, countdown_seconds, 
        color_scheme, seed)

snake.play(policy)

# snake.play(policy, save_video=True)
# video_path = f'demo_{n_episodes}.mp4'
# snake.save_video(video_path, fps=12)

