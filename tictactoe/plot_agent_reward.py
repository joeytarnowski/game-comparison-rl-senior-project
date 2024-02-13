import argparse
import os
import pickle
import sys
import numpy as np
import matplotlib.pylab as plt


def plot_agent_reward(rewards, name, *args, **kwargs):
    rewards2 = kwargs.get('r2', None)
    name2 = kwargs.get('n2', None)
    rewards3 = kwargs.get('r3', None)
    name3 = kwargs.get('n3', None)
    rewards4 = kwargs.get('r4', None)
    name4 = kwargs.get('n4', None)

    """ Function to plot agent's accumulated reward vs. iteration """
    plt.rcParams["figure.autolayout"] = True
    plt.plot(np.cumsum(rewards), label=name)
    plt.plot(np.cumsum(rewards2), label=name2)
    plt.plot(np.cumsum(rewards3), label=name3)
    plt.plot(np.cumsum(rewards4), label=name4)
    plt.title('Agent Cumulative Reward vs. Iteration')
    plt.ylabel('Reward')
    plt.xlabel('Episode')
    plt.legend(loc='upper right')
    plt.show()


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Plot agent reward.")
    parser.add_argument("-p", "--path", type=str, required=True)
    parser.add_argument("-n", "--name", type=str, required=True)
    parser.add_argument("-p2", "--path2", type=str, required=False)
    parser.add_argument("-n2", "--name2", type=str, required=False)
    parser.add_argument("-p3", "--path3", type=str, required=False)
    parser.add_argument("-n3", "--name3", type=str, required=False)
    parser.add_argument("-p4", "--path4", type=str, required=False)
    parser.add_argument("-n4", "--name4", type=str, required=False)
    args = parser.parse_args()

    if not os.path.isfile(args.path):
        print("Cannot load agent: file does not exist. Quitting.")
        sys.exit(0)
    with open(args.path, 'rb') as f:
        agent = pickle.load(f)

    if args.path2:
        if not os.path.isfile(args.path2):
            print("Cannot load agent: file 2 does not exist. Quitting.")
            sys.exit(0)
        with open(args.path2, 'rb') as g:
            agent2 = pickle.load(g)
    else:
        agent2 = None

    if args.path3:
        if not os.path.isfile(args.path3):
            print("Cannot load agent: file 3 does not exist. Quitting.")
            sys.exit(0)
        with open(args.path3, 'rb') as h:
            agent3 = pickle.load(h)
    else:
        agent3 = None

    if args.path4:
        if not os.path.isfile(args.path4):
            print("Cannot load agent: file 4 does not exist. Quitting.")
            sys.exit(0)
        with open(args.path4, 'rb') as i:
            agent4 = pickle.load(i)
    else:
        agent4 = None

    if agent4 is not None:
        plot_agent_reward(agent.rewards, args.name, r2=agent2.rewards, n2=args.name2, r3=agent3.rewards, n3=args.name3, r4=agent4.rewards, n4=args.name4)
    elif agent3 is not None:
        plot_agent_reward(agent.rewards, args.name, r2=agent2.rewards, n2=args.name2, r3=agent3.rewards, n3=args.name3)
    elif agent2 is not None:
        plot_agent_reward(agent.rewards, args.name, r2=agent2.rewards, n2=args.name2)
    else:
        plot_agent_reward(agent.rewards, args.name)