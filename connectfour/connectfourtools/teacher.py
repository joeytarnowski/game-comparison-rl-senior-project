import random
from copy import deepcopy
import collections
import os
import pickle


class Teacher:
    """ 
    A class to implement a teacher that knows the optimal playing strategy via MinMax.
    Teacher returns the best move at any time given the current state of the game.


    Parameters
    ----------
    level : float 
        teacher ability level. This is a value between 0-1 that indicates the
        probability of making the optimal move at any given time.
    """

    def __init__(self, level=1, depth=5):
        """
        Ability level determines the probability that the teacher will follow
        the optimal strategy as opposed to choosing a random available move.
        """
        self.ability_level = level
        self.WIDTH = 7
        self.HEIGHT = 6
        self.EMPTY_SPOT = 0
        self.P1 = 1
        self.P2 = 2
        self.depth = depth
        self.num_calc = 0
        self.saved_moves = {}

    def save_moves(self):
        with open("minimax_table.pkl", "wb") as f:
            pickle.dump(self.saved_moves, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    def load_moves(self):
        if os.path.isfile("minimax_table.pkl"):
            with open("minimax_table.pkl", "rb") as f:
                self.saved_moves = pickle.load(f)

    def get_outcome(self, spots):
        """
        Gets the outcome of the game currently being played.
        0: Game is still going
        1: Player 1 wins
        2: Player 2 wins
        3: Game is a tie
        """
        
        # Test for vertical wins
        for x in range(self.WIDTH):
            for y in range(self.HEIGHT - 3):
                test_spots = [spots[x][y+1], spots[x][y+2], spots[x][y+3]]
                if spots[x][y] == test_spots[0] == test_spots[1] == test_spots[2] and spots[x][y] != self.EMPTY_SPOT:
                    return 1 if spots[x][y] == self.P1 else 2
                
        # Test for horizontal wins
        for x in range(self.WIDTH - 3):
            for y in range(self.HEIGHT):
                test_spots = [spots[x+1][y], spots[x+2][y], spots[x+3][y]]
                if spots[x][y] == test_spots[0] == test_spots[1] == test_spots[2] and spots[x][y] != self.EMPTY_SPOT:
                        return 1 if spots[x][y] == self.P1 else 2
                
        # Test for diagonal wins
        for x in range(self.WIDTH - 3):
            for y in range(self.HEIGHT):
                if y < 3:
                    test_spots = [spots[x+1][y+1], spots[x+2][y+2], spots[x+3][y+3]]
                    if spots[x][y] == test_spots[0] == test_spots[1] == test_spots[2] and spots[x][y] != self.EMPTY_SPOT:
                        return 1 if spots[x][y] == self.P1 else 2
                else:
                    test_spots = [spots[x+1][y-1], spots[x+2][y-2], spots[x+3][y-3]]
                    if spots[x][y] == test_spots[0] == test_spots[1] == test_spots[2] and spots[x][y] != self.EMPTY_SPOT:
                        return 1 if spots[x][y] == self.P1 else 2
        
        # Test for draw
        for x in range(self.WIDTH):
            if self.EMPTY_SPOT in spots[x]:
                return 0
        return 3

    def calc_reward(self, spots):
        """
        Calculates the reward for a given board by finding the longest unblocked sequence 
        of one player's pieces minus the longest unblocked sequence of the other player's pieces.
        """
        value = 0
        # Test for vertical sequences
        for x in range(self.WIDTH):
            for y in range(self.HEIGHT - 3):
                test_spots = [spots[x][y+1], spots[x][y+2], spots[x][y+3]]
                # Test for 3 in a row
                if (spots[x][y] == test_spots[0] == test_spots[1]) and (test_spots[2] == self.EMPTY_SPOT) and (spots[x][y] != self.EMPTY_SPOT):
                    value = value+3 if spots[x][y] == self.P1 else value-3
                # Test for 2 in a row
                elif (spots[x][y] == test_spots[0]) and (test_spots[1] == self.EMPTY_SPOT) and (spots[x][y] != self.EMPTY_SPOT):
                    value = value+2 if spots[x][y] == self.P1 else value-2
        # Test for horizontal sequences
        for x in range(self.WIDTH - 3):
            for y in range(self.HEIGHT):
                test_spots = [spots[x][y], spots[x+1][y], spots[x+2][y], spots[x+3][y]]
                # Test for 3 in complete or incomplete open row
                counter = collections.Counter(test_spots)
                if 3 in counter.values() and test_spots.count(self.EMPTY_SPOT) == 1:
                    value = value+3 if test_spots.count(self.P1) > 1 else value-3
                    break
                # Test for 2 in a row
                elif (spots[x][y] == test_spots[0]) and (test_spots[1] == self.EMPTY_SPOT) and (spots[x][y] != self.EMPTY_SPOT):
                    value = value+2 if spots[x][y] == self.P1 else value-2
        # Test for diagonal sequences
        for x in range(self.WIDTH - 3):
            for y in range(self.HEIGHT):
                if y < 3:
                    test_spots = [spots[x][y], spots[x+1][y+1], spots[x+2][y+2], spots[x+3][y+3]]
                    # Test for 3 in complete or incomplete open row
                    counter = collections.Counter(test_spots)
                    if 3 in counter.values() and test_spots.count(self.EMPTY_SPOT) == 1:
                        value = value+3 if test_spots.count(self.P1) > 1 else value-3
                    # Test for 2 in a row
                    elif (spots[x][y] == test_spots[0]) and (test_spots[1] == test_spots[2] == self.EMPTY_SPOT) and (spots[x][y] != self.EMPTY_SPOT):
                        value = value+2 if spots[x][y] == self.P1 else value-2
                else:
                    test_spots = [spots[x][y], spots[x+1][y-1], spots[x+2][y-2], spots[x+3][y-3]]
                    # Test for 3 in a row
                    if 3 in counter.values() and test_spots.count(self.EMPTY_SPOT) == 1:
                        value = value+3 if test_spots.count(self.P1) > 1 else value-3
                    # Test for 2 in a row
                    elif (test_spots[1] == test_spots[2]) and (spots[x][y] == test_spots[0] == self.EMPTY_SPOT) and (test_spots[2] != self.EMPTY_SPOT):
                        value = value+2 if test_spots[2] == self.P1 else value-2
        return value

    def minimax(self, current_board, depth, is_maxim, alpha, beta):
        self.num_calc += 1
        board = current_board
        # Depth is added to calculation to ensure teacher chooses the fastest win
        outcome = self.get_outcome(board)
        if outcome == 1:
            return 1000 - depth
        elif outcome == 2:
            return -1000 + depth
        elif outcome == 3:
            return 0
        
        if depth == self.depth:
            return self.calc_reward(board)
        
        # Maximizer
        if (is_maxim) : 
            v = float('-inf')
            possibles = self.get_possible_next_moves(board)
            for i in possibles:
                change_coord = self.change_board(i, board)
                board[change_coord[0]][change_coord[1]] = 1
                result = self.minimax(board, depth + 1, not is_maxim, alpha, beta)
                if v < result:
                    v = result
                    alpha = max(alpha, v)
                board[change_coord[0]][change_coord[1]] = self.EMPTY_SPOT
                if beta <= alpha:
                    break

            return v

        # Minimizer
        else:
            v = float('inf')
            possibles = self.get_possible_next_moves(board)
            for i in possibles:
                change_coord = self.change_board(i, board)
                board[change_coord[0]][change_coord[1]] = 2
                result = self.minimax(board, depth + 1, not is_maxim, alpha, beta)
                if v > result:
                    v = result
                    beta = min(beta, v)
                board[change_coord[0]][change_coord[1]] = self.EMPTY_SPOT
                if beta <= alpha:
                    break

            return v
        
    def translate_board(self, board_key):
        """
        Translates the board key into a format that can be used by the minimax function.
        """
        board_key = str(board_key)
        if len(board_key) < (self.HEIGHT * self.WIDTH):
            for j in range(self.WIDTH*self.HEIGHT - len(board_key)):
                board_key = f"0{board_key}"
        spots = [[] for j in range(self.WIDTH)]
        for j in range(self.WIDTH):
            for i in range(self.HEIGHT):
                spots[j].append(int(board_key[j * self.HEIGHT + i]))
        return spots
    
    def change_board(self, move, board):
        """
        Makes a given move on the board, and (as long as is wanted) switches the indicator for
        which players turn it is.
        """

        coordinate = []
        for i in range(self.HEIGHT):
            if board[move][i] == self.EMPTY_SPOT:
                coordinate = [move, i]
                break
        
        return coordinate

    def get_possible_next_moves(self, board):
        """
        Gets the possible moves that can be made from the current board configuration.
        """
        possible_moves = []
        for i in range(self.WIDTH):
            if board[i][self.HEIGHT - 1] == self.EMPTY_SPOT:
                possible_moves.append(i)
        return possible_moves
    
    def random_move(self, board):
        """ Chose a random move from the available options. """
        possibles = self.get_possible_next_moves(board)
        return possibles[random.randint(0, len(possibles)-1)]

    def mirror_key(self, board_key):
        """
        Gets a string representation of the current game board mirrored.
        """
        board = self.translate_board(board_key)
        mirror_key = 0
        for x in range(self.WIDTH - 1, -1, -1):
            for y in range(self.HEIGHT):
                mirror_key += board[x][y]
                mirror_key *= 10
        mirror_key = mirror_key // 10
        return mirror_key

    def make_move_key(self, board_key):
        board = self.translate_board(board_key)

        # Chose randomly with some probability so that the teacher does not always win
        if random.random() > self.ability_level:
            return self.random_move(board)
        
        if self.mirror_key(board_key) in self.saved_moves:
            return (self.WIDTH - 1) - self.saved_moves[self.mirror_key(board_key)]
        
        if board_key not in self.saved_moves:
            self.saved_moves[board_key] = self.make_move(board)
        
        

        return self.saved_moves[board_key]
    
    def make_move(self, board):
        self.num_calc = 0
        # Reset values
        self.moves_dict = {}

        # Follow optimal strategy
        possibles = self.get_possible_next_moves(board)
        # Record all move values in dictionary
        for i in possibles:
            result = self.start_minimax(i, board)
            self.moves_dict[result[0]] = result[1]

        # Get the best move and if there are multiple best moves, chose randomly
        max_val = max(self.moves_dict.values())
        opt_moves = {k:v for k, v in self.moves_dict.items() if v == max_val}
        best_move = list(opt_moves.keys())[random.randint(0, len(opt_moves)-1)]

        return best_move

    def start_minimax(self, i, board):
        board = deepcopy(board)
        change_coord = self.change_board(i, board)
        board[change_coord[0]][change_coord[1]] = self.P1
        move_val = self.minimax(board, 0, False, -100000, 100000)
        board[change_coord[0]][change_coord[1]] = self.EMPTY_SPOT
        return [i, move_val]
    


        