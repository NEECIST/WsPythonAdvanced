import os

class TicTacToe():
    player = 'X'
    board = [[" "," "," "], [" "," "," "], [" "," "," "]]        
        
    def check_win(self):
        win = 0
        for i in [0, 1, 2]:
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != " ":
                win = 1
                break
            elif self.board[0][i] == self.board[1][i] == self.board[2][i] != ' ':
                win = 1
                break
            elif self.board[0][0] == self.board[1][1] == self.board[2][2] != ' ':
                win = 1
                break
            elif self.board[0][2] == self.board[1][1] == self.board[2][0]!= ' ':
                win = 1
                break
        return win
    
    def checkDraw(self):
        for i in [0, 1, 2]:
            for j in [0, 1, 2]:
                if self.board[i][j] == " ": #não há empate
                    return
    
    def validate_input(self, row, column):
        if self.board[row][column] == " ":
            return True
        return False

    def display_board(self):
        for i in [0, 1, 2]:
            for j in [0, 1, 2]:
                print(self.board[i][j], end = "")
                if j==2:
                    print("\n", end = "")
                elif j!=2:
                    print("|", end = "")
        print("")

    def getPlayer(self):
        return self.player
    
    def swapPlayer(self):
        if self.player == 'X':
            self.player = 'O'
            return self.player
        
        if self.player == 'O':
            self.player = 'X' 
            return self.player       
    
    def play(self, row, column):
        if self.validate_input(row, column) == False:
            print("Erro!!")
            return -1

        self.board[row][column] = self.player

        if self.checkDraw():
            return 0

        if self.check_win() == 1:
            return 1

game = TicTacToe()

while (True):
    os.system('cls||clear')
    game.display_board()
    userInput = input(f"Player {game.getPlayer()} its your turn, where do you want to play? x y : ").split(" ")

    try:
        x = int(userInput[0])
        y = int(userInput[1])
    except:
        print("Erro, insere um inteiro")

    ret = game.play(x, y)

    if ret == -1:
        continue
    elif ret == 0:
        print("Empate!!!")
        exit()
    elif ret == 1:
        print(f"Jogador {game.getPlayer()} ganhou!!!")
        game.display_board()
        exit()
    
    game.swapPlayer()
