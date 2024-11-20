from utils import position_to_indices

class Piece:
    def __init__(self, color, position):
        self.color = color  # 'white' or 'black'
        self.position = position
        
    def set_position(self, position):
        if self.is_valid_position(position):
            self.position = position
        else:
            raise ValueError(f"Invalid position: {position}")
    
    def get_position(self):
        return self.position

    def is_valid_position(self, position):
        # Check if the position is within 'a'-'h' and '1'-'8'
        if len(position) != 2:
            return False
        file, rank = position[0], position[1]
        return file in 'abcdefgh' and rank in '12345678'

    def __str__(self):
        # To be overridden in subclasses
        pass

class King(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)

    def __str__(self):
        return 'K' if self.color == 'white' else 'k'
    
    def valid_moves(self, board, start_pos, end_pos):
        """
        Determines if moving the king from start_pos to end_pos is valid.

        Parameters:
        - board: The current state of the chessboard.
        - start_pos: Starting position string (e.g., 'e1').
        - end_pos: Ending position string (e.g., 'e2').

        Returns:
        - True if the move is valid, False otherwise.
        """
        # Convert positions to indices
        try:
            start_row, start_col = position_to_indices(start_pos)
            end_row, end_col = position_to_indices(end_pos)
        except ValueError as e:
            print(e)
            return False
        
        # Calculate movement differences
        col_diff = abs(end_col - start_col)
        row_diff = abs(end_row - start_row)

        if max(col_diff, row_diff) == 1:
            # King moves one square in any direction
            target_piece = board[end_row][end_col]
            if target_piece is None or target_piece.color != self.color:
                return True
        # Castling logic can be added here if desired
        return False

    
