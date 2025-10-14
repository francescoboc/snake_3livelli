from multiplayer_tools import *

# import default variables
from defaults import box_size, snake_speed, periodic, action_mode, rand_init_body_length, \
    rand_init_direction, state_mode, show_state, show_actions, sound_effects, countdown_seconds

def main():
    # put all shared variables into a list for convenience
    shared_vars = [box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_state, show_actions, 
        sound_effects, countdown_seconds]

    # load a saved policy
    n_episodes = int(1e7)
    pi_star = load_policy(periodic, action_mode, state_mode, n_episodes, verbose=False)

    # build lists of policies and team names
    policies, team_names = [None, pi_star], ['Umano', 'AI']

    # pass the same seed to all the games
    seed = random.randrange(sys.maxsize)

    # run the games in parallel
    scores_dict = human_policy_vs_ai(policies, team_names, shared_vars, seed)

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')
    main()
