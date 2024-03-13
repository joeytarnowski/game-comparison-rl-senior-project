import seoulai_gym as gym
from seoulai_gym.envs.checkers.agents import RandomAgentLight
from seoulai_gym.envs.checkers.agents import RandomAgentDark
from seoulai_gym.envs.checkers.utils import board_list2numpy
from seoulai_gym.envs.checkers.utils import BoardEncoding
from seoulai_gym.envs.checkers.rules import Rules

"""
Notes for board display: 
Dark: 10.
Dark king: 11.
Light: 20.
Light king: 21. 
"""

env = gym.make("Checkers")

a1 = RandomAgentLight()
a2 = RandomAgentDark()

enc = BoardEncoding()

obs = env.reset()

current_agent = a1
next_agent = a2
i = 0
while i < 1000:
    from_row, from_col, to_row, to_col = current_agent.act(obs)
    obs, rew, done, info = env.step(current_agent, from_row, from_col, to_row, to_col)
    valid_moves = Rules.generate_valid_moves(obs,current_agent.ptype, 8)
    current_agent.consume(obs, rew, done)
    print(board_list2numpy(obs))
    print(f"Valid Moves: {valid_moves}")

    if done:
        print(f"Game over! {current_agent} agent wins.")
        print(board_list2numpy(obs))
        obs = env.reset()

    # switch agents
    temporary_agent = current_agent
    current_agent = next_agent
    next_agent = temporary_agent

    env.render()
    i += 1

env.close()