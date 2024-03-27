import random
import pickle
import os
import numpy as np

class Learner:
    """
    A class to be inherited by any class representing a checkers player.
    This is used so that other functions can be written for more general use,
    without worry of crashing (e.g. play_n_games).
    """

    def __init__(self, alpha, gamma, eps, eps_decay = 0.):
        # Agent parameters
        self.alpha = alpha
        self.gamma = gamma
        self.eps = eps
        self.eps_decay = eps_decay
        self.train_time = 0
        self.num_wins, self.num_losses, self.num_draws = (0 for i in range(3))
        self.testing_results_rand = [[],[],[],[]]
        self.testing_results_opt = [[],[],[],[]]
        self.HEIGHT = 8
        self.WIDTH = 4

        # Initialize Q table to empty list to hold state-action pairs.
        # Access value for state s, action (move, piece) via Q[s][a]
        self.Q = {}
        self.C = {}
        # Keep a list of reward received at each episode
        self.rewards = []
    
    def ep_init(self):
        # Only used for MC agents
        self.trajectory = []
        self.target_trajectory = []
        self.reward_cache = []

    def update_count(self, result):
        match result:
            case "win":
                self.num_wins += 1
            case "loss":
                self.num_losses += 1
            case _:
                self.num_draws += 1

    def get_action(self, s, possible_actions):
        """
        Select an action given the current game state.

        Parameters
        ----------
        s : string
            state
        """
        try:
            values = np.array([self.Q[s][tuple([tuple(a[0]), tuple(a[1])])] for a in possible_actions])
        except KeyError:
            self.Q[s] = {}
            for a in possible_actions:
                self.Q[s][tuple([tuple(a[0]), tuple(a[1])])] = 0
            values = np.array([self.Q[s][tuple([tuple(a[0]), tuple(a[1])])] for a in possible_actions])
        # Find location of max
        ix_max = np.where(values == np.max(values))[0]
        if random.random() < self.eps:
            # Random choose.
            action = possible_actions[random.randint(0,len(possible_actions)-1)]
        else:
            # Greedy choose.
            if len(ix_max) > 1:
                # If multiple actions were max, then sample from them
                ix_select = np.random.choice(ix_max, 1)[0]
            else:
                # If unique max action, select that one
                ix_select = ix_max[0]
            action = possible_actions[ix_select]

        if len(self.target_trajectory) == 0:
            traj = []
            for i in ix_max:
                traj.append(possible_actions[i])
            self.target_trajectory.append(traj)

        return action
    
    def compute_cum_rewards(self, gamma, t, rewards) -> float:
        """Cumulative reward function"""
        cum_reward = 0
        for tau in range(t, len(rewards)):
            cum_reward += gamma ** (tau - t) * rewards[tau]
        return cum_reward

    def save(self, path):
        """ Pickle the agent object instance to save the agent's state. """
        if os.path.isfile(path):
            os.remove(path)
        f = open(path, 'wb')
        pickle.dump(self, f)
        f.close()
    
    def set_board(self, the_board):
        """
        Sets the Board object which is known by the AI.
        """
        self.board = the_board
    
        """
        Should be overridden if AI implementing this class should be notified 
        of when a game ends, before the board is wiped.
        """
        pass
    

class Qlearner(Learner):
    """
    A class to implement the Q-learning agent.
    """
    def __init__(self, alpha, gamma, eps, eps_decay=0.):
        super().__init__(alpha, gamma, eps, eps_decay)
    

    def update(self, s, s_, a, a_, r, possible_actions):
        """
        Perform the Q-Learning update of Q values.

        Parameters
        ----------
        s : int
            previous state
        s_ : int
            new state
        a : (i,j) tuple
            previous action
        a_ : (i,j) tuple
            new action. NOT used by Q-learner!
        r : int
            reward received after executing action "a" in state "s"
        possible_actions : list
            list of possible actions from state "s".
        """
        a = tuple([tuple(a[0]), tuple(a[1])])
        
        # Update Q(s,a)
        if s_ is not None:
            # hold list of Q values for all a_,s_ pairs. We will access the max later
            Q_options = [self.Q[s_][tuple([tuple(action[0]), tuple(action[1])])] for action in possible_actions]
            # update
            self.Q[s][a] += self.alpha*(r + self.gamma*max(Q_options) - self.Q[s][a])

        else:
            # terminal state update
            self.Q[s][a] += self.alpha*(r - self.Q[s][a])

        # add r to rewards list
        self.rewards.append(r)

    def end_update(self):
        # update epsilon; geometric decay
        self.eps *= (1.-self.eps_decay)

