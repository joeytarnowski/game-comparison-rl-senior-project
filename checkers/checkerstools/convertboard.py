def print_board(WIDTH, HEIGHT, boardstring):
    """
    Prints a string representation of the current game board.
    """
    norm_line = "|---|---|---|---|---|---|---|---|"
    print(norm_line)
    for j in range(HEIGHT):
        if j % 2 == 1:
            temp_line = "|///|"
        else:
            temp_line = "|"
        for i in range(WIDTH):
            temp_line = temp_line + " " + getsymbol(boardstring[4*j + i]) + " |"
            if i != 3 or j % 2 != 1:  # should figure out if this 3 should be changed to self.WIDTH-1
                temp_line = temp_line + "///|"
        print(temp_line)
        print(norm_line)     

def getsymbol(piece):
    """
    Returns the symbol for the given piece.
    """
    if piece == "0":
        return " "
    elif piece == "1":
        return "o"
    elif piece == "2":
        return "x"
    elif piece == "3":
        return "O"
    else:
        return "X"


input_board = input("Enter the board string: ")   
if len(input_board) < 32:
    for i in range(32-len(input_board)):
        input_board = "0" + input_board
print_board(4, 8, input_board)   

