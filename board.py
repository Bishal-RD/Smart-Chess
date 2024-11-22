from pieces import *
from utils import position_to_indices

def print_board(board):
    """
    Prints the chessboard in standard chess notation.
    Rows are labeled 8 to 1 from top to bottom, and columns are labeled a to h.
    The (0, 0) position of the array corresponds to bottom-left, and (7, 7) is top-right.
    """
    # Print column labels (a-h)
    print("    " + " ".join('a b c d e f g h'.split()))
    print("  +" + "---" * 6 + "+")
    
    for row_idx in range(7, -1, -1):  # Start from 7 (row 8) to 0 (row 1)
        row = board[row_idx]
        rank = row_idx + 1  # Rank is row_idx + 1
        print(f"{rank} | " + " ".join(str(piece) if piece else '.' for piece in row) + " |")
    
    print("  +" + "---" * 6 + "+")
    # Print column labels again at the bottom
    print("    " + " ".join('a b c d e f g h'.split()))


def initialize_board(player_color):
    """
    Initializes the chessboard with pieces for the given player color.
    The player's color pieces are placed on ranks 1 and 2.
    The opponent's color pieces are placed on ranks 7 and 8.

    Parameters:
    - player_color (str): 'white' or 'black', representing the player's color.

    Returns:
    - board (list): 2D list representing the chessboard with pieces.
    """
    # Initialize an empty 8x8 board
    board = [[None for _ in range(8)] for _ in range(8)]

    # Determine the opponent's color
    opponent_color = 'white' if player_color == 'black' else 'black'

    # Player's pieces (a1-h1 for player_color)
    player_pieces = [
        Rook(player_color, 'a1'),
        Knight(player_color, 'b1'),
        Bishop(player_color, 'c1'),
        Queen(player_color, 'd1'),
        King(player_color, 'e1'),
        Bishop(player_color, 'f1'),
        Knight(player_color, 'g1'),
        Rook(player_color, 'h1'),
        Pawn(player_color, 'a2'),
        Pawn(player_color, 'b2'),
        Pawn(player_color, 'c2'),
        Pawn(player_color, 'd2'),
        Pawn(player_color, 'e2'),
        Pawn(player_color, 'f2'),
        Pawn(player_color, 'g2'),
        Pawn(player_color, 'h2'),
    ]

    # Opponent's pieces (a8-h8 for opponent_color)
    opponent_pieces = [
        Pawn(opponent_color, 'a7'),
        Pawn(opponent_color, 'b7'),
        Pawn(opponent_color, 'c7'),
        Pawn(opponent_color, 'd7'),
        Pawn(opponent_color, 'e7'),
        Pawn(opponent_color, 'f7'),
        Pawn(opponent_color, 'g7'),
        Pawn(opponent_color, 'h7'),
        Rook(opponent_color, 'a8'),
        Knight(opponent_color, 'b8'),
        Bishop(opponent_color, 'c8'),
        Queen(opponent_color, 'd8'),
        King(opponent_color, 'e8'),
        Bishop(opponent_color, 'f8'),
        Knight(opponent_color, 'g8'),
        Rook(opponent_color, 'h8'),
    ]

    # Combine all pieces
    all_pieces = player_pieces + opponent_pieces

    # Place each piece on the board according to its position
    for piece in all_pieces:
        position_str = piece.position  # e.g., 'e4'
        row, col = position_to_indices(position_str)
        board[row][col] = piece

    return board
