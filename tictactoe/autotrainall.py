import argparse
import play
from types import SimpleNamespace
"""
Trains all agents for set amount of games
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Tic-Tac-Toe AI.")
    parser.add_argument("-t", "--teacher_episodes", default=1000, type=int,
                    help="employ teacher agent who knows the optimal "
                            "strategy and will play for TEACHER_EPISODES games")
    temp_args = parser.parse_args()
    # SARSA
    args = SimpleNamespace(agent_type='s', path='sarsa_agent.pkl', load=False, teacher_episodes=temp_args.teacher_episodes)
    print(args)
    play.initGame(args,override=True)

    # Q-Learning
    args = SimpleNamespace(agent_type='q', path='q_agent.pkl', load=False, teacher_episodes=temp_args.teacher_episodes)
    play.initGame(args,override=True)

    # Monte Carlo On-Policy
    args = SimpleNamespace(agent_type='mcon', path='mcon_agent.pkl', load=False, teacher_episodes=temp_args.teacher_episodes)
    play.initGame(args,override=True)

    # Monte Carlo Off-Policy
    args = SimpleNamespace(agent_type='mcoff', path='mcoff_agent.pkl', load=False, teacher_episodes=temp_args.teacher_episodes)
    play.initGame(args,override=True)