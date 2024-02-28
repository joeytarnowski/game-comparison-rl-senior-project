import random
import pickle

class Teacher:
    """ 
    A class to implement a teacher that knows the optimal playing strategy.
    Teacher returns the best move at any time given the current state of the game.
    Note: this is based off the MinMax algorithm in minimaxteacher.py - all potential
    board states are stored in minimax_table.pkl and the 9 character board key is used
    to look up the optimal move

    Parameters
    ----------
    level : float 
        teacher ability level. This is a value between 0-1 that indicates the
        probability of making the optimal move at any given time.
    """

    def __init__(self, level=0.9):
        """
        Ability level determines the probability that the teacher will follow
        the optimal strategy as opposed to choosing a random available move.
        """
        self.ability_level = level
        self.begin_board = []
        # Load data
        with open('minimax_table.pkl', 'rb') as handle:
            self.moves_dict = pickle.load(handle)

    def getMoves(self, board):
        possibles = []
        for i in range(3):
            for j in range(3):
                if board[i][j] == '-':
                    possibles += [(i, j)]
        return possibles
    
    def randomMove(self, board):
        """ Chose a random move from the available options. """
        possibles = self.getMoves(board)
        return possibles[random.randint(0, len(possibles)-1)]
    
    def makeKey(self, board):
        key = ""
        for subboard in board:
            for state in subboard:
                key += state
        return key

    def makeMove(self, current_board):
        """
        Trainer goes through a hierarchy of moves, making the best move that
        is currently available each time. A touple is returned that represents
        (row, col).
        """
        # Chose randomly with some probability so that the teacher does not always win
        if random.random() > self.ability_level:
            return self.randomMove(current_board)
        
            
        # Follow optimal strategy
        move_key = self.makeKey(current_board)
        best_move = self.moves_dict[move_key]
        return best_move

    