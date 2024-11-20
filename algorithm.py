from board import position_to_indices
from game_status import check_game_status, get_all_legal_moves

def evaluate_board(board, color):
    """
    Evaluates the board state from the perspective of the given color.

    Parameters:
    - board: The current state of the chessboard.
    - color: 'white' or 'black'.

    Returns:
    - A numerical value representing the board's desirability.
    """
    piece_values = {
        'Pawn': 1,
        'Knight': 3,
        'Bishop': 3,
        'Rook': 5,
        'Queen': 9,
        'King': 0  # King's value is typically considered infinite, but we can use 0 here
    }

    total_value = 0

    for row in board:
        for piece in row:
            if piece:
                value = piece_values[type(piece).__name__]
                if piece.color == color:
                    total_value += value
                else:
                    total_value -= value

    return total_value

# algorithm.py (continued)

import copy

def minimax(board, depth, alpha, beta, maximizing_player, current_color):
    """
    Minimax algorithm with alpha-beta pruning.

    Parameters:
    - board: The current state of the chessboard.
    - depth: The maximum depth of the search tree.
    - alpha: The best already explored option along the path to the root for the maximizer.
    - beta: The best already explored option along the path to the root for the minimizer.
    - maximizing_player: True if the current move is for the maximizing player.
    - current_color: 'white' or 'black' indicating whose turn it is.

    Returns:
    - A tuple (value, move), where 'value' is the evaluation of the board,
      and 'move' is the best move found.
    """
    # Base case: maximum depth reached or game over
    game_over, result = check_game_status(board, current_color)
    if depth == 0 or game_over:
        evaluation = evaluate_board(board, 'black')  # Assuming AI plays black
        return evaluation, None

    legal_moves = get_all_legal_moves(board, current_color)

    if maximizing_player:
        max_eval = float('-inf')
        best_move = None
        for move in legal_moves:
            start_pos, end_pos = move
            # Make a deep copy of the board to simulate the move
            new_board = copy.deepcopy(board)
            piece = new_board[position_to_indices(start_pos)[0]][position_to_indices(start_pos)[1]]
            move_piece_simulation(new_board, piece, start_pos, end_pos)
            evaluation, _ = minimax(new_board, depth - 1, alpha, beta, False, 'white')
            if evaluation > max_eval:
                max_eval = evaluation
                best_move = move
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break  # Beta cutoff
        return max_eval, best_move
    else:
        min_eval = float('inf')
        best_move = None
        for move in legal_moves:
            start_pos, end_pos = move
            new_board = copy.deepcopy(board)
            piece = new_board[position_to_indices(start_pos)[0]][position_to_indices(start_pos)[1]]
            move_piece_simulation(new_board, piece, start_pos, end_pos)
            evaluation, _ = minimax(new_board, depth - 1, alpha, beta, True, 'black')
            if evaluation < min_eval:
                min_eval = evaluation
                best_move = move
            beta = min(beta, evaluation)
            if beta <= alpha:
                break  # Alpha cutoff
        return min_eval, best_move
    
# algorithm.py (continued)

def move_piece_simulation(board, piece, start_pos, end_pos):
    """
    Simulates moving a piece on the board copy.

    Parameters:
    - board: The board copy on which to simulate the move.
    - piece: The piece to move.
    - start_pos: The starting position of the piece.
    - end_pos: The ending position of the piece.
    """
    start_row, start_col = position_to_indices(start_pos)
    end_row, end_col = position_to_indices(end_pos)
    # Move the piece
    board[end_row][end_col] = piece
    board[start_row][start_col] = None
    # Update the piece's position
    piece.position = end_pos
    # If the piece has a 'has_moved' attribute, set it to True
    if hasattr(piece, 'has_moved'):
        piece.has_moved = True

