from tools import *
from snake import *
import multiprocessing

color_schemes = ['green', 'blue', 'red', 'orange', 'purple', 'pink', 'grey', 'brown']
color_schemes_rgb = [green, blue, red, orange, purple, pink, grey, brown]

# test a single policy (to be used in multiprocessing loop)
def test_policy_multiprocess(policy, team_name, shared_vars, scores_dict=None, seeds_dict=None, n_games=1000):
    # unpack shared variables
    box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, \
        show_state_info, countdown_seconds = shared_vars 

    # this doesn't really matter because we are not rendering the game window
    cell_size = 10

    # little hack: make sure that the action mode is set to 3 when testing policies
    action_mode = 3

    # create snake game object
    snake = Snake(action_mode, state_mode, cell_size, box_size, snake_speed, periodic, 
            rand_init_body_length, rand_init_direction, show_compass, sound_effects, 
            show_state_info, team_name, window_position=None, verbose=False)

    scores, seeds = [], []
    for n in range(n_games):
        seed = snake.seed_rng()
        score, truncated = snake.play(policy, render=False)
        scores.append(score)
        seeds.append(seed)

    # calculte mean score
    mean_score = np.mean(scores)

    # get seed that gave best score
    best_seed = seeds[np.argmax(scores)]

    print(f'{team_name}    {np.max(scores)}')

    # append mean score to the shared scores list
    if scores_dict is not None:
        scores_dict[team_name] = mean_score

    # append best seed to the shared seeds list
    if seeds_dict is not None:
        seeds_dict[team_name] = best_seed

# test multiple policies in parallel
def test_policies_in_parallel(policies, team_names, shared_vars, n_games):
    # unpack shared variables
    box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, \
        show_state_info, countdown_seconds = shared_vars 

    # count policies to get number of teams
    n_teams = len(policies)

    # create a multiprocessing manager to store scoreseedsnd seeds
    manager = multiprocessing.Manager()
    scores_dict = manager.dict()
    seeds_dict = manager.dict()

    print(f'Team\tPunteggio max')

    # create a new process for each game
    processes = []
    for i in range(n_teams):
        policy, team_name, = policies[i], team_names[i],
        p = multiprocessing.Process(target=test_policy_multiprocess, args=(policy, team_name, 
            shared_vars, scores_dict, seeds_dict, n_games))
        processes.append(p)
        p.start()

    # wait for all processes to finish
    for p in processes:
        p.join()

    return dict(scores_dict), dict(seeds_dict)


def run_one_game(policy, team_name, shared_vars, seeds=None):
    # unpack shared variables
    box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, \
        show_state_info, countdown_seconds = shared_vars 

    # count policies to get number of teams
    n_teams = 1

    # get window size and positions
    cell_size, window_positions = calculate_size_and_positions(n_teams, box_size)

    # shut up
    verbose = False

    # create a new process for each game
    color_scheme = 'green'
    window_position = window_positions[0]

    # if a seeds list was passed, read the corresponding seed
    if seeds is not None: 
        seed = seeds[i]
    else:
        seed = None

    p = multiprocessing.Process(target=run_snake_game, args=(
        policy, team_name, window_position, cell_size, shared_vars, color_scheme, 
        verbose, seed))
    p.start()

    # wait for all processes to finish
    p.join()

# run a single snake game (simple non-multiprocessing version)
def run_snake_game(policy, team_name, window_position, cell_size, shared_vars, color_scheme,
        verbose=False, seed=None):
    # unpack shared variables
    box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, \
        show_state_info, countdown_seconds = shared_vars 

    # create snake game object
    snake = Snake(action_mode, state_mode, cell_size, box_size, snake_speed, periodic, 
            rand_init_body_length, rand_init_direction, show_compass, sound_effects, 
            show_state_info, team_name, window_position, verbose, countdown_seconds,
            color_scheme, seed)

    # play the game with the provided policy
    snake.play(policy)

