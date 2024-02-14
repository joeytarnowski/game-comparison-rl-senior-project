from abc import ABC, abstractmethod
import os
import pickle
import collections
import numpy as np
import random


class Learner(ABC):
    """
    Parent class for Q-learning and SARSA agents.

    Parameters
    ----------
    alpha : float 
        learning rate
    gamma : float
        temporal discounting rate
    eps : float 
        probability of random action vs. greedy action
    eps_decay : float
        epsilon decay rate. Larger value = more decay
    """
    def __init__(self, alpha, gamma, eps, eps_decay=0.):
        # Agent parameters
        self.alpha = alpha
        self.gamma = gamma
        self.eps = eps
        self.eps_decay = eps_decay
        # Possible actions correspond to the set of all x,y coordinate pairs
        self.actions = []
        for i in range(3):
            for j in range(3):
                self.actions.append((i,j))
        # Initialize Q values to 0 for all state-action pairs.
        # Access value for action a, state s via Q[a][s]
        self.Q = {}
        for action in self.actions:
            self.Q[action] = collections.defaultdict(int)
        # Keep a list of reward received at each episode
        print(len(self.Q))
        self.rewards = []
    
    def ep_init(self):
        self.trajectory = []
        self.reward_cache = []

    def get_action(self, s):
        """
        Select an action given the current game state.

        Parameters
        ----------
        s : string
            state
        """
        # Only consider the allowed actions (empty board spaces)
        possible_actions = [a for a in self.actions if s[a[0]*3 + a[1]] == '-']
        if random.random() < self.eps:
            # Random choose.
            action = possible_actions[random.randint(0,len(possible_actions)-1)]
        else:
            # Greedy choose.
            values = np.array([self.Q[a][s] for a in possible_actions])
            # Find location of max
            ix_max = np.where(values == np.max(values))[0]
            if len(ix_max) > 1:
                # If multiple actions were max, then sample from them
                ix_select = np.random.choice(ix_max, 1)[0]
            else:
                # If unique max action, select that one
                ix_select = ix_max[0]
            action = possible_actions[ix_select]

        # update epsilon; geometric decay
        self.eps *= (1.-self.eps_decay)
        return action
    
    def compute_cum_rewards(self, gamma, t, rewards) -> float:
        """Cumulative reward function"""
        cum_reward = 0
        # cum_reward = rewards[-1] 
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

    def displayrewards(self):
        print(self.rewards)
        print(f"Length of reward array: {len(self.rewards)}")

    def displayq(self):
        with open('output.txt', 'w') as f:
            f.write(str(self.Q))

    @abstractmethod
    def update(self, s, s_, a, a_, r):
        pass


class Qlearner(Learner):
    """
    A class to implement the Q-learning agent.
    """
    def __init__(self, alpha, gamma, eps, eps_decay=0.):
        super().__init__(alpha, gamma, eps, eps_decay)

    def update(self, s, s_, a, a_, r):
        """
        Perform the Q-Learning update of Q values.

        Parameters
        ----------
        s : string
            previous state
        s_ : string
            new state
        a : (i,j) tuple
            previous action
        a_ : (i,j) tuple
            new action. NOT used by Q-learner!
        r : int
            reward received after executing action "a" in state "s"
        """
        # Update Q(s,a)
        if s_ is not None:
            # hold list of Q values for all a_,s_ pairs. We will access the max later
            possible_actions = [action for action in self.actions if s_[action[0]*3 + action[1]] == '-']
            Q_options = [self.Q[action][s_] for action in possible_actions]
            # update
            self.Q[a][s] += self.alpha*(r + self.gamma*max(Q_options) - self.Q[a][s])
        else:
            # terminal state update
            self.Q[a][s] += self.alpha*(r - self.Q[a][s])

        # add r to rewards list
        self.rewards.append(r)

    def end_update(self,r):
        """Dummy function-only used with MC"""
        pass



class SARSAlearner(Learner):
    """
    A class to implement the SARSA agent.
    """
    def __init__(self, alpha, gamma, eps, eps_decay=0.):
        super().__init__(alpha, gamma, eps, eps_decay)

    def update(self, s, s_, a, a_, r):
        """
        Perform the SARSA update of Q values.

        Parameters
        ----------
        s : string
            previous state
        s_ : string
            new state
        a : (i,j) tuple
            previous action
        a_ : (i,j) tuple
            new action
        r : int
            reward received after executing action "a" in state "s"
        """
        # Update Q(s,a)
        if s_ is not None:
            self.Q[a][s] += self.alpha*(r + self.gamma*self.Q[a_][s_] - self.Q[a][s])
        else:
            # terminal state update
            self.Q[a][s] += self.alpha*(r - self.Q[a][s])

        # add r to rewards list
        self.rewards.append(r)
        

    def end_update(self,r):
        """Dummy function-only used with MC"""
        pass

class MCOffPolicyLearner(Learner):
    """
    A class to implement the Monte Carlo Off Policy agent.
    """    
    def __init__(self, alpha, gamma, eps, eps_decay=0.):
        super().__init__(alpha, gamma, eps, eps_decay)
    
    def update(self, s, s_, a, a_, r):
        """
        Perform the MC Off Policy update of Q values.

        Parameters
        ----------
        s : string
            previous state
        s_ : string
            new state
        a : (i,j) tuple
            previous action
        a_ : (i,j) tuple
            new action
        r : int
            reward received after executing action "a" in state "s"
        """
        # Update Q(s,a)
        if s_ is not None:
            self.Q[a][s] += self.alpha*(r + self.gamma*self.Q[a_][s_] - self.Q[a][s])
        else:
            # terminal state update
            self.Q[a][s] += self.alpha*(r - self.Q[a][s])

        # add r to rewards list
        self.rewards.append(r)

class MCOnPolicyLearner(Learner):
    """
    A class to implement the Monte Carlo On Policy agent.
    """    
    def __init__(self, alpha, gamma, eps, eps_decay=0.):
        super().__init__(alpha, gamma, eps, eps_decay)

    def update(self, s, s_, a, a_, r):
        """
        Perform the Monte Carlo update of *trajectory*.

        Parameters
        ----------
        s : string
            previous state
        s_ : string
            new state. NOT USED
        a : (i,j) tuple
            previous action
        a_ : (i,j) tuple
            new action. NOT USED
        r : int
            reward received after executing action "a" in state "s"
        """
        self.reward_cache.append(r)
        self.rewards.append(r)
        self.trajectory.append([s,a])
                

    def end_update(self, r):
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
            reward = self.reward_cache[t]
            cum_reward = self.compute_cum_rewards(self.gamma, t, self.reward_cache) + reward
            self.Q[action][state] += self.alpha * (cum_reward - self.Q[action][state])
            t += 1
        

