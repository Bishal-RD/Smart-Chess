import numpy as np  # NumPy for array computations
import chess.pgn
from tqdm import tqdm  # For progress bar
import pickle

def extract_positions_and_labels(pgn_file, max_games=50000):
    """
    Extract positions and labels from a PGN file.
    Each move alternates between Player 1 and Player 2, and is labeled accordingly.
    Args:
        pgn_file (str): Path to the PGN file.
        max_games (int, optional): Maximum number of games to process.
    Returns:
        tuple: List of positions (FEN strings) and labels (results).
    """
    positions = []
    labels = []
    game_count = 0

    # Read games and extract positions with tqdm for progress tracking
    with tqdm(desc="Parsing PGN file", total=max_games) as pbar:
        while True:
            # Read a game from the PGN file
            game = chess.pgn.read_game(pgn_file)
            if game is None:  # No more games to read
                break

            board = game.board()  # Initialize a new board
            moves = list(game.mainline_moves())  # Extract moves
            result = game.headers.get("Result", "*")

            # Determine labeling based on the result
            if result == "1-0":
                labels_mapping = [1 if i % 2 == 0 else 0 for i in range(len(moves))]
            elif result == "0-1":
                labels_mapping = [0 if i % 2 == 0 else 1 for i in range(len(moves))]
            elif result == "1/2-1/2":
                labels_mapping = [0.5] * len(moves)
            else:
                # Skip games without a clear result
                continue

            # Process moves and assign labels
            for move, label in zip(moves, labels_mapping):
                board.push(move)  # Apply move to the board
                positions.append(board.fen())  # Save the board state in FEN format
                labels.append(label)  # Assign the move's label

            game_count += 1
            pbar.update(1)

            # Stop if we reach the max_games limit
            if game_count >= max_games:
                break

    return positions, labels


def fen_to_input(fen):
    """
    Convert FEN string to a numerical representation.
    Args:
        fen (str): FEN string.
    Returns:
        numpy.ndarray: 8x8x12 array representation of the board.
    """
    board_array = np.zeros((8, 8, 12), dtype=np.float32)  # CPU array
    piece_map = {
        "p": 0, "n": 1, "b": 2, "r": 3, "q": 4, "k": 5,  # Black pieces
        "P": 6, "N": 7, "B": 8, "R": 9, "Q": 10, "K": 11  # White pieces
    }
    board = fen.split(" ")[0]
    for row_idx, row in enumerate(board.split("/")):
        col_idx = 0
        for char in row:
            if char.isdigit():
                col_idx += int(char)  # Empty squares
            else:
                piece_idx = piece_map[char]
                board_array[row_idx, col_idx, piece_idx] = 1
                col_idx += 1
    return board_array


if __name__ == "__main__":
    # File paths for .pkl files
    dataset_file = "C:/Users/User/Desktop/AI/Projects/Smart-Chess/model_training/Datasets/split_data_50k.pkl"

    try:
        # Check if the dataset has already been processed and saved
        with open(dataset_file, "rb") as file:
            data = pickle.load(file)
            positions = data["positions"]
            labels = data["labels"]
            print("Datasets loaded successfully from .pkl file!")
    except FileNotFoundError:
        print("No preprocessed dataset found. Processing from scratch...")

        # Load PGN file and process games
        pgn_path = "C:/Users/User/Desktop/AI/Projects/Smart-Chess/model_training/Datasets/lichess_db_standard_rated_2014-12.pgn"
        with open(pgn_path) as pgn_file:
            positions, labels = extract_positions_and_labels(pgn_file)

        # Save positions and labels to a .pkl file
        print("Saving processed dataset...")
        with open(dataset_file, "wb") as file:
            pickle.dump({"positions": positions, "labels": labels}, file)
        print("Dataset saved successfully!")

    # Example to check the output
    for position, label in zip(positions[:5], labels[:5]):
        print(f"Label: {label}")
        print(position)
        print("-" * 50)
