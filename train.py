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

# TODO pass these rewards to the snake object
food_rew = 1.0
lose_rew = -100.0
step_rew = -0.1

game = Snake(cell_size, box_size, snake_speed, periodic, food_rew, lose_rew, step_rew)

# ql agent parameters
n_episodes = int(1e3)
epsilon_i = 1.0
epsilon_f = 0.1
learning_rate = 0.05
discount_factor = 1

agent = QLearningAgent(game, n_episodes, epsilon_i, epsilon_f, learning_rate, discount_factor)

q_star, pi_star = agent.train()

game.play(pi_star)
