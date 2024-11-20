# Define the position_to_indices function
def position_to_indices(position):
    """
    Convert chessboard position (e.g., 'a1') to indices (row, col).
    'a1' corresponds to (0, 0) and 'h8' corresponds to (7, 7).

    :param position: The chessboard position as a string (e.g., 'a1').
    :return: A tuple of (row, col) indices.
    """
    col = ord(position[0].lower()) - ord('a')  # Convert column 'a'-'h' to 0-7
    row = int(position[1]) - 1  # Convert row '1'-'8' to 0-7
    return row, col

def indices_to_position(col, row):
    """
    :param indices: A tuple of (row, col) indices.
    :return: The chessboard position as a string (e.g., 'a1').
    """
    col_letter = chr(col + ord('a'))  # Convert column index (0-7) to letter ('a'-'h')
    row_number = str(row + 1)        # Convert row index (0-7) to number ('1'-'8')
    return col_letter + row_number


def get_piece_info(board, position_str):
    """
    Returns the type and color of the piece at the given position.

    Parameters:
    - board: The current state of the chessboard.
    - position_str: A string representing the position (e.g., 'e4').

    Returns:
    - (piece_type, color): Tuple containing the subclass name and color.
      Returns (None, None) if there's no piece at the position.
    """
    # Convert position string to board indices
    try:
        row, col = position_to_indices(position_str)
    except ValueError as e:
        print(e)
        return None, None

    # Access the piece at the given position
    piece = board[row][col]

    if piece:
        # Get the subclass name (piece type)
        piece_type = type(piece).__name__
        # Get the color of the piece
        color = piece.color
        return piece_type, color
    else:
        # No piece at this position
        return None, None
    
def move_piece(board, start_pos, end_pos):
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

    check = piece.valid_moves(board, start_pos, end_pos)

    # Check if the move is valid according to the piece's valid_moves function
    if check:
        # Move is valid, perform the move
        end_row, end_col = position_to_indices(end_pos)
        target_piece = board[end_row][end_col]

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

        # If the piece has a 'has_moved' attribute (e.g., pawn), set it to True
        if hasattr(piece, 'has_moved'):
            piece.has_moved = True

        print(f"{color} {piece_type} moved from {start_pos} to {end_pos}")
        return True
    else:
        print(f"Invalid move for {color} {piece_type} from {start_pos} to {end_pos}")
        return False