class SARSAlearner(Learner):
    """
    A class to implement the SARSA agent.
    """
    def __init__(self, alpha, gamma, eps, eps_decay=0.):
        super().__init__(alpha, gamma, eps, eps_decay)
    

    def update(self, s, s_, a, a_, r, possible_actions):
        """
        Perform the SARSA update of Q values.

        Parameters
        ----------
        s : int
            previous state
        s_ : int
            new state
        a : (i,j) tuple
            previous action
        a_ : (i,j) tuple
            new action
        r : int
            reward received after executing action "a" in state "s"
        possible_actions : list
            list of possible actions from state "s". NOT USED WITH ON-POLICY AGENT
        """
        a = tuple([tuple(a[0]), tuple(a[1])])

        # Update Q(s,a)
        if s_ is not None:
            a_ = tuple([tuple(a_[0]), tuple(a_[1])])
            self.Q[s][a] += self.alpha*(r + self.gamma*self.Q[s_][a_] - self.Q[s][a])
        else:
            # terminal state update
            self.Q[s][a] += self.alpha*(r - self.Q[s][a])

        # add r to rewards list
        self.rewards.append(r)

    def end_update(self):
        # update epsilon; geometric decay
        self.eps *= (1.-self.eps_decay)

class MCOffPolicyLearner(Learner):
    """
    A class to implement the Monte Carlo Off Policy agent.
    """    
    def __init__(self, alpha, gamma, eps, eps_decay=0.):
        super().__init__(alpha, gamma, eps, eps_decay)

    def update(self, s, s_, a, a_, r, possible_actions):
        """
        Perform the Monte Carlo update of *trajectory*.

        Parameters
        ----------
        s : int
            previous state
        s_ : int
            new state. NOT USED
        a : (i,j) tuple
            previous action
        a_ : (i,j) tuple
            new action.
        r : int
            reward received after executing action "a" in state "s"
        possible_actions : list
            list of possible actions from state "s".
        """
        a = tuple([tuple(a[0]), tuple(a[1])])
        self.reward_cache.append(r)
        self.rewards.append(r)
        self.trajectory.append([s,a])
        if s_ is not None:
            # hold list of Q values for all a_,s_ pairs. We will access the max later
            Q_options = [self.Q[s_][tuple([tuple(action[0]), tuple(action[1])])] for action in possible_actions]
            # update target trajectory
            max_Q = max(Q_options)
            traj = []
            for i in range(len(Q_options)):
                if Q_options[i] == max_Q:
                    traj.append(possible_actions[i])
            self.target_trajectory.append(traj)
        else:
            # store last move in trajectory
            self.target_trajectory.append(a)

    def end_update(self):
        """
        Perform the Monte Carlo off-policy update of Q values.
        """
        if self.alpha != 0:
            t = len(self.trajectory) - 1
            # update Q table for full trajectory
            for state, action in self.trajectory [::-1]:
                action = tuple([tuple(action[0]), tuple(action[1])])
                reward = self.reward_cache[t]
                cum_reward = self.compute_cum_rewards(self.gamma, t, self.reward_cache) + reward
                try:
                    self.C[state][action] += self.alpha
                except KeyError:
                    if self.C.get(state) is None:
                        self.C[state] = {}
                    self.C[state][action] = self.alpha
                self.Q[state][action] += (cum_reward - self.Q[state][action]) * (self.alpha/self.C[state][action])
                
                if list([list(action[0]),list(action[1])]) not in self.target_trajectory[t]:
                    break
                t -= 1

        # update epsilon; geometric decay
        self.eps *= (1.-self.eps_decay)


class MCOnPolicyLearner(Learner):
    """
    A class to implement the Monte Carlo On Policy agent.
    """    
    def __init__(self, alpha, gamma, eps, eps_decay=0.):
        super().__init__(alpha, gamma, eps, eps_decay)

    def update(self, s, s_, a, a_, r, possible_actions):
        """
        Perform the Monte Carlo update of *trajectory*.

        Parameters
        ----------
        s : int
            previous state
        s_ : int
            new state. NOT USED
        a : (i,j) tuple
            previous action
        a_ : (i,j) tuple
            new action. NOT USED
        r : int
            reward received after executing action "a" in state "s"
        possible_actions : list
            list of possible actions from state "s". NOT USED WITH ON-POLICY AGENT
        """
        a = tuple([tuple(a[0]), tuple(a[1])])
        self.reward_cache.append(r)
        self.rewards.append(r)
        self.trajectory.append([s,a])
                

    def end_update(self):
        """
        Perform the Monte Carlo update of Q values.

        Parameters
        ----------
        reward : int
            Reward received after completing the episode
        """
        t = 0
        # update Q table for full trajectory
        for state, action in self.trajectory:
            action = tuple([tuple(action[0]), tuple(action[1])])
            reward = self.reward_cache[t]
            cum_reward = self.compute_cum_rewards(self.gamma, t, self.reward_cache) + reward
            try:
                self.Q[state][action] += self.alpha * (cum_reward - self.Q[state][action])
            except KeyError:
                self.Q[state][action] = self.alpha * (cum_reward - self.Q[state][action])
            t += 1

        # update epsilon; geometric decay
        self.eps *= (1.-self.eps_decay)