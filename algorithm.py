import copy
import time
from utils import position_to_indices, indices_to_position
from game_logic import check_game_status, get_all_legal_moves, move_piece_simulation

# Constants for piece values
PIECE_VALUES = {
    'Pawn': 10,
    'Knight': 30,
    'Bishop': 30,
    'Rook': 50,
    'Queen': 90,
    'King': 900
}

def evaluate_board(board, color, last_move):
    """
    Evaluates the board state from the perspective of the given color.

    Parameters:
    - board: The current state of the chessboard.
    - color: 'white' or 'black'.
    - last_move: The last move made in the game.

    Returns:
    - A numerical value representing the board's desirability.
    """
    total_value = 0
    opponent_color = 'black' if color == 'white' else 'white'

    # Initialize positional bonuses (simple example: center control)
    center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]

    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece:
                piece_type = type(piece).__name__
                value = PIECE_VALUES.get(piece_type, 0)

                # Add positional bonuses
                positional_bonus = 0
                if (row, col) in center_squares:
                    positional_bonus += 5  # Control of the center is valuable

                # King safety: penalize if the king is under threat
                if piece_type == 'King':
                    if is_king_under_attack(board, color, last_move):
                        positional_bonus -= 50  # High penalty for king being in check or threatened

                # Mobility: number of legal moves available to the piece
                mobility = count_piece_mobility(board, color, last_move, (row, col))
                positional_bonus += mobility * 0.1  # Small bonus for mobility

                # Combine piece value and positional bonus
                if piece.color == color:
                    total_value += value + positional_bonus
                else:
                    total_value -= (value + positional_bonus)

    return total_value

def is_king_under_attack(board, color, last_move):
    """
    Checks if the king of the given color is under attack.

    Parameters:
    - board: The current state of the chessboard.
    - color: 'white' or 'black'.
    - last_move: The last move made in the game.

    Returns:
    - True if the king is under attack, False otherwise.
    """
    king_position = None
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and type(piece).__name__ == 'King' and piece.color == color:
                king_position = (row, col)
                break
        if king_position:
            break

    if not king_position:
        # King is not on the board, which shouldn't happen in a normal game
        return True

    # Check all opponent moves to see if any can capture the king
    opponent_color = 'black' if color == 'white' else 'white'
    opponent_moves = get_all_legal_moves(board, opponent_color, last_move)

    for move in opponent_moves:
        _, end_pos = move
        if position_to_indices(end_pos) == king_position:
            return True
    return False

def count_piece_mobility(board, color, last_move, piece_position):
    """
    Counts the number of legal moves for a specific piece.

    Parameters:
    - board: The current state of the chessboard.
    - color: 'white' or 'black'.
    - last_move: The last move made in the game.
    - piece_position: A tuple (row, col) indicating the piece's position.

    Returns:
    - An integer representing the number of legal moves for the piece.
    """
    row, col = piece_position
    piece = board[row][col]
    if not piece or piece.color != color:
        return 0

    legal_moves = []
    start_pos = indices_to_position(row, col)

    for end_row in range(8):
        for end_col in range(8):
            end_pos = indices_to_position(end_row, end_col)
            if piece.valid_moves(board, start_pos, end_pos, last_move):
                # Make a deep copy of the board to test the move
                board_copy = copy.deepcopy(board)
                # Get the piece on the copied board
                piece_copy = board_copy[row][col]
                # Simulate the move on the copied board
                move_piece_simulation(board_copy, piece_copy, start_pos, end_pos, last_move)
                # Update the last move for the simulation
                simulated_last_move = (start_pos, end_pos)
                # Check if the king would be in check after the move
                if not is_king_under_attack(board_copy, color, simulated_last_move):
                    legal_moves.append((start_pos, end_pos))

    return len(legal_moves)

def evaluate_move_loss(piece, captured_piece):
    """
    Evaluates the loss of a piece based on the priority.

    Parameters:
    - piece: The piece being captured.
    - captured_piece: The piece capturing it.

    Returns:
    - A numerical value representing the loss.
    """
    # Assign priority: Pawn < Knight/Bishop < Rook < Queen < King
    loss_priority = {
        'Pawn': 1,
        'Knight': 2,
        'Bishop': 2,
        'Rook': 3,
        'Queen': 4,
        'King': 5
    }
    return loss_priority.get(type(piece).__name__, 0)

