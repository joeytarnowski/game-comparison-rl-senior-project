import numpy as np
import copy
import math
from functools import reduce 

class Agent:
    def __init__(self, game):
        # Possible actions correspond to the set of all x,y coordinate pairs
        self.actions = []
        for i in range(3):
            for j in range(3):
                self.actions.append((i,j))

        self.Q = {}
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
        

    def get_action_tictactoe(self, s):
        """
        Select an action given the current game state.

        Parameters
        ----------
        s : string
            boardstate
        """
        # Only consider the allowed actions (empty board spaces)
        possible_actions = [a for a in self.actions if s[a[0]*3 + a[1]] == '-']
        values = np.array([self.Q[a][s] for a in possible_actions])
        # Find location of max
        ix_max = np.where(values == np.max(values))[0]
        # Greedy choose.
        if len(ix_max) > 1:
            # If multiple actions were max, then sample from them
            ix_select = np.random.choice(ix_max, 1)[0]
        else:
            # If unique max action, select that one
            ix_select = ix_max[0]
        action = possible_actions[ix_select]

        return action
    
    def get_action_checkers(self, s):
        """
        Select an action given the current game state.

        Parameters
        ----------
        s : string
            state
        """
        # get possible actions
        possible_actions = self.get_possible_moves_ch(s)

        # Find optimal action
        try:
            values = np.array([self.Q[s][tuple([tuple(a[0]), tuple(a[1])])] for a in possible_actions])
        except KeyError:
            self.Q[s] = {}
            for a in possible_actions:
                self.Q[s][tuple([tuple(a[0]), tuple(a[1])])] = 0
            values = np.array([self.Q[s][tuple([tuple(a[0]), tuple(a[1])])] for a in possible_actions])
        # Find location of max
        ix_max = np.where(values == np.max(values))[0]
        # Greedy choose.
        if len(ix_max) > 1:
            # If multiple actions were max, then sample from them
            ix_select = np.random.choice(ix_max, 1)[0]
        else:
            # If unique max action, select that one
            ix_select = ix_max[0]
        action = possible_actions[ix_select]

        return action

    def get_possible_moves_ch(self, s):
        EMPTY_SPOT = 0
        P1 = 1
        P2 = 2
        P1_K = 3
        P2_K = 4
        BACKWARDS_PLAYER = P2
        HEIGHT = 8
        WIDTH = 4
        

        def get_spots(board_key):
            """
            Gets the board spots from a given board_key.
            """
            answer = []
            board_key = str(board_key)
            if len(board_key) < (HEIGHT * WIDTH):
                for j in range(WIDTH*HEIGHT - len(board_key)):
                    board_key = f"0{board_key}"
            for j in range(HEIGHT):
                answer.append([])
                for i in range(WIDTH):
                    answer[j].append(int(board_key[j * WIDTH + i]))

            return answer
    
        def not_spot(loc):
            """
            Finds out of the spot at the given location is an actual spot on the game board.
            """
            if len(loc) == 0 or loc[0] < 0 or loc[0] > HEIGHT - 1 or loc[1] < 0 or loc[1] > WIDTH - 1:
                return True
            return False
        
        def get_spot_info(loc):
            """
            Gets the information about the spot at the given location.
            
            NOTE:
            Might want to not use this for the sake of computational time.
            """
            return spots[loc[0]][loc[1]]
        
        def forward_n_locations(start_loc, n, backwards=False):
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

            if not_spot(answer[0]):
                answer[0] = []
            if not_spot(answer[1]):
                answer[1] = []
                
            return answer
    
        def get_simple_moves(start_loc):
            """    
            Gets the possible moves a piece can make given that it does not capture any opponents pieces.
            
            PRE-CONDITION:
            -start_loc is a location with a players piece
            """
            if board[start_loc[0]][start_loc[1]] > 2:
                next_locations = forward_n_locations(start_loc, 1)
                next_locations.extend(forward_n_locations(start_loc, 1, True))
            elif board[start_loc[0]][start_loc[1]] == BACKWARDS_PLAYER:
                next_locations = forward_n_locations(start_loc, 1, True)  # Switched the true from the statement below
            else:
                next_locations = forward_n_locations(start_loc, 1)
            

            possible_next_locations = []

            for location in next_locations:
                if len(location) != 0:
                    if board[location[0]][location[1]] == EMPTY_SPOT:
                        possible_next_locations.append(location)
                
            return [[start_loc, end_spot] for end_spot in possible_next_locations]      
                
        def get_capture_moves(start_loc, move_beginnings=None):
            """
            Recursively get all of the possible moves for a piece which involve capturing an opponent's piece.
            """
            if move_beginnings is None:
                move_beginnings = [start_loc]
                
            answer = []
            if board[start_loc[0]][start_loc[1]] > 2:  
                next1 = forward_n_locations(start_loc, 1)
                next2 = forward_n_locations(start_loc, 2)
                next1.extend(forward_n_locations(start_loc, 1, True))
                next2.extend(forward_n_locations(start_loc, 2, True))
            elif board[start_loc[0]][start_loc[1]] == BACKWARDS_PLAYER:
                next1 = forward_n_locations(start_loc, 1, True)
                next2 = forward_n_locations(start_loc, 2, True)
            else:
                next1 = forward_n_locations(start_loc, 1)
                next2 = forward_n_locations(start_loc, 2)
            
            
            for j in range(len(next1)):
                if (not not_spot(next2[j])) and (not not_spot(next1[j])) :  # if both spots exist
                    if get_spot_info(next1[j]) != EMPTY_SPOT and get_spot_info(next1[j]) % 2 != get_spot_info(start_loc) % 2:  # if next spot is opponent
                        if get_spot_info(next2[j]) == EMPTY_SPOT:  # if next next spot is empty
                            temp_move1 = copy.deepcopy(move_beginnings)
                            temp_move1.append(next2[j])
                            
                            answer_length = len(answer)
                            
                            if get_spot_info(start_loc) != P1 or next2[j][0] != HEIGHT - 1: 
                                if get_spot_info(start_loc) != P2 or next2[j][0] != 0: 

                                    temp_move2 = [start_loc, next2[j]]
                                    
                                    
                                    make_move(temp_move2, False)

                                    answer.extend(get_capture_moves(temp_move2[1], temp_move1))
                                    
                            if len(answer) == answer_length:
                                answer.append(temp_move1)
                                
            return answer
                
        def get_possible_next_moves():
            """
            Gets the possible moves that can be made from the current board configuration.
            """
            piece_locations = []
            for j in range(HEIGHT):
                for i in range(WIDTH):
                    if board[j][i] == P2 or board[j][i] == P2_K:
                        piece_locations.append([j, i])
            try:  #Should check to make sure if this try statement is still necessary 
                capture_moves = list(reduce(lambda a, b: a + b, list(map(get_capture_moves, piece_locations))))  # CHECK IF OUTER LIST IS NECESSARY

                if len(capture_moves) != 0:
                    for x in capture_moves:
                        x = tuple([tuple(x[0]), tuple(x[1])])
                    return capture_moves

                
                basic_moves = list(reduce(lambda a, b: a + b, list(map(get_simple_moves, piece_locations))))  # CHECK IF OUTER LIST IS NECESSARY
                for x in basic_moves:
                    x = tuple([tuple(x[0]), tuple(x[1])])
                return basic_moves
            except TypeError:
                return []
            
        def make_move(move, switch_player_turn=True):
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
                            
                    spots[int((move[j][0] + move[j + 1][0]) / 2)][middle_y] = EMPTY_SPOT
                    
                    
            spots[move[len(move) - 1][0]][move[len(move) - 1][1]] = spots[move[0][0]][move[0][1]]
            # Promote to king if at the end of the board
            if move[len(move) - 1][0] == HEIGHT - 1 and spots[move[len(move) - 1][0]][move[len(move) - 1][1]] == P1:
                spots[move[len(move) - 1][0]][move[len(move) - 1][1]] = P1_K
            elif move[len(move) - 1][0] == 0 and spots[move[len(move) - 1][0]][move[len(move) - 1][1]] == P2:
                spots[move[len(move) - 1][0]][move[len(move) - 1][1]] = P2_K
            else:
                spots[move[len(move) - 1][0]][move[len(move) - 1][1]] = spots[move[0][0]][move[0][1]]
                
            spots[move[0][0]][move[0][1]] = EMPTY_SPOT
                    
            if switch_player_turn:
                player_turn = not player_turn

        board = get_spots(s)
        spots = copy.deepcopy(board)
        return get_possible_next_moves(spots)

    def get_action_connect_four(self, s):
        board = self.translate_board_c4(s)
        # Get possible actions
        possible_actions = self.get_possible_moves_c4(board)
        # Find optimal action
        using_mirror = False
        try:
            values = np.array([self.Q[a][s] for a in possible_actions])
        except KeyError:
            m_s = self.get_mirrored_key(board)
            try:
                values = np.array([self.Q[a][m_s] for a in possible_actions])
                using_mirror = True
            except KeyError:
                self.Q[s] = {}
                for a in possible_actions:
                    self.Q[a][s] = 0
                values = np.array([self.Q[a][s] for a in possible_actions])
        # Find location of max
        ix_max = np.where(values == np.max(values))[0]
        # Greedy choose.
        if len(ix_max) > 1:
            # If multiple actions were max, then sample from them
            ix_select = np.random.choice(ix_max, 1)[0]
        else:
            # If unique max action, select that one
            ix_select = ix_max[0]
        action = possible_actions[ix_select]

        if using_mirror:
            action = (6) - action
        
        print(values)

        return action
    
    def get_possible_moves_c4(self, board):
        """
        Gets the possible moves that can be made from the current board configuration.
        """
        possible_moves = []
        for i in range(7):
            if board[i][5] == 0:
                possible_moves.append(i)
        return possible_moves
    
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
