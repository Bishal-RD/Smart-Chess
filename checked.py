from utils import indices_to_position

def is_square_attacked(board, pos, color, last_move):
    """
    Checks if a square is attacked by any opponent piece.

    Parameters:
    - board: The current state of the chessboard.
    - pos: The position to check (e.g., 'e4').
    - color: The color of the player (e.g., 'white' or 'black').
    - last_move: The last move made in the game.

    Returns:
    - True if the square is attacked by an opponent's piece, False otherwise.
    """
    
    from pieces import Pawn
    
    opponent_color = 'black' if color == 'white' else 'white'
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and piece.color == opponent_color:
                start_pos = indices_to_position(col, row)
                if isinstance(piece, Pawn):
                    is_valid = piece.valid_moves(board, start_pos, pos, last_move)
                else:
                    is_valid = piece.valid_moves(board, start_pos, pos, last_move)
                if is_valid:
                    return True
    return False


def is_in_check(board, color, last_move):
    """
    Determines if the king of the given color is in check.

    Parameters:
    - board: The current state of the chessboard.
    - color: 'white' or 'black'.
    - last_move: A tuple (last_start_pos, last_end_pos) representing the opponent's last move.

    Returns:
    - True if the king is in check, False otherwise.
    """
    from pieces import King
    
    # Find the king's position
    king_position = None
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and isinstance(piece, King) and piece.color == color:
                king_position = indices_to_position(col, row)
                break
        if king_position:
            break

    if not king_position:
        # The king is not on the board (should not happen in a normal game)
        return True

    # Get opponent's color
    opponent_color = 'black' if color == 'white' else 'white'

    return is_square_attacked(board, king_position, color, last_move)