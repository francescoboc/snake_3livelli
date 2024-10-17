from snake import *
from qlearning import *

# in case we need to reload the library
from importlib import reload
reload(sys.modules['snake'])
reload(sys.modules['qlearning'])
from snake import *
from qlearning import *

# game parameters
box_size = 30
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
# step_rew = 0.0
trun_rew = -10
# trun_rew = -5

print(state_mode)
print(food_rew, lose_rew, step_rew, trun_rew)
# policy_label = 'sr_-0.01_tr-5'
# policy_label = 'sr_0.0_tr_-5'
# policy_label = 'sr_0.0_tr_-10'
policy_label = 'sr_-0.01_tr-10'

# ql agent parameters
n_episodes = int(1e7)
epsilon_i = 1.0
epsilon_f = 0.1
learning_rate = 0.05
discount_factor = 1.0

# these are not important because we are not rendering the game window
cell_size = 20
snake_speed = 15

best_score = 0

for g in range(1000):
    print(g)
    # seed to initialize the RNG
    seed = None
    seed_rng(seed, verbose=False)

    # create snake game object
    snake = Snake(action_mode, state_mode, cell_size, box_size, snake_speed, periodic,
            rand_init_body_length, rand_init_direction, verbose=False, 
            food_rew=food_rew, lose_rew=lose_rew, step_rew=step_rew, trun_rew=trun_rew)

    agent = QLearningAgent(snake, n_episodes, epsilon_i, epsilon_f, learning_rate, discount_factor)

    q_star, pi_star = agent.train(use_tqdm=False)

    # snake.play(pi_star)

    # number of teset games
    n_games = 1000
    mean_score, trun_ratio = test_policy(action_mode, state_mode, box_size, periodic, 
            rand_init_body_length, rand_init_direction, n_games, pi_star, verbose=False, use_tqdm=False)

    print(f'CURRENT BEST SCORE:{best_score}')
    if mean_score >= best_score:
        save_policy(pi_star, periodic, action_mode, state_mode, n_episodes, label=policy_label)
        best_score = mean_score
        print(f'NEW BEST SCORE:{best_score}')

    print('----------')

    # # prompt user to save or not the policy
    # while True:
    #     user_input = input("\nSave learned policy? (yes/no): ")
    #     if user_input.lower() in ["yes", "y"]:
    #         save_policy(pi_star, periodic, box_size, action_mode, state_mode, n_episodes)
    #         break
    #     elif user_input.lower() in ["no", "n"]:
    #         print("Exiting...")
    #         break
    #     else:
    #         print("Invalid input. Please enter yes/no.")


