import random, sys, signal, os, time
from tqdm import tqdm
import numpy as np

# hide pygame welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame

# load retro font 
FONT_PATH = 'fonts/pixel_emulator.otf'  

# hack to prevent raising KeyboardInterrupt when stopping the script with ctrl-c
# https://stackoverflow.com/questions/7073268/remove-traceback-in-python-on-ctrl-c
signal.signal(signal.SIGINT, lambda x, y: sys.exit())

# create the random number generator object
rng = random.Random()

# colors
green = pygame.Color(6, 128, 81)
lightGreen = pygame.Color(148, 191, 48)

blue = pygame.Color(28, 117, 189)
lightBlue = pygame.Color(73, 194, 242)

red = pygame.Color(245, 49, 65)
lightRed = pygame.Color(255, 112, 112)

orange = pygame.Color(242, 98, 31)
lightOrange = pygame.Color(250, 217, 55)

purple = pygame.Color(119, 59, 191)
lightPurple = pygame.Color(226, 155, 250)

pink = pygame.Color(217, 76, 142)
lightPink = pygame.Color(250, 187, 175)

grey = pygame.Color(105, 101, 112)
lightGrey = pygame.Color(166, 154, 156)

brown = pygame.Color(110, 66, 80)
lightBrown = pygame.Color(181, 140, 127)

brightRed = pygame.Color(245, 61, 5)
yellow = pygame.Color(252, 252, 25)
white = pygame.Color(253, 250, 230)
black = pygame.Color(20, 20, 20)

# head directions
head_dirs = ['UP', 'RIGHT', 'DOWN', 'LEFT']

# compass directions
compass_dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']

# proximity values
prox_values = ['', 'f', 'l', 'r', 'fl', 'fr', 'lr', 'flr']

# initial direction and size of the snake
init_direction = 'RIGHT' 
init_size = 4

# read keys pressed by the user
def read_keys():
    escape_pressed = False
    action = 'NO_TURN'
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                action = 'UP'
            if event.key == pygame.K_DOWN:
                action = 'DOWN'
            if event.key == pygame.K_LEFT:
                action = 'LEFT'
            if event.key == pygame.K_RIGHT:
                action = 'RIGHT'
            if  event.key == pygame.K_ESCAPE:
                escape_pressed = True
    return action, escape_pressed

# simpler version that only checks for escape keypress
def read_esc():
    escape_pressed = False
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if  event.key == pygame.K_ESCAPE:
                escape_pressed = True
    return escape_pressed

# initialise the RNG with a given seed or a random one
def seed_rng(seed=None, verbose=True):
    if seed is None:
        seed = random.randrange(sys.maxsize)
    rng.seed(seed)
    if verbose:
        print(f'RNG seed = {seed}')
    return seed

# load a saved policy
def load_policy(periodic, action_mode, state_mode, n_episodes, verbose=True):
    if periodic: policy_folder = f'policies/periodic'
    else: policy_folder = f'policies/non_periodic'
    policy_name = f'pi_{action_mode}_{state_mode}_{n_episodes:.0e}'
    try: 
        policy = np.load(f'{policy_folder}/{policy_name}.npy', allow_pickle=True).item()
        if verbose:
            print(f'Policy {policy_name} loaded!')
    except:
        raise Exception(f'Policy {policy_name} not found!')
    return policy

# save a policy
def save_policy(policy, periodic, action_mode, state_mode, n_episodes):
    if periodic: policy_folder = f'policies/periodic'
    else: policy_folder = f'policies/non_periodic'
    policy_name = f'pi_{action_mode}_{state_mode}_{n_episodes:.0e}'
    np.save(f'{policy_folder}/{policy_name}.npy', policy)
    print(f'Policy {policy_name} saved!')

# load and convert a text policy to a dictionary
def load_user_policy(filename, folder, verbose=False):
    path = f'{folder}/{filename}'
    text_array = np.loadtxt(path, dtype='str')
    policy_dict = {}
    for row in text_array:
        state, action = row
        # split the state into two parts
        state_parts = state.split('_')  
        if len(state_parts) == 2:
            key = (state_parts[0], state_parts[1])  
            policy_dict[key] = action
        else:
            raise Exception(f'State {state} not recognized!')
    if verbose:
        print(f'Policy {path} loaded!')
    # add terminal state
    policy_dict['Term'] = None
    return policy_dict

# change position of window
def set_window_position(x, y):
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"

# test a single policy
def test_policy(action_mode, state_mode, box_size, periodic, rand_init_body_length, rand_init_direction, n_games, policy, verbose=True, use_tqdm=True):
    from snake import Snake
    # these are not important because we are not rendering the game window
    cell_size = 30
    snake_speed = 100

    # create snake game object
    snake = Snake(action_mode, state_mode, cell_size, box_size, snake_speed, periodic, rand_init_body_length, rand_init_direction, verbose=False)

    seeds, scores = [], []
    truncated_count = 0
    if use_tqdm: iterator = tqdm(range(n_games), ascii=' █')
    else: iterator = range(n_games)
    for n in iterator:
        seed = seed_rng(verbose=False)
        score, truncated = snake.play(policy, render=False)
        seeds.append(seed)
        scores.append(score)
        if truncated:
            truncated_count += 1

    mean_score = np.mean(scores)
    trun_ratio = truncated_count/n_games
    best_score = np.max(scores)
    best_seed = seeds[np.argmax(scores)]

    if verbose:
        print(f'Mean score: {mean_score:.3f}, Truncated episodes ratio: {trun_ratio:.2f}')
        print(f'Best score: {best_score}, Seed: {best_seed}')

    return mean_score, trun_ratio
