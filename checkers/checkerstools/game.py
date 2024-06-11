"""
NOTES:
-Should store moves as array of locations e.g.: [[y1,x1],[y2,x2],[y3,x3]]
which is showing the piece at [y1,x1] goes to [y2,x2] then [y3,x3] as one move
-0 is empty spot, 1 is p1, 2 is p2, 3 is p1 king, 4 is p2 king
-if self.player_turn == True then it is player 1's turn
-the player/teacher is always player 1
"""


import math
import random
import copy
from functools import reduce 

class Game:
    """
    A class to represent and play an 8x8 game of checkers.
    """
    EMPTY_SPOT = 0
    P1 = 1
    P2 = 2
    P1_K = 3
    P2_K = 4
    BACKWARDS_PLAYER = P2
    HEIGHT = 8
    WIDTH = 4
    
    
    def __init__(self, agent, teacher=None, old_spots=None, player_turn=True):
        """
        Initializes a new instance of the Game class.  Unless specified otherwise, 
        the board will be created with a start board configuration.
        """
        self.agent = agent
        self.teacher = teacher
        self.player_turn = player_turn
        self.draw_counter = 0
        self.total_moves = 0
        self.rep_counter = 0
        self.rep_moves = []
        if old_spots is None:   
            self.spots = [[j, j, j, j] for j in [self.P1, self.P1, self.P1, self.EMPTY_SPOT, self.EMPTY_SPOT, self.P2, self.P2, self.P2]]
        else:
            self.spots = old_spots
    
    def empty_board(self):
        """
        Removes any pieces currently on the board and leaves the board with nothing but empty spots.
        """
        self.spots = [[j, j, j, j] for j in [self.EMPTY_SPOT] * self.HEIGHT]  # Make sure [self.EMPTY_SPOT]*self.HEIGHT] has no issues
    

    def get_outcome(self):
        """
        Gets the outcome of the game currently being played.
        0: Game is still going
        1: Player 1 wins
        2: Player 2 wins
        3: Game is a tie
        """
        piece_counter = self.get_number_of_pieces_and_kings()
        if piece_counter[0] != 0 or piece_counter[2] != 0:
            if piece_counter[1] != 0 or piece_counter[3] != 0:
                if self.draw_counter >= 50:
                    return 3
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


    def get_number_of_pieces_and_kings(self):
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
                                
                                temp_board = Game(self.agent, old_spots=copy.deepcopy(self.spots), player_turn=self.player_turn)
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
    
    
    def player_move(self):
        """
        Query player for a move and update the board accordingly.
        """
        if self.teacher is not None:
            key = self.get_state_key()
            self.teacher.new_board(self, key)
            action = self.teacher.get_next_move()
            self.make_move(action)
        else:
            self.print_board()
            piece = []
            move = []
            possible_moves = self.get_possible_next_moves()
            valid_pieces = [possible_moves[x][0] for x in range(len(possible_moves))]
            while True:
                piece_i = input("Your move! Please select the piece you want to move "
                             "in the format row,col: ")
                print('\n')
                try:
                    row, col = int(piece_i[0]) - 1, int(piece_i[2]) - 1
                    print(f"row: {row}, col: {col}")
                except ValueError:
                    print("INVALID INPUT! Please use the correct format.")
                    continue
                if (self.get_spot_info([row, col]) != self.P1 and self.get_spot_info([row, col]) != self.P1_K) or (valid_pieces.count([row, col]) == 0):
                    print("INVALID PIECE! Choose again.")
                    continue
                piece = [row, col]
                break
            
            while True:
                move_i = input("Your move! Please select the location you want to move to "
                             "in the format row,col: ")
                print('\n')
                try:
                    row, col = int(move_i[0]) - 1, int(move_i[2]) - 1
                    move = [row, col]
                except ValueError:
                    print("INVALID INPUT! Please use the correct format.")
                    continue
                if (row not in range(4) or col not in range(7)) or (possible_moves.count([piece,move]) == 0):
                    print("INVALID MOVE! Choose again.")
                    continue
                break
            self.make_move([piece, move])


    def agent_move(self, action):
        self.make_move(action)


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
        # Promote to king if at the end of the board
        if move[len(move) - 1][0] == self.HEIGHT - 1 and self.spots[move[len(move) - 1][0]][move[len(move) - 1][1]] == self.P1:
            self.spots[move[len(move) - 1][0]][move[len(move) - 1][1]] = self.P1_K
        elif move[len(move) - 1][0] == 0 and self.spots[move[len(move) - 1][0]][move[len(move) - 1][1]] == self.P2:
            self.spots[move[len(move) - 1][0]][move[len(move) - 1][1]] = self.P2_K
        else:
            self.spots[move[len(move) - 1][0]][move[len(move) - 1][1]] = self.spots[move[0][0]][move[0][1]]
            
        self.spots[move[0][0]][move[0][1]] = self.EMPTY_SPOT
                
        if switch_player_turn:
            self.player_turn = not self.player_turn
       

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
        
        
    def insert_pieces(self, pieces_info):
        """
        Inserts a set of pieces onto a board.

        pieces_info is in the form: [[vert1, horz1, piece1], [vert2, horz2, piece2], ..., [vertn, horzn, piecen]]
        """
        for piece_info in pieces_info:
            self.spots[piece_info[0]][piece_info[1]] = piece_info[2]
        
    
    def get_symbol(self, location):
        """
        Gets the symbol for what should be at a board location.
        """
        if self.spots[location[0]][location[1]] == self.EMPTY_SPOT:
            return " "
        elif self.spots[location[0]][location[1]] == self.P1:
            return "o"
        elif self.spots[location[0]][location[1]] == self.P2:
            return "x"
        elif self.spots[location[0]][location[1]] == self.P1_K:
            return "O"
        else:
            return "X"
    
    
    def get_state_key(self):
        """
        Gets a string representation of the current game board.
        """
        answer = 0
        for j in range(self.HEIGHT):
            for i in range(self.WIDTH):
                answer += self.spots[j][i]
                answer *= 10
        answer = answer // 10
        return answer

   
    def output_board(self):
        """
        Prints a string representation of the current game board.
        """
        norm_line = "|---|---|---|---|---|---|---|---|"
        with open("board.txt", "a") as f:
            f.write(norm_line + "\n")
            for j in range(self.HEIGHT):
                if j % 2 == 1:
                    temp_line = "|///|"
                else:
                    temp_line = "|"
                for i in range(self.WIDTH):
                    temp_line = temp_line + " " + self.get_symbol([j, i]) + " |"
                    if i != 3 or j % 2 != 1:  # should figure out if this 3 should be changed to self.WIDTH-1
                        temp_line = temp_line + "///|"
                f.write(temp_line + "\n")
                f.write(norm_line + "\n")

            f.write(f"\nplayer turn: {self.player_turn}\n")
            f.write(f"draw counter: {self.draw_counter}\n")    
            f.write(f"rep counter: {self.rep_counter}\n") 
            f.write(f"total moves: {self.total_moves}\n") 


    def print_board(self):
        """
        Prints a string representation of the current game board.
        """
        norm_line = "|---|---|---|---|---|---|---|---|"
        print(norm_line)
        for j in range(self.HEIGHT):
            if j % 2 == 1:
                temp_line = "|///|"
            else:
                temp_line = "|"
            for i in range(self.WIDTH):
                temp_line = temp_line + " " + self.get_symbol([j, i]) + " |"
                if i != 3 or j % 2 != 1:  # should figure out if this 3 should be changed to self.WIDTH-1
                    temp_line = temp_line + "///|"
            print(temp_line)
            print(norm_line)            


    def calc_reward(self, prev_state):
        """
        Calculate the reward for the current game state for PLAYER 2. 
        """
        prev_state = str(prev_state)
        prev_state_val = (prev_state.count("2") + 2 * prev_state.count("4")) - (prev_state.count("1") + 2 * prev_state.count("3"))
        new_state = str(self.get_state_key())
        new_state_val = (new_state.count("2") + 2 * new_state.count("4")) - (new_state.count("1") + 2 * new_state.count("3"))
        return new_state_val - prev_state_val


    def play_game(self, player_first):
        """ 
        Begin the checkers game loop. 

        Parameters
        ----------
        player_first : boolean
            Whether or not the player will move first. If False, the
            agent goes first.

        """
        self.player_turn = player_first
        # Initialize the agent's state and action
        if player_first:
            self.player_move()
        self.agent.ep_init()
        prev_state = self.get_state_key()
        possible_actions = self.get_possible_next_moves()
        prev_action = self.agent.get_action(prev_state, possible_actions)

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
                self.agent.update_count("win")
                reward = 100
                break
            check = self.get_outcome()
            if not check == 0:
                self.agent.update_count("loss" if check == 1 else "draw")
                reward = -100 if check == 1 else 0
                break
            else:
                # game continues
                reward = self.calc_reward(prev_state)
            new_state = self.get_state_key()
            if reward != 0:
                self.draw_counter = 0
            else:
                self.draw_counter += 1
                # Check for threefold repetition
                if len(self.rep_moves) <= 1:
                    self.rep_moves.append(prev_state)
                    self.rep_moves.append(new_state)
                else:
                    if new_state == self.rep_moves[0] and prev_state == self.rep_moves[1]:
                        self.rep_counter += 1
                        if self.rep_counter >= 2:
                            self.agent.update_count("draw")
                            reward = 0
                            break
                    else:
                        self.rep_counter = 0
                        self.rep_moves = []
            # determine new action (epsilon-greedy)
            new_possible_actions = self.get_possible_next_moves()
            try:
                new_action = self.agent.get_action(new_state, new_possible_actions)
                # update Q-values
                self.agent.update(prev_state, new_state, prev_action, new_action, reward, new_possible_actions)
                # reset "previous" values
                prev_state = new_state
                prev_action = new_action
                possible_actions = new_possible_actions
            except ValueError:
                # Catches no more possible moves
                self.agent.update_count("loss")
                reward = -100
                break
            self.total_moves += 1

        # Game over. Perform final update
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

