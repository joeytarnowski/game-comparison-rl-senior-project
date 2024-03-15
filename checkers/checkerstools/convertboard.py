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
            temp_line = temp_line + " " + boardstring[4*j + i] + " |"
            if i != 3 or j % 2 != 1:  # should figure out if this 3 should be changed to self.WIDTH-1
                temp_line = temp_line + "///|"
        print(temp_line)
        print(norm_line)     

input_board = input("Enter the board string: ")   
input_board = input_board[:32] 
print_board(4, 8, input_board)   

