from utils import get_piece_info
from game_logic import move_piece
from board import initialize_board, print_board
from game_logic import check_game_status
from algorithm import minimax

def main():
    board = initialize_board()
    print("Welcome to the Chess Game!")
    print_board(board)
    
    human_color = 'white'  # Human plays white
    ai_color = 'black'     # AI plays black
    turn = 'white'         # White starts first
    last_move = None  # Keep track of the last move

    while True:
        print(f"\n{turn.capitalize()}'s turn")
        # Check if the game is over before the player's move
        game_over, result = check_game_status(board, turn, last_move=last_move)

        if game_over:
            break

        if turn == human_color:
            move_input = input("Enter your move (e.g., e2 e4) or 'exit' to quit: ").strip()
            if move_input.lower() == 'exit':
                print("Thank you for playing!")
                break
            try:
                start_pos, end_pos = move_input.split()
                # Get the piece at the starting position
                piece_type, color = get_piece_info(board, start_pos)
                if color != turn:
                    print(f"It's {turn}'s turn. Please move your own pieces.")
                    continue
                # Attempt to move the piece
                if move_piece(board, start_pos, end_pos, last_move):
                    # Update the last move
                    last_move = (start_pos, end_pos)
                    print_board(board)
                    # Switch turns
                    turn = ai_color
                else:
                    print("Move was not successful. Try again.")
            except ValueError:
                print("Invalid input format. Please enter moves in the format 'e2 e4'.")
            except Exception as e:
                print(f"An error occurred: {e}")
                continue
        else:
            # AI's turn
            print("AI is thinking...")
            evaluation, ai_move = minimax(board, depth=3, alpha=float('-inf'), beta=float('inf'),
                                          maximizing_player=True, current_color=ai_color, last_move=last_move)
            if ai_move:
                start_pos, end_pos = ai_move
                move_piece(board, start_pos, end_pos, last_move)
                print(f"AI moved from {start_pos} to {end_pos}")
                print_board(board)
                # Switch turns
                turn = human_color
            else:
                print("AI has no valid moves. Game over.")
                break

    # After game over, display the result
    if result == 'white_win':
        print("White wins the game!")
    elif result == 'black_win':
        print("Black wins the game!")
    elif result == 'draw':
        print("The game ended in a draw.")

if __name__ == "__main__":
    main()
