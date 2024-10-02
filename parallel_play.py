from tools import *
from snake import *
import multiprocessing

# in case we need to reload the library
from importlib import reload
reload(sys.modules['snake'])
from snake import *

# TODO add a countdown in snake!

# function to set global variables
def set_global_variables():
    global box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info

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

# function to run each snake game in a separate process
def run_snake_game(policy, game_id, window_position):
    # seed to initialize the RNG
    seed = 666
    seed_rng(seed, verbose=False)

    # create snake game object
    snake = Snake(action_mode, state_mode, cell_size, box_size, snake_speed, periodic, 
            rand_init_body_length, rand_init_direction, show_compass, sound_effects, 
            show_state_info, window_position, 'test team', verbose=False)

    # Play the game with the provided policy
    snake.play(policy)

# function to launch multiple games in parallel
def run_games_in_parallel(policies):
    # count policies to get number of teams
    n_teams = len(policies)

    if n_teams > 6: raise Exception('The maximum number of supported policies is 6')

    # get screen resolution
    pygame.display.init()
    display_sizes = pygame.display.get_desktop_sizes()
    pygame.display.quit()
    if len(display_sizes)>1:
        resolution = display_sizes[1]
        print(f'Secondary screen detected with resolution {resolution}')
    else:
        resolution = display_sizes[0]

    margin = 0

    global cell_size

    # window parameters
    if n_teams == 6:
        cell_size = (resolution[0]//3)//box_size
        window_width = cell_size*box_size
        window_positions = []
        for l in range(2):
            for c in range(3):
                shift_x = (window_width + margin)*c
                # eventual fine tuning of position
                # shift_x += (window_width + margin)//3
                window_positions.append((shift_x, window_width*l))

    # create a new process for each game
    processes = []
    for i, policy in enumerate(policies):
        p = multiprocessing.Process(target=run_snake_game, args=(policy, i+1, window_positions[i]))
        processes.append(p)
        p.start()

    # wait for all processes to finish
    for p in processes:
        p.join()

if __name__ == "__main__":
    set_global_variables()

    # load different policies (pi1, pi2, pi3...)
    n_episodes = int(1e7)
    pi1 = load_policy(periodic, box_size, action_mode, state_mode, n_episodes)

    # folder, filename = 'user_policies', 'test'
    # pi2 = load_user_policy(filename, folder)

    policies = [pi1, pi1, pi1, pi1, pi1, pi1]  

    # run the games in parallel
    run_games_in_parallel(policies)
