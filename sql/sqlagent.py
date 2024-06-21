import numpy as np
import copy
import math
import mysql.connector
from mysql.connector import errorcode
from functools import reduce 

class Agent:
    def __init__(self, conn, id, game):
        # Possible actions correspond to the set of all x,y coordinate pairs
        self.actions = []
        for i in range(3):
            for j in range(3):
                self.actions.append((i,j))

        self.conn = conn
        self.id = id
        self.game = game


    def get_action(self, s):
        match self.game:
            case 't':
                return self.get_action_tictactoe(s)
            case 'ch':
                return self.get_action_checkers(s)
            case 'c4':
                return self.get_action_connect_four(s)
            case _:
                raise ValueError("Invalid game type.")
        
    def get_q_values(self, s):
        # Get QValues for board state
        try:
            self.conn.execute("SELECT action, value FROM QValue WHERE boardstate = %s AND agent_id = %s", (s, self.id))
            return self.conn.fetchall()
        except mysql.connector.Error as err:
            print("Error getting QValues:", err)
            return None
        
    def get_action_tictactoe(self, s):
        """
        Select an action given the current game state.

        Parameters
        ----------
        s : string
            boardstate
        """
        # Get QValues for board state
        q_values = self.get_q_values(s)
        
        # Find max QValue
        max_q = -math.inf
        for action, value in q_values:
            print(f"Action: {action}, Value: {value}")
            if value > max_q:
                max_q = value
                max_action = action
        try:
            return max_action
        except UnboundLocalError:
            # If no QValues exist, select a random action
            possible_actions = [a for a in self.actions if s[a[0]*3 + a[1]] == '-']
            print("No QValues found. Selecting random action.")
            return possible_actions[np.random.choice(len(possible_actions))]
        
    
    def get_action_connect_four(self, s):
        print("Getting action for Connect Four")
        # Get QValues for board state
        q_values = self.get_q_values(s)
        if q_values is None:
            print("No QValues found. Testing mirrored board.")
            # If no QValues exist, search mirrored board
            m_s = self.get_mirrored_key(s)
            q_values = self.get_q_values(m_s)
        # Find max QValue
        max_q = -math.inf
        for action, value in q_values:
            print(f"Action: {action}, Value: {value}")
            if value > max_q:
                max_q = value
                max_action = action
        try:
            return max_action
        except UnboundLocalError:
            # If no QValues exist, select a random action
            print("No QValues found. Selecting random action.")
            board = self.translate_board_c4(s)
            # Get possible actions
            possible_actions = self.get_possible_moves_c4(board)
            return possible_actions[np.random.choice(len(possible_actions))]
    
    def translate_board_c4(self, board_key):
        """
        Translates the board key into a format that can be used by the minimax function.
        """
        height = 6
        width = 7
        board_key = str(board_key)
        if len(board_key) < (height * width):
            for j in range(width*height - len(board_key)):
                board_key = f"0{board_key}"
        spots = [[] for j in range(width)]
        for j in range(width):
            for i in range(height):
                spots[j].append(int(board_key[j * height + i]))
        return spots
    
    def get_mirrored_key(self, board):
        height = 6
        width = 7
        
        # get mirrored key
        mirror_key = 0
        for x in range(width - 1, -1, -1):
            for y in range(height):
                mirror_key += board[x][y]
                mirror_key *= 10
