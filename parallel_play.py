from tools import *
from snake import *

# in case we need to reload the library
from importlib import reload
reload(sys.modules['snake'])
from snake import *

import multiprocessing

# Function to run each snake game in a separate process
def run_snake_game(policy, game_id):
    # seed to initialize the RNG
    seed = 666
    seed_rng(seed, verbose=False)

    shift_x = (window_width + margin)*(game_id-1)
    window_position = (shift_x, 0)

    # create snake game object
    snake = Snake(action_mode, state_mode, cell_size, box_size, snake_speed, periodic, 
            rand_init_body_length, rand_init_direction, show_compass, sound_effects, 
            show_state_info, window_position, 'test team', verbose=False)

    # # Set a unique window title (to differentiate windows)
    # pygame.display.set_caption(f"Snake Game {game_id}")
    
    # Play the game with the provided policy
    snake.play(policy)


# Function to launch multiple games in parallel
def run_games_in_parallel(*policies):
    processes = []
    for i, policy in enumerate(policies):
        # create a new process for each game with a unique policy
        p = multiprocessing.Process(target=run_snake_game, args=(policy, i+1))
        processes.append(p)
        p.start()

    # wait for all processes to finish
    for p in processes:
        p.join()

if __name__ == "__main__":
    # snake parameters
    cell_size = 10
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

    # window parameters
    window_width = cell_size*box_size
    margin = 0
    # TODO add a countdown in snake!

    # Define different policies (pi1, pi2, pi3...)
    n_episodes = int(1e7)
    pi1 = load_policy(periodic, box_size, action_mode, state_mode, n_episodes)

    folder, filename = 'user_policies', 'test'
    pi2 = load_user_policy(filename, folder)

    # Run the games in parallel
    run_games_in_parallel(pi1, pi2, pi1, pi2)
    # run_games_in_parallel(pi1, pi2)