# run a single snake game (with multiprocessing barrier to wait for the other games to end)
def run_snake_game_with_barrier(policy, team_name, window_position, cell_size, shared_vars,
        color_scheme, verbose, seed, scores_dict, game_over_barrier, winner_display_event):
    # unpack shared variables
    box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, \
        show_state_info, countdown_seconds = shared_vars 

    # create snake game object
    snake = Snake(action_mode, state_mode, cell_size, box_size, snake_speed, periodic, 
            rand_init_body_length, rand_init_direction, show_compass, sound_effects, 
            show_state_info, team_name, window_position, verbose, countdown_seconds,
            color_scheme, seed)

    # play until game over
    snake.init_render()
    if snake.countdown_seconds > 0: snake.countdown()
    state = snake.reset()

    # game loop
    escape_pressed = False
    while not escape_pressed:
        if policy is None:
            # check if an action key has been pressed
            action, escape_pressed = read_keys()
        else:
            # check if ESC has been pressed
            escape_pressed = read_esc()
            action = policy[state]
        next_state, reward, terminated, truncated = snake.step(action)
        if terminated or truncated:
            # go in game_over state but without waiting for the user to press ESC
            # (the games will be all simultaneously closed by the main thread)
            snake.game_over(wait_for_user=False)
            break
        snake.render_frame()
        state = next_state

    # append the score to the shared scores list
    if scores_dict is not None:
        scores_dict[team_name] = snake.score

    # wait for all games to finish before proceeding
    if game_over_barrier is not None:
        game_over_barrier.wait()

    # keep the game window open until the winner is displayed
    if winner_display_event is not None:
        while not winner_display_event.is_set():
            # prevent window from freezing
            pygame.event.pump()  

# function to launch multiple games in parallel
def run_games_in_parallel(policies, team_names, shared_vars, seeds=None):
    # unpack shared variables
    box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, \
        show_state_info, countdown_seconds = shared_vars 

    # if no seeds are passed, generate a random seed for all the games
    if seeds is None: seed = None

    # count policies to get number of teams
    n_teams = len(policies)

    # get window size and positions
    cell_size, window_positions = calculate_size_and_positions(n_teams, box_size)

    # shut up
    verbose = False

    # create a multiprocessing manager to store scores
    manager = multiprocessing.Manager()
    scores_dict = manager.dict()

    # create a barrier for all games to reach game_over (+1 is to include the main process as well)
    game_over_barrier = multiprocessing.Barrier(n_teams+1)

    # create an event to signal the end of the winner display
    winner_display_event = multiprocessing.Event()

    # create a new process for each game
    processes = []
    for i in range(n_teams):
        color_scheme = color_schemes[i]
        policy, team_name, window_position = policies[i], team_names[i], window_positions[i]
        # if a seeds list was passed, read the corresponding seed
        if seeds is not None:
            seed = seeds[i]
        # little hack: whenever we are using an actual policy (and not human input),
        # make sure that the action mode is set to 3!
        if policy != None:
            shared_vars_copy = shared_vars.copy()
            shared_vars_copy[3] = 3
            p = multiprocessing.Process(target=run_snake_game_with_barrier, args=(
                policy, team_name, window_position, cell_size, shared_vars_copy, color_scheme, 
                verbose, seed, scores_dict, game_over_barrier, winner_display_event))
        else:
            p = multiprocessing.Process(target=run_snake_game_with_barrier, args=(
                policy, team_name, window_position, cell_size, shared_vars, color_scheme, 
                verbose, seed, scores_dict, game_over_barrier, winner_display_event))
        processes.append(p)
        p.start()

    # wait for all games to reach the game_over state (main process waits here too)
    game_over_barrier.wait()

    # once all the games has reached the game_over state, calculte team ranking
    scores_dict = dict(scores_dict)
    ranking = sorted(zip(scores_dict.values(), scores_dict.keys()), reverse=True)
    winner_score, winner_name = ranking[0][0], ranking[0][1]

    # display winner on a new sindow
    display_winner(winner_score, winner_name)

    # signal all games to close
    winner_display_event.set()

    # wait for all processes to finish
    for p in processes:
        p.join()

    return scores_dict

