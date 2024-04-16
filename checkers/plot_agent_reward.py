import argparse
import os
import pickle
import sys
import numpy as np
import matplotlib.pylab as plt

def best_fit(X, Y):
    xbar = sum(X)/len(X)
    ybar = sum(Y)/len(Y)
    n = len(Y) # or len(Y)

    numer = sum([xi*yi for xi,yi in zip(X,Y)]) - n * xbar * ybar
    denum = sum([xi**2 for xi in X]) - n * xbar**2

    b = numer / denum
    a = ybar - b * xbar

    print('best fit line:\ny = {:.2f} + {:.2f}x'.format(a, b))

    return a, b

def plot_agent_reward(agent, name, *args, **kwargs):
    test_type = kwargs.get('t', None)
    rewards = agent[0]
    train_time = agent[1]
    rand_results = agent[2]
    opt_results = agent[3]
    agent2 = kwargs.get('a2', None)
    if agent2:
        rewards2 = agent2[0]
        train_time2 = agent2[1]
        rand_results2 = agent2[2]
        opt_results2 = agent2[3]
    name2 = kwargs.get('n2', None)
    agent3 = kwargs.get('a3', None)
    if agent3:
        rewards3 = agent3[0]
        train_time3 = agent3[1]
        rand_results3 = agent3[2]
        opt_results3 = agent3[3]
    name3 = kwargs.get('n3', None)
    agent4 = kwargs.get('a4', None)
    if agent4:
        rewards4 = agent4[0]
        train_time4 = agent4[1]
        rand_results4 = agent4[2]
        opt_results4 = agent4[3]
    name4 = kwargs.get('n4', None)
    print(test_type)
    match test_type:
        case "rand":
            plt.rcParams["figure.autolayout"] = True
            plt.plot(rand_results[0], label="Wins")
            plt.plot(rand_results[1], label="Losses")
            plt.plot(rand_results[2], label="Draws")
            plt.title(f'{name} Results vs Random Moves')
            plt.ylabel('Number of Test Games')
            plt.xlabel('Training Games (per hundred)')
            plt.legend(loc='center right')
            plt.show()
        case "opt":
            plt.rcParams["figure.autolayout"] = True
            plt.plot(opt_results[0], label="Wins")
            plt.plot(opt_results[1], label="Losses")
            plt.plot(opt_results[2], label="Draws")
            plt.title(f'{name} Results vs Optimal Moves')
            plt.ylabel('Number of Test Games')
            plt.xlabel('Training Games (per hundred)')
            plt.legend(loc='center right')
            plt.show()
        case "all":
            plt.rcParams["figure.autolayout"] = True
            fig, (ax1, ax2) = plt.subplots(2)
            fig.suptitle(f'{name} Results vs Random and Optimal Moves')
            # plot of random moves
            ax1.plot(rand_results[0], label="Wins")
            ax1.plot(rand_results[1], label="Losses")
            ax1.plot(rand_results[2], label="Draws")
            ax1.set_title(f'vs Random Moves')
            ax1.set_ylabel('Number of Test Games')
            ax1.set_xlabel('Training Games (per hundred)')
            ax1.legend(loc='center right')
            # plot of optimal moves
            ax2.plot(opt_results[0], label="Wins")
            ax2.plot(opt_results[1], label="Losses")
            ax2.plot(opt_results[2], label="Draws")
            ax2.set_title(f'vs Optimal Moves')
            ax2.set_ylabel('Number of Test Games')
            ax2.set_xlabel('Training Games (per hundred)')
            ax2.legend(loc='center right')
            plt.show()
        case "time":
            x = np.array([name,name2,name3,name4])
            y = np.array([train_time, train_time2, train_time3, train_time4])
            plt.ylim((y.min() - (y.min()*.05)), (y.max() + (y.max()*.05)))
            plt.bar(x,y)
            plt.title('Time to Train Per Agent')
            plt.ylabel('Time (Seconds)')
            plt.xlabel('Agent')
            plt.show()
        case "totalrand":
            names = (name,name2,name3,name4)
            agent_data_rand = {
                'Wins': (sum(rand_results[0]), sum(rand_results2[0]), sum(rand_results3[0]), sum(rand_results4[0])),
                'Losses': (sum(rand_results[1]), sum(rand_results2[1]), sum(rand_results3[1]), sum(rand_results4[1])),
                'Draws': (sum(rand_results[2]), sum(rand_results2[2]), sum(rand_results3[2]), sum(rand_results4[2]))
            }
            x = np.arange(len(names))  # the label locations
            width = 0.25  # the width of the bars
            multiplier = 0

            fig, ax = plt.subplots(layout='constrained')

            for result, num in agent_data_rand.items():
                offset = width * multiplier
                rects = ax.bar(x + offset, num, width, label=result)
                ax.bar_label(rects, padding=3)
                multiplier += 1
            ax.set_ylim((min(agent_data_rand['Draws']) - (min(agent_data_rand['Draws'])*.05)), (max(agent_data_rand['Wins']) + (max(agent_data_rand['Wins'])*.05)))
            # Add some text for labels, title and custom x-axis tick labels, etc.
            ax.set_ylabel('Number of Games')
            ax.set_title('Win/Loss/Draw Results vs Random Moves')
            ax.set_xticks(x + width, names)
            ax.legend(loc='upper left', ncols=3)

            plt.show()
        case "totalopt":
            names = (name,name2,name3,name4)
            agent_data_opt = {
                'Wins': (sum(opt_results[0]), sum(opt_results2[0]), sum(opt_results3[0]), sum(opt_results4[0]),), 
                'Losses': (sum(opt_results[1]), sum(opt_results2[1]), sum(opt_results3[1]), sum(opt_results4[1])),
                'Draws': (sum(opt_results[2]), sum(opt_results2[2]), sum(opt_results3[2]), sum(opt_results4[2]))
            } 
            x = np.arange(len(names))  # the label locations
            width = 0.25  # the width of the bars
            multiplier = 0

            fig, ax = plt.subplots(layout='constrained')

            for result, num in agent_data_opt.items():
                offset = width * multiplier
                rects = ax.bar(x + offset, num, width, label=result)
                ax.bar_label(rects, padding=3)
                multiplier += 1
            ax.set_ylim(0, (max(agent_data_opt['Losses']) + (max(agent_data_opt['Losses'])*.05)))
            # Add some text for labels, title and custom x-axis tick labels, etc.
            ax.set_ylabel('Number of Games')
            ax.set_title('Win/Loss/Draw Results vs Optimal Moves')
            ax.set_xticks(x + width, names)
            ax.legend(loc='upper left', ncols=2)

            plt.show()
        case "opt_best_fit":
            X = [i for i in range(len(opt_results[2]))]
            Y1 = opt_results[2]
            a1, b1 = best_fit(X, Y1)
            Y2 = opt_results2[2]
            a2, b2 = best_fit(X, Y2)
            Y3 = opt_results3[2]
            a3, b3 = best_fit(X, Y3)
            Y4 = opt_results4[2]
            a4, b4 = best_fit(X, Y4)

            plt.rcParams["figure.autolayout"] = True
            yfit1 = [a1 + b1 * xi for xi in X]
            yfit2 = [a2 + b2 * xi for xi in X]
            yfit3 = [a3 + b3 * xi for xi in X]
            yfit4 = [a4 + b4 * xi for xi in X]
            plt.plot(X, yfit1, label=name)
            plt.plot(X, yfit2, label=name2)
            plt.plot(X, yfit3, label=name3)
            plt.plot(X, yfit4, label=name4)
            plt.title('Line of Best Fit for Draws vs. Optimal Moves')
            plt.ylabel('Draws')
            plt.xlabel('Training Games (per hundred)')
            plt.legend()
            plt.show()
        case "rand_best_fit":
            X = [i for i in range(len(rand_results[0]))]
            Y1 = rand_results[0]
            a1, b1 = best_fit(X, Y1)
            Y2 = rand_results2[0]
            a2, b2 = best_fit(X, Y2)
            Y3 = rand_results3[0]
            a3, b3 = best_fit(X, Y3)
            Y4 = rand_results4[0]
            a4, b4 = best_fit(X, Y4)

            plt.rcParams["figure.autolayout"] = True
            yfit1 = [a1 + b1 * xi for xi in X]
            yfit2 = [a2 + b2 * xi for xi in X]
            yfit3 = [a3 + b3 * xi for xi in X]
            yfit4 = [a4 + b4 * xi for xi in X]
            plt.plot(X, yfit1, label=name)
            plt.plot(X, yfit2, label=name2)
            plt.plot(X, yfit3, label=name3)
            plt.plot(X, yfit4, label=name4)
            plt.title('Line of Best Fit for Wins vs. Random Moves')
            plt.ylabel('Wins')
            plt.xlabel('Training Games (per hundred)')
            plt.legend()
            plt.show()
        case _:
            """ Function to plot agent's accumulated reward vs. iteration """
            plt.rcParams["figure.autolayout"] = True
            plt.plot(np.cumsum(rewards), label=name)
            plt.plot(np.cumsum(rewards2), label=name2)
            plt.plot(np.cumsum(rewards3), label=name3)
            plt.plot(np.cumsum(rewards4), label=name4)
            plt.title('Agent Cumulative Reward vs. Iteration')
            plt.ylabel('Reward')
            plt.xlabel('Episode')
            plt.legend()
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
    parser.add_argument("-t", "--test", type=str, required=False)
    args = parser.parse_args()

    agentinfo, agent2info, agent3info, agent4info = [], [], [], []
    with open('Results/res.pkl', 'rb') as f:
        res = pickle.load(f)

    if not os.path.isfile(args.path):
        print("Cannot load agent: file does not exist. Quitting.")
        sys.exit(0)
    reskey = args.path[8:]
    agentinfo = res[reskey]
    print("Agent loaded")


    if args.path2:
        if not os.path.isfile(args.path2):
            print("Cannot load agent: file 2 does not exist. Quitting.")
            sys.exit(0)
        reskey2 = args.path2[8:]
        agent2info = res[reskey2]
        print("Agent 2 loaded")
    else:
        agent2info = None


    if args.path3:
        if not os.path.isfile(args.path3):
            print("Cannot load agent: file 3 does not exist. Quitting.")
            sys.exit(0)
        reskey3 = args.path3[8:]
        agent3info = res[reskey3]
        print("Agent 3 loaded")
    else:
        agent3info = None

    if args.path4:
        if not os.path.isfile(args.path4):
            print("Cannot load agent: file 4 does not exist. Quitting.")
            sys.exit(0)
        reskey4 = args.path4[8:]
        agent4info = res[reskey4]
        print("Agent 4 loaded")
    else:
        agent4info = None

    if agent4info is not None:
        plot_agent_reward(agentinfo, args.name, a2=agent2info, n2=args.name2, a3=agent3info, n3=args.name3, a4=agent4info, n4=args.name4, t=args.test)
    elif agent3info is not None:
        plot_agent_reward(agentinfo, args.name, a2=agent2info, n2=args.name2, a3=agent3info, n3=args.name3)
    elif agent2info is not None:
        plot_agent_reward(agentinfo, args.name, a2=agent2info, n2=args.name2)
    else:
        plot_agent_reward(agentinfo, args.name, t=args.test)