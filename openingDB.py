import json
import chess.pgn
from collections import defaultdict

# Example usage
def get_opening_moves(fen):  
    # Load the opening book from the JSON file
    with open('opening_book_20000.json', 'r') as json_file:
        opening_book = json.load(json_file)

    return opening_book.get(fen, [])

def convert_move_to_tuple(move):
    """
    Converts a chess move notation (e.g., 'e2e4') into a tuple of start and end positions.

    Parameters:
        move (str): The move in chess notation, e.g., 'e2e4'.

    Returns:
        tuple: A tuple of the start and end positions, e.g., ('e2', 'e4').
    """
    if len(move) != 4:
        raise ValueError("Invalid move format. Must be exactly 4 characters, e.g., 'e2e4'.")
    
    start = move[:2]  # First two characters (e.g., 'e2')
    end = move[2:]    # Last two characters (e.g., 'e4')
    return (start, end)


if __name__ == "__main__":

    # Path to your PGN file
    pgn_path = 'C:/Users/User/Desktop/AI/Projects/Smart-Chess/model_training/Datasets/lichess_db_standard_rated_2014-12.pgn'

    opening_book = defaultdict(list)

    max_games = 20000
    game_count = 0

    # Open the PGN file and process the games
    with open(pgn_path) as pgn_file:
        game = chess.pgn.read_game(pgn_file)
        while game and game_count < max_games:
            board = game.board()
            for move in game.mainline_moves():
                fen_before_move = board.fen()  # FEN before the move
                board.push(move)
                fen_after_move = board.fen()  # FEN after the move
                
                # Store the opponent's move for the previous FEN
                opening_book[fen_before_move].append(str(move))
            
            game_count += 1
            game = chess.pgn.read_game(pgn_file)

        print(f"Processed {game_count} games.")

    # Save the opening book to a JSON file
    with open(f'opening_book_{game_count}.json', 'w') as json_file:
        json.dump(opening_book, json_file)
