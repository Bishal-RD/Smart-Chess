from utils import indices_to_position, position_to_indices
from pieces import Pawn

def get_move_weight(board, move):
    """
    Assigns a weight to a move based on heuristics.
    Capturing higher-value pieces gets higher weight.
    
    Parameters:
    - board: The current state of the chessboard.
    - move: A tuple (start_pos, end_pos) representing the move.
    
    Returns:
    - An integer representing the weight of the move.
    """
    piece_values = {
        'Pawn': 1,
        'Knight': 3,
        'Bishop': 3,
        'Rook': 5,
        'Queen': 9,
        'King': 0  # Capturing the king is not possible
    }
    start_pos, end_pos = move
    start_row, start_col = position_to_indices(start_pos)
    end_row, end_col = position_to_indices(end_pos)
    piece = board[start_row][start_col]
    target_piece = board[end_row][end_col]
    weight = 1  # Default weight for non-capture moves
    
    if target_piece and target_piece.color != piece.color:
        # Capture move
        target_piece_type = type(target_piece).__name__
        capture_value = piece_values.get(target_piece_type, 0)
        weight += capture_value  # Higher weight for capturing valuable pieces
    # Additional heuristics can be added here
    return weight

def get_attackers(board, position, opponent_color, last_move):
    """
    Returns a list of opponent pieces that can attack the given position.

    Parameters:
    - board: The current state of the chessboard.
    - position: Tuple (row, col) of the position to check.
    - opponent_color: The opponent's color.

    Returns:
    - A list of opponent pieces attacking the position.
    """
    attackers = []
    row, col = position
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece and piece.color == opponent_color:
                start_pos = indices_to_position(r, c)
                end_pos = indices_to_position(row, col)
                if isinstance(piece, Pawn):
                    is_valid = piece.valid_moves(board, start_pos, end_pos, last_move)
                else:
                    is_valid = piece.valid_moves(board, start_pos, end_pos)
                if is_valid:
                    attackers.append(piece)
    return attackers

def evaluate_pawn_structure(board, color, own_pawns):
    """
    Evaluates the pawn structure for the given color.

    Parameters:
    - board: The current state of the chessboard.
    - color: 'white' or 'black'.
    - own_pawns: List of positions (row, col) of own pawns.

    Returns:
    - A numerical value representing the pawn structure evaluation.
    """
    score = 0
    columns_with_pawns = {}

    for row, col in own_pawns:
        # Check for doubled pawns
        if col in columns_with_pawns:
            # Found a doubled pawn
            score -= 20  # Penalty for doubled pawn
        else:
            columns_with_pawns[col] = True

        # Check for isolated pawns
        is_isolated = True
        for offset in [-1, 1]:
            neighbor_col = col + offset
            if 0 <= neighbor_col <= 7:
                if any(pawn_col == neighbor_col for _, pawn_col in own_pawns):
                    is_isolated = False
                    break
        if is_isolated:
            score -= 10  # Penalty for isolated pawn

        # Check for passed pawns
        is_passed = True
        for opponent_row in range(8):
            for offset in [-1, 0, 1]:
                opponent_col = col + offset
                if 0 <= opponent_col <= 7:
                    opponent_piece = board[opponent_row][opponent_col]
                    if opponent_piece and opponent_piece.color != color and isinstance(opponent_piece, Pawn):
                        # Opponent pawn blocks our pawn
                        is_passed = False
                        break
            if not is_passed:
                break
        if is_passed:
            score += 20  # Bonus for passed pawn

    return score

def evaluate_king_safety(board, color, king_position, last_move):
    """
    Evaluates the king safety for the given color.

    Parameters:
    - board: The current state of the chessboard.
    - color: 'white' or 'black'.
    - king_position: Tuple (row, col) of the king's position.

    Returns:
    - A numerical value representing the king safety evaluation.
    """
    if king_position is None:
        # King is missing, game should be over
        return -10000

    row, col = king_position
    safety_score = 0

    # Check for pawn shield around the king
    pawn_shield_rows = [row + 1] if color == 'white' else [row - 1]
    for shield_row in pawn_shield_rows:
        for shield_col in [col - 1, col, col + 1]:
            if 0 <= shield_row <= 7 and 0 <= shield_col <= 7:
                piece = board[shield_row][shield_col]
                if not (piece and piece.color == color and isinstance(piece, Pawn)):
                    safety_score -= 10  # Penalty for missing pawn shield

    # Penalize exposed king
    safety_score -= len(get_attackers(board, king_position, 'black' if color == 'white' else 'white', last_move=last_move)) * 50

    return safety_score

def evaluate_center_control(board, color):
    """
    Evaluates the control of the center squares.

    Parameters:
    - board: The current state of the chessboard.
    - color: 'white' or 'black'.

    Returns:
    - A numerical value representing the center control evaluation.
    """
    center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
    score = 0

    for row, col in center_squares:
        piece = board[row][col]
        if piece:
            if piece.color == color:
                score += 20  # Bonus for controlling center square
            else:
                score -= 20  # Penalty if opponent controls center square

    return score

