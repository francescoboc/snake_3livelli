from snake import *

# in case we need to reload the library
from importlib import reload
reload(sys.modules['snake'])
from snake import *

# snake parameters
cell_size = 30
box_size = 30
snake_speed = 150
periodic = True

action_mode = 4

# state_mode = 'simple'
# state_mode = 'body_length'
# state_mode = 'tail_compass'
# state_mode = 'com_compass'
state_mode = 'proximity'

rand_init_body_length = False
rand_init_direction = False

snake = Snake(action_mode, state_mode, cell_size, box_size, snake_speed, periodic, rand_init_body_length, rand_init_direction, verbose=False)

# load a saved policy
n_episodes = int(1e7)
pi_star = load_policy(periodic, box_size, action_mode, state_mode, n_episodes)

n_games = 1000

seeds, scores = [], []
success_counter = 0
for n in tqdm(range(n_games), ascii=' █') :
    seed = seed_rng(verbose=False)
    score, truncated = snake.play(pi_star, render=False)
    if not truncated:
        seeds.append(seed)
        scores.append(score)
        success_counter += 1

print(f'Mean score: {np.mean(scores)}, Success rate: {(success_counter/n_games):.2f}')
print(f'Best score: {np.max(scores)}, Seed: {seeds[np.argmax(scores)]}')