# function to challenge ai and a human policy
def human_policy_vs_ai(policies, team_names, shared_vars, seed=None, color_scheme='green'):
    # unpack shared variables
    box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, \
        show_state_info, countdown_seconds = shared_vars 

    # count policies to get number of teams
    n_teams = 2

    # get window size and positions
    cell_size, window_positions = calculate_size_and_positions(n_teams, box_size)

    # shut up
    verbose = False

    # create a multiprocessing manager to store scores
    manager = multiprocessing.Manager()
    scores_dict = manager.dict()

    # create a barrier for all games to reach game_over 
    # (+1 is to include the main process as well)
    game_over_barrier = multiprocessing.Barrier(n_teams+1)

    # create an event to signal the end of the winner display
    winner_display_event = multiprocessing.Event()

    # create a new process for each game
    processes = []
    for i in range(n_teams):
        policy, team_name, window_position = policies[i], team_names[i], window_positions[i]
        # the first istance is the human policy, which needs state_mode = 'simple' to work
        if i == 0:
            shared_vars_copy = shared_vars.copy()
            shared_vars_copy[6] = 'simple'
            p = multiprocessing.Process(target=run_snake_game_with_barrier, args=(
                policy, team_name, window_position, cell_size, shared_vars_copy,
                color_scheme, verbose, seed, scores_dict, game_over_barrier, 
                winner_display_event))
        # the second istance is the RL policy, and we use the best seed to show it
        else:
            if state_mode == 'simple': 
                color_scheme = 'grey'
                # TODO put here seed of AI or use the same seed of human policy
            elif state_mode == 'proximity': 
                color_scheme = 'brown'
            p = multiprocessing.Process(target=run_snake_game_with_barrier, args=(
                policy, team_name, window_position, cell_size, shared_vars, 
                color_scheme, verbose, seed, scores_dict, game_over_barrier, 
                winner_display_event))
        processes.append(p)
        p.start()

    # wait for all games to reach the game_over state (main process waits here too)
    game_over_barrier.wait()

    # once all the games has reached the game_over state, calculte team ranking
    scores_dict = dict(scores_dict)
    ranking = sorted(zip(scores_dict.values(), scores_dict.keys()), reverse=True)
    winner_score, winner_name = ranking[0][0], ranking[0][1]

    # display winner on a new sindow
    display_winner(winner_score, winner_name)

    # Signal all games to close
    winner_display_event.set()

    # wait for all processes to finish
    for p in processes:
        p.join()

    return scores_dict

# function to get screen resolution
def get_screen_resolution(verbose=False):
    pygame.display.init()
    # get the number of displays and their sizes
    display_count = pygame.display.get_num_displays()
    display_sizes = pygame.display.get_desktop_sizes()
    pygame.display.quit()

    # # this approach has problems on mac
    # if display_count==1:
    #     resolution = display_sizes[0]
    #     if verbose: print(f'Primary screen detected with resolution {resolution}')
    # else:
    #     resolution = display_sizes[1]
    #     if verbose: print(f'Secondary screen detected with resolution {resolution}')

    # we just always use the primary display and set it as the main display from the os
    resolution = display_sizes[0]

    screen_width, screen_heigth = resolution[0], resolution[1]

    return screen_width, screen_heigth

