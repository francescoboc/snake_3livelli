# ****************** Boccardo Gagliardi @PiMlB MALGA  ***************
# LEARNING: input environment and learning parameters --> trained policy
# 
# ********************************************************************

from tools import *

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

        # extract number of actions and create a list of action indexes
        self.action_size = len(self.environment.actions)
        self.action_indexes = np.arange(self.action_size)

        # initialise q table as a dictionary
        self.q_table = {state: np.array([rng.random() for a in range(self.action_size)]) for state in self.environment.states}

        # set Q(Term, .) = 0 
        self.q_table['Term'] = np.zeros(self.action_size)
    
    def q_norm(self, q1, q2):
        return (sum(np.sum((q1[key]-q2[key])**2 for key in q1)))

    def train(self):
        # initialise exploration rate
        epsilon = self.epsilon_i

        # calculate episodic reduction for linear decay of exploration rate
        reduction = (self.epsilon_i - self.epsilon_f)/self.n_episodes

        iterator = tqdm(range(self.n_episodes), ascii=' █') 
        for epi in iterator:
        # for epi in range(self.n_episodes):

            # reset timestep counter
            step = 0

            # initialize environment and get initial state
            state = self.environment.reset()

            # run episode
            while True:
                # select a random action using behavior policy
                action_id = self.random_action_id(state, epsilon)

                # take action, observe reward and next state
                action = self.environment.actions[action_id]
                next_state, reward, terminated, truncated = self.environment.step(action)

                # Q-Learning update rule 
                # off-policy: Q is updated on the optimal policy, different from the behavior one 
                # -> we consider only the action that maximizes Q
                old_q = self.q_table[state][action_id] 
                self.q_table[state][action_id] +=  self.learning_rate*(reward + self.discount_factor*max(self.q_table[next_state]) - self.q_table[state][action_id])
                new_q = self.q_table[state][action_id] 
                # delta = max(delta, abs(old_q-new_q))

                # shift state
                state = next_state

                # increase timestep counter
                step += 1

                # if a terminal state was reached, break 
                if terminated or truncated:
                    break

            # decay epsilon linearly
            epsilon -= reduction

        # extract optimal policy from q table
        pi_star = self.extract_policy_from_q()

        return self.q_table, pi_star

    def random_action_id(self, state, epsilon):
        # with probability epsilon choose a random action (exploration)
        if rng.random() < epsilon:
            return rng.choice(self.action_indexes)
        # with probability 1-epsilon choose an optimal action (exploitation)
        else:
            max_q = max(self.q_table[state])
            optimal_action_ids = [a for a in range(self.action_size) if self.q_table[state][a] == max_q]
            if len(optimal_action_ids) == 1: return optimal_action_ids[0]
            else: return rng.choice(optimal_action_ids)

        # # TODO this is extremely slow... why?
        # # only choose among non-optimal actions
        # max_q = max(self.q_table[state])
        # optimal_actions_ids = [a for a in range(self.action_size) if self.q_table[state][a] == max_q]
        # # with probability 1-epsilon choose an optimal action (exploitation)
        # if rng.random() < 1-epsilon:
        #     if len(optimal_actions_ids) == 1: return optimal_actions_ids[0]
        #     else: return rng.choice(optimal_actions_ids)
        # # with probability epsilon choose a random non-optimal action (exploration)
        # else:
        #     non_optimal_actions_ids = np.delete(self.action_indexes, optimal_actions_ids)
        #     return rng.choice(non_optimal_actions_ids)

    def extract_policy_from_q(self):
        # initialise dictionary for policy
        pi_star = {state: None for state in self.environment.states}

        # determine best action(s)
        for state in self.environment.states:
            max_q = max(self.q_table[state])
            optimal_action_ids = [a for a in range(self.action_size) if self.q_table[state][a] == max_q]
            # assign the best action to policy pi_star
            if len(optimal_action_ids) == 1: pi_star[state] = self.environment.actions[optimal_action_ids[0]]
            else: pi_star[state] = self.environment.actions[rng.choice(optimal_action_ids)]
            pi_star['Term'] = None

        return pi_star
