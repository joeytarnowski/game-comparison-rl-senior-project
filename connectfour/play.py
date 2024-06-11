import argparse
import os
import pickle
import sys
import time

from connectfourtools.agent import Qlearner, SARSAlearner, MCOffPolicyLearner, MCOnPolicyLearner
from connectfourtools.game import Game
from connectfourtools.teacher import Teacher


class GameLearning(object):
    """
    A class that holds the state of the learning process. Learning
    agents are created/loaded here, and a count is kept of the
    games that have been played.
    """
    def __init__(self, args, alpha=0.5, gamma=0.9, epsilon=1, overridecheck=False):
        self.eps_decay = 0.00003

        if args.load:
            # load an existing agent and continue training
            if not os.path.isfile(args.path):
                raise ValueError("Cannot load agent: file does not exist.")
            with open(args.path, 'rb') as f:
                agent = pickle.load(f)
        else:
            # check if agent state file already exists, and ask
            # user whether to overwrite if so
            if os.path.isfile(args.path) and overridecheck == False:
                print('An agent is already saved at {}.'.format(args.path))
                while True:
                    response = input("Are you sure you want to overwrite? [y/n]: ")
                    if response.lower() in ['y', 'yes']:
                        break
                    elif response.lower() in ['n', 'no']:
                        print("OK. Quitting.")
                        sys.exit(0)
                    else:
                        print("Invalid input. Please choose 'y' or 'n'.")
            if args.agent_type == "q":
                agent = Qlearner(alpha,gamma,epsilon,self.eps_decay)
            elif args.agent_type == "mcon":
                agent = MCOnPolicyLearner(alpha,gamma,epsilon,self.eps_decay)
            elif args.agent_type == "mcoff":
                agent = MCOffPolicyLearner(alpha,gamma,epsilon,self.eps_decay)
            else:
                agent = SARSAlearner(alpha,gamma,epsilon,self.eps_decay)

        self.games_played = 0
        self.path = args.path
        self.agent = agent
        self.agent_type = args.agent_type

    def begin_playing(self):
        """ Loop through game iterations with a human player. """

        def play_again():
            print("Games played: %i" % self.games_played)
            while True:
                play = input("Do you want to play again? [y/n]: ")
                if play == 'y' or play == 'yes':
                    return True
                elif play == 'n' or play == 'no':
                    return False
                else:
                    print("Invalid input. Please choose 'y' or 'n'.")

        while True:
            game = Game(self.agent)
            game.start()
            self.games_played += 1
            self.agent.save(self.path)
            if not play_again():
                print("OK. Quitting.")
                break

    def begin_teaching(self, episodes):
        """ Loop through game iterations with a teaching agent. """
        train_time =  time.perf_counter()
        # Teacher parameters
        depth = 5
        level = 0.9
        teacher = Teacher(depth=depth, level=level)
        teacher.load_moves()
        print(f"Training agent {self.agent_type} for {episodes} episodes")

        # Initial test
        self.agent.save(self.path)
        self.run_diag(True, teacher)
        self.run_diag(False, teacher)
        teacher.depth = depth
        teacher.ability_level = level

        # Train for alotted number of episodes
        while self.games_played < episodes:
            game = Game(self.agent, teacher=teacher)
            game.start()
            self.games_played += 1
            # Monitor progress
            if self.games_played % 1000 == 0:
                # Save agent
                self.agent.save(self.path)
                # Run random and optimal tests
                self.run_diag(True, teacher)
                self.run_diag(False, teacher)
                # Reload teacher
                teacher.depth = depth
                teacher.ability_level = level

            if self.games_played % 10 == 0:
                print("Games played: %i" % self.games_played)

        self.agent.train_time = time.perf_counter() - train_time
        print(f"Training time: {self.agent.train_time}")
        # save final agent
        self.agent.save(self.path)
        teacher.save_moves()
        print(f"The agent won {self.agent.num_wins} times")
        print(f"The agent lost {self.agent.num_losses} times")
        print(f"The agent drew {self.agent.num_draws} times")

    def run_diag(self, is_rand, test_teacher):
        """ Run a diagnostic test with the agent. """

        print(f"Running test with {'random' if is_rand else 'optimal'} teacher")
        test_time = time.perf_counter()
        i = 0
        prev_wins = self.agent.num_wins
        prev_losses = self.agent.num_losses
        prev_draws = self.agent.num_draws
        self.agent.num_wins, self.agent.num_losses, self.agent.num_draws = (0 for i in range(3))
        prev_eps = self.agent.eps
        prev_alpha = self.agent.alpha
        self.agent.eps = 0
        self.agent.alpha = 0
        if not is_rand:
            test_teacher.ability_level = 1.0
            test_teacher.depth = 5
        else:
            test_teacher.ability_level = 0.0

        test_teacher.agent_id = self.agent_type
        while i < (100 if is_rand else 20):
            game = Game(self.agent, teacher=test_teacher)
            game.start()
            i += 1
            
        test_res = [self.agent.num_wins, self.agent.num_losses, self.agent.num_draws]

        if is_rand:
            for i in range(3):
                self.agent.testing_results_rand[i].append(test_res[i])
        else:
            for i in range(3):
                self.agent.testing_results_opt[i].append(test_res[i])
        # Restore agent to previous state
        self.agent.eps = prev_eps
        self.agent.alpha = prev_alpha
        self.agent.num_wins = prev_wins
        self.agent.num_losses = prev_losses
        self.agent.num_draws = prev_draws
        print(f"Test time: {time.perf_counter() - test_time}")
        print(f"Agent won {test_res[0]} times, lost {test_res[1]} times, and drew {test_res[2]} times")

def init_game(args, override=False):
    # initialize game instance
    gl = GameLearning(args,overridecheck=override)

    # play or teach
    if args.teacher_episodes is not None:
        gl.begin_teaching(args.teacher_episodes)
    else:
        gl.begin_playing()

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Play Tic-Tac-Toe.")
    parser.add_argument('-a', "--agent_type", type=str, default="q",
                        choices=['q', 's', 'mcon', 'mcoff'],
                        help="Specify the computer agent learning algorithm. "
                             "AGENT_TYPE='q' for Q-learning, AGENT_TYPE='s' "
                             "for Sarsa-learning, AGENT_TYPE='mcoff' for "
                             "Monte Carlo off-policy, and AGENT_TYPE='mcon' "
                             "for Monte Carlo on-policy.")
    parser.add_argument("-p", "--path", type=str, required=False,
                        help="Specify the path for the agent pickle file. "
                             "Defaults to q_agent.pkl for AGENT_TYPE='q', "
                             "mcoff.pkl for AGENT_TYPE='mcoff', mcon.pkl "
                             "for AGENT_TYPE='mcon', and sarsa_agent.pkl"
                             "for AGENT_TYPE='s'.")
    parser.add_argument("-l", "--load", action="store_true",
                        help="whether to load trained agent")
    parser.add_argument("-t", "--teacher_episodes", default=None, type=int,
                        help="employ teacher agent who knows the optimal "
                             "strategy and will play for TEACHER_EPISODES games")
    args = parser.parse_args()

    # set default path
    if args.path is None:
        match args.agent_type:
            case 'q':
                args.path = 'q_agent.pkl'
            case 'mcon':
                args.path = 'mcon_agent.pkl'
            case 'mcoff':
                args.path = 'mcoff_agent.pkl'
            case _:
                args.path = 'sarsa_agent.pkl'
    init_game(args)