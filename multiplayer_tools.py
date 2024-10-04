from tools import *
from snake import *
import multiprocessing

# function to run each snake game in a separate process
def run_snake_game(policy, team_name, game_id, window_position, cell_size, shared_vars, seed=None, scores_dict=None):
    # unpack shared variables
    box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info = shared_vars 

    seed_rng(seed, verbose=False)

    # create snake game object
    snake = Snake(action_mode, state_mode, cell_size, box_size, snake_speed, periodic, 
            rand_init_body_length, rand_init_direction, show_compass, sound_effects, 
            show_state_info, window_position, team_name, verbose=False)

    # Play the game with the provided policy
    score, truncated = snake.play(policy)

    # append the score to the shared scores list
    if scores_dict is not None:
        scores_dict[team_name] = score

# function to launch multiple games in parallel
def run_games_in_parallel(policies, team_names, shared_vars):
    # unpack shared variables
    box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info = shared_vars 

    # count policies to get number of teams
    n_teams = len(policies)

    # get window size and positions
    cell_size, window_positions = calculate_size_and_positions(n_teams, box_size)

    # seed to initialize the RNG
    seed = 666
    # seed = None

    # create a multiprocessing manager to store scores
    manager = multiprocessing.Manager()
    scores_dict = manager.dict()

    # create a new process for each game
    processes = []
    for i in range(n_teams):
        policy, team_name, window_position = policies[i], team_names[i], window_positions[i]
        game_id = i+1
        p = multiprocessing.Process(target=run_snake_game, args=(policy, team_name, 
            i+1, window_position, cell_size, shared_vars, seed, scores_dict))
        processes.append(p)
        p.start()

    # wait for all processes to finish
    for p in processes:
        p.join()

    return dict(scores_dict)

def calculate_size_and_positions(n_teams, box_size, verbose=False):
    # get screen resolution
    pygame.display.init()
    display_sizes = pygame.display.get_desktop_sizes()
    pygame.display.quit()
    if len(display_sizes)==1:
        resolution = display_sizes[0]
        if verbose: print(f'Primary screen detected with resolution {resolution}')
    else:
        resolution = display_sizes[1]
        if verbose: print(f'Secondary screen detected with resolution {resolution}')
    screen_width, screen_heigth = resolution[0], resolution[1]

    # calculate window size and positions depending on number of teams
    if n_teams == 1:
        cell_size = int(screen_heigth//1.25)//box_size
        window_width = cell_size*box_size - 2
        window_positions = []
        rigid_shift_x = (screen_width-window_width)//2
        rigid_shift_y = (screen_heigth-window_width)//2
        for c in range(2):
            shift_x = window_width*c + rigid_shift_x
            shift_y = rigid_shift_y
            window_positions.append((shift_x, shift_y))

    elif n_teams == 2:
        cell_size = int(screen_heigth//1.5)//box_size
        window_width = cell_size*box_size - 2
        window_positions = []
        rigid_shift_x = (screen_width-window_width*2)//2
        rigid_shift_y = (screen_heigth-window_width)//2
        for c in range(2):
            shift_x = window_width*c + rigid_shift_x
            shift_y = rigid_shift_y
            window_positions.append((shift_x, shift_y))

    elif n_teams == 3:
        cell_size = int(screen_heigth//2)//box_size
        window_width = cell_size*box_size - 2
        window_positions = []
        rigid_shift_x = (screen_width-window_width*3)//2
        rigid_shift_y = (screen_heigth-window_width)//2
        for c in range(3):
            shift_x = window_width*c + rigid_shift_x
            shift_y = rigid_shift_y
            window_positions.append((shift_x, shift_y))

    elif n_teams == 4:
        cell_size = min( (screen_width//2)//box_size, (screen_heigth//2)//box_size )
        window_width = cell_size*box_size - 2
        window_positions = []
        rigid_shift_x = (screen_width-window_width*2)//2
        for l in range(2):
            for c in range(2):
                shift_x = window_width*c + rigid_shift_x
                shift_y = window_width*l
                window_positions.append((shift_x, shift_y))

    elif n_teams == 5 or n_teams == 6:
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

def display_winner(team_name, score):
        # initialise pygame  display module
        pygame.display.init()

        # initialise game window (add height of info bar)
        self.game_window = pygame.display.set_mode((self.box_length, self.box_height), pygame.NOFRAME)
        
        # create main font object 
        self.main_font = pygame.font.SysFont('arial', 22)

        # wait for user input to exit
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN 
                        and event.key == pygame.K_ESCAPE):
                    pygame.display.quit()
                    return
            

