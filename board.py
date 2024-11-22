from pieces import *
from utils import position_to_indices

# Now you can print the board to verify
def print_board(board):
    print("   " + " ".join('a b c d e f g h'.split()))
    print("-"*18)
    for row_idx, row in enumerate(board):
        rank = row_idx + 1  # Convert row index to rank
        print(f"{rank}| " + " ".join(str(piece) if piece else '.' for piece in row))

    # Print horizontal indices ('a' to 'h')
    print("-"*18)
    print("   " + " ".join('a b c d e f g h'.split()))

def initialize_board():

    # Initialize an empty 8x8 board
    board = [[None for _ in range(8)] for _ in range(8)]

    # Create all the pieces with their positions
    all_pieces = [
        # Black pieces
        Rook('black', 'a1'),
        Knight('black', 'b1'),
        Bishop('black', 'c1'),
        Queen('black', 'd1'),
        King('black', 'e1'),
        Bishop('black', 'f1'),
        Knight('black', 'g1'),
        Rook('black', 'h1'),
        Pawn('black', 'a2'),
        Pawn('black', 'b2'),
        Pawn('black', 'c2'),
        Pawn('black', 'd2'),
        Pawn('black', 'e2'),
        Pawn('black', 'f2'),
        Pawn('black', 'g2'),
        Pawn('black', 'h2'),
        # White pieces
        Pawn('white', 'a7'),
        Pawn('white', 'b7'),
        Pawn('white', 'c7'),
        Pawn('white', 'd7'),
        Pawn('white', 'e7'),
        Pawn('white', 'f7'),
        Pawn('white', 'g7'),
        Pawn('white', 'h7'),
        Rook('white', 'a8'),
        # Knight('white', 'b8'),
        # Bishop('white', 'c8'),
        # Queen('white', 'd8'),
        King('white', 'e8'),
        # Bishop('white', 'f8'),
        # Knight('white', 'g8'),
        Rook('white', 'h8'),
    ]

    # Place each piece on the board according to its position
    for piece in all_pieces:
        position_str = piece.position  # e.g., 'e4'
        row, col = position_to_indices(position_str)
        # print(position_str, row, col)
        board[row][col] = piece

    return board