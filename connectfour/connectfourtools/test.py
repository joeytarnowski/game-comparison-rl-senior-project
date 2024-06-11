class Game:
    def __init__(self):
        self.WIDTH = 7
        self.HEIGHT = 6
        self.P1 = 1
        self.P2 = 2
        self.EMPTY_SPOT = 0
        self.board = [[0 for _ in range(self.HEIGHT)] for _ in range(self.WIDTH)]
        self.games_played = 0

    def get_outcome(self, spots):
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
                test_spots = [spots[x][y+1], spots[x][y+2], spots[x][y+3]]
                if spots[x][y] == test_spots[0] == test_spots[1] == test_spots[2] and spots[x][y] != self.EMPTY_SPOT:
                    return 1 if spots[x][y] == self.P1 else 2
                
        # Test for horizontal wins
        for x in range(self.WIDTH - 3):
            for y in range(self.HEIGHT):
                test_spots = [spots[x+1][y], spots[x+2][y], spots[x+3][y]]
                if spots[x][y] == test_spots[0] == test_spots[1] == test_spots[2] and spots[x][y] != self.EMPTY_SPOT:
                        return 1 if spots[x][y] == self.P1 else 2
                
        # Test for diagonal wins
        for x in range(self.WIDTH - 3):
            for y in range(self.HEIGHT):
                if y < 3:
                    test_spots = [spots[x+1][y+1], spots[x+2][y+2], spots[x+3][y+3]]
                    if spots[x][y] == test_spots[0] == test_spots[1] == test_spots[2] and spots[x][y] != self.EMPTY_SPOT:
                        return 1 if spots[x][y] == self.P1 else 2
                else:
                    test_spots = [spots[x+1][y-1], spots[x+2][y-2], spots[x+3][y-3]]
                    if spots[x][y] == test_spots[0] == test_spots[1] == test_spots[2] and spots[x][y] != self.EMPTY_SPOT:
                        return 1 if spots[x][y] == self.P1 else 2
        
        # Test for draw
        for x in range(self.WIDTH):
            if self.EMPTY_SPOT in spots[x]:
                return 0
        return 3
    
    def get_possible_next_moves(self, spots):
        """
        Gets the possible moves that can be made from the current board configuration.
        """
        possible_moves = []
        print(spots)
        for i in range(self.WIDTH):
            if spots[i][self.HEIGHT - 1] == self.EMPTY_SPOT:
                possible_moves.append(i)
        return possible_moves
    
    def translate_board(self, board_key):
        """
        Translates the board key into a format that can be used by the minimax function.
        """
        board_key = str(board_key)
        if len(board_key) < (self.HEIGHT * self.WIDTH):
            for j in range(self.WIDTH*self.HEIGHT - len(board_key)):
                board_key = f"0{board_key}"
        spots = [[0, 0, 0, 0, 0, 0] for j in range(self.WIDTH)]
        for j in range(self.WIDTH):
            for i in range(self.HEIGHT):
                spots[j][i] = int(board_key[j * self.HEIGHT + i])
        return spots
    
    def print_board(self, spots):
        """
        Prints a string representation of the current game board.
        """
        norm_line = "|---|---|---|---|---|---|---|"
        print(norm_line)
        for j in range(self.HEIGHT - 1, -1, -1):
            temp_line = "|"
            for i in range(self.WIDTH):
                temp_line = temp_line + " " + str(spots[i][j]) + " |"
            print(temp_line)
            print(norm_line) 
        print("\n\n")
    
test_game = Game()
test_board = test_game.translate_board(110000121200211000100000200000000000222000)
print(test_game.get_possible_next_moves(test_board)) # 0
print(test_game.get_outcome(test_board))
test_game.print_board(test_board)
"""Teacher about to move: 110000121000200000100000200000000000220000
Agent about to move: 110000121000210000100000200000000000220000
Teacher about to move: 110000121200210000100000200000000000220000
Agent about to move: 110000121200211000100000200000000000220000
Teacher about to move: 110000121200211000100000200000000000222000
Agent about to move: 110000121200211000100000210000000000222000
110000121200211000100000210000000000222200"""