def minimax(board, depth, alpha, beta, maximizing_player, current_color, last_move):
    """
    Minimax algorithm with alpha-beta pruning and enhanced evaluation.

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
        # Assuming 'black' is the AI; adjust as needed
        evaluation = evaluate_board(board, 'black', last_move)
        return evaluation, None

    legal_moves = get_all_legal_moves(board, current_color, last_move)

    if not legal_moves:
        # No legal moves available
        evaluation = evaluate_board(board, 'black', last_move)
        return evaluation, None

    if maximizing_player:
        max_eval = float('-inf')
        best_moves = []
        for move in legal_moves:
            start_pos, end_pos = move
            # Simulate the move
            new_board = copy.deepcopy(board)
            start_row, start_col = position_to_indices(start_pos)
            piece = new_board[start_row][start_col]
            captured_piece = new_board[position_to_indices(end_pos)[0]][position_to_indices(end_pos)[1]]

            move_piece_simulation(new_board, piece, start_pos, end_pos, last_move)
            new_last_move = (start_pos, end_pos)

            # Recursive call, switch player and color
            evaluation, _ = minimax(new_board, depth - 1, alpha, beta, False, 'white', new_last_move)

            # Prefer moves that do not lose pieces, or lose lower priority pieces
            if captured_piece:
                loss_value = evaluate_move_loss(captured_piece, piece)
                # Subtract loss_value from evaluation to prioritize moves that lose less
                evaluation -= loss_value * 10  # Adjust the multiplier as needed

            if evaluation > max_eval:
                max_eval = evaluation
                best_moves = [(move, PIECE_VALUES.get(type(captured_piece).__name__, 0) if captured_piece else 0)]
            elif evaluation == max_eval:
                best_moves.append((move, PIECE_VALUES.get(type(captured_piece).__name__, 0) if captured_piece else 0))

            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break  # Beta cutoff

        if best_moves:
            # Prioritize moves that capture higher value pieces
            best_moves.sort(key=lambda x: x[1], reverse=True)
            selected_move = best_moves[0][0]  # Choose the move that captures the highest value piece
            return max_eval, selected_move
        else:
            return max_eval, None
    else:
        min_eval = float('inf')
        best_moves = []
        for move in legal_moves:
            start_pos, end_pos = move
            # Simulate the move
            new_board = copy.deepcopy(board)
            start_row, start_col = position_to_indices(start_pos)
            piece = new_board[start_row][start_col]
            captured_piece = new_board[position_to_indices(end_pos)[0]][position_to_indices(end_pos)[1]]

            move_piece_simulation(new_board, piece, start_pos, end_pos, last_move)
            new_last_move = (start_pos, end_pos)

            # Recursive call, switch player and color
            evaluation, _ = minimax(new_board, depth - 1, alpha, beta, True, 'black', new_last_move)

            # Opponent prefers moves that maximize their advantage
            if captured_piece:
                loss_value = evaluate_move_loss(captured_piece, piece)
                # Add loss_value to evaluation to prioritize moves that lose less
                evaluation += loss_value * 10  # Adjust the multiplier as needed

            if evaluation < min_eval:
                min_eval = evaluation
                best_moves = [(move, PIECE_VALUES.get(type(captured_piece).__name__, 0) if captured_piece else 0)]
            elif evaluation == min_eval:
                best_moves.append((move, PIECE_VALUES.get(type(captured_piece).__name__, 0) if captured_piece else 0))

            beta = min(beta, evaluation)
            if beta <= alpha:
                break  # Alpha cutoff

        if best_moves:
            # Prioritize moves that capture lower value pieces
            best_moves.sort(key=lambda x: x[1])
            selected_move = best_moves[0][0]  # Choose the move that captures the lowest value piece
            return min_eval, selected_move
        else:
            return min_eval, None
        
def iterative_deepening(board, color, last_move, max_depth=5, time_limit=None):
    """
    Performs Iterative Deepening Search to find the best move.

    Parameters:
    - board: The current state of the chessboard.
    - color: 'white' or 'black'.
    - last_move: The last move made in the game.
    - max_depth: The maximum depth to search.
    - time_limit: Optional time limit in seconds for the search.

    Returns:
    - The best move found as a tuple (start_pos, end_pos).
    """
    best_move = None
    start_time = time.time()

    for depth in range(1, max_depth + 1):
        evaluation, current_move = minimax(
            board, 
            depth=depth, 
            alpha=float('-inf'), 
            beta=float('inf'), 
            maximizing_player=(color == 'black'), 
            current_color=color, 
            last_move=last_move
        )

        # Update the best move
        if current_move:
            best_move = current_move
            print(f"Depth {depth}: Best Move = {best_move}, Evaluation = {evaluation}")

        # Optional: Check if time limit is reached
        if time_limit:
            elapsed_time = time.time() - start_time
            print(elapsed_time, "seconds elapsed")
            if elapsed_time >= time_limit:
                print(f"Time limit of {time_limit} seconds reached at depth {depth}.")
                break

    return best_move

