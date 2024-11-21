import tkinter as tk
from tkinter import messagebox
from multiprocessing import Process, Queue
from utils import get_piece_info
from game_logic import move_piece, check_game_status
from board import initialize_board
from ai_worker import calculate_ai_move  # AI logic moved to a separate file


class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Game")
        self.board = initialize_board()
        self.turn = 'white'
        self.last_move = None
        self.human_color = 'white'
        self.ai_color = 'black'
        self.selected_piece = None  # To track the piece selected by the player
        self.highlighted_cell = None  # Store the coordinates of the highlighted cell
        self.buttons = {}  # Store the button references
        self.create_board()
        self.update_board()

    def create_board(self):
        """Create the chessboard grid using Tkinter buttons."""
        # Add row and column labels
        for col in range(8):
            # Column labels (a-h)
            tk.Label(self.root, text=chr(97 + col), font=("Helvetica", 12)).grid(row=0, column=col + 1)
            tk.Label(self.root, text=chr(97 + col), font=("Helvetica", 12)).grid(row=9, column=col + 1)

        for row in range(8):
            # Row labels (1-8, top to bottom)
            tk.Label(self.root, text=str(row + 1), font=("Helvetica", 12)).grid(row=row + 1, column=0)
            tk.Label(self.root, text=str(row + 1), font=("Helvetica", 12)).grid(row=row + 1, column=9)

        # Create the chessboard grid
        for row in range(8):
            for col in range(8):
                color = "#f0d9b5" if (row + col) % 2 == 0 else "#b58863"
                button = tk.Button(
                    self.root,
                    bg=color,
                    font=("Helvetica", 20),
                    width=4,
                    height=2,
                    command=lambda r=row, c=col: self.on_square_click(r, c)
                )
                # Place the button
                button.grid(row=row + 1, column=col + 1)
                self.buttons[(row, col)] = button

    def update_board(self):
        """Update the board display based on the current game state."""
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                button = self.buttons[(row, col)]
                if piece:
                    button.config(text=str(piece), state="normal")
                else:
                    button.config(text="", state="normal")

                # Reset background color to default
                color = "#f0d9b5" if (row + col) % 2 == 0 else "#b58863"
                button.config(bg=color)

        # Disable buttons for AI's turn
        if self.turn == self.ai_color:
            for button in self.buttons.values():
                button.config(state="disabled")
            # Start AI calculation in a separate process
            self.root.after(100, self.start_ai_move)
        else:
            for button in self.buttons.values():
                button.config(state="normal")

    def on_square_click(self, row, col):
        """Handle clicks on the chessboard."""
        position = self.indices_to_position(row, col)
        button = self.buttons[(row, col)]

        if not self.selected_piece:
            # First click: Select a piece
            piece_info = get_piece_info(self.board, position)
            if piece_info and piece_info[1] == self.turn:
                self.selected_piece = position
                self.highlight_cell(row, col, "red")
            else:
                messagebox.showinfo("Invalid Selection", "Please select one of your own pieces.")
        else:
            # Second click: Check if the user wants to select a new piece
            piece_info = get_piece_info(self.board, position)
            if piece_info and piece_info[1] == self.turn:
                # User selects another piece; reset the previous selection
                self.clear_highlight()
                self.selected_piece = position
                self.highlight_cell(row, col, "red")
            else:
                # User attempts to move the previously selected piece
                start_pos = self.selected_piece
                end_pos = position
                move_success = move_piece(self.board, start_pos, end_pos, self.last_move)
                if move_success:
                    self.last_move = (start_pos, end_pos)
                    self.selected_piece = None
                    self.highlighted_cell = None
                    self.turn = self.ai_color if self.turn == self.human_color else self.human_color
                    self.update_board()

                    # Check for game over
                    game_over, result = check_game_status(self.board, self.turn, self.last_move)
                    if game_over:
                        self.show_result(result)
                else:
                    messagebox.showinfo("Invalid Move", "This move is not allowed.")
                    # Reset selection
                    self.selected_piece = None
                    self.clear_highlight()

    def start_ai_move(self):
        """Start AI calculation in a separate process."""
        queue = Queue()
        process = Process(target=calculate_ai_move, args=(self.board, self.ai_color, self.last_move, queue))
        process.start()
        self.root.after(100, self.check_ai_move, queue, process)

    def check_ai_move(self, queue, process):
        """Check if the AI has finished its move."""
        if process.is_alive():
            self.root.after(100, self.check_ai_move, queue, process)
        else:
            process.join()
            if not queue.empty():
                ai_move = queue.get()
                if ai_move:
                    start_pos, end_pos = ai_move
                    move_piece(self.board, start_pos, end_pos, self.last_move)
                    self.last_move = (start_pos, end_pos)
                    self.turn = self.human_color
                    self.update_board()

                    # Check for game over
                    game_over, result = check_game_status(self.board, self.turn, self.last_move)
                    if game_over:
                        self.show_result(result)

    def highlight_cell(self, row, col, color):
        """Highlight a cell with a given color (50% opacity)."""
        self.clear_highlight()  # Clear previous highlight
        button = self.buttons[(row, col)]
        button.config(bg=color)
        self.highlighted_cell = (row, col)

    def clear_highlight(self):
        """Clear the highlight from the previously selected cell."""
        if self.highlighted_cell:
            row, col = self.highlighted_cell
            color = "#f0d9b5" if (row + col) % 2 == 0 else "#b58863"
            self.buttons[(row, col)].config(bg=color)
            self.highlighted_cell = None

    def show_result(self, result):
        """Display the result of the game."""
        if result == "white_win":
            messagebox.showinfo("Game Over", "White wins!")
        elif result == "black_win":
            messagebox.showinfo("Game Over", "Black wins!")
        elif result == "draw":
            messagebox.showinfo("Game Over", "It's a draw!")
        self.root.quit()

    @staticmethod
    def indices_to_position(row, col):
        """Convert board indices to chess position (e.g., (0, 0) -> 'a1')."""
        return f"{chr(col + 97)}{row + 1}"


if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()  # Required for multiprocessing on Windows
    root = tk.Tk()
    ChessGUI(root)
    root.mainloop()
