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
