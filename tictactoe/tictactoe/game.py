import random

class Game:
    """ The game class. New instance created for each new game. """
    def __init__(self, agent, teacher=None):
        self.agent = agent
        self.teacher = teacher
        # initialize the game board
        self.board = [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']]
        self.gui = None
        self.play_again = None

    def set_GUI(self, gui):
        self.gui = gui

    def playerMove(self, first_move=False):
        """
        Query player for a move and update the board accordingly.
        """
        if self.teacher is not None:
            if first_move:
                save_level = self.teacher.ability_level
                self.teacher.ability_level = 0
                action = self.teacher.makeMove(self.board)
                self.board[action[0]][action[1]] = 'X'
                self.teacher.ability_level = save_level
            else:
                action = self.teacher.makeMove(self.board)
                self.board[action[0]][action[1]] = 'X'
        else:
            self.gui.update_board(self.board)
            while True:
                move = self.gui.get_move()
                try:
                    row, col = int(move[0]), int(move[1])
                except TypeError:
                    continue
                if row not in range(3) or col not in range(3) or not self.board[row][col] == '-':
                    self.gui.display_error("INVALID MOVE! Choose again.")
                    continue
                self.board[row][col] = 'X'
                self.gui.reset_move()
                self.gui.update_board(self.board)
                break
        
    def agentMove(self, action):
        """
        Update board according to agent's move.
        """
        self.board[action[0]][action[1]] = 'O'
        self.gui.update_board(self.board)

    def checkForWin(self, key):
        """
        Check to see whether the player/agent with token 'key' has won.
        Returns a boolean holding truth value.

        Parameters
        ----------
        key : string
            token of most recent player. Either 'O' or 'X'
        """
        # check for player win on diagonals
        a = [self.board[0][0], self.board[1][1], self.board[2][2]]
        b = [self.board[0][2], self.board[1][1], self.board[2][0]]
        if a.count(key) == 3 or b.count(key) == 3:
            return True
        # check for player win on rows/columns
        for i in range(3):
            col = [self.board[0][i], self.board[1][i], self.board[2][i]]
            row = [self.board[i][0], self.board[i][1], self.board[i][2]]
            if col.count(key) == 3 or row.count(key) == 3:
                return True
        return False

    def checkForDraw(self):
        """
        Check to see whether the game has ended in a draw. Returns a
        boolean holding truth value.
        """
        draw = True
        for row in self.board:
            for elt in row:
                if elt == '-':
                    draw = False
        return draw

    def checkForEnd(self, key):
        """
        Checks if player/agent with token 'key' has ended the game. Returns -1
        if the game is still going, 0 if it is a draw, and 1 if the player/agent
        has won.

        Parameters
        ----------
        key : string
            token of most recent player. Either 'O' or 'X'
        """
        if self.checkForWin(key):
            if self.teacher is None:
                if key == 'X':
                    self.play_again = self.gui.display_winner("win")
                else:
                    self.play_again = self.gui.display_winner("lose")
            return 1
        elif self.checkForDraw():
            if self.teacher is None:
                self.play_again = self.gui.display_winner("draw")
            return 0
        return -1

    def playGame(self, player_first):
        """ 
        Begin the tic-tac-toe game loop. 

        Parameters
        ----------
        player_first : boolean
            Whether or not the player will move first. If False, the
            agent goes first.

        """
        # Initialize the agent's state and action
        if player_first:
            self.playerMove(first_move=True)
        self.agent.ep_init()
        prev_state = getStateKey(self.board)
        prev_action = self.agent.get_action(prev_state)

        # iterate until game is over
        while True:
            # execute oldAction, observe reward and state
            self.agentMove(prev_action)
            check = self.checkForEnd('O')
            if not check == -1:
                # game is over. +1 reward if win, 0 if draw
                reward = check
                self.agent.update_count("win" if reward == 1 else "draw")
                break
            self.playerMove()
            check = self.checkForEnd('X')
            if not check == -1:
                # game is over. -1 reward if lose, 0 if draw
                reward = -1*check
                self.agent.update_count("loss" if reward == -1 else "draw")
                break
            else:
                # game continues. 0 reward
                reward = 0
            new_state = getStateKey(self.board)

            # determine new action (epsilon-greedy)
            new_action = self.agent.get_action(new_state)
            # update Q-values
            self.agent.update(prev_state, new_state, prev_action, new_action, reward)
            # reset "previous" values
            prev_state = new_state
            prev_action = new_action

        # Game over. Perform final update
        self.agent.update(prev_state, None, prev_action, None, reward)
        self.agent.end_update()

    def start(self):
        """
        Function to determine who moves first, and subsequently, start the game.
        If a teacher is employed, first mover is selected at random.
        If a human is playing, the human is asked whether he/she would
        like to move fist. 
        """
        if self.teacher is not None:
            # During teaching, chose who goes first randomly with equal probability
            if random.random() < 0.5:
                self.playGame(player_first=False)
            else:
                self.playGame(player_first=True)
        else:
            while True:
                response = self.gui.ask_go_first()
                print('')
                if response == 'n' or response == 'no':
                    self.playGame(player_first=False)
                    break
                elif response == 'y' or response == 'yes':
                    self.playGame(player_first=True)
                    break
                else:
                    print("Invalid input. Please enter 'y' or 'n'.")

def printBoard(board):
    """
    Prints the game board as text output to the terminal.

    Parameters
    ----------
    board : list of lists
        the current game board
    """
    print('    0   1   2\n')
    for i, row in enumerate(board):
        print('%i   ' % i, end='')
        for elt in row:
            print('%s   ' % elt, end='')
        print('\n')

def writeBoard(board,key):
    """
    Prints the game board as text output to a file.

    Parameters
    ----------
    board : list of lists
        the current game board
    key : string
        token of most recent player. Either 'O' or 'X'
    """
    with open('outputboard.txt', 'a') as f:
        f.write(f'{key} Wins\n')
        f.write('    0   1   2\n')
        for i, row in enumerate(board):
            f.write('%i   ' % i)
            for elt in row:
                f.write('%s   ' % elt)
            f.write('\n')
        f.write('\n')
        f.write('\n')    

def getStateKey(board):
    """
    Converts 2D list representing the board state into a string key
    for that state. Keys are used for Q-value hashing.

    Parameters
    ----------
    board : list of lists
        the current game board
    """
    key = ''
    for row in board:
        for elt in row:
            key += elt
    return key




