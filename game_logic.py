import copy
from pieces import Pawn, King, Queen
from utils import get_piece_info, position_to_indices, indices_to_position

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
                if isinstance(piece, Pawn):
                    is_valid = piece.valid_moves(board, start_pos, king_position, last_move)
                else:
                    is_valid = piece.valid_moves(board, start_pos, king_position)
                if is_valid:
                    return True  # King is in check

    return False  # King is not in check


import copy

def get_all_legal_moves(board, color, last_move):
    """
    Generates all legal moves for the player of the given color.

    Parameters:
    - board: The current state of the chessboard.
    - color: 'white' or 'black'.
    - last_move: A tuple (last_start_pos, last_end_pos) representing the opponent's last move.

    Returns:
    - A list of tuples (start_pos, end_pos) representing legal moves.
    """
    legal_moves = []

    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and piece.color == color:
                start_pos = indices_to_position(col, row)  # Ensure correct order
                # Generate all possible end positions for the piece
                for end_row in range(8):
                    for end_col in range(8):
                        end_pos = indices_to_position(end_col, end_row)  # Ensure correct order
                        # Check if the move is valid
                        if isinstance(piece, Pawn):
                            is_valid = piece.valid_moves(board, start_pos, end_pos, last_move)
                        else:
                            is_valid = piece.valid_moves(board, start_pos, end_pos)
                        if is_valid:
                            # Make a deep copy of the board to test the move
                            board_copy = copy.deepcopy(board)
                            # Get the piece on the copied board
                            piece_copy = board_copy[row][col]
                            # Simulate the move on the copied board
                            move_piece_simulation(board_copy, piece_copy, start_pos, end_pos, last_move)
                            # Update the last move for the simulation
                            simulated_last_move = (start_pos, end_pos)
                            # Check if the king would be in check after the move
                            if not is_in_check(board_copy, color, simulated_last_move):
                                legal_moves.append((start_pos, end_pos))

    return legal_moves

def check_game_status(board, color, last_move):
    """
    Determines the game status.

    Parameters:
    - board: The current state of the chessboard.
    - color: The color of the player to check ('white' or 'black').
    - last_move: A tuple (last_start_pos, last_end_pos) representing the last move made.

    Returns:
    - A tuple (is_over, result), where:
        - is_over: True if the game is over, False otherwise.
        - result: 'white_win', 'black_win', 'draw', or None if the game is not over.
    """
    # Check if the player is in check
    check = is_in_check(board, color, last_move)

    if check:
        # Check if the player has any legal moves
        legal_moves = get_all_legal_moves(board, color, last_move)
        if not legal_moves:
            # Player is in checkmate
            winner = 'black' if color == 'white' else 'white'
            # print(f"Checkmate! {winner.capitalize()} wins.")
            return True, f"{winner}_win"
    else:
        # Player is not in check but may have no legal moves (stalemate)
        legal_moves = get_all_legal_moves(board, color, last_move)

        if not legal_moves:
            # Stalemate
            print("Stalemate! The game is a draw.")
            return True, 'draw'

    # Game is not over
    return False, None


def move_piece(board, start_pos, end_pos, last_move):
    """
    Moves a piece from start_pos to end_pos if the move is valid.

    Parameters:
    - board: The current state of the chessboard.
    - start_pos: Starting position string (e.g., 'e2').
    - end_pos: Ending position string (e.g., 'e4').

    Returns:
    - True if the move was successful, False otherwise.
    """

    # Get the piece at start_pos
    piece_type, color = get_piece_info(board, start_pos)
    if piece_type is None:
        print(f"No piece at starting position {start_pos}")
        return False

    # Get the piece object from the board
    start_row, start_col = position_to_indices(start_pos)
    piece = board[start_row][start_col]

    # Check if the move is valid according to the piece's valid_moves function
    if isinstance(piece, Pawn):
        is_valid = piece.valid_moves(board, start_pos, end_pos, last_move)
    else:
        is_valid = piece.valid_moves(board, start_pos, end_pos)

    # Check if the move is valid according to the piece's valid_moves function
    if is_valid:
        # Move is valid, perform the move
        end_row, end_col = position_to_indices(end_pos)
        target_piece = board[end_row][end_col]

        # Handle en passant capture for pawn
        if isinstance(piece, Pawn):
            # En passant capture
            if abs(end_col - start_col) == 1 and board[end_row][end_col] is None:
                # The pawn moves diagonally to an empty square, possible en passant
                captured_row = start_row  # The pawn being captured is on the starting row
                captured_col = end_col
                captured_pawn = board[captured_row][captured_col]
                if isinstance(captured_pawn, Pawn) and captured_pawn.color != piece.color:
                    # Remove the captured pawn
                    board[captured_row][captured_col] = None
                    print(f"{piece.color.capitalize()} Pawn captures en passant at {indices_to_position(captured_col, captured_row)}")

        # Capture logic (if there's an opponent's piece at the destination)
        if target_piece and target_piece.color != piece.color:
            print(f"{color} {piece_type} captures {target_piece.color} {type(target_piece).__name__} at {end_pos}")
        elif target_piece:
            print(f"Cannot capture your own piece at {end_pos}")
            return False

        # Move the piece to end position
        board[end_row][end_col] = piece
        board[start_row][start_col] = None
        piece.set_position(end_pos)

        # Handle pawn promotion
        if isinstance(piece, Pawn):
            promotion_row = 0 if piece.color == 'white' else 7
            if end_row == promotion_row:
                # Pawn reaches the last rank, promotion occurs
                promoted_piece = piece.promote_pawn(piece.color, end_pos)
                board[end_row][end_col] = promoted_piece
                print(f"{piece.color.capitalize()} Pawn promoted to {type(promoted_piece).__name__} at {end_pos}")
            else:
                # Pawn did not promote, update has_moved
                piece.has_moved = True

        else:
            # If the piece has a 'has_moved' attribute (e.g., rook, king), set it to True
            if hasattr(piece, 'has_moved'):
                piece.has_moved = True

        print(f"{color} {piece_type} moved from {start_pos} to {end_pos}")
        return True
    else:
        print(f"Invalid move for {color} {piece_type} from {start_pos} to {end_pos}")
        return False

def move_piece_simulation(board, piece, start_pos, end_pos, last_move):
    """
    Simulates moving a piece on the board copy, including pawn promotion and en passant.

    Parameters:
    - board: The board copy on which to simulate the move.
    - piece: The piece to move.
    - start_pos: The starting position of the piece.
    - end_pos: The ending position of the piece.
    - last_move: A tuple representing the opponent's last move.

    Returns:
    - None
    """
    start_row, start_col = position_to_indices(start_pos)
    end_row, end_col = position_to_indices(end_pos)

    # Handle en passant capture
    if isinstance(piece, Pawn):
        if abs(end_col - start_col) == 1 and board[end_row][end_col] is None:
            # En passant capture
            captured_row = start_row
            captured_col = end_col
            board[captured_row][captured_col] = None

    # Move the piece
    board[end_row][end_col] = piece
    board[start_row][start_col] = None
    piece.position = end_pos

    # Handle pawn promotion
    if isinstance(piece, Pawn):
        promotion_row = 0 if piece.color == 'white' else 7
        if end_row == promotion_row:
            # Promote to Queen by default in simulation
            promoted_piece = Queen(piece.color, end_pos)
            board[end_row][end_col] = promoted_piece
        else:
            piece.has_moved = True
    elif hasattr(piece, 'has_moved'):
        piece.has_moved = True
