from multiplayer_tools import *

# # in case we need to reload the library
# from importlib import reload
# reload(sys.modules['snake'])
# from snake import *

# TODO add a countdown in snake!

def demo_1player_nocompass():
    # snake parameters
    box_size = 30
    snake_speed = 10

    # game parameters
    periodic = True
    action_mode = 3
    rand_init_body_length = False
    rand_init_direction = False

    # state mode
    state_mode = 'simple'
    # state_mode = 'proximity'

    # visual and sound effects
    show_compass = False
    sound_effects = True
    show_state_info = False

    # put all shared variables into a list for convenience
    shared_vars = [box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info]

    # if policy is None the game is launched in interactive mode
    policies = [None]  

    # run the games in parallel
    run_games_in_parallel(policies, shared_vars)

def test():
    # snake parameters
    box_size = 30
    snake_speed = 10

    # game parameters
    periodic = True
    action_mode = 3
    rand_init_body_length = True
    rand_init_direction = False

    # state mode
    state_mode = 'simple'
    # state_mode = 'proximity'

    # visual and sound effects
    show_compass = True
    sound_effects = False
    show_state_info = False

    # put all shared variables into a list for convenience
    shared_vars = [box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info]

    # load different policies (pi1, pi2, pi3...)
    n_episodes = int(1e7)
    pi1 = load_policy(periodic, box_size, action_mode, state_mode, n_episodes)

    # folder, filename = 'user_policies', 'test'
    # pi2 = load_user_policy(filename, folder)

    policies = [None]  
    # policies = [None, pi1]  
    # policies = [None, pi1, pi1]  
    # policies = [pi1, pi1, pi1, pi1]
    # policies = [pi1, pi1, pi1, pi1, pi1]
    # policies = [pi1, pi1, pi1, pi1, pi1, pi1]  

    # run the games in parallel
    run_games_in_parallel(policies, shared_vars)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Please specify one game mode!')
    else:
        game_mode = sys.argv[1]

        if game_mode == 'demo':
            demo_1player_nocompass()
        else:
            print('Game mode not recognized!')



