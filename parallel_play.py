from tools import *
from snake import *
import multiprocessing

# in case we need to reload the library
from importlib import reload
reload(sys.modules['snake'])
from snake import *

# TODO add a countdown in snake!

# function to run each snake game in a separate process
def run_snake_game(policy, game_id, window_position, cell_size, shared_vars):
    # unpack shared variables
    box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info = shared_vars 

    # seed to initialize the RNG
    seed = 666
    seed_rng(seed, verbose=False)

    # create snake game object
    snake = Snake(action_mode, state_mode, cell_size, box_size, snake_speed, periodic, 
            rand_init_body_length, rand_init_direction, show_compass, sound_effects, 
            show_state_info, window_position, 'test team', verbose=False)

    # Play the game with the provided policy
    snake.play(policy)

def calculate_size_and_positions(n_teams, box_size):
    # get screen resolution
    pygame.display.init()
    display_sizes = pygame.display.get_desktop_sizes()
    pygame.display.quit()
    if len(display_sizes)==1:
        resolution = display_sizes[0]
        print(f'Primary screen detected with resolution {resolution}')
    else:
        resolution = display_sizes[1]
        print(f'Secondary screen detected with resolution {resolution}')
    screen_width, screen_heigth = resolution[0], resolution[1]

    # window parameters
    if n_teams == 1: raise Exception('Please provide at least 2 teams!')

    elif n_teams == 2:
        cell_size = (screen_heigth//2)//box_size
        window_width = cell_size*box_size - 2
        window_positions = []
        rigid_shift_x = (screen_width-window_width*2)//2
        rigid_shift_y = (screen_heigth-window_width)//2
        for c in range(2):
            shift_x = window_width*c + rigid_shift_x
            shift_y = rigid_shift_y
            window_positions.append((shift_x, shift_y))

    elif n_teams == 6:
        cell_size = min( (screen_width//3)//box_size, (screen_heigth//2)//box_size )
        window_width = cell_size*box_size - 2
        window_positions = []
        rigid_shift_x = (screen_width-window_width*3)//2
        for l in range(2):
            for c in range(3):
                shift_x = window_width*c + rigid_shift_x
                shift_y = window_width*l
                window_positions.append((shift_x, shift_y))

    elif n_teams > 6: raise Exception('The maximum number of teams is 6!')

    return cell_size, window_positions


# function to launch multiple games in parallel
def run_games_in_parallel(policies, shared_vars):
    # unpack shared variables
    box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info = shared_vars 

    # count policies to get number of teams
    n_teams = len(policies)

    cell_size, window_positions = calculate_size_and_positions(n_teams, box_size)

    # create a new process for each game
    processes = []
    for i, policy in enumerate(policies):
        p = multiprocessing.Process(target=run_snake_game, args=(policy, i+1,
            window_positions[i], cell_size, shared_vars))
        processes.append(p)
        p.start()

    # wait for all processes to finish
    for p in processes:
        p.join()

if __name__ == "__main__":
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

    policies = [pi1, pi1]  
    # policies = [pi1, pi1, pi1, pi1, pi1, pi1]  

    # run the games in parallel
    run_games_in_parallel(policies, shared_vars)
