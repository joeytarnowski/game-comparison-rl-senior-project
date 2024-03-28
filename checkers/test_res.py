import pickle
import os
import sys
from copy import deepcopy

path = 'res.pkl'
agentname = input("Enter agent path: ")
if os.path.isfile(path):
    with open(path, 'rb') as f:
        res = pickle.load(f)
else:
    res = {}

print("Agent loading...")
with open(agentname, 'rb') as f:
    agent = pickle.load(f)
    rewards = agent.rewards
    time = agent.train_time
    rand_results = [agent.testing_results_rand[0], agent.testing_results_rand[1], agent.testing_results_rand[2]]
    opt_results = [agent.testing_results_opt[0], agent.testing_results_opt[1], agent.testing_results_opt[2]]
    print(f"rewards size: {sys.getsizeof(rewards)}")
    print(f"rewards[0] type: {type(rewards[0])}")
    print(f"time size: {sys.getsizeof(time)}")
    print(f"rand_results size: {sys.getsizeof(rand_results)}")
    print(f"opt_results size: {sys.getsizeof(opt_results)}")
    agentinfo = [rewards, time, rand_results, opt_results]
    print(f"agentinfo size: {sys.getsizeof(agentinfo)}")

res[agentname] = agentinfo

print("Res saving...")
with open(path, 'wb') as handle:
    pickle.dump(res, handle, -1)