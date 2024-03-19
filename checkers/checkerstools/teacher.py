import random
import copy
import pickle
import os
import time
import math
from functools import reduce 

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


class Alpha_beta(Teacher):
    """
    A class representing a checkers playing AI using Alpha-Beta pruning.   
    
    TO DO:
    1) Be able to take in any reward function (for when not win/loss) 
    so that you can make a more robust set of training AI
    """
    
    def __init__(self, level=0.0, player_id=True, depth=2, the_board=None):
        """
        Initialize the instance variables to be stored by the AI. 
        """
        self.board = the_board
        self.depth = depth
        self.player_id = player_id
        self.level = level
        self.moves_dict = {}
        self.board_key = None
        self.tested_states = 0
        self.teach_time =  time.perf_counter()
        self.agent_id = ""
        self.p_tokens = []
        self.dimensions = []
        self.draw_counter = 0

    def new_board(self, board, board_key):
        """
        Sets the Board object which is known by the AI.
        """
        self.board = board
        self.p_tokens = [board.P1, board.P1_K, board.P2, board.P2_K, board.EMPTY_SPOT]
        self.dimensions = [board.HEIGHT, board.WIDTH]
        self.board_key = board_key
        self.draw_counter = board.draw_counter

    def save_moves_dict(self, filename = None):
        while True:
            try:
                # Store data (serialize)
                if filename is None:
                    # Syncs the moves_dict with the file
                    if os.path.isfile(f'checkers_table{self.depth}.pkl'):
                        with open(f'checkers_table{self.depth}.pkl', 'rb') as handle:
                                self.moves_dict.update(pickle.load(handle))
                    # Save the new combined moves_dict
