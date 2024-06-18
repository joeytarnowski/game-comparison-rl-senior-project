import argparse
import json
import os
import pickle
from agent import Agent

class Game:
    def __init__(self, args):
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
        # select based on game
        match args.game:
            case 't':
                args.path = f"tictactoe/{args.path}"
            case 'ch':
                args.path = f"checkers/{args.path}"
            case 'c4':
                args.path = f"connectfour/{args.path}"
            case _:
                raise ValueError("Invalid game type. Please select 't', 'ch', or 'c4'.")
                
        
        # load the agent
        agent = Agent(args.game)
        if not os.path.isfile(args.path):
            print("Current Working Directory:", os.getcwd())
            raise ValueError(f"Cannot load agent: file {args.path} does not exist.")
        with open(args.path, 'rb') as f:
            agent.Q = pickle.load(f)
            

        # load the board state
        if args.boardstate:
            with open('boardstate.json', 'r') as f:
                boardstatefile = json.load(f)
                if args.game == 't':
                    boardstate = boardstatefile['boardstate'].upper()
                else:
                    boardstate = int(boardstatefile['boardstate'])
                print(boardstate)
    
        self.path = args.path
        self.agent = agent
        self.boardstate = boardstate
    
    def find_move(self):
        """
        Function to find the best move for the computer agent.
        """
        # Get the best move from the agent
        action = self.agent.get_action(self.boardstate)
        return action


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
    parser.add_argument("-g", "--game", type=str, default="t",
                        choices=['t', 'ch', 'c4'],
                        help="Specify the game. GAME='t' for Tic-Tac-Toe, "
                             "GAME='ch' for Checkers, and GAME='c4' for "
                             "Connect Four.")
    parser.add_argument("-b", "--boardstate", type=str, default="boardstate.json",
                        help="file that contains board state")
    args = parser.parse_args()

    game = Game(args)
    print(game.find_move())