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
box_size = 20
snake_speed = 15
periodic = True

action_mode = 3
rand_init_body_length = True
rand_init_direction = True

state_mode = 'simple'
# state_mode = 'proximity'

# rewards
food_rew = 1.0
lose_rew = -10.0
step_rew = -0.01
trun_rew = -5

# create snake game object
snake = Snake(action_mode, state_mode, cell_size, box_size, snake_speed, periodic,
        rand_init_body_length, rand_init_direction, food_rew=food_rew, 
        lose_rew=lose_rew, step_rew=step_rew, trun_rew=trun_rew)

# ql agent parameters
# n_episodes = int(1e7)
n_episodes = int(1e5)
epsilon_i = 1.0
epsilon_f = 0.1
learning_rate = 0.05
discount_factor = 1.0

agent = QLearningAgent(snake, n_episodes, epsilon_i, epsilon_f, learning_rate, discount_factor)

q_star, pi_star = agent.train()

# snake.play(pi_star)

save_policy(pi_star, periodic, box_size, action_mode, state_mode, n_episodes)
