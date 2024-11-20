from utils import indices_to_position
from pieces import King

def is_in_check(board, color):
    """
    Determines if the king of the given color is in check.

    Parameters:
    - board: The current state of the chessboard.
    - color: 'white' or 'black'.

    Returns:
    - True if the king is in check, False otherwise.
    """
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

    # Check if any opponent piece can move to the king's position
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and piece.color == opponent_color:
                start_pos = indices_to_position(col, row)
                if piece.valid_moves(board, start_pos, king_position):
                    return True  # King is in check

    return False  # King is not in check


def get_all_legal_moves(board, color):
    """
    Generates all legal moves for the player of the given color.

    Parameters:
    - board: The current state of the chessboard.
    - color: 'white' or 'black'.

    Returns:
    - A list of tuples (start_pos, end_pos) representing legal moves.
    """
    legal_moves = []

    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and piece.color == color:
                start_pos = indices_to_position(col, row)
                # Generate all possible end positions for the piece
                for end_row in range(8):
                    for end_col in range(8):
                        end_pos = indices_to_position(end_col, end_row)
                        # Check if the move is valid
                        if piece.valid_moves(board, start_pos, end_pos):
                            # Make a copy of the board to test the move
                            board_copy = [row[:] for row in board]
                            # Move the piece on the copy
                            board_copy[end_row][end_col] = piece
                            board_copy[row][col] = None
                            # Update piece position temporarily
                            original_position = piece.position
                            piece.set_position(end_pos)
                            # Check if the king would be in check after the move
                            if not is_in_check(board_copy, color):
                                legal_moves.append((start_pos, end_pos))
                            # Restore the piece's original position
                            piece.set_position(original_position)

    return legal_moves

def check_game_status(board, color):
    """
    Determines the game status.

    Parameters:
    - board: The current state of the chessboard.
    - color: The color of the player to check ('white' or 'black').

    Returns:
    - A tuple (is_over, result), where:
        - is_over: True if the game is over, False otherwise.
        - result: 'white_win', 'black_win', 'draw', or None if the game is not over.
    """
    if is_in_check(board, color):
        # Check if the player has any legal moves
        legal_moves = get_all_legal_moves(board, color)
        if not legal_moves:
            # Player is in checkmate
            winner = 'black' if color == 'white' else 'white'
            print(f"Checkmate! {winner.capitalize()} wins.")
            return True, f"{winner}_win"
    else:
        # Player is not in check but may have no legal moves (stalemate)
        legal_moves = get_all_legal_moves(board, color)
        if not legal_moves:
            # Stalemate
            print("Stalemate! The game is a draw.")
            return True, 'draw'

    # Game is not over
    return False, None