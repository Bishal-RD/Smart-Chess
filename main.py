from utils import get_piece_info
from game_logic import move_piece
from board import initialize_board, print_board, board_to_fen
from game_logic import check_game_status
# from deep_algo import minimax
from algorithm import minimax
from encoder_decoder import decode_move, encode_move
from generate_pgn import generate_pgn, save_pgn
from model import ChessEvaluationModel
import torch

def main():
    print("Welcome to the Chess Game!")
    
    human_color = 'white'  # Human plays white
    ai_color = 'black'     # AI plays black
    turn = 'white'         # White starts first
    last_move = None  # Keep track of the last move
    ai_last_move = None  # Keep track of the last move for the AI

    user_moves = []
    ai_moves = []

    model_path = "C:/Users/User/Desktop/AI/Projects/Smart-Chess/models/new_model_670.pth"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(device)

    model = ChessEvaluationModel().to(device)
    # Load the model weights
    state_dict = torch.load(model_path, map_location=device, weights_only=True)  # Explicitly set weights_only=True
    model.load_state_dict(state_dict)

    board = initialize_board()
    print_board(board)

    while True:
        fen = board_to_fen(board)
        # print("FEN:", fen)

        print(f"\n{turn.capitalize()}'s turn")
        # Check if the game is over before the player's move
        game_over, result = check_game_status(board, turn, last_move=last_move)

        if game_over:
            break

        if turn == human_color:
            move_input = input("Enter your move (e.g., e4) or 'q' to quit: ")

            # Check if the user wants to quit
            if move_input.lower() == 'q':
                result = "*"
                print("Thank you for playing!")
                break

            user_moves.append(move_input)
            move_input = decode_move(move_input, board, player='white', last_move=last_move)
            # print(move_input)

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
            evaluation, ai_move = minimax(board, depth=5, alpha=float('-inf'), beta=float('inf'),
                                          maximizing_player=True, current_color=ai_color, last_move=ai_last_move, model=model)
            if ai_move:
                encode_ai = encode_move(ai_move, board, player='black')
                # print(encode_ai)
                ai_moves.append(encode_ai)
                
                # Execute the AI's move
                start_pos, end_pos = ai_move
                move_piece(board, start_pos, end_pos, ai_last_move)
                # Update the last move
                ai_last_move = (start_pos, end_pos)
                print_board(board)
                # Switch turns
                turn = human_color
            else:
                print("AI has no valid moves. Game over.")
                break

    # After game over, display the result
    if result == '1-0':
        print("White wins the game!")
    elif result == '0-1':
        print("Black wins the game!")
    elif result == '1/2-1/2':
        print("The game ended in a draw.")

    pgn = generate_pgn(user_moves, ai_moves, result)
    print("\nGame in Portable Game Notation (PGN):")
    print(pgn)
    save_pgn(pgn)

    # Release the model
    del model

if __name__ == "__main__":
    main()
