from algorithm import minimax

def calculate_ai_move(board, ai_color, last_move, queue):
    """Calculate AI move and put the result in a queue."""
    evaluation, ai_move = minimax(
        board, depth=3, alpha=float('-inf'), beta=float('inf'),
        maximizing_player=True, current_color=ai_color, last_move=last_move
    )
    queue.put(ai_move)