#                    with open(f'{self.agent_id}teachinfo.txt', 'a') as f:
#                        f.write(f"\n\nSaving. Moves dictionary length: {len(self.moves_dict)}\n\n")
                    
                    with open(f'checkers_table{self.depth}.pkl', 'wb') as handle:
                        pickle.dump(self.moves_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
                else:
                    with open(filename, 'wb') as handle:
                        pickle.dump(self.moves_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
                break
            except pickle.UnpicklingError:
                print("Error saving moves dictionary")
            except EOFError:
                print("Error saving moves dictionary")
            

    
    def load_moves_dict(self, filename = None):
        while True:
            try:
                # Load data (deserialize)
                if filename is None:
                    if os.path.isfile(f'checkers_table{self.depth}.pkl'):
                        with open(f'checkers_table{self.depth}.pkl', 'rb') as handle:
                            self.moves_dict = pickle.load(handle)
                else:
                    if os.path.isfile(filename):
                        with open(filename, 'rb') as handle:
                            self.moves_dict = pickle.load(handle)
                break
            except pickle.UnpicklingError:
                print("Error loading moves dictionary")
            except EOFError:
                print("Error loading moves dictionary")

    def alpha_beta(self, board_key, depth, alpha, beta, maximizing_player):
        """
        A method implementing alpha-beta pruning to decide what move to make given 
        the current board configuration. 
        """
        # make new board
        board = Board(self.p_tokens, self.dimensions, board_key, self.draw_counter, maximizing_player)

        self.tested_states += 1
        if board_key in self.moves_dict:
            return self.moves_dict[board_key]

        if board.get_outcome() != 0:
            if board.get_number_of_pieces_and_kings(board.player_turn) == [0,0]:
                if maximizing_player:
                    #Using integers instead of float("inf") so it's less than float("inf") not equal to
                    return -10000000, None
                else:
                    return 10000000, None
            elif board.get_number_of_pieces_and_kings(not board.player_turn) == [0,0]:
                if maximizing_player:
                    return 1000000, None
                else:
                    return -1000000, None
            else:
                return 0, None

        if depth == 0:
            players_info = board.get_number_of_pieces_and_kings()
            if board.player_turn != maximizing_player:
                return (players_info[1] + 2 * players_info[3]) - (players_info[0] + 2 * players_info[2]), None
            return (players_info[0] + 2 * players_info[2]) - (players_info[1] + 2 * players_info[3]), None
        possible_moves = board.get_possible_next_moves()
        potential_spots = board.get_potential_spots_from_moves(possible_moves)

        # Tests to see if draw counter increases
        if len(potential_spots) == 1:
            test_key = board.get_state_key(potential_spots[0])
            if board_key.count('o') == test_key.count('o') and board_key.count('x') == test_key.count('x') and board_key.count('O') == test_key.count('O') and board_key.count('X') == test_key.count('X'):
                self.draw_counter += 1

        desired_move_index = None
        if maximizing_player:
            v = float('-inf')
            for j in range(len(potential_spots)):
                new_key = board.get_state_key(potential_spots[j])
                alpha_beta_results = self.alpha_beta(new_key, depth - 1, alpha, beta, False)
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
                new_key = board.get_state_key(potential_spots[j])
                alpha_beta_results = self.alpha_beta(new_key, depth - 1, alpha, beta, True)
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
        self.tested_states = 0
        self.teach_time =  time.perf_counter()

        possible_actions = self.board.get_possible_next_moves()

        # Chose randomly with some probability so that the teacher does not always win
        if random.random() > self.level:
            if possible_actions == []:
                return None
            else:
                return possible_actions[random.randint(0,len(possible_actions)-1)]
            
        # Does not test if there is only one possible action
        if len(possible_actions) == 1:
            return possible_actions[0]
            
        # If the board configuration has not been seen before, use alpha-beta to decide the next move
        if self.board_key not in self.moves_dict:
#            with open(f'{self.agent_id}teachinfo.txt', 'a') as f:
#                f.write(f"Beginning teaching time: {time.perf_counter()-self.teach_time}.\n")
            alpha_beta_results = self.alpha_beta(self.board_key, self.depth, float('-inf'), float('inf'), self.player_id)
#            with open(f'{self.agent_id}teachinfo.txt', 'a') as f:
#                f.write(f"Found teaching time: {time.perf_counter()-self.teach_time}.\n")
            self.moves_dict[self.board_key] = alpha_beta_results
            selected_move = alpha_beta_results[1]
            
        else:
#            with open(f'{self.agent_id}teachinfo.txt', 'a') as f:
#                f.write(f"Begin find teaching time: {self.teach_time-time.perf_counter()}.\n")
            selected_move = self.moves_dict[self.board_key][1]
        self.teach_time = time.perf_counter() - self.teach_time
#        with open(f'{self.agent_id}teachinfo.txt', 'a') as f:
#            f.write(f"Teacher returning move {selected_move} for board ({self.board_key})\n")
#            f.write(f"Total teaching time: {self.teach_time}. Tested states: {self.tested_states}\n\n")
        
        return selected_move
 

class Board:
    """
    Creates a lightweight board object to be used by the teacher.
    """
    def __init__(self, player_tokens, dimensions, board_key, draw_counter, player_turn):
        self.player_tokens = player_tokens
        self.dimensions = dimensions
        self.P1 = player_tokens[0]
        self.P1_K = player_tokens[1]
        self.P2 = player_tokens[2]
        self.P2_K = player_tokens[3]
        self.EMPTY_SPOT = player_tokens[4]
        self.HEIGHT = dimensions[0]
        self.WIDTH = dimensions[1]
        self.BACKWARDS_PLAYER = self.P2
        self.board_key = board_key
        self.spots = self.get_spots(board_key)
        self.player_turn = player_turn
        self.draw_counter = draw_counter


    def get_symbol(self, board_spots, location):
        """
        Gets the symbol for what should be at a board location.
        """
        if board_spots[location[0]][location[1]] == self.EMPTY_SPOT:
            return " "
        elif board_spots[location[0]][location[1]] == self.P1:
            return "o"
        elif board_spots[location[0]][location[1]] == self.P2:
            return "x"
        elif board_spots[location[0]][location[1]] == self.P1_K:
            return "O"
        else:
            return "X"
        
    def reverse_symbol(self, symbol):
        """
        Gets the symbol for what should be at a board location.
        """
        if symbol == " ":
            return self.EMPTY_SPOT
        elif symbol == "o":
            return self.P1
        elif symbol == "x":
            return self.P2
        elif symbol == "O":
            return self.P1_K
        else:
            return self.P2_K
    
    def get_state_key(self, spots):
        """
        Gets a string representation of the current game board.
        """
        answer = ""
        for j in range(self.HEIGHT):
            for i in range(self.WIDTH):
                answer += self.get_symbol(spots, [j, i])
        return answer
    
    def get_spots(self, board_key):
        """
        Gets the board spots from a given board_key.
        """
        answer = []
        for j in range(self.HEIGHT):
            answer.append([])
            for i in range(self.WIDTH):
                answer[j].append(self.reverse_symbol(board_key[j * self.WIDTH + i]))
        return answer

    def get_outcome(self):
        """
        Gets the outcome of the game currently being played.
        0: Game is still going
        1: Player 1 wins
        2: Player 2 wins
        3: Game is a tie (NOT IMPLEMENTED IN MINMAX YET)
        """
        piece_counter = self.get_number_of_pieces_and_kings()
        if piece_counter[0] != 0 or piece_counter[2] != 0:
            if piece_counter[1] != 0 or piece_counter[3] != 0:
                return 0
            return 1
        return 2


    def is_game_over(self):
        """
        Finds out and returns weather the game currently being played is over or
        not.
        """
        if not self.get_possible_next_moves():
            return True
        return False


    def get_number_of_pieces_and_kings(self, player_id=None):
        """
        Gets the number of pieces and the number of kings that each player has on the current 
        board configuration represented in the given spots. The format of the function with defaults is:
        [P1_pieces, P2_pieces, P1_kings, P2_kings]
        and if given a player_id:
        [player_pieces, player_kings]
        """
        piece_counter = [0,0,0,0]  
        for row in self.spots:
            for element in row:
                if element != 0:
                    piece_counter[element-1] = piece_counter[element-1] + 1
        if player_id is not None:
            if player_id == True:
                return [piece_counter[0], piece_counter[2]]
            return [piece_counter[1], piece_counter[3]]
        
        return piece_counter
    

    def not_spot(self, loc):
        """
        Finds out of the spot at the given location is an actual spot on the game board.
        """
        if len(loc) == 0 or loc[0] < 0 or loc[0] > self.HEIGHT - 1 or loc[1] < 0 or loc[1] > self.WIDTH - 1:
            return True
        return False
    
    
    def get_spot_info(self, loc):
        """
        Gets the information about the spot at the given location.
        
        NOTE:
        Might want to not use this for the sake of computational time.
        """
        return self.spots[loc[0]][loc[1]]
    
    
    def forward_n_locations(self, start_loc, n, backwards=False):
        """
        Gets the locations possible for moving a piece from a given location diagonally
        forward (or backwards if wanted) a given number of times(without directional change midway).  
        """
        if n % 2 == 0:
            temp1 = 0
            temp2 = 0
        elif start_loc[0] % 2 == 0:
            temp1 = 0
            temp2 = 1 
        else:
            temp1 = 1
            temp2 = 0

        answer = [[start_loc[0], start_loc[1] + math.floor(n / 2) + temp1], [start_loc[0], start_loc[1] - math.floor(n / 2) - temp2]]

        if backwards: 
            answer[0][0] = answer[0][0] - n
            answer[1][0] = answer[1][0] - n
        else:
            answer[0][0] = answer[0][0] + n
            answer[1][0] = answer[1][0] + n

        if self.not_spot(answer[0]):
            answer[0] = []
        if self.not_spot(answer[1]):
            answer[1] = []
            
        return answer
    

    def get_simple_moves(self, start_loc):
        """    
        Gets the possible moves a piece can make given that it does not capture any opponents pieces.
        
        PRE-CONDITION:
        -start_loc is a location with a players piece
        """
        if self.spots[start_loc[0]][start_loc[1]] > 2:
            next_locations = self.forward_n_locations(start_loc, 1)
            next_locations.extend(self.forward_n_locations(start_loc, 1, True))
        elif self.spots[start_loc[0]][start_loc[1]] == self.BACKWARDS_PLAYER:
            next_locations = self.forward_n_locations(start_loc, 1, True)  # Switched the true from the statement below
        else:
            next_locations = self.forward_n_locations(start_loc, 1)
        

        possible_next_locations = []

        for location in next_locations:
            if len(location) != 0:
                if self.spots[location[0]][location[1]] == self.EMPTY_SPOT:
                    possible_next_locations.append(location)
            
        return [[start_loc, end_spot] for end_spot in possible_next_locations]      
           
     
    def get_capture_moves(self, start_loc, move_beginnings=None):
        """
        Recursively get all of the possible moves for a piece which involve capturing an opponent's piece.
        """
        if move_beginnings is None:
            move_beginnings = [start_loc]
            
        answer = []
        if self.spots[start_loc[0]][start_loc[1]] > 2:  
            next1 = self.forward_n_locations(start_loc, 1)
            next2 = self.forward_n_locations(start_loc, 2)
            next1.extend(self.forward_n_locations(start_loc, 1, True))
            next2.extend(self.forward_n_locations(start_loc, 2, True))
        elif self.spots[start_loc[0]][start_loc[1]] == self.BACKWARDS_PLAYER:
            next1 = self.forward_n_locations(start_loc, 1, True)
            next2 = self.forward_n_locations(start_loc, 2, True)
        else:
            next1 = self.forward_n_locations(start_loc, 1)
            next2 = self.forward_n_locations(start_loc, 2)
        
        
        for j in range(len(next1)):
            if (not self.not_spot(next2[j])) and (not self.not_spot(next1[j])) :  # if both spots exist
                if self.get_spot_info(next1[j]) != self.EMPTY_SPOT and self.get_spot_info(next1[j]) % 2 != self.get_spot_info(start_loc) % 2:  # if next spot is opponent
                    if self.get_spot_info(next2[j]) == self.EMPTY_SPOT:  # if next next spot is empty
                        temp_move1 = copy.deepcopy(move_beginnings)
                        temp_move1.append(next2[j])
                        
                        answer_length = len(answer)
                        
                        if self.get_spot_info(start_loc) != self.P1 or next2[j][0] != self.HEIGHT - 1: 
                            if self.get_spot_info(start_loc) != self.P2 or next2[j][0] != 0: 

                                temp_move2 = [start_loc, next2[j]]
                                temp_board = Board(self.player_tokens, self.dimensions, copy.deepcopy(self.board_key), self.draw_counter, self.player_turn)
                                temp_board.make_move(temp_move2, False)

                                answer.extend(temp_board.get_capture_moves(temp_move2[1], temp_move1))
                                
                        if len(answer) == answer_length:
                            answer.append(temp_move1)
                            
        return answer
    
        
    def get_possible_next_moves(self):
        """
        Gets the possible moves that can be made from the current board configuration.
        """
        piece_locations = []
        for j in range(self.HEIGHT):
            for i in range(self.WIDTH):
                if (self.player_turn == False and (self.spots[j][i] == self.P2 or self.spots[j][i] == self.P2_K)) or (self.player_turn == True and (self.spots[j][i] == self.P1 or self.spots[j][i] == self.P1_K)):
                    piece_locations.append([j, i])
        try:  #Should check to make sure if this try statement is still necessary 
            capture_moves = list(reduce(lambda a, b: a + b, list(map(self.get_capture_moves, piece_locations))))  # CHECK IF OUTER LIST IS NECESSARY

            if len(capture_moves) != 0:
                for x in capture_moves:
                    x = tuple([tuple(x[0]), tuple(x[1])])
                return capture_moves

            
            basic_moves = list(reduce(lambda a, b: a + b, list(map(self.get_simple_moves, piece_locations))))  # CHECK IF OUTER LIST IS NECESSARY
            for x in basic_moves:
                x = tuple([tuple(x[0]), tuple(x[1])])
            return basic_moves
        except TypeError:
            return []
    

    def get_potential_spots_from_moves(self, moves):
        """
        Get's the potential spots for the board if it makes any of the given moves.
        If moves is None then returns it's own current spots.
        """
        if moves is None:
            return self.spots
        answer = []
        for move in moves:
            original_spots = copy.deepcopy(self.spots)
            self.make_move(move, switch_player_turn=False)
            answer.append(self.spots) 
            self.spots = original_spots 
        return answer
        
        
    def make_move(self, move, switch_player_turn=True):
        """
        Makes a given move on the board, and (as long as is wanted) switches the indicator for
        which players turn it is.
        """
        if abs(move[0][0] - move[1][0]) == 2:
            for j in range(len(move) - 1):
                if move[j][0] % 2 == 1:
                    if move[j + 1][1] < move[j][1]:
                        middle_y = move[j][1]
                    else:
                        middle_y = move[j + 1][1]
                else:
                    if move[j + 1][1] < move[j][1]:
                        middle_y = move[j + 1][1]
                    else:
                        middle_y = move[j][1]
                        
                self.spots[int((move[j][0] + move[j + 1][0]) / 2)][middle_y] = self.EMPTY_SPOT
                
                
        self.spots[move[len(move) - 1][0]][move[len(move) - 1][1]] = self.spots[move[0][0]][move[0][1]]
        if move[len(move) - 1][0] == self.HEIGHT - 1 and self.spots[move[len(move) - 1][0]][move[len(move) - 1][1]] == self.P1:
            self.spots[move[len(move) - 1][0]][move[len(move) - 1][1]] = self.P1_K
        elif move[len(move) - 1][0] == 0 and self.spots[move[len(move) - 1][0]][move[len(move) - 1][1]] == self.P2:
            self.spots[move[len(move) - 1][0]][move[len(move) - 1][1]] = self.P2_K
        else:
            self.spots[move[len(move) - 1][0]][move[len(move) - 1][1]] = self.spots[move[0][0]][move[0][1]]
        self.spots[move[0][0]][move[0][1]] = self.EMPTY_SPOT
                
        if switch_player_turn:
            self.player_turn = not self.player_turn