import copy
import random
from evaluate import evaluate_pawn_structure, evaluate_king_safety, evaluate_center_control
from evaluate import get_move_weight
from utils import position_to_indices
from game_logic import check_game_status, get_all_legal_moves, move_piece_simulation

def evaluate_board(board, color, last_move):
    """
    Evaluates the board state from the perspective of the given color.

    Parameters:
    - board: The current state of the chessboard.
    - color: 'white' or 'black'.

    Returns:
    - A numerical value representing the board's desirability for the given color.
      Positive values favor the given color, negative values favor the opponent.
    """
    import copy

    # Piece values
    piece_values = {
        'Pawn': 100,
        'Knight': 320,
        'Bishop': 330,
        'Rook': 500,
        'Queen': 900,
        'King': 20000  # High value to prioritize king safety
    }

    # Positional tables for each piece type (simplified for demonstration)
    pawn_table = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [5, 5, 10, 25, 25, 10, 5, 5],
        [0, 0, 0, 20, 20, 0, 0, 0],
        [5, -5, -10, 0, 0, -10, -5, 5],
        [5, 10, 10, -20, -20, 10, 10, 5],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]

    knight_table = [
        [-50, -40, -30, -30, -30, -30, -40, -50],
        [-40, -20, 0, 5, 5, 0, -20, -40],
        [-30, 5, 10, 15, 15, 10, 5, -30],
        [-30, 0, 15, 20, 20, 15, 0, -30],
        [-30, 5, 15, 20, 20, 15, 5, -30],
        [-30, 0, 10, 15, 15, 10, 0, -30],
        [-40, -20, 0, 0, 0, 0, -20, -40],
        [-50, -40, -30, -30, -30, -30, -40, -50]
    ]

    bishop_table = [
        [-20, -10, -10, -10, -10, -10, -10, -20],
        [-10, 0, 0, 0, 0, 0, 0, -10],
        [-10, 0, 5, 10, 10, 5, 0, -10],
        [-10, 5, 5, 10, 10, 5, 5, -10],
        [-10, 0, 10, 10, 10, 10, 0, -10],
        [-10, 10, 10, 10, 10, 10, 10, -10],
        [-10, 5, 0, 0, 0, 0, 5, -10],
        [-20, -10, -10, -10, -10, -10, -10, -20]
    ]

    rook_table = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [5, 10, 10, 10, 10, 10, 10, 5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [0, 0, 0, 5, 5, 0, 0, 0]
    ]

    queen_table = [
        [-20, -10, -10, -5, -5, -10, -10, -20],
        [-10, 0, 0, 0, 0, 0, 0, -10],
        [-10, 0, 5, 5, 5, 5, 0, -10],
        [-5, 0, 5, 5, 5, 5, 0, -5],
        [0, 0, 5, 5, 5, 5, 0, -5],
        [-10, 5, 5, 5, 5, 5, 0, -10],
        [-10, 0, 5, 0, 0, 0, 0, -10],
        [-20, -10, -10, -5, -5, -10, -10, -20]
    ]

    king_table = [
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-20, -30, -30, -40, -40, -30, -30, -20],
        [-10, -20, -20, -20, -20, -20, -20, -10],
        [20, 20, 0, 0, 0, 0, 20, 20],
        [20, 30, 10, 0, 0, 10, 30, 20]
    ]

    # Initialize total evaluation
    total_evaluation = 0

    # Mobility counts
    own_mobility = 0
    opponent_mobility = 0

    # List to hold positions of pieces for king safety and pawn structure
    own_pawns = []
    own_king_position = None

    # Get opponent's color
    opponent_color = 'black' if color == 'white' else 'white'

    # Calculate material and positional value
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece:
                piece_type = type(piece).__name__
                piece_value = piece_values[piece_type]

                # Positional bonus
                if piece_type == 'Pawn':
                    table = pawn_table
                elif piece_type == 'Knight':
                    table = knight_table
                elif piece_type == 'Bishop':
                    table = bishop_table
                elif piece_type == 'Rook':
                    table = rook_table
                elif piece_type == 'Queen':
                    table = queen_table
                elif piece_type == 'King':
                    table = king_table
                else:
                    table = [[0]*8]*8  # Default to zero if not specified

                # Adjust for piece color
                if piece.color == 'white':
                    position_bonus = table[row][col]
                else:
                    position_bonus = table[7 - row][col]

                # Total piece value including positional bonus
                total_piece_value = piece_value + position_bonus

                if piece.color == color:
                    total_evaluation += total_piece_value
                    # Collect own pawns and king position
                    if piece_type == 'Pawn':
                        own_pawns.append((row, col))
                    if piece_type == 'King':
                        own_king_position = (row, col)
                else:
                    total_evaluation -= total_piece_value

    # Evaluate mobility
    own_mobility = len(get_all_legal_moves(board, color, last_move))
    opponent_mobility = len(get_all_legal_moves(board, opponent_color, last_move))

    # Add mobility to evaluation
    mobility_score = own_mobility - opponent_mobility
    total_evaluation += 10 * mobility_score  # Weight mobility by 10

    # Evaluate pawn structure
    total_evaluation += evaluate_pawn_structure(board, color, own_pawns)

    # Evaluate king safety
    total_evaluation += evaluate_king_safety(board, color, own_king_position, last_move)

    # Evaluate control of the center
    total_evaluation += evaluate_center_control(board, color)

    return total_evaluation



def minimax(board, depth, alpha, beta, maximizing_player, current_color, last_move):
    """
    Minimax algorithm with alpha-beta pruning.

    Parameters:
    - board: The current state of the chessboard.
    - depth: The maximum depth of the search tree.
    - alpha: The best already explored option along the path to the root for the maximizer.
    - beta: The best already explored option along the path to the root for the minimizer.
    - maximizing_player: True if the current move is for the maximizing player.
    - current_color: 'white' or 'black' indicating whose turn it is.
    - last_move: The last move made in the game, required for en passant.

    Returns:
    - A tuple (value, move), where 'value' is the evaluation of the board,
      and 'move' is the best move found.
    """
    # Base case: maximum depth reached or game over
    game_over, result = check_game_status(board, current_color, last_move)
    if depth == 0 or game_over:
        evaluation = evaluate_board(board, 'black', last_move)  # Assuming AI plays black
        return evaluation, None

    legal_moves = get_all_legal_moves(board, current_color, last_move)

    if not legal_moves:
        # No legal moves available
        evaluation = evaluate_board(board, 'black', last_move)
        return evaluation, None

    if maximizing_player:
        max_eval = float('-inf')
        best_move = []
        for move in legal_moves:
            start_pos, end_pos = move
            # Get the move weight before simulating the move
            move_weight = get_move_weight(board, move)
            # Make a deep copy of the board to simulate the move
            new_board = copy.deepcopy(board)
            # Get the piece from the new board
            start_row, start_col = position_to_indices(start_pos)
            piece = new_board[start_row][start_col]
            # Simulate the move
            move_piece_simulation(new_board, piece, start_pos, end_pos, last_move)
            new_last_move = (start_pos, end_pos)
            # Recursive call, switch player and color
            evaluation, _ = minimax(new_board, depth - 1, alpha, beta, False, 'white', new_last_move)
            if evaluation > max_eval:
                max_eval = evaluation
                best_moves = [(move, move_weight)]
            elif evaluation == max_eval:
                best_moves.append((move, move_weight))
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break  # Beta cutoff
        if best_moves:
            # Use probabilities to choose the move based on weights
            moves, weights = zip(*best_moves)
            selected_move = random.choices(moves, weights=weights, k=1)[0]
            return max_eval, selected_move
        else:
            return max_eval, None
    else:
        min_eval = float('inf')
        best_move = []
        for move in legal_moves:
            start_pos, end_pos = move
            # Get the move weight before simulating the move
            move_weight = get_move_weight(board, move)
            new_board = copy.deepcopy(board)
            start_row, start_col = position_to_indices(start_pos)
            piece = new_board[start_row][start_col]
            move_piece_simulation(new_board, piece, start_pos, end_pos, last_move)
            new_last_move = (start_pos, end_pos)
            evaluation, _ = minimax(new_board, depth - 1, alpha, beta, True, 'black', new_last_move)
            if evaluation < min_eval:
                min_eval = evaluation
                best_moves = [(move, move_weight)]
            elif evaluation == min_eval:
                best_moves.append((move, move_weight))
            beta = min(beta, evaluation)
            if beta <= alpha:
                break  # Alpha cutoff
        if best_moves:
            moves, weights = zip(*best_moves)
            selected_move = random.choices(moves, weights=weights, k=1)[0]
            return min_eval, selected_move
        else:
            return min_eval, None
