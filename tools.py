import sys, signal, os, time, csv
from tqdm import tqdm
import numpy as np
from collections import deque

# hide OpenGL warning message
sys.stderr.flush()
devnull_fd = os.open(os.devnull, os.O_WRONLY)
os.dup2(devnull_fd, 2)
os.close(devnull_fd)

# hide pygame welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame

# load retro font 
FONT_PATH = 'fonts/pixel_emulator.otf'  

# hack to prevent raising KeyboardInterrupt when stopping the script with ctrl-c
# https://stackoverflow.com/questions/7073268/remove-traceback-in-python-on-ctrl-c
signal.signal(signal.SIGINT, lambda x, y: sys.exit())

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
init_size = 6

# initialize a global deque to store key presses
key_queue = deque(maxlen=3)

# joystick button and axis ids
button_id = 0
axh_id = 0
axv_id = 1

# check for joystick events
def read_joystick(joystick, direction=None):
    pygame.event.pump()

    button_value = joystick.get_button(button_id)

    if button_value == 1: button_pressed = True
    else: button_pressed = False

    axh_value = joystick.get_axis(axh_id)
    axv_value = joystick.get_axis(axv_id)

    action = 'NO_TURN'
    right, left, down, up = False, False, False, False

    if axh_value < -0.5:
        action = 'RIGHT'
        right = True
    elif axh_value > 0.5:
        action = 'LEFT'
        left = True

    if axv_value < -0.5:
        action = 'DOWN'
        down = True
    elif axv_value > 0.5:
        action = 'UP'
        up = True

    # handle diagonal movements
    if right and down:
        if direction=='RIGHT': action = 'DOWN'
        elif direction=='DOWN': action = 'RIGHT'

    if right and up:
        if direction=='RIGHT': action = 'UP'
        elif direction=='UP': action = 'RIGHT'

    if left and down:
        if direction=='LEFT': action = 'DOWN'
        elif direction=='DOWN': action = 'LEFT'

    if left and up:
        if direction=='LEFT': action = 'UP'
        elif direction=='UP': action = 'LEFT'

    return action, button_pressed

# check for user keypresses and get the next action from to the queue
def read_keys():
    escape_pressed = False

    # process events and queue key presses
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                key_queue.append('UP')
            elif event.key == pygame.K_DOWN:
                key_queue.append('DOWN')
            elif event.key == pygame.K_LEFT:
                key_queue.append('LEFT')
            elif event.key == pygame.K_RIGHT:
                key_queue.append('RIGHT')
            elif event.key == pygame.K_ESCAPE:
                escape_pressed = True

    # get the next action from the queue, or return 'NO_TURN' if empty
    if key_queue: action = key_queue.popleft()
    else: action = 'NO_TURN'

    return action, escape_pressed

# simpler version that only checks for escape keypress
def read_esc():
    escape_pressed = False

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if  event.key == pygame.K_ESCAPE:
                escape_pressed = True

    return escape_pressed

# load a saved policy
def load_policy(periodic, action_mode, state_mode, n_episodes, verbose=True, label=None):
    if periodic: policy_folder = f'policies/periodic'
    else: policy_folder = f'policies/non_periodic'

    # add a label if provided
    if label is not None:
        policy_name = f'pi_{action_mode}_{state_mode}_{n_episodes:.0e}_{label}'
    else:
        policy_name = f'pi_{action_mode}_{state_mode}_{n_episodes:.0e}'

    try: 
        policy = np.load(f'{policy_folder}/{policy_name}.npy', allow_pickle=True).item()
        if verbose:
            print(f'Policy {policy_name} loaded!')
    except:
        raise Exception(f'Policy {policy_name} not found!')

    return policy

# save a policy
def save_policy(policy, periodic, action_mode, state_mode, n_episodes, label=None):
    if periodic: policy_folder = f'policies/periodic'
    else: policy_folder = f'policies/non_periodic'

    # add a label if provided
    if label is not None:
        policy_name = f'pi_{action_mode}_{state_mode}_{n_episodes:.0e}_{label}'
    else:
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
    snake_speed = 50

    # create snake game object
    snake = Snake(action_mode, state_mode, cell_size, box_size, snake_speed, periodic, rand_init_body_length, rand_init_direction, verbose=False)

    seeds, scores = [], []
    truncated_count = 0
    if use_tqdm: iterator = tqdm(range(n_games), ascii=' █')
    else: iterator = range(n_games)
    for n in iterator:
        seed = snake.seed_rng()
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

    # # render best game
    # snake.seed_rng(best_seed)
    # score, truncated = snake.play(policy, render=True)

    return mean_score, trun_ratio
