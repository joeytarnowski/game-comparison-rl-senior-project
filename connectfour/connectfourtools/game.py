"""
NOTES:
-Should store moves as a location x, representing the row to put new piece on,
since connect four's pieces always fall to the bottom of the board.
-0 is empty spot, 1 is p1, 2 is p2
-if self.player_turn == True then it is player 1's turn
-the player/teacher is always player 1
"""

import random

class Game:
    """
    A class to represent and play a 7x6 game of connect four.
    """
    EMPTY_SPOT = 0
    P1 = 1
    P2 = 2
    WIDTH = 7
    HEIGHT = 6
    
    
    def __init__(self, agent, teacher=None, old_spots=None, player_turn=True):
        """
        Initializes a new instance of the Game class.  Unless specified otherwise, 
        the board will be created with a start board configuration.
        """
        self.agent = agent
        self.teacher = teacher
        self.player_turn = player_turn
        self.spots = [[j, j, j, j, j, j] for j in [self.EMPTY_SPOT] * self.WIDTH]

    
    def empty_board(self):
        """
        Removes any pieces currently on the board and leaves the board with nothing but empty spots.
        """
        self.spots = [[j, j, j, j, j, j] for j in [self.EMPTY_SPOT] * self.WIDTH]  
    

    def get_outcome(self):
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
                test_spots = [self.spots[x][y+1], self.spots[x][y+2], self.spots[x][y+3]]
                if self.spots[x][y] == test_spots[0] == test_spots[1] == test_spots[2] and self.spots[x][y] != self.EMPTY_SPOT:
                    return 1 if self.spots[x][y] == self.P1 else 2
                
        # Test for horizontal wins
        for x in range(self.WIDTH - 3):
            for y in range(self.HEIGHT):
                test_spots = [self.spots[x+1][y], self.spots[x+2][y], self.spots[x+3][y]]
                if self.spots[x][y] == test_spots[0] == test_spots[1] == test_spots[2] and self.spots[x][y] != self.EMPTY_SPOT:
                        return 1 if self.spots[x][y] == self.P1 else 2
                
        # Test for diagonal wins
        for x in range(self.WIDTH - 3):
            for y in range(self.HEIGHT):
                if y < 3:
                    test_spots = [self.spots[x+1][y+1], self.spots[x+2][y+2], self.spots[x+3][y+3]]
                    if self.spots[x][y] == test_spots[0] == test_spots[1] == test_spots[2] and self.spots[x][y] != self.EMPTY_SPOT:
                        return 1 if self.spots[x][y] == self.P1 else 2
                else:
                    test_spots = [self.spots[x+1][y-1], self.spots[x+2][y-2], self.spots[x+3][y-3]]
                    if self.spots[x][y] == test_spots[0] == test_spots[1] == test_spots[2] and self.spots[x][y] != self.EMPTY_SPOT:
                        return 1 if self.spots[x][y] == self.P1 else 2
        
        # Test for draw
        for x in range(self.WIDTH):
            if self.EMPTY_SPOT in self.spots[x]:
                return 0
        return 3


    def get_possible_next_moves(self):
        """
        Gets the possible moves that can be made from the current board configuration.
        """
        possible_moves = []
        for i in range(self.WIDTH):
            if self.spots[i][self.HEIGHT - 1] == self.EMPTY_SPOT:
                possible_moves.append(i)
        return possible_moves
    
    
    def player_move(self, is_first=False):
        """
        Query player for a move and update the board accordingly.
        """
        if self.teacher is not None:
            save_level = self.teacher.ability_level
            if is_first:
                self.teacher.ability_level = 0
            key = self.get_state_key()
            self.make_move(self.teacher.make_move_key(key))
            self.teacher.ability_level = save_level
        else:
            self.print_board()
            move = -1
            possible_moves = self.get_possible_next_moves()
            
            while True:
                move_i = input("Your move! Please select the row you want to move: ")
                print('\n')
                if move_i.isdigit() and int(move_i - 1) in possible_moves:
                    move = int(move_i - 1)
                    break
                else:
                    print("Invalid input. Please enter a valid row number.")
            
            self.make_move(move, True)


    def agent_move(self, action):
        self.make_move(action, False)


    def make_move(self, move, is_player=True):
        """
        Makes a given move on the board, and (as long as is wanted) switches the indicator for
        which players turn it is.
        """
        if is_player:
            player = self.P1
        else:
            player = self.P2
        for i in range(self.HEIGHT):
            if self.spots[move][i] == self.EMPTY_SPOT:
                self.spots[move][i] = player
                break
        if is_player:
            self.player_turn = not self.player_turn

            
    def get_symbol(self, location):
        """
        Gets the symbol for what should be at a board location.
        """
        if self.spots[location[0]][location[1]] == self.P1:
            return "o"
        elif self.spots[location[0]][location[1]] == self.P2:
            return "x"
        else:
            return " "
    
    
    def get_state_key(self):
        """
        Gets a string representation of the current game board.
        """
        key = 0
        for x in range(self.WIDTH):
            for y in range(self.HEIGHT):
                key += self.spots[x][y]
                key *= 10
        key = key // 10
        return key
    

    def get_mirror_state_key(self):
        """
        Gets a string representation of the current game board, mirrored.
        """
        key = 0
        for x in range(self.WIDTH - 1, -1, -1):
            for y in range(self.HEIGHT):
                key += self.spots[x][y]
                key *= 10
        key = key // 10
        return key

   
    def print_board(self):
        """
        Prints a string representation of the current game board.
        """
        print(self.get_state_key())
        norm_line = "|---|---|---|---|---|---|---|"
        print(norm_line)
        for j in range(self.HEIGHT - 1, -1, -1):
            temp_line = "|"
            for i in range(self.WIDTH):
                temp_line = temp_line + " " + self.get_symbol([i,j]) + " |"
            print(temp_line)
            print(norm_line) 
        print("\n\n")


    def play_game(self, player_first):
        """ 
        Begin the connect four game loop. 

        Parameters
        ----------
        player_first : boolean
            Whether or not the player will move first. If False, the
            agent goes first.

        """
        self.player_turn = player_first
        # Initialize the agent's state and action
        if player_first:
            self.player_move(is_first=True)
        self.agent.ep_init()
        prev_state = self.get_state_key()
        prev_state_mirror = self.get_mirror_state_key()
        possible_actions = self.get_possible_next_moves()
        prev_action, using_mirror = self.agent.get_action(prev_state, prev_state_mirror, possible_actions)

        # iterate until game is over
        while True:
            # execute oldAction, observe reward and state
            self.agent_move(prev_action)
            # check if game is over
            check = self.get_outcome()
            if check != 0:
                self.agent.update_count("win" if check == 2 else "draw")
                reward = 100 if check == 2 else 0
                break
            # player move
            try:
                self.player_move()
            except TypeError:
                # Catches no more possible moves
                self.agent.update_count("draw")
                reward = 0
                break
            check = self.get_outcome()
            if check != 0:
                self.agent.update_count("loss" if check == 1 else "draw")
                reward = -100 if check == 1 else 0
                break
            else:
                # game continues
                reward = 0
            new_state = self.get_state_key()
            new_state_mirror = self.get_mirror_state_key()
            
            # determine new action (epsilon-greedy)
            new_possible_actions = self.get_possible_next_moves()
            try:
                new_action, new_using_mirror = self.agent.get_action(new_state, new_state_mirror, new_possible_actions)
                # update Q-values
                if new_using_mirror:
                    new_possible_actions_mirror = [(self.WIDTH - 1) - i for i in new_possible_actions]
                    if using_mirror:
                        self.agent.update(prev_state_mirror, new_state_mirror, ((self.WIDTH - 1) - prev_action), ((self.WIDTH - 1) - new_action), reward, new_possible_actions_mirror)
                    else:
                        self.agent.update(prev_state, new_state_mirror, prev_action, ((self.WIDTH - 1) - new_action), reward, new_possible_actions_mirror)
                else:
                    if using_mirror:
                        self.agent.update(prev_state_mirror, new_state, ((self.WIDTH - 1) - prev_action), new_action, reward, new_possible_actions)
                    else:
                        self.agent.update(prev_state, new_state, prev_action, new_action, reward, new_possible_actions)
                # reset "previous" values
                prev_state = new_state
                prev_action = new_action
                possible_actions = new_possible_actions
                using_mirror = new_using_mirror
            except ValueError:
                # Catches no more possible moves
                self.agent.update_count("draw")
                reward = 0
                break
        # Game over. Perform final update
        if using_mirror:
            possible_actions = [(self.WIDTH - 1) - i for i in possible_actions]
            self.agent.update(prev_state_mirror, None, ((self.WIDTH - 1) - prev_action), None, reward, possible_actions)
        else:
            self.agent.update(prev_state, None, prev_action, None, reward, possible_actions)
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
                self.play_game(player_first=False)
            else:
                self.play_game(player_first=True)
        else:
            while True:
                response = input("Would you like to go first? [y/n]: ")
                print('')
                if response == 'n' or response == 'no':
                    self.play_game(player_first=False)
                    break
                elif response == 'y' or response == 'yes':
                    self.play_game(player_first=True)
                    break
                else:
                    print("Invalid input. Please enter 'y' or 'n'.")

