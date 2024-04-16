import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

class TicTacToeGUI:
    def __init__(self):
        self.prev_move = None
        self.can_click = False
        self.master = tk.Tk()
        self.master.title("Tic-Tac-Toe with AI")
        
        # Set the window to fullscreen
        self.master.attributes('-fullscreen', True)
        self.master.bind("<Escape>", lambda event: self.master.attributes("-fullscreen", False))
        self.master.configure(bg='black')  # Set the background color of the window

        # Use a frame to center the contents on the screen
        self.center_frame = tk.Frame(self.master)
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.center_frame.configure(bg='black')  # Set the background color of the frame

        # Adding a label to display a title above the game grid
        self.title_label = tk.Label(self.center_frame, text="PLAY TIC-TAC-TOE AGAINST AN AI",
                                    font=('Helvetica', 24, 'bold'), fg='white', bg='black')
        self.title_label.grid(row=0, column=0, columnspan=3, pady=(10, 20))
        self.move_label = tk.Label(self.center_frame, text="(You are X, the AI is O)",
                                    font=('Helvetica', 24, 'bold'), fg='white', bg='black')
        self.move_label.grid(row=1, column=0, columnspan=3, pady=(10, 20))

        self.waitVar = tk.BooleanVar()
        self.buttons = [[tk.Button(self.center_frame, text='', font=('normal', 40), height=2, width=5,
                                   command=lambda r=i, c=j: self.on_button_click(r, c))
                         for j in range(3)] for i in range(3)]
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].grid(row=i+2, column=j, padx=10, pady=10)  # Padding for better spacing

    def reset_move(self):
        self.can_click = False
        self.prev_move = None

    def get_move(self):
        self.can_click = True
        self.buttons[0][0].wait_variable(self.waitVar)
        self.waitVar.set(False)
        return self.prev_move

    def update_board(self, board):
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text=board[i][j])

    def on_button_click(self, row, col):
        if self.can_click:
            self.prev_move = [row, col]
            self.waitVar.set(True)
            print(f"Move made: {self.prev_move}")

    def display_error(self, message):
        messagebox.showerror("Error", message)

    def display_winner(self, winlose):
        playagain = messagebox.askquestion("Game Over", f"You {winlose}! Play again?", type=messagebox.YESNO)
        return playagain

    def ask_go_first(self):
        gofirst = messagebox.askquestion("Begin Game", "Would you like to go first?", type=messagebox.YESNO)
        return gofirst

    def ask_agent(self):
        # Launch the agent selection dialog
        dialog = AgentSelectionDialog(self.master)
        agent_type = dialog.result
        match agent_type:
            case 'Q-Learner':
                agent_type = 'q'
            case 'SARSA':
                agent_type = 's'
            case 'MC Off-Policy':
                agent_type = 'mcoff'
            case 'MC On-Policy':
                agent_type = 'mcon'
        return agent_type

    def reset_game(self):
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text='')


class AgentSelectionDialog(simpledialog.Dialog):
    def body(self, master):
        ttk.Label(master, text="Choose an agent:").grid(row=0)
        self.agent_type = tk.StringVar(master)
        self.combobox = ttk.Combobox(master, textvariable=self.agent_type,
                                     values=['Q-Learner', 'SARSA', 'MC Off-Policy', 'MC On-Policy'])
        self.combobox.grid(row=0, column=1)
        self.combobox.current(0)  # Default to Q-Learner
        return self.combobox  # initial focus

    def apply(self):
        self.result = self.agent_type.get()