def calculate_size_and_positions(n_teams, box_size):
    # get screen resolution
    screen_width, screen_heigth = get_screen_resolution()

    # calculate window size and positions depending on number of teams
    if n_teams == 1:
        cell_size = int(screen_heigth//1.25)//box_size
        window_width = cell_size*box_size - 2
        window_positions = []
        rigid_shift_x = (screen_width-window_width)//2
        rigid_shift_y = (screen_heigth-window_width)//2
        shift_x = rigid_shift_x
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

def display_winner(score, team_name):
    # Initialize pygame display and font modules
    pygame.display.init()
    pygame.font.init()

    # Calculate desired window size
    screen_width, screen_height = get_screen_resolution()
    window_size = (screen_width // 3, screen_height // 3)

    # Create a window without frame
    screen = pygame.display.set_mode(window_size, pygame.NOFRAME)

    # Set retro style font, colors, and background
    font = pygame.font.Font(FONT_PATH, window_size[1]//5)
    text_color = yellow
    bg_color = black
    border_color = yellow

    # Create the winner and score text
    winner_text = f"{team_name}"
    if score == 1: score_text = f"{score} PUNTO" 
    else: score_text = f"{score} PUNTI"
    winner_surface = font.render(winner_text, True, text_color)
    score_surface = font.render(score_text, True, text_color)

    # Load and display the image at the top of the screen
    image = pygame.image.load('img/crown.png')

    # Get the original image size
    image_rect = image.get_rect()
    image_width, image_height = image_rect.size

    # Calculate the scale factor to fit the image while preserving aspect ratio
    max_width = window_size[0] // 2
    max_height = window_size[1] // 3
    scale_factor = min(max_width / image_width, max_height / image_height)

    # Scale the image while maintaining aspect ratio
    new_width = int(image_width * scale_factor)
    new_height = int(image_height * scale_factor)
    image = pygame.transform.scale(image, (new_width, new_height))

    # Get the size of the text and screen
    winner_rect = winner_surface.get_rect(center=(window_size[0] // 2, window_size[1] // 2 - 40))
    score_rect = score_surface.get_rect(center=(window_size[0] // 2, window_size[1] // 2 + 40))

    # Calculate total content height (image + winner text + score text)
    total_height = new_height + winner_rect.height + score_rect.height + 40  # Add spacing between elements

    # Calculate the top offset to center the content vertically
    top_offset = (window_size[1] - total_height) // 2

    # Position elements relative to the top_offset
    image_rect = image.get_rect(center=(window_size[0] // 2, top_offset + new_height // 2))
    winner_rect = winner_surface.get_rect(center=(window_size[0] // 2, image_rect.bottom + winner_rect.height // 2 + 20))
    score_rect = score_surface.get_rect(center=(window_size[0] // 2, winner_rect.bottom + score_rect.height // 2 + 20))

    # Fill background
    screen.fill(bg_color)

    # Blit the image and text onto the screen
    screen.blit(image, image_rect)
    screen.blit(winner_surface, winner_rect)
    screen.blit(score_surface, score_rect)

    # Draw the border (blink effect)
    pygame.draw.rect(screen, border_color, screen.get_rect(), 1)

    # Update the display
    pygame.display.flip()

    # Retro blinking effect
    blink = True
    last_time = time.time()

    # Blinking effect
    while True:
        if time.time() - last_time > 0.25:
            last_time = time.time()
            blink = not blink

        if blink:
            # screen.blit(image, image_rect)
            screen.blit(winner_surface, winner_rect)
            screen.blit(score_surface, score_rect)
        else:
            # screen.fill(bg_color, image_rect)
            screen.fill(bg_color, winner_rect)
            screen.fill(bg_color, score_rect)

        pygame.display.flip()

        # Wait for exit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.display.quit()
                return

def load_policies_from_folder(policies_folder):
    policies, team_names = [], []
    files_list = sorted(os.listdir(policies_folder))
    for filename in files_list:
        policies.append(load_user_policy(filename, policies_folder))
        team_names.append(filename.replace('.txt',''))
    return policies, team_names

def load_ranking(turn_folder):
    ranking_file = turn_folder + '/ranking.txt'
    scores, seeds = {}, {}
    try: lines = np.loadtxt(ranking_file, delimiter='\t', dtype=str, ndmin=2)
    except: raise Warning('Ranking file not found! Did you run the statistical challenge?')
    for line in lines:
        team_name = line[1]
        scores[team_name] = float(line[0])
        seeds[team_name] = int(line[2])
    return scores, seeds
