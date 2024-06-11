from teacher import Teacher
import pickle
import time
import os

totalstates = 0
if os.path.isfile('minimax_table.pkl'):
    with open('minimax_table.pkl', 'rb') as handle:
        moves_dict = pickle.load(handle)
else:
    moves_dict = {}
WIDTH = 7
HEIGHT = 6
P1 = 1
P2 = 2
EMPTY_SPOT = 0
setnum = 0
subsetnum = 0

def get_outcome(spots):
        """
        Gets the outcome of the game currently being played.
        0: Game is still going
        1: Player 1 wins
        2: Player 2 wins
        3: Game is a tie
        """
        
        # Test for vertical wins
        for x in range(WIDTH):
            for y in range(HEIGHT - 3):
                test_spots = [spots[x][y+1], spots[x][y+2], spots[x][y+3]]
                if spots[x][y] == test_spots[0] == test_spots[1] == test_spots[2] and spots[x][y] != EMPTY_SPOT:
                    return 1 if spots[x][y] == P1 else 2
                
        # Test for horizontal wins
        for x in range(WIDTH - 3):
            for y in range(HEIGHT):
                test_spots = [spots[x+1][y], spots[x+2][y], spots[x+3][y]]
                if spots[x][y] == test_spots[0] == test_spots[1] == test_spots[2] and spots[x][y] != EMPTY_SPOT:
                        return 1 if spots[x][y] == P1 else 2
                
        # Test for diagonal wins
        for x in range(WIDTH - 3):
            for y in range(HEIGHT):
                if y < 3:
                    test_spots = [spots[x+1][y+1], spots[x+2][y+2], spots[x+3][y+3]]
                    if spots[x][y] == test_spots[0] == test_spots[1] == test_spots[2] and spots[x][y] != EMPTY_SPOT:
                        return 1 if spots[x][y] == P1 else 2
                else:
                    test_spots = [spots[x+1][y-1], spots[x+2][y-2], spots[x+3][y-3]]
                    if spots[x][y] == test_spots[0] == test_spots[1] == test_spots[2] and spots[x][y] != EMPTY_SPOT:
                        return 1 if spots[x][y] == P1 else 2
        
        # Test for draw
        for x in range(WIDTH):
            if EMPTY_SPOT in spots[x]:
                return 0
        return 3

    
def get_possible_next_moves(board):
        """
        Gets the possible moves that can be made from the current board configuration.
        """
        possible_moves = []
        for i in range(WIDTH):
            if board[i][HEIGHT - 1] == EMPTY_SPOT:
                possible_moves.append(i)
        return possible_moves

def make_key(spots):
        """
        Gets a string representation of the current game board.
        """
        key = 0
        for x in range(WIDTH):
            for y in range(HEIGHT):
                key += spots[x][y]
                key *= 10
        key = key // 10
        return key

def make_mirror_key(spots):
        """
        Gets a string representation of the current game board mirrored.
        """
        key = 0
        for x in range(WIDTH -1, -1, -1):
            for y in range(HEIGHT):
                key += spots[x][y]
                key *= 10
        key = key // 10
        return key

def change_board(move, board):
        """
        Makes a given move on the board, and (as long as is wanted) switches the indicator for
        which players turn it is.
        """
        for i in range(HEIGHT):
            if board[move][i] == EMPTY_SPOT:
                coordinate = [move, i]
                break
        
        return coordinate

def testall (boardstate, player, teacher, depth=0):
    global totalstates
    global moves_dict
    global setnum
    global subsetnum
    moves = get_possible_next_moves(boardstate)
    next_player = 1 if player == 2 else 2

    if depth == 1:
         setnum += 1
         subsetnum = 0
         print(f"Testing set {setnum}/14")
    elif depth == 2:
        subsetnum += 1
        print(f"Testing subset {subsetnum}/7")


    if get_outcome(boardstate) == 0:
        dict_key = make_key(boardstate)
        # If the boardstate is not a draw or a win, and the boardstate or its mirror is not in the dictionary, add it to the dictionary
        if make_mirror_key(boardstate) not in moves_dict and dict_key not in moves_dict and player == 1:
            opt_move = teacher.make_move_key(dict_key)
            moves_dict[dict_key] = opt_move

        # Recursively call the function for all possible moves
        for move in moves:
            if depth >= 6:
                 break
            change_coord = change_board(move, boardstate)
            boardstate[change_coord[0]][change_coord[1]] = player
            testall(boardstate,next_player,teacher, depth + 1)
            boardstate[change_coord[0]][change_coord[1]] = EMPTY_SPOT
            
if __name__ == "__main__":
    timer = time.perf_counter()
    board = [[j, j, j, j, j, j] for j in [EMPTY_SPOT] * WIDTH]
    teacher = Teacher()
    teacher.depth = 5
    testall(board,1, teacher)
    print("All states for player 1 moving first done")
    # Store data (serialize)
    with open('minimax_table.pkl', 'wb') as handle:
        pickle.dump(moves_dict, handle, protocol=pickle.HIGHEST_PROTOCOL) 
    testall(board,2, teacher)
    print(len(moves_dict))
    print(f"Time taken: {time.perf_counter() - timer}")

    # Store data (serialize)
    with open('minimax_table.pkl', 'wb') as handle:
        pickle.dump(moves_dict, handle, protocol=pickle.HIGHEST_PROTOCOL) 
    print(f"Total states: {totalstates}")  