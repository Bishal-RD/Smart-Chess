import numpy as np
import copy
import random
from pieces import Pawn
from evaluate import get_move_weight
from utils import position_to_indices
from board import board_to_fen
from game_logic import check_game_status, get_all_legal_moves, move_piece_simulation

# Helper function to convert FEN to input format
def fen_to_input(fen):
    board_array = np.zeros((8, 8, 12))  # 8x8 board, 12 piece types
    piece_map = {
        "p": 0, "n": 1, "b": 2, "r": 3, "q": 4, "k": 5,  # Black pieces
        "P": 6, "N": 7, "B": 8, "R": 9, "Q": 10, "K": 11  # White pieces
    }
    board = fen.split(" ")[0]
    for row_idx, row in enumerate(board.split("/")):
        col_idx = 0
        for char in row:
            if char.isdigit():
                col_idx += int(char)  # Empty squares
            else:
                piece_idx = piece_map[char]
                board_array[row_idx, col_idx, piece_idx] = 1
                col_idx += 1
    return board_array

def evaluate_board(board, model):
    """
    Evaluates the board position using the trained neural network.
    Args:
        board (chess.Board): Current board state.
    Returns:
        float: Evaluation score (win probability).
    """

    fen = board_to_fen(board)  # Get the FEN string of the board

    input_data = np.expand_dims(fen_to_input(fen), axis=0)  # Convert to model input format
    score = model.predict(input_data)[0][0]  # Predict win probability
    return score

def minimax(board, depth, alpha, beta, maximizing_player, current_color, last_move, model):
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
        evaluation = evaluate_board(board, model)  # Assuming AI plays black
        return evaluation, None

    legal_moves = get_all_legal_moves(board, current_color, last_move)

    if not legal_moves:
        # No legal moves available
        evaluation = evaluate_board(board, model)
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
        