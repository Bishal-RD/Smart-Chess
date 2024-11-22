import cupy as cp  # NVIDIA cuPy for GPU computation
import chess.pgn
from sklearn.model_selection import train_test_split
from tqdm import tqdm  # For progress bar
import pickle

def extract_positions_and_labels(pgn_file):
    """
    Extract positions and labels from a PGN file.
    Args:
        pgn_file (str): Path to the PGN file.
    Returns:
        tuple: List of positions (FEN strings) and labels (results).
    """
    positions = []
    labels = []

    # Read games and extract positions with tqdm for progress tracking
    with tqdm(desc="Parsing PGN file", total=None) as pbar:
        while True:
            game = chess.pgn.read_game(pgn_file)
            if game is None:
                break

            board = game.board()
            result = game.headers["Result"]
            if result == "1-0":
                label = 1  # White wins
            elif result == "0-1":
                label = 0  # Black wins
            else:
                label = 0.5  # Draw

            for move in game.mainline_moves():
                board.push(move)
                positions.append(board.fen())  # Save board state in FEN format
                labels.append(label)

            pbar.update(1)

    return positions, labels

def fen_to_input(fen):
    """
    Convert FEN string to a GPU-accelerated numerical representation.
    Args:
        fen (str): FEN string.
    Returns:
        cupy.ndarray: 8x8x12 array representation of the board.
    """
    board_array = cp.zeros((8, 8, 12), dtype=cp.float32)  # GPU array
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
    dataset_file = "C:/Users/User/Desktop/AI/Projects/Smart-Chess/model_training/Datasets/split_data.pkl"

    try:
        # Check if the dataset has already been processed and saved
        with open(dataset_file, "rb") as file:
            data = pickle.load(file)
            X_train = data["X_train"]
            X_test = data["X_test"]
            y_train = data["y_train"]
            y_test = data["y_test"]
            print("Datasets loaded successfully from .pkl file!")
    except FileNotFoundError:
        print("No preprocessed dataset found. Processing from scratch...")

        # Load data
        with open("C:/Users/User/Desktop/AI/Projects/Smart-Chess/model_training/Datasets/lichess_db_standard_rated_2014-12.pgn") as pgn:
            positions, labels = extract_positions_and_labels(pgn)

        # Convert all positions with GPU acceleration and tqdm progress bar
        print("Converting positions to numerical representation...")
        inputs = cp.array([fen_to_input(fen) for fen in tqdm(positions, desc="Processing positions")], dtype=cp.float32)
        labels = cp.array(labels, dtype=cp.float32)

        # Split data
        print("Splitting dataset...")
        X_train, X_test, y_train, y_test = train_test_split(inputs, labels, test_size=0.2, random_state=42)

        # Save the split data to a .pkl file
        print("Saving preprocessed dataset...")
        with open(dataset_file, "wb") as file:
            pickle.dump({
                "X_train": cp.asnumpy(X_train),
                "X_test": cp.asnumpy(X_test),
                "y_train": cp.asnumpy(y_train),
                "y_test": cp.asnumpy(y_test)
            }, file)

        print("Datasets saved successfully as .pkl file!")
