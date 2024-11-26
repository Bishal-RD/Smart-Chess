import copy
import time
import math
import random
from concurrent.futures import ThreadPoolExecutor
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

class MCTSNode:
    def __init__(self, board, color, last_move, parent=None, move=None):
        self.board = board
        self.color = color
        self.last_move = last_move
        self.parent = parent
        self.children = []
        self.visits = 0
        self.wins = 0
        self.move = move  # The move that led to this node

    def is_fully_expanded(self):
        return len(self.children) == len(get_all_legal_moves(self.board, self.color, self.last_move))

    def best_child(self, exploration_weight=1.0):
        """
        Returns the best child node based on UCB1 formula.
        """
        if not self.children:
            return None
        return max(
            self.children,
            key=lambda child: (child.wins / (child.visits + 1e-6)) +
            exploration_weight * math.sqrt(math.log(self.visits + 1) / (child.visits + 1e-6))
        )

    def expand(self):
        """
        Expands the current node by adding a new child node.
        """
        legal_moves = get_all_legal_moves(self.board, self.color, self.last_move)
        for move in legal_moves:
            if not any(child.move == move for child in self.children):
                # Simulate the move
                new_board = copy.deepcopy(self.board)
                start_pos, end_pos = move
                start_row, start_col = position_to_indices(start_pos)
                piece = new_board[start_row][start_col]
                move_piece_simulation(new_board, piece, start_pos, end_pos, self.last_move)

                # Add the new child node
                new_color = 'white' if self.color == 'black' else 'black'
                child_node = MCTSNode(new_board, new_color, (start_pos, end_pos), parent=self, move=move)
                self.children.append(child_node)
                return child_node
        return None

    def simulate(self, n_simulations=10):
        """
        Performs a Best of N simulation from the current node and evaluates the position.
        """
        total_score = 0
        for _ in range(n_simulations):
            total_score += self.simulate_once()
        return total_score / n_simulations
    
    def simulate_parallel(self, n_simulations=5):
        """
        Performs parallel simulations for the current node using threading.

        Parameters:
        - n_simulations: The number of simulations to perform.

        Returns:
        - The average result of the simulations.
        """
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(lambda _: self.simulate_once(), range(n_simulations)))
        return sum(results) / len(results)

    def simulate_once(self):
        """
        Simulates a random playout using domain knowledge scoring.
        """
        current_board = copy.deepcopy(self.board)
        current_color = self.color
        current_last_move = self.last_move

        while True:
            game_over, result = check_game_status(current_board, current_color, current_last_move)
            if game_over:
                # Assign rewards based on game outcome
                if result == current_color:
                    return 1000  # Win
                elif result == 'draw':
                    return 0  # Draw
                else:
                    return -1000  # Loss

            # Choose a random move
            legal_moves = get_all_legal_moves(current_board, current_color, current_last_move)
            if not legal_moves:
                return -1000  # Stalemate or no legal moves

            move = random.choice(legal_moves)
            start_pos, end_pos = move
            start_row, start_col = position_to_indices(start_pos)
            piece = current_board[start_row][start_col]
            move_piece_simulation(current_board, piece, start_pos, end_pos, current_last_move)

            # Update the color and last move
            current_color = 'white' if current_color == 'black' else 'black'
            current_last_move = move

            # Evaluate using domain knowledge
            score = evaluate_board_with_domain_knowledge(current_board, current_color, current_last_move)
            return score

    def backpropagate(self, result):
        """
        Backpropagates the simulation result through the tree, updating visits and wins.
        """
        self.visits += 1
        self.wins += result
        if self.parent:
            self.parent.backpropagate(1 - result if self.color != self.parent.color else result)

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

def is_passed_pawn(board, color, position):
    """
    Determines if a pawn is a passed pawn.

    Parameters:
    - board: The current chessboard state.
    - color: 'white' or 'black', the color of the pawn.
    - position: A tuple (row, col) representing the position of the pawn.

    Returns:
    - True if the pawn is a passed pawn, False otherwise.
    """
    row, col = position
    direction = 1 if color == 'white' else -1  # White pawns move up, black pawns move down
    opponent_color = 'black' if color == 'white' else 'white'

    # Check the files: current, left, and right
    for file_offset in [-1, 0, 1]:
        check_col = col + file_offset
        if 0 <= check_col < 8:  # Ensure column is within bounds
            for check_row in range(row + direction, 8 if color == 'white' else -1, direction):
                opponent_piece = board[check_row][check_col]
                if opponent_piece and type(opponent_piece).__name__ == 'Pawn' and opponent_piece.color == opponent_color:
                    return False  # Opponent pawn blocks the path

    return True  # No opposing pawns block the path

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

def evaluate_board_with_domain_knowledge(board, color, last_move):
    total_score = 0
    opponent_color = 'black' if color == 'white' else 'white'

    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece:
                piece_type = type(piece).__name__
                piece_value = PIECE_VALUES.get(piece_type, 0)

                # Add material value
                if piece.color == color:
                    total_score += piece_value
                else:
                    total_score -= piece_value

                # Center control
                if (row, col) in [(3, 3), (3, 4), (4, 3), (4, 4)]:
                    if piece.color == color:
                        total_score += 5
                    else:
                        total_score -= 5

                # King safety
                if piece_type == 'King' and is_king_under_attack(board, piece.color, last_move):
                    if piece.color == color:
                        total_score -= 50
                    else:
                        total_score += 50

                # Mobility
                mobility = count_piece_mobility(board, piece.color, last_move, (row, col))
                mobility_bonus = 0.1 * mobility if piece_type == 'Pawn' else 0.2 * mobility
                total_score += mobility_bonus if piece.color == color else -mobility_bonus

                # Passed pawns
                if piece_type == 'Pawn' and is_passed_pawn(board, piece.color, (row, col)):
                    total_score += 20 if piece.color == color else -20

    return total_score

def mcts(root_board, root_color, root_last_move, simulations=1000, time_limit=None):
    """
    Performs Monte Carlo Tree Search with Best of N simulations.

    Parameters:
    - root_board: The initial state of the chessboard.
    - root_color: 'white' or 'black', the player to move.
    - root_last_move: The last move made in the game.
    - simulations: Number of simulations to perform.
    - time_limit: Optional time limit for the search.

    Returns:
    - The best move found.
    """
    root_node = MCTSNode(root_board, root_color, root_last_move)
    start_time = time.time()

    for _ in range(simulations):
        if time_limit and (time.time() - start_time) >= time_limit:
            break

        # Step 1: Selection
        node = root_node
        while node.is_fully_expanded() and node.children:
            node = node.best_child()

        # Step 2: Expansion
        if not node.is_fully_expanded():
            node = node.expand()

        # Step 3: Simulation
        if node:
            result = node.simulate_parallel(n_simulations=10)  # Parallel simulation with 10 simulations
            # result = node.simulate(n_simulations=5)  # Best of 5 simulations for each playout

        # Step 4: Backpropagation
        if node:
            node.backpropagate(result)

    # Return the best move found
    best_child = root_node.best_child(exploration_weight=0)
    return best_child.move if best_child else None
