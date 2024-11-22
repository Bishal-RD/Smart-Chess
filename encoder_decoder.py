# translator.py

import re
from utils import position_to_indices, indices_to_position, get_piece_info
from pieces import King, Queen, Rook, Bishop, Knight, Pawn

def piece_class_name(piece_letter):
    """
    Returns the full class name of the piece based on the letter.

    Args:
        piece_letter (str): The piece letter (e.g., 'N', 'Q').

    Returns:
        str: The full class name (e.g., 'Knight', 'Queen').
    """
    class_map = {
        'K': 'King',
        'Q': 'Queen',
        'R': 'Rook',
        'B': 'Bishop',
        'N': 'Knight',
        'P': 'Pawn'
    }
    return class_map.get(piece_letter, 'Pawn')

def decode_move(move, board, player='white', last_move=None):
    """
    Translates a standard chess move notation into start and end coordinates.

    Args:
        move (str): The chess move in standard algebraic notation (e.g., 'e4', 'Nf3', 'O-O').
        board (list of lists): The current state of the chessboard.
        player (str): 'white' or 'black' indicating which player is making the move.
        last_move (tuple): The last move made, formatted as (start_pos, end_pos). Useful for en passant.

    Returns:
        str: The start and end positions in algebraic notation (e.g., 'e2 e4'), or an error message.
    """
    # Handle castling
    if move in ['O-O', '0-0']:
        if player == 'white':
            return 'e1 g1'  # White kingside castling
        else:
            return 'e8 g8'  # Black kingside castling
    elif move in ['O-O-O', '0-0-0']:
        if player == 'white':
            return 'e1 c1'  # White queenside castling
        else:
            return 'e8 c8'  # Black queenside castling

    # Regular expression to parse the move, including promotion
    # Pattern breakdown:
    # ^(?P<piece>[KQRBN]?) - Optional piece letter
    # (?P<from_file>[a-h]?) - Optional origin file
    # (?P<from_rank>[1-8]?) - Optional origin rank
    # (?P<capture>x?) - Optional capture 'x'
    # (?P<to_file>[a-h]) - Destination file
    # (?P<to_rank>[1-8]) - Destination rank
    # (?:=(?P<promotion_piece>[QRBN]))? - Optional promotion e.g., =Q
    # (?P<check>[+#]?)$ - Optional check or mate indicator
    pattern = r'^(?P<piece>[KQRBN]?)(?P<from_file>[a-h]?)(?P<from_rank>[1-8]?)(?P<capture>x?)(?P<to_file>[a-h])(?P<to_rank>[1-8])(?:=(?P<promotion_piece>[QRBN]))?(?P<check>[+#]?)$'
    match = re.match(pattern, move)

    if not match:
        if move == 'q':
            return 'q'
        return f"Invalid move notation: {move}"

    groups = match.groupdict()

    piece = groups['piece'] if groups['piece'] else 'P'  # Default to Pawn if no piece is specified
    from_file = groups['from_file']
    from_rank = groups['from_rank']
    to_square = groups['to_file'] + groups['to_rank']
    capture = groups['capture'] == 'x'
    promotion_piece = groups.get('promotion_piece')
    check = groups['check']

    # Map piece letters to classes
    piece_map = {
        'K': King,
        'Q': Queen,
        'R': Rook,
        'B': Bishop,
        'N': Knight,
        'P': Pawn  # Although 'P' is not explicitly used, it's for default pawn moves
    }

    PieceClass = piece_map.get(piece, Pawn)  # Default to Pawn

    # Collect all pieces of the player that match the piece type
    possible_pieces = []
    for row in range(8):
        for col in range(8):
            current_piece = board[row][col]
            if current_piece is not None and current_piece.color == player:
                if isinstance(current_piece, PieceClass):
                    possible_pieces.append(current_piece)

    # If there's disambiguation in the move, filter the possible pieces
    if from_file:
        possible_pieces = [p for p in possible_pieces if p.position[0] == from_file]
    if from_rank:
        possible_pieces = [p for p in possible_pieces if p.position[1] == from_rank]

    # Now, for each possible piece, check if it can move to the target square
    valid_moves = []
    for piece_instance in possible_pieces:
        if piece_instance.valid_moves(board, piece_instance.position, to_square, last_move):
            valid_moves.append(piece_instance.position)

    if len(valid_moves) == 1:
        start_pos = valid_moves[0]
        end_pos = to_square

        # Handle promotion if applicable
        if promotion_piece:
            # Replace the pawn with the promoted piece
            promotion_map = {
                'Q': Queen,
                'R': Rook,
                'B': Bishop,
                'N': Knight
            }
            PromotionClass = promotion_map.get(promotion_piece, Queen)  # Default to Queen

            promoted_piece = PromotionClass(player, end_pos)

            # Update the board: place the promoted piece and remove the pawn
            end_row, end_col = position_to_indices(end_pos)
            board[end_row][end_col] = promoted_piece

            start_row, start_col = position_to_indices(start_pos)
            board[start_row][start_col] = None

        return f"{start_pos} {end_pos}"
    elif len(valid_moves) > 1:
        # Ambiguous move: multiple pieces can perform the move
        return f"Ambiguous move: {move}. Possible starting squares: {', '.join(valid_moves)}"
    else:
        # No valid piece found to perform the move
        return f"No valid {piece_class_name(piece)} can perform the move: {move}"

def encode_move(ai_move, board, player='black'):
    """
    Encodes an AI-generated move from coordinate pairs to standard algebraic notation.
    
    Args:
        ai_move (tuple): A tuple containing (start_pos, end_pos), e.g., ('c8', 'd7').
        board (list of lists): The current state of the chessboard.
        player (str, optional): The player making the move ('white' or 'black'). Defaults to 'black'.
        
    Returns:
        str: The move in standard algebraic notation, e.g., 'Bd7'.
    """
    start_pos, end_pos = ai_move
    piece_type, color = get_piece_info(board, start_pos)
    
    if piece_type is None:
        return f"Error: No piece at starting position {start_pos}."
    
    # Handle Castling
    if piece_type == 'King':
        if player == 'white' and start_pos == 'e1' and end_pos == 'g1':
            return 'O-O'
        elif player == 'white' and start_pos == 'e1' and end_pos == 'c1':
            return 'O-O-O'
        elif player == 'black' and start_pos == 'e8' and end_pos == 'g8':
            return 'O-O'
        elif player == 'black' and start_pos == 'e8' and end_pos == 'c8':
            return 'O-O-O'
    
    # Determine if the move is a capture
    target_piece_type, target_color = get_piece_info(board, end_pos)
    is_capture = target_piece_type is not None and target_color != player
    
    # Handle Promotion
    promotion = ''
    if piece_type == 'Pawn':
        end_row, _ = position_to_indices(end_pos)
        if (player == 'white' and end_row == 7) or (player == 'black' and end_row == 0):
            # Assume promotion to Queen; modify as needed
            promotion = '=Q'
    
    # Start building the move notation
    move_notation = ''
    
    # Add piece letter (omit for pawns)
    if piece_type != 'Pawn':
        move_notation += piece_type[0].upper()
    
    # Disambiguation: Check if multiple pieces of the same type can move to end_pos
    ambiguous_pieces = []
    for row in range(8):
        for col in range(8):
            current_piece = board[row][col]
            if (current_piece is not None and
                current_piece.color == player and
                type(current_piece).__name__ == piece_type and
                (row, col) != position_to_indices(start_pos)):
                other_start_pos = indices_to_position(row, col)
                # Pass the actual end_pos to valid_moves
                if current_piece.valid_moves(board, other_start_pos, end_pos, last_move=None):
                    ambiguous_pieces.append(other_start_pos)
    
    if ambiguous_pieces:
        # Need to disambiguate
        start_file = start_pos[0]
        start_rank = start_pos[1]
        # Check if disambiguation by file is enough
        need_file = any(pos[0] == start_file for pos in ambiguous_pieces)
        need_rank = any(pos[1] == start_rank for pos in ambiguous_pieces)
        
        if need_file and need_rank:
            move_notation += start_pos  # Both file and rank
        elif need_file:
            move_notation += start_file  # Only file
        elif need_rank:
            move_notation += start_rank  # Only rank
        else:
            move_notation += start_pos  # Both file and rank
    
    # Add capture indicator
    if is_capture:
        if piece_type == 'Pawn' and not ambiguous_pieces:
            # For pawn captures, include the originating file
            move_notation += start_pos[0]
        move_notation += 'x'
    
    # Add destination square
    move_notation += end_pos
    
    # Add promotion if applicable
    move_notation += promotion
    
    # Optionally, you can add check '+' or checkmate '#' indicators here
    # This requires additional game state analysis
    
    return move_notation
