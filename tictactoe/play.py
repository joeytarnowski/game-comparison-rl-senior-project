import argparse
import os
import pickle
import sys
import time

from tictactoe.agent import Qlearner, SARSAlearner, MCOffPolicyLearner, MCOnPolicyLearner
from tictactoe.game import Game
from tictactoe.dictteacher import Teacher
from tictactoe.gui import TicTacToeGUI


class GameLearning(object):
    """
    A class that holds the state of the learning process. Learning
    agents are created/loaded here, and a count is kept of the
    games that have been played.
    """
    def __init__(self, args, alpha=0.5, gamma=0.9, epsilon=1, overridecheck=False):
        self.eps_decay = 0.0001
        self.gui = TicTacToeGUI()
        if args.teacher_episodes is None:
            args.agent_type = self.gui.ask_agent()
            args.load = True

        # set default path
        if args.path is None:
            match args.agent_type:
                case 'q':
                    args.path = os.path.join('Demo','q_agent.pkl')
                case 'mcon':
                    args.path = os.path.join('Demo','mcon_agent.pkl')
                case 'mcoff':
                    args.path = os.path.join('Demo','mcoff_agent.pkl')
                case _:
                    args.path = os.path.join('Demo', 'sarsa_agent.pkl')

        if args.load:
            # load an existing agent and continue training
            if not os.path.isfile(args.path):
                print("Current Working Directory:", os.getcwd())
                raise ValueError(f"Cannot load agent: file {args.path} does not exist.")
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

    def beginPlaying(self):
        """ Loop through game iterations with a human player. """
        self.agent.eps = 0

        def play_again(play):
            print("Games played: %i" % self.games_played)
            while True:
                if play == 'y' or play == 'yes':
                    return True
                elif play == 'n' or play == 'no':
                    return False
                else:
                    print("Invalid input. Please choose 'y' or 'n'.")

        while True:
            game = Game(self.agent)
            game.set_GUI(self.gui)
            game.start()
            self.games_played += 1
            self.agent.save(self.path)
            if not play_again(game.play_again):
                print("OK. Quitting.")
                break
            self.gui.reset_game()

    def beginTeaching(self, episodes):
        """ Loop through game iterations with a teaching agent. """
        train_time =  time.perf_counter()
        teacher = Teacher()
        # Initial test
        self.runDiag(True)
        self.runDiag(False)
        # Train for alotted number of episodes
        while self.games_played < episodes:
            game = Game(self.agent, teacher=teacher)
            game.start()
            self.games_played += 1
            # Monitor progress
            if self.games_played % 100 == 0:
                # Run random and optimal tests
                self.runDiag(True)
                self.runDiag(False)
            if self.games_played % 1000 == 0:
                print("Games played: %i" % self.games_played)
        self.agent.train_time = time.perf_counter() - train_time
        # save final agent
        self.agent.save(self.path)
        print(f"The agent won {self.agent.num_wins} times")
        print(f"The agent lost {self.agent.num_losses} times")
        print(f"The agent drew {self.agent.num_draws} times")

    def runDiag(self, is_rand):
        self.agent.save(self.path)
        i = 0
        self.agent.num_wins, self.agent.num_losses, self.agent.num_draws = (0 for i in range(3))
        self.agent.eps = 0
        test_teacher = Teacher(0) if is_rand else Teacher(1.0)
        while i < 100:
            game = Game(self.agent, teacher=test_teacher)
            game.start()
            i += 1
        test_res = [self.agent.num_wins, self.agent.num_losses, self.agent.num_draws]
        with open(self.path, 'rb') as f:
            self.agent = pickle.load(f)
        if is_rand:
            self.agent.testing_results_rand[0].append(test_res[0])
            self.agent.testing_results_rand[1].append(test_res[1])
            self.agent.testing_results_rand[2].append(test_res[2])
        else:
            self.agent.testing_results_opt[0].append(test_res[0])
            self.agent.testing_results_opt[1].append(test_res[1])
            self.agent.testing_results_opt[2].append(test_res[2])

def initGame(args, override=False):
    # initialize game instance
    gl = GameLearning(args,overridecheck=override)
    print(args)

    # play or teach
    if args.teacher_episodes is not None:
        gl.beginTeaching(args.teacher_episodes)
    else:
        gl.beginPlaying()

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
    print(args)

    initGame(args)