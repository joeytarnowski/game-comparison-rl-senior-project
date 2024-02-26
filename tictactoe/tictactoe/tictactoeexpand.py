"""
Helper script to create a full dictionary with every optimal move from the minimax algorithm
"""
from tictactoe.minimaxteacher import MMTeacher
import pickle

totalstates = 0
moves_dict = {}


def win(board, key='X'):
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

def draw(board):
    for i in range(3):
        for j in range(3):
            if board[i][j] == '-':
                return False
    return True

def getavailmoves(board):
    x = 0
    avail_moves = []
    for j in board:
        y = 0
        for move in j:
            if move == '-':
                avail_moves.append([x,y])
            y += 1
        x += 1
    return avail_moves

def makeKey(board):
    key = ""
    for subboard in board:
        for state in subboard:
            key += state
    return key

def testall (boardstate, key, teacher):
    global totalstates;
    global moves_dict;
    moves = getavailmoves(boardstate)
    nextkey = 'O' if key == 'X' else 'X'

    if (not draw(boardstate)) and (not win(boardstate)) and (not win(boardstate,'O')):
        if key == 'X':
            opt_move = teacher.makeMove(boardstate)
            dict_key = makeKey(boardstate)
            moves_dict[dict_key] = opt_move
            with open('output_move_dict.txt', 'a') as f:
                end_str = f"\nState {totalstates}: \n{boardstate[0]}\n{boardstate[1]}\n{boardstate[2]}\nKey: {dict_key}\nOptimal move: {opt_move}"
                f.write(end_str)

        for move in moves:
            boardstate[move[0]][move[1]] = key
            totalstates += 1
            testall(boardstate,nextkey,teacher)
            boardstate[move[0]][move[1]] = '-'
            
if __name__ == "__main__":
    board = [['-','-','-'],['-','-','-'],['-','-','-']]
    teacher = MMTeacher()
    testall(board,'X', teacher)
    testall(board,'O', teacher)
    print(len(moves_dict))

    # Store data (serialize)
    with open('minimax_table.pkl', 'wb') as handle:
        pickle.dump(moves_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
