from multiplayer_tools import *
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--level', choices=['easy', 'medium', 'hard'], default='medium')
    return parser.parse_args()

# import default variables
from defaults import box_size, snake_speed, periodic, action_mode, rand_init_body_length, \
    rand_init_direction, state_mode, show_state, show_actions, sound_effects, countdown_seconds

# put all shared variables into a list for convenience
shared_vars = [box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
rand_init_direction, state_mode, show_state, show_actions, 
sound_effects, countdown_seconds]

# parse argument to set level of AI
args = parse_args()
level = args.level

# load a saved policy
if level == 'easy':
    n_episodes = int(1e2)
    ai_color = 'blue'
elif level == 'medium':
    n_episodes = int(1e4)
    ai_color = 'orange'
elif level == 'hard':
    n_episodes = int(1e7)
    ai_color = 'pink'

pi_star = load_policy(periodic, action_mode, state_mode, n_episodes, verbose=False)

# build lists of policies and team names
policies, team_names = [None, pi_star], ['Umano', 'AI']

# pass the same seed to all the games
seed = random.randrange(sys.maxsize)

# run the games in parallel
scores_dict = human_policy_vs_ai(policies, team_names, shared_vars, seed, ai_color)
