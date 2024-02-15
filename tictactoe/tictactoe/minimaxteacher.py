import random

class Teacher:
    """ 
    A class to implement a teacher that knows the optimal playing strategy.
    Teacher returns the best move at any time given the current state of the game.
    Note: things are a bit more hard-coded here, as this was not the main focus of
    the exercise so I did not spend as much time on design/style. Everything works
    properly when tested.

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
        self.minimax_log = 0

    def win(self, board, key='X'):
        """ If we have two in a row and the 3rd is available, take it. """
        # Check for diagonal wins
        a = [board[0][0], board[1][1], board[2][2]]
        b = [board[0][2], board[1][1], board[2][0]]
        if a.count(key) == 3 or b.count(key) == 3:
            return True
        # Now check for 2 in a row/column + empty 3rd
        for i in range(3):
            c = [board[0][i], board[1][i], board[2][i]]
            d = [board[i][0], board[i][1], board[i][2]]
            if c.count(key) == 3 or d.count(key) == 3:
                return True
        return False

    def minimax(self, board, depth, is_maxim):
        x = 0

    def randomMove(self, board):
        """ Chose a random move from the available options. """
        possibles = []
        for i in range(3):
            for j in range(3):
                if board[i][j] == '-':
                    possibles += [(i, j)]
        return possibles[random.randint(0, len(possibles)-1)]

    def makeMove(self, board):
        """
        Trainer goes through a hierarchy of moves, making the best move that
        is currently available each time. A touple is returned that represents
        (row, col).
        """
        # Chose randomly with some probability so that the teacher does not always win
        if random.random() > self.ability_level:
            return self.randomMove(board)
        # Follow optimal strategy
        