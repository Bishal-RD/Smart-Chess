import copy
import random
from pieces import Pawn
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
    - A numerical value representing the board's desirability.
    """
    piece_values = {
        'Pawn': 10,
        'Knight': 30,
        'Bishop': 30,
        'Rook': 50,
        'Queen': 90,
        'King': 900
    }

    total_value = 0

    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece:
                value = piece_values[type(piece).__name__]
                # Add positional bonuses (e.g., center control)
                position_bonus = 0
                if isinstance(piece, Pawn):
                    # Pawns get bonus for advancing
                    if piece.color == 'white':
                        position_bonus = (6 - row)
                    else:
                        position_bonus = (row - 1)
                # Combine piece value and positional bonus
                value += position_bonus
                if piece.color == color:
                    total_value += value
                else:
                    total_value -= value

    return total_value

def minimax(board, depth, alpha, beta, maximizing_player, current_color, last_move, model=None):
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
