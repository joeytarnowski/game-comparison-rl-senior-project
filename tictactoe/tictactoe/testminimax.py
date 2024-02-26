from tictactoe.minimaxteacher import MMTeacher
if __name__ == "__main__":
    board = [['X','O','X'],['O','X','O'],['-','-','-']]
    teacher = MMTeacher()
    print(teacher.makeMove(board))