import argparse
import json
import os
import pickle
import mysql.connector
from mysql.connector import errorcode
from sqlagent import Agent

try:
    connect = mysql.connector.connect(
        user = 'root',
        password = '--------',
        host = 'localhost',
        database = 'GameRL',
        port = '3306'
    )
except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
             print('Invalid credentials')
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
             print('Database not found')
        else:
             print('Cannot connect to database:', err)

conn = connect.cursor()

class Game:
    def __init__(self, args):
        # set agent type
        match args.agent_type:
            case 'q':
                a_name = 'Q-Learning'
            case 'mcon':
                a_name = 'MC On-Policy'
            case 'mcoff':
                a_name = 'MC Off-Policy'
            case _:
                a_name = 'SARSA'
        # select based on game
        match args.game:
            case 't':
                game_id = 1
            case 'ch':
                game_id = 2
            case 'c4':
                game_id = 3
            case _:
                raise ValueError("Invalid game type. Please select 't', 'ch', or 'c4'.")
                
        # load the agent
        agent_id = self.get_agent_id(a_name, game_id)
        agent = Agent(conn, agent_id, args.game)

        # load the board state
        if args.boardstate:
            with open('boardstate.json', 'r') as f:
                boardstatefile = json.load(f)
                if args.game == 't':
                    boardstate = boardstatefile['boardstate'].upper()
                else:
                    boardstate = int(boardstatefile['boardstate'])
                print(boardstate)
    
        self.agent = agent
        self.boardstate = boardstate
    
    def find_move(self):
        """
        Function to find the best move for the computer agent.
        """
        # Get the best move from the agent
        action = self.agent.get_action(self.boardstate)
        return action
    
    def get_agent_id(self, agent_name, game_type):
        """
        Function to get the agent id based on the agent name and game type
        """
        conn.execute("SELECT id FROM Agent WHERE name = %s AND gametype_id = %s", (agent_name, game_type))
        agent_id = conn.fetchone()
        return agent_id[0]


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