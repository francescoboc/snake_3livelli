from snake import *

# in case we need to reload the library
from importlib import reload
reload(sys.modules['snake'])
from snake import *

# snake parameters
cell_size = 30
box_size = 30
snake_speed = 15
periodic = True

action_mode = 3

# state_mode = 'simple'
# state_mode = 'body_length'
# state_mode = 'tail_compass'
# state_mode = 'com_compass'
state_mode = 'proximity'
# state_mode = 'spirality'

rand_init_body_length = False
rand_init_direction = False

snake = Snake(action_mode, state_mode, cell_size, box_size, snake_speed, periodic, rand_init_body_length, rand_init_direction, verbose=False)

# load a saved policy
n_episodes = int(1e7)
pi_star = load_policy(periodic, box_size, action_mode, state_mode, n_episodes)

# custom_label = 'francesco'
# if periodic: policy_folder = f'policies/periodic'
# else: policy_folder = f'policies/non_periodic'
# policy_name = f'pi_{box_size}_{action_mode}_{state_mode}_{custom_label}'
# pi_star = np.load(f'{policy_folder}/{policy_name}.npy', allow_pickle=True).item()
# print(f'Policy {policy_name} loaded!')

n_games = 1000

seeds, scores = [], []
truncated_count = 0
for n in tqdm(range(n_games), ascii=' █') :
    seed = seed_rng(verbose=False)
    score, truncated = snake.play(pi_star, render=False)
    if not truncated:
        seeds.append(seed)
        scores.append(score)
    else:
        truncated_count += 1

print(f'Mean score: {np.mean(scores):.3f}, Truncated episodes ratio: {(truncated_count/n_games):.2f}')
print(f'Best score: {np.max(scores)}, Seed: {seeds[np.argmax(scores)]}')
