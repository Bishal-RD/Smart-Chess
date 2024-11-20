from utils import get_piece_info, move_piece
from display_board import initialize_board, print_board
from game_over import check_game_status

def main():
    board = initialize_board()
    print("Welcome to the Chess Game!")    
    turn = 'white'  # 'white' starts first
    print_board(board)
    
    while True:
        print(f"\n{turn.capitalize()}'s turn")

        # Check if the game is over before the player's move
        game_over, result = check_game_status(board, turn)
        if game_over:
            break

        move_input = input("Enter your move (e.g., e2 e4) or 'exit' to quit: ").strip()
        if move_input.lower() == 'exit':
            print("Thank you for playing!")
            break
        try:
            start_pos, end_pos = move_input.split()
            # Get the piece at the starting position
            piece_type, color = get_piece_info(board, start_pos)
            if piece_type is None:
                print(f"No piece at starting position {start_pos}")
                continue

            if color != turn:
                print(f"It's {turn}'s turn. Please move your own pieces.")
                continue
            
            # Attempt to move the piece
            if move_piece(board, start_pos, end_pos):
                print_board(board)
                # Switch turns
                turn = 'black' if turn == 'white' else 'white'
            else:
                print("Move was not successful. Try again.")
        except ValueError:
            print("Invalid input format. Please enter moves in the format 'e2 e4'.")
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

    # After game over, display the result
    if result == 'white_win':
        print("White wins the game!")
    elif result == 'black_win':
        print("Black wins the game!")
    elif result == 'draw':
        print("The game ended in a draw.")

if __name__ == "__main__":
    main()
