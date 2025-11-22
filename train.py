from snake import *
from qlearning import *

# in case we need to reload libraries
from importlib import reload
reload(sys.modules['snake'])
reload(sys.modules['qlearning'])
from snake import *
from qlearning import *

# game parameters
box_size = 18
periodic = True
action_mode = 3
rand_init_body_length = True
rand_init_direction = True

# state mode
# state_mode = 'simple'
state_mode = 'proximity'

# rewards
food_rew = 1.0
lose_rew = -10.0
step_rew = -0.01
trun_rew = -5

# these are not important because we are not rendering the game window
cell_size = 20
snake_speed = 15

# create snake game object
snake = Snake(action_mode, state_mode, cell_size, box_size, snake_speed, periodic,
        rand_init_body_length, rand_init_direction, food_rew=food_rew, 
        lose_rew=lose_rew, step_rew=step_rew, trun_rew=trun_rew)

# ql agent parameters
n_episodes = int(1e5)
epsilon_i = 1.0
epsilon_f = 0.1
learning_rate = 0.05
discount_factor = 1.0

agent = QLearningAgent(snake, n_episodes, epsilon_i, epsilon_f, learning_rate, discount_factor)

q_star, pi_star = agent.train()

# snake.play(pi_star)

# number of test games
n_games = 1000
mean_score, trun_ratio = test_policy(action_mode, state_mode, box_size, periodic, rand_init_body_length, rand_init_direction, n_games, pi_star)

save_policy(pi_star, periodic, action_mode, state_mode, n_episodes, label=None)

# # prompt user to save or not the policy
# while True:
#     user_input = input("\nSave learned policy? (yes/no): ")
#     if user_input.lower() in ["yes", "y"]:
#         save_policy(pi_star, periodic, action_mode, state_mode, n_episodes, label=None)
#         break
#     elif user_input.lower() in ["no", "n"]:
#         print("Exiting...")
#         break
#     else:
#         print("Invalid input. Please enter yes/no.")