class Queen(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
    
    def __str__(self):
        return 'Q' if self.color == 'white' else 'q'
    
    def valid_moves(self, board, start_pos, end_pos):
        """
        Determines if moving the queen from start_pos to end_pos is valid.

        Parameters:
        - board: The current state of the chessboard.
        - start_pos: Starting position string (e.g., 'd1').
        - end_pos: Ending position string (e.g., 'h5').

        Returns:
        - True if the move is valid, False otherwise.
        """
        # Convert positions to indices
        try:
            start_row, start_col = position_to_indices(start_pos)
            end_row, end_col = position_to_indices(end_pos)
        except ValueError as e:
            print(e)
            return False
        
        col_diff = end_col - start_col
        row_diff = end_row - start_row

        if start_row == end_row or start_col == end_col:
            # Rook-like movement (along row or column)
            # Determine the direction of movement
            col_step = 0
            if start_col < end_col:
                col_step = 1
            elif start_col > end_col:
                col_step = -1

            row_step = 0
            if start_row < end_row:
                row_step = 1
            elif start_row > end_row:
                row_step = -1

            # Check all squares between start and end for obstructions
            col, row = start_col + col_step, start_row + row_step
            while (col != end_col or row != end_row):
                if board[row][col] is not None:
                    return False
                col += col_step
                row += row_step

            # Check the destination square
            target_piece = board[end_row][end_col]
            if target_piece is None or target_piece.color != self.color:
                return True
        elif abs(col_diff) == abs(row_diff):
            # Bishop-like movement (along diagonal)
            col_step = 1 if col_diff > 0 else -1
            row_step = 1 if row_diff > 0 else -1

            col, row = start_col + col_step, start_row + row_step
            while (col != end_col and row != end_row):
                if board[row][col] is not None:
                    return False
                col += col_step
                row += row_step

            target_piece = board[end_row][end_col]
            if target_piece is None or target_piece.color != self.color:
                return True

        # If move is not along row, column, or diagonal, invalid
        return False

class Rook(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.has_moved = False  # For castling purposes

    def __str__(self):
        return 'R' if self.color == 'white' else 'r'
    
    def valid_moves(self, board, start_pos, end_pos):
        """
        Determines if moving the rook from start_pos to end_pos is valid.

        Parameters:
        - board: The current state of the chessboard.
        - start_pos: Starting position string (e.g., 'a1').
        - end_pos: Ending position string (e.g., 'a4').

        Returns:
        - True if the move is valid, False otherwise.
        """
        # Convert positions to indices
        try:
            start_row, start_col = position_to_indices(start_pos)
            end_row, end_col = position_to_indices(end_pos)
        except ValueError as e:
            print(e)
            return False
        
        # Check if move is along the same row or column
        if start_row == end_row or start_col == end_col:
            # Determine the direction of movement
            col_step = 0
            if start_col < end_col:
                col_step = 1
            elif start_col > end_col:
                col_step = -1
            
            row_step = 0
            if start_row < end_row:
                row_step = 1
            elif start_row > end_row:
                row_step = -1

            # Check all squares between start and end for obstructions
            col, row = start_col + col_step, start_row + row_step
            while (col != end_col or row != end_row):
                if board[row][col] is not None:
                    # There's a piece blocking the rook's path
                    return False
                col += col_step
                row += row_step

            # Check the destination square
            target_piece = board[end_row][end_col]
            if target_piece is None or target_piece.color != self.color:
                return True

        # If move is not along row or column, invalid
        return False

class Bishop(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
    
    def __str__(self):
        return 'B' if self.color == 'white' else 'b'
    
    def valid_moves(self, board, start_pos, end_pos):
        """
        Determines if moving the bishop from start_pos to end_pos is valid.

        Parameters:
        - board: The current state of the chessboard.
        - start_pos: Starting position string (e.g., 'c1').
        - end_pos: Ending position string (e.g., 'h6').

        Returns:
        - True if the move is valid, False otherwise.
        """
        # Convert positions to indices
        try:
            start_row, start_col = position_to_indices(start_pos)
            end_row, end_col = position_to_indices(end_pos)
        except ValueError as e:
            print(e)
            return False
        
        # Calculate movement differences
        col_diff = end_col - start_col
        row_diff = end_row - start_row
        
        # Check if move is along a diagonal
        if abs(col_diff) == abs(row_diff):
            # Determine the direction of movement
            col_step = 1 if col_diff > 0 else -1
            row_step = 1 if row_diff > 0 else -1

            # Check all squares between start and end for obstructions
            col, row = start_col + col_step, start_row + row_step
            while (col != end_col and row != end_row):
                if board[row][col] is not None:
                    # There's a piece blocking the bishop's path
                    return False
                col += col_step
                row += row_step

            # Check the destination square
            target_piece = board[end_row][end_col]
            if target_piece is None or target_piece.color != self.color:
                return True

        # If move is not along a diagonal, invalid
        return False

class Knight(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
    
    def __str__(self):
        return 'N' if self.color == 'white' else 'n'
    
    def valid_moves(self, board, start_pos, end_pos):
        """
        Determines if moving the knight from start_pos to end_pos is valid.

        Parameters:
        - board: The current state of the chessboard.
        - start_pos: Starting position string (e.g., 'g1').
        - end_pos: Ending position string (e.g., 'f3').

        Returns:
        - True if the move is valid, False otherwise.
        """
        # Convert positions to indices
        try:
            start_row, start_col = position_to_indices(start_pos)
            end_row, end_col = position_to_indices(end_pos)
        except ValueError as e:
            print(e)
            return False
        
        # Calculate movement differences
        col_diff = abs(end_col - start_col)
        row_diff = abs(end_row - start_row)
        
        # Check if the move is a valid knight move
        if (col_diff == 2 and row_diff == 1) or (col_diff == 1 and row_diff == 2):
            target_piece = board[end_row][end_col]
            # Check if the destination is empty or contains an opponent's piece
            if target_piece is None or target_piece.color != self.color:
                return True
        # If none of the valid moves apply
        return False

class Pawn(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.has_moved = False  # Tracks whether the pawn has moved
        
    def __str__(self):
        return 'P' if self.color == 'white' else 'p'
    
    def valid_moves(self, board, start_pos, end_pos):
        """
        Determines if moving the pawn from start_pos to end_pos is valid.

        Parameters:
        - board: The current state of the chessboard.
        - start_pos: Starting position string (e.g., 'e2').
        - end_pos: Ending position string (e.g., 'e4').

        Returns:
        - True if the move is valid, False otherwise.
        """
        # Convert positions to indices
        try:
            start_row, start_col = position_to_indices(start_pos)
            end_row, end_col = position_to_indices(end_pos)
        except ValueError as e:
            print(e)
            return False
        
        # Calculate the direction of movement
        if self.color == 'white':
            direction = -1  # White moves up (decreasing row index)
        else:
            direction = 1   # Black moves down (increasing row index)

        # Calculate movement differences
        col_diff = end_col - start_col
        row_diff = end_row - start_row
    
        # Check if the pawn moves forward
        if col_diff == 0:
            # Moving forward
            if row_diff == direction:
                # One square forward
                if board[end_row][end_col] is None:
                    return True
            elif row_diff == 2 * direction:
                # Two squares forward from starting position
                if not self.has_moved:
                    intermediate_row = start_row + direction
                    if (board[intermediate_row][start_col] is None and
                            board[end_row][end_col] is None):
                        return True
        elif abs(col_diff) == 1 and row_diff == direction:
            # Diagonal capture
            target_piece = board[end_row][end_col]
            if target_piece and target_piece.color != self.color:
                return True

        # If none of the valid moves apply
        return False
