import random
from copy import deepcopy


class MMTeacher:
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

    def __init__(self, level=1):
        """
        Ability level determines the probability that the teacher will follow
        the optimal strategy as opposed to choosing a random available move.
        """
        self.ability_level = level
        self.begin_board = []
        self.moves_dict = {}

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

    def draw(self, board):
        for i in range(3):
            for j in range(3):
                if board[i][j] == '-':
                    return False
        return True

    
    def minimax(self, current_board, depth, is_maxim, alpha, beta):
        board = current_board
        if self.win(board):
            return 10 - depth
        elif self.win(board, 'O'):
            return -10 + depth

        if self.draw(board):
            return 0
        
            # Maximizer
        if (is_maxim) :    
            best = -1000
            possibles = self.getMoves(board)
            for i in possibles:
                board[i[0]][i[1]] = "X"
                best = max(best, self.minimax(board, depth + 1, not is_maxim, alpha, beta))
                board[i[0]][i[1]] = "-"
                alpha = max(alpha, best)
                if beta < alpha:
                    break

            return best

        # Minimizer
        else:
            best = 1000
            possibles = self.getMoves(board)
            for i in possibles:
                board[i[0]][i[1]] = "O"
                best = min(best, self.minimax(board, depth + 1, not is_maxim, alpha, beta))
                board[i[0]][i[1]] = "-"
                beta = min(beta, best)
                if beta < alpha:
                    break

            return best

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

    def makeMove(self, current_board):
        # Reset values
        self.begin_board = current_board
        self.moves_dict = {}
        """
        Trainer goes through a hierarchy of moves, making the best move that
        is currently available each time. A touple is returned that represents
        (row, col).
        """
        # Chose randomly with some probability so that the teacher does not always win
        if random.random() > self.ability_level:
            return self.randomMove(current_board)
            
        # Follow optimal strategy

        possibles = self.getMoves(self.begin_board)
        # Record all move values in dictionary
        for i in possibles:
            result = self.startMinimax(i)
            self.moves_dict[result[0]] = result[1]
        best_move = max(zip(self.moves_dict.values(), self.moves_dict.keys()))[1]
        return best_move

    def startMinimax(self,i):
        board = deepcopy(self.begin_board)
        board[i[0]][i[1]] = "X"
        move_val = self.minimax(board, 0, False, 0, 0)
        board[i[0]][i[1]] = "-"
        return [(i[0],i[1]), move_val]
    


        