from tools import *

# game parameters
box_size = 20
periodic = True
action_mode = 3
rand_init_body_length = False
rand_init_direction = False

# state mode
state_mode = 'simple'
# state_mode = 'proximity'

# number of teset games
n_games = 1000

# load a saved policy
n_episodes = int(1e7)
box_size = 30
policy = load_policy(periodic, action_mode, state_mode, n_episodes)

mean_score, trun_ratio = test_policy(action_mode, state_mode, box_size, periodic, rand_init_body_length, rand_init_direction, n_games, policy)
