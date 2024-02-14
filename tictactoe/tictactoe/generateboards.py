def generate_boards():
    boards = []

    def check_for_win(board):
        # Check rows
        for row in board:
            if row[0] != '-' and row[0] == row[1] == row[2]:
                return True
        # Check columns
        for col in range(3):
            if board[0][col] != '-' and board[0][col] == board[1][col] == board[2][col]:
                return True
        # Check diagonals
        if board[0][0] != '-' and board[0][0] == board[1][1] == board[2][2]:
            return True
        if board[0][2] != '-' and board[0][2] == board[1][1] == board[2][0]:
            return True
        return False

    def check_for_draw(board):
        for row in board:
            if '-' in row:
                return False
        return True

    def backtrack(board):
        num_x = sum(row.count('X') for row in board)
        num_o = sum(row.count('O') for row in board)

        if num_x == num_o:
            player = 'X'
        else:
            player = 'O'

        if check_for_win(board) or check_for_draw(board):
            return

        if player == 'X':
            boards.append(board)  # Append the board here

        for i in range(3):
            for j in range(3):
                if board[i][j] == '-':
                    new_board = [row[:] for row in board]
                    new_board[i][j] = player
                    backtrack(new_board)

    initial_board = [['-'] * 3 for _ in range(3)]
    backtrack(initial_board)
    return boards

all_boards = generate_boards()

# Print all generated boards
print(f"total number of boards: {len(all_boards)}")
with open('output.txt', 'w') as f:
    f.write("Every possible tic-tac-toe board\n\n")
    for board in all_boards:
        f.write('\n'.join(' '.join(row) for row in board))
        f.write("\n\n")

        