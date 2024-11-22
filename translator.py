import re
from pieces import King, Queen, Rook, Bishop, Knight, Pawn  # Ensure this imports your Piece classes
from utils import position_to_indices, indices_to_position
from checked import is_square_attacked, is_in_check

def chess_move_to_positions(move, board, player='white', last_move=None):
    """
    Convert a standard chess move notation into start and end positions using Piece classes' valid_moves.

    Args:
        move (str): The chess move in standard algebraic notation (e.g., 'e4', 'Nf3', 'Nxd5', 'O-O').
        board (list of list): The current state of the chessboard.
        player (str): 'white' or 'black' indicating the player's perspective.
        last_move (tuple): The last move made, formatted as (start_pos, end_pos).

    Returns:
        str: The start and end positions in algebraic notation (e.g., 'e2 e4'), or an error message.
    """
    # Handle castling
    if move == 'O-O' or move == '0-0':
        if player == 'white':
            return 'e1 g1'  # White kingside castling
        else:
            return 'e8 g8'  # Black kingside castling
    elif move == 'O-O-O' or move == '0-0-0':
        if player == 'white':
            return 'e1 c1'  # White queenside castling
        else:
            return 'e8 c8'  # Black queenside castling

    # Regular expression to parse the move
    pattern = r'^(?P<piece>[KQRBN]?)(?P<from_file>[a-h]?)(?P<from_rank>[1-8]?)(?P<capture>x?)(?P<to_file>[a-h])(?P<to_rank>[1-8])(=?[QRBN]?)(?P<check>[+#]?)$'
    match = re.match(pattern, move)

    if not match:
        return 'Invalid move notation'

    groups = match.groupdict()

    piece = groups['piece'] if groups['piece'] else 'P'  # Default to Pawn if no piece is specified
    from_file = groups['from_file']
    from_rank = groups['from_rank']
    to_square = groups['to_file'] + groups['to_rank']
    capture = groups['capture'] == 'x'
    promotion = groups.get('promotion')
    check = groups['check']

    # Map piece letters to class names
    piece_map = {
        'K': King,
        'Q': Queen,
        'R': Rook,
        'B': Bishop,
        'N': Knight,
        'P': Pawn
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
        return f"{valid_moves[0]} {to_square}"
    elif len(valid_moves) > 1:
        return f"Ambiguous move: {move}. Possible starting squares: {', '.join(valid_moves)}"
    else:
        return f"No valid pieces can perform the move: {move}"

# Example Usage
if __name__ == "__main__":
    # Initialize an empty board
    board = [[None for _ in range(8)] for _ in range(8)]

    # Place some pieces for testing
    board[1][4] = Pawn('white', 'e2')   # White pawn at e2
    board[0][1] = Knight('white', 'b1') # White knight at b1
    board[0][6] = Knight('white', 'g1') # White knight at g1
    board[7][3] = Queen('black', 'd8')  # Black queen at d8
    board[6][4] = Pawn('black', 'e7')   # Black pawn at e7
    board[7][0] = Rook('black', 'a8')   # Black rook at a8

    # Define last_move if needed (for en passant, etc.)
    last_move = ('e7', 'e5')  # Example last move

    # Test moves
    test_moves = ['e4', 'Nf3', 'Nxd5', 'Nc6+', 'Qb7#', 'O-O', 'O-O-O']

    for move in test_moves:
        result = chess_move_to_positions(move, board, player='white', last_move=last_move)
        print(f"Move: {move} => {result}")
