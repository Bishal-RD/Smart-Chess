from pieces import *
from utils import position_to_indices

# Now you can print the board to verify
def print_board(board):
    print("   " + " ".join('a b c d e f g h'.split()))
    print("-"*18)
    for row_idx in range(7, -1, -1):
        rank = row_idx + 1
        row = board[row_idx]
        print(f"{rank}| " + " ".join(str(piece) if piece else '.' for piece in row))

    # Print horizontal indices ('a' to 'h')
    print("-"*18)
    print("   " + " ".join('a b c d e f g h'.split()))

def initialize_board():

    # Initialize an empty 8x8 board
    board = [[None for _ in range(8)] for _ in range(8)]

    # Create all the pieces with their positions
    all_pieces = [
        # White pieces (ranks 1-2)
        Rook('white', 'a1'),
        Knight('white', 'b1'),
        Bishop('white', 'c1'),
        Queen('white', 'd1'),
        King('white', 'e1'),
        Bishop('white', 'f1'),
        Knight('white', 'g1'),
        Rook('white', 'h1'),
        Pawn('white', 'a2'),
        Pawn('white', 'b2'),
        Pawn('white', 'c2'),
        Pawn('white', 'd2'),
        Pawn('white', 'e2'),
        Pawn('white', 'f2'),
        Pawn('white', 'g2'),
        Pawn('white', 'h2'),
        # Black pieces (ranks 7-8)
        Pawn('black', 'a7'),
        Pawn('black', 'b7'),
        Pawn('black', 'c7'),
        Pawn('black', 'd7'),
        Pawn('black', 'e7'),
        Pawn('black', 'f7'),
        Pawn('black', 'g7'),
        Pawn('black', 'h7'),
        Rook('black', 'a8'),
        Knight('black', 'b8'),
        Bishop('black', 'c8'),
        Queen('black', 'd8'),
        King('black', 'e8'),
        Bishop('black', 'f8'),
        Knight('black', 'g8'),
        Rook('black', 'h8'),
    ]

    # Place each piece on the board according to its position
    for piece in all_pieces:
        position_str = piece.position  # e.g., 'e4'
        row, col = position_to_indices(position_str)
        # print(position_str, row, col)
        board[row][col] = piece

    return board