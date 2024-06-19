from snake import *
from qlearning import *

# in case we need to reload the library
from importlib import reload
reload(sys.modules['snake'])
reload(sys.modules['qlearning'])
from snake import *
from qlearning import *

# seed to initialize the RNG
seed = None
seed_rng(seed)

# snake parameters
cell_size = 30
box_size = 30
snake_speed = 10
periodic = True

action_mode = 3
rand_init_body_length = True
rand_init_direction = True

# state_mode = 'simple'
# state_mode = 'body_length'
# state_mode = 'tail_compass'
state_mode = 'com_compass'

# rewards
food_rew = 1.0
lose_rew = -10.0
step_rew = -0.02

snake = Snake(action_mode, state_mode, cell_size, box_size, snake_speed, periodic, food_rew, lose_rew, step_rew, rand_init_body_length, rand_init_direction)

# ql agent parameters
n_episodes = int(1e3)
epsilon_i = 1.0
epsilon_f = 0.1
learning_rate = 0.05
discount_factor = 1.0

agent = QLearningAgent(snake, n_episodes, epsilon_i, epsilon_f, learning_rate, discount_factor)

q_star, pi_star = agent.train()

snake.play(pi_star)

# np.save(f'policies/pi_{box_size}_{action_mode}_{state_mode}_{n_episodes}.npy', pi_star)
