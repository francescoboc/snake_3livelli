# ****************** Boccardo Gagliardi @PiMlB MALGA  ***************
# LEARNING: input environment and learning parameters --> trained policy
# 
# ********************************************************************

import numpy as np
import random, sys, signal
from tqdm import tqdm

# hack to prevent raising KeyboardInterrupt when stopping the script with ctrl-c
# https://stackoverflow.com/questions/7073268/remove-traceback-in-python-on-ctrl-c
signal.signal(signal.SIGINT, lambda x, y: sys.exit())

def initialise_rng(seed):
    global rng 
    rng = random.Random(seed)

class QLearningAgent:
    def __init__(self, 
            environment, 
            n_episodes, 
            epsilon_i, 
            epsilon_f, 
            learning_rate, 
            discount_factor, 
            ):

        self.environment = environment
        self.n_episodes = int(n_episodes)
        self.epsilon_i = epsilon_i
        self.epsilon_f = epsilon_f
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor

        self.action_size = len(self.environment.actions)
        self.enumerated_actions = np.arange(self.action_size)

        # initialise q table as a dictionary
        self.q_table = {state: np.zeros(self.action_size) for state in self.environment.states}
    
    def q_norm(self, q1, q2):
        return (sum(np.sum((q1[key]-q2[key])**2 for key in q1)))

    def play(self, policy, test_steps, real_time_plot = True):
        # reset timestep counter
        step = 0

        # initialize environment and get initial state
        # state = self.environment.reset(real_time_plot)
        state = self.environment.reset()

        # run episode
        while True:
            # select action based on policy
            action = policy[state]

            # take action, observe reward and next state
            # state, reward, terminated = self.environment.update(action, real_time_plot)
            state, reward, terminated = self.environment.step(action)

            # if we reached a terminal state (capture) or reached max number of test steps, end the episode 
            if terminated or step == test_steps:
                break

            # increase timestep counter
            step += 1

        return reward

    def train(self, real_time_plot = False):
        # initialise the random number generator
        seed = random.randrange(sys.maxsize)
        initialise_rng(seed)

        # initialise exploration rate
        epsilon = self.epsilon_i

        # calculate episodic reduction for linear decay of exploration rate
        reduction = (self.epsilon_i - self.epsilon_f)/self.n_episodes

        for epi in tqdm(range(self.n_episodes), ascii=' █'):
        # for epi in range(self.n_episodes):

            # reset timestep counter
            step = 0

            # initialize environment and get initial state
            # state = self.environment.reset(real_time_plot)
            state = self.environment.reset()

            # run episode
            while True:
                # select a random action using behavior policy
                action = self.random_action(state, epsilon)

                # take action, observe reward and next state
                # next_state, reward, terminated = self.environment.step(action, real_time_plot)
                action_label = self.environment.actions[action]
                next_state, reward, terminated = self.environment.step(action_label)

                # Q-Learning update rule 
                # off-policy: Q is updated on the optimal policy, different from the behavior one 
                # -> we consider only the action that maximizes Q
                old_q = self.q_table[state][action] 
                self.q_table[state][action] +=  self.learning_rate*(reward + self.discount_factor*max(self.q_table[next_state]) - self.q_table[state][action])
                new_q = self.q_table[state][action] 
                # delta = max(delta, abs(old_q-new_q))

                # shift state
                state = next_state

                # increase timestep counter
                step += 1

                # if a terminal state was reached, break and use q-learning update rule with Q(s', .) = 0 
                if terminated:
                    self.q_table[state][action] +=  self.learning_rate*(reward - self.q_table[state][action])
                    break

            # decay epsilon linearly
            epsilon -= reduction

        # extract optimal policy from q table
        pi_star = self.extract_policy_from_q()

        return self.q_table, pi_star

    def random_action(self, state, epsilon):
        # with probability epsilon choose a random action (exploration)
        if rng.random() < epsilon:
            return rng.choice(self.enumerated_actions)
        # with probability 1-epsilon choose an optimal action (exploitation)
        else:
            max_q = max(self.q_table[state])
            optimal_actions = [a for a in range(self.action_size) if self.q_table[state][a] == max_q]
            if len(optimal_actions) == 1: return optimal_actions[0]
            else: return rng.choice(optimal_actions)

        # TODO this does not work because at t=0 all actions have the same value = 0!
        # # find best actions for the current state based on q
        # max_q = max(self.q_table[state])
        # optimal_actions = [a for a in range(self.action_size) if self.q_table[state][a] == max_q]
        # # with probability 1-epsilon choose an optimal action (exploitation)
        # if rng.random() < 1-epsilon:
        #     if len(optimal_actions) == 1: return optimal_actions[0]
        #     else: return rng.choice(optimal_actions)
        # # with probability epsilon choose a random non-optimal action (exploration)
        # else:
        #     non_optimal_actions = np.delete(self.environment.actions, optimal_actions)
        #     return rng.choice(non_optimal_actions)

    def extract_policy_from_q(self):
        # initialise dictionary for policy
        pi_star = {state: None for state in self.environment.states}

        # determine best action(s)
        for state in self.environment.states:
            max_q = max(self.q_table[state])
            optimal_actions = [a for a in range(self.action_size) if self.q_table[state][a] == max_q]
            # assign the best action to policy pi_star
            if len(optimal_actions) == 1: pi_star[state] = self.environment.actions[optimal_actions[0]]
            else: pi_star[state] = self.environment.actions[rng.choice(optimal_actions)]

        return pi_star
