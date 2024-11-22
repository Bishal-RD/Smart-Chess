from pieces import *
from utils import position_to_indices

def board_to_fen(board, active_color='w', castling_rights='KQkq', en_passant='-', halfmove_clock=0, fullmove_number=1):
    """
    Converts the current board state to a FEN string.

    Args:
        board (list of list): The chessboard represented as an 8x8 list of lists.
                              Each element is either None or an instance of a Piece subclass.
        active_color (str): 'w' if white to move, 'b' if black to move.
        castling_rights (str): Castling availability (e.g., 'KQkq', 'Kq', '-').
        en_passant (str): En passant target square (e.g., 'e3'), or '-' if not available.
        halfmove_clock (int): Number of halfmoves since the last pawn advance or capture.
        fullmove_number (int): The number of full moves. It starts at 1 and increments after Black's move.

    Returns:
        str: The FEN string representing the board state.
    """
    # Helper mapping from Piece class to FEN character
    def piece_to_fen(piece):
        if piece is None:
            return ''
        piece_type = type(piece).__name__
        color = piece.color
        fen_char = ''
        if piece_type == 'King':
            fen_char = 'K'
        elif piece_type == 'Queen':
            fen_char = 'Q'
        elif piece_type == 'Rook':
            fen_char = 'R'
        elif piece_type == 'Bishop':
            fen_char = 'B'
        elif piece_type == 'Knight':
            fen_char = 'N'
        elif piece_type == 'Pawn':
            fen_char = 'P'
        else:
            raise ValueError(f"Unknown piece type: {piece_type}")

        return fen_char.upper() if color == 'white' else fen_char.lower()

    fen_rows = []
    for row in board:
        fen_row = ''
        empty_count = 0
        for cell in row:
            if cell is None:
                empty_count += 1
            else:
                if empty_count > 0:
                    fen_row += str(empty_count)
                    empty_count = 0
                fen_row += piece_to_fen(cell)
        if empty_count > 0:
            fen_row += str(empty_count)
        fen_rows.append(fen_row)
    
    piece_placement = '/'.join(fen_rows)
    fen = f"{piece_placement} {active_color} {castling_rights} {en_passant} {halfmove_clock} {fullmove_number}"
    return fen


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


def initialize_board(fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
    """
    Initializes the chessboard based on a FEN string.
    
    Args:
        fen (str, optional): Forsyth-Edwards Notation string representing the board state.
                             Defaults to the standard starting position.
                             
    Returns:
        list: 8x8 list of lists representing the chessboard with Piece instances or None.
    """
    # Initialize an empty 8x8 board
    board = [[None for _ in range(8)] for _ in range(8)]
    
    # Split the FEN string into its components
    fen_parts = fen.split(' ')
    if len(fen_parts) != 6:
        raise ValueError("Invalid FEN string: Incorrect number of fields.")
    
    piece_placement, active_color, castling, en_passant, halfmove_clock, fullmove_number = fen_parts
    
    # Split the piece placement into ranks
    ranks = piece_placement.split('/')
    if len(ranks) != 8:
        raise ValueError("Invalid FEN string: Incorrect number of ranks.")
    
    # Iterate over each rank and place pieces on the board
    for i, rank_str in enumerate(ranks):
        row = 7 - i  # FEN starts from rank 8 (row 7) to rank 1 (row 0)
        col = 0
        for char in rank_str:
            if char.isdigit():
                # Empty squares
                empty_squares = int(char)
                col += empty_squares
            elif char.isalpha():
                # Place the corresponding piece
                color = 'white' if char.isupper() else 'black'
                piece_char = char.upper()
                position = indices_to_position(row, col)
                
                if piece_char == 'K':
                    piece = King(color, position)
                elif piece_char == 'Q':
                    piece = Queen(color, position)
                elif piece_char == 'R':
                    piece = Rook(color, position)
                elif piece_char == 'B':
                    piece = Bishop(color, position)
                elif piece_char == 'N':
                    piece = Knight(color, position)
                elif piece_char == 'P':
                    piece = Pawn(color, position)
                else:
                    raise ValueError(f"Invalid piece character in FEN: {char}")
                
                board[row][col] = piece
                col += 1
            else:
                raise ValueError(f"Invalid character in FEN piece placement: {char}")
    
    return board
