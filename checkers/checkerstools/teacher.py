'''
Created on Mar 12, 2024

@author: Sam Ragusa
'''

import random
import copy
import pickle
import os

class Teacher:
    """
    A class to be inherited by any class representing a checkers player.
    This is used so that other functions can be written for more general use,
    without worry of crashing (e.g. play_n_games).
    
    NOTES:
    1) Create set playerID method
    """
    
    def set_board(self, the_board):
        """
        Sets the Board object which is known by the AI.
        """
        self.board = the_board
    
    def game_completed(self):
        """
        Should be overridden if AI implementing this class should be notified 
        of when a game ends, before the board is wiped.
        """
        pass
    
    def get_next_move(self):
        """
        Gets the desired next move from the AI.
        """
        pass


def reward_function(state_info1, state_info2):
    """
    Reward for transitioning from state with state_info1 to state with state_info2.
    
    NOTE:
    1) do something better with where/how this is implemented
    2) should give some kind of negative for tieing
    """
    if state_info2[1] == 0 and state_info2[3] == 0:
        return 12
    if state_info2[0] == 0 and state_info2[2] == 0:
        return -12
    return state_info2[0]-state_info1[0] + 2*(state_info2[2]-state_info1[2])-(state_info2[1]-state_info1[1])-2*(state_info2[3]-state_info1[3])


def get_number_of_pieces_and_kings(spots, player_id=None):
    """
    Gets the number of pieces and the number of kings that each player has on the current 
    board configuration represented in the given spots. The format of the function with defaults is:
    [P1_pieces, P2_pieces, P1_kings, P2_kings]
    and if given a player_id:
    [player_pieces, player_kings]
    """
    piece_counter = [0,0,0,0]  
    for row in spots:
        for element in row:
            if element != 0:
                piece_counter[element-1] = piece_counter[element-1] + 1
    
    if player_id == True:
        return [piece_counter[0], piece_counter[2]]
    elif player_id == False:
        return [piece_counter[1], piece_counter[3]]
    else:
        return piece_counter
    

class Alpha_beta(Teacher):
    """
    A class representing a checkers playing AI using Alpha-Beta pruning.   
    
    TO DO:
    1) Be able to take in any reward function (for when not win/loss) 
    so that you can make a more robust set of training AI
    """
    
    def __init__(self, level=.9, the_player_id=True, the_depth=6, the_board=None):
        """
        Initialize the instance variables to be stored by the AI. 
        """
        self.board = the_board
        self.depth = the_depth
        self.player_id = the_player_id
        self.level = level
        self.moves_dict = {}
        self.board_key = None

    def save_moves_dict(self, filename = None):
        # Store data (serialize)
        if filename is None:
            with open('checkers_table.pkl', 'wb') as handle:
                pickle.dump(self.moves_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            with open(filename, 'wb') as handle:
                pickle.dump(self.moves_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    def load_moves_dict(self, filename = None):
        # Load data (deserialize)
        if filename is None:
            if os.path.isfile('checkers_table.pkl'):
                with open('checkers_table.pkl', 'rb') as handle:
                    self.moves_dict = pickle.load(handle)
        else:
            if os.path.isfile(filename):
                with open(filename, 'rb') as handle:
                    self.moves_dict = pickle.load(handle)

    def alpha_beta(self, board, depth, alpha, beta, maximizing_player):
        """
        A method implementing alpha-beta pruning to decide what move to make given 
        the current board configuration. 
        """
        if board.is_game_over():
            if get_number_of_pieces_and_kings(board.spots, board.player_turn) == [0,0]:
                if maximizing_player:
                    #Using integers instead of float("inf") so it's less than float("inf") not equal to
                    return -10000000, None
                else:
                    return 10000000, None
            elif get_number_of_pieces_and_kings(board.spots, not board.player_turn) == [0,0]:
                if maximizing_player:
                    return 1000000, None
                else:
                    return -1000000, None
            else:
                return 0, None

        if depth == 0:
            players_info = get_number_of_pieces_and_kings(board.spots)
            if board.player_turn != maximizing_player:
                return  players_info[1] + 2 * players_info[3] - (players_info[0] + 2 * players_info[2]), None
            return  players_info[0] + 2 * players_info[2] - (players_info[1] + 2 * players_info[3]), None
        possible_moves = board.get_possible_next_moves()

        potential_spots = board.get_potential_spots_from_moves(possible_moves)
        desired_move_index = None
        if maximizing_player:
            v = float('-inf')
            for j in range(len(potential_spots)):
                cur_board = copy.deepcopy(board)
                cur_board.old_spots = potential_spots[j]
                cur_board.player_turn = not board.player_turn
                alpha_beta_results = self.alpha_beta(cur_board, depth - 1, alpha, beta, False)
                if v < alpha_beta_results[0]: 
                    v = alpha_beta_results[0]
                    alpha = max(alpha, v)
                    desired_move_index = j
                if beta <= alpha: 
                    break
            if desired_move_index is None:
                return v, None
            
            return v, possible_moves[desired_move_index]
        else:
            v = float('inf')
            for j in range(len(potential_spots)):
                cur_board = copy.deepcopy(board)
                cur_board.old_spots = potential_spots[j]
                cur_board.player_turn = not board.player_turn
                alpha_beta_results = self.alpha_beta(cur_board, depth - 1, alpha, beta, True)
                if v > alpha_beta_results[0]:  
                    v = alpha_beta_results[0]
                    desired_move_index = j
                    beta = min(beta, v)
                if beta <= alpha:
                    break
            if desired_move_index is None:
                return v, None
            
            return v, possible_moves[desired_move_index]
    
    def get_next_move(self):
        self.board_key = self.get_state_key()

        # Chose randomly with some probability so that the teacher does not always win
        if random.random() > self.level:
            possible_actions = self.board.get_possible_next_moves()
            return possible_actions[random.randint(0,len(possible_actions)-1)]
        if self.board_key not in self.moves_dict:
            self.moves_dict[self.board_key] = self.alpha_beta(self.board, self.depth, float('-inf'), float('inf'), self.player_id)[1]
        return self.moves_dict[self.board_key]
 

    def get_symbol(self, location):
        """
        Gets the symbol for what should be at a board location.
        """
        if self.board.spots[location[0]][location[1]] == self.board.EMPTY_SPOT:
            return " "
        elif self.board.spots[location[0]][location[1]] == self.board.P1:
            return "o"
        elif self.board.spots[location[0]][location[1]] == self.board.P2:
            return "x"
        elif self.board.spots[location[0]][location[1]] == self.board.P1_K:
            return "O"
        else:
            return "X"
    
    
    def get_state_key(self):
        """
        Gets a string representation of the current game board.
        """
        answer = ""
        for j in range(self.board.HEIGHT):
            for i in range(self.board.WIDTH):
                answer += self.get_symbol([j, i])
        return answer