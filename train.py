from snake import *
from qlearning import *

# in case we need to reload the library
from importlib import reload
reload(sys.modules['snake'])
reload(sys.modules['qlearning'])
from snake import *
from qlearning import *

# snake parameters
cell_size = 30
box_size = 30
snake_speed = 15
periodic = True

actionMode = 4

stateMode = 'simple'
# stateMode = 'body_length'
# stateMode = 'tail_compass'

# rewards
food_rew = 1.0
lose_rew = -10.0
step_rew = -0.01

snake = Snake(actionMode, stateMode, cell_size, box_size, snake_speed, periodic, food_rew, lose_rew, step_rew)

# ql agent parameters
n_episodes = int(5e3)
epsilon_i = 1.0
epsilon_f = 0.1
learning_rate = 0.05
discount_factor = 1.0

agent = QLearningAgent(snake, n_episodes, epsilon_i, epsilon_f, learning_rate, discount_factor)

q_star, pi_star = agent.train()

snake.play(pi_star)

# np.save(f'policies/pi_{cell_size}_{actionMode}_{stateMode}_{n_episodes}.npy', pi_star)
