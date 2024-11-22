# generate_pgn.py
import os
from datetime import datetime

def generate_pgn(user_moves, ai_moves, result="*", white_player="Human", black_player="AI",
                event="Smart Chess Game", site="Local", date=None, round_num="1"):
    """
    Generates a standard PGN string for a chess game based on the moves made by the user and the AI.
    
    Args:
        user_moves (list of str): List of user's moves in standard algebraic notation.
        ai_moves (list of str): List of AI's moves in standard algebraic notation.
        white_player (str, optional): Name of the White player. Defaults to "Human".
        black_player (str, optional): Name of the Black player. Defaults to "AI".
        event (str, optional): Name of the event. Defaults to "Smart Chess Game".
        site (str, optional): Location where the game was played. Defaults to "Local".
        date (str, optional): Date of the game in "YYYY.MM.DD" format. If None, current date is used.
        round_num (str or int, optional): Round number. Defaults to "1".
        result (str, optional): Result of the game ("1-0", "0-1", "1/2-1/2", or "*"). Defaults to "*".
        
    Returns:
        str: The game in standard PGN format.
    """
    
    # Validate inputs
    if not isinstance(user_moves, list) or not isinstance(ai_moves, list):
        raise TypeError("user_moves and ai_moves must be lists of move strings.")
    
    # Handle date
    if date is None:
        current_date = datetime.now()
        date_str = current_date.strftime("%Y.%m.%d")
    else:
        # Validate date format
        if not isinstance(date, str):
            raise TypeError("date must be a string in 'YYYY.MM.DD' format.")
        if len(date) != 10 or date[4] != '.' or date[7] != '.':
            raise ValueError("date must be in 'YYYY.MM.DD' format.")
        date_str = date
    
    # Construct PGN tags
    pgn_tags = [
        f'[Event "{event}"]',
        f'[Site "{site}"]',
        f'[Date "{date_str}"]',
        f'[Round "{round_num}"]',
        f'[White "{white_player}"]',
        f'[Black "{black_player}"]',
        f'[Result "{result}"]'
    ]
        
    # Initialize move text
    move_text = ""
    move_number = 1
    total_moves = max(len(user_moves), len(ai_moves))
    
    for i in range(total_moves):
        # Add move number and White's move
        if i < len(user_moves):
            move_text += f"{move_number}. {user_moves[i]} "
        else:
            # Handle cases where White has no move
            move_text += f"{move_number}. ... "
        
        # Add Black's move
        if i < len(ai_moves):
            move_text += f"{ai_moves[i]} "
        else:
            # If Black has no move, it's possibly a game end after White's move
            pass
        
        move_number += 1
    
    # Trim any trailing whitespace and add result if not already present
    move_text = move_text.strip()
    
    # Append the result if it's not already part of the move text
    if not move_text.endswith(result):
        move_text += f" {result}"
    
    # Combine tags and move text
    pgn = "\n".join(pgn_tags) + "\n\n" + move_text
    
    return pgn

def save_pgn(pgn, directory="games"):
    """
    Saves the PGN string to a text file with a unique filename based on the current timestamp.
    
    Args:
        pgn (str): The PGN string to save.
        directory (str, optional): Directory where PGN files will be saved. Defaults to "games".
        
    Returns:
        str: The path to the saved PGN file.
    """
    # Ensure the directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Generate a unique filename using timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"game_{timestamp}.pgn"
    filepath = os.path.join(directory, filename)
    
    # Save the PGN to the file
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(pgn)
    
    print(f"Game saved as {filepath}")
    return filepath
