"""
Lasker Morris AI player implementation using Gemini AI 2.0.
"""

import sys
import time
import os
from typing import Dict, List, Optional, Tuple, Set
from google import genai
import random
import re

# Game constants
TIME_LIMIT = 60  # 60 seconds time limit for LLM player
API_CALL_BUFFER = 2  # Buffer time for API calls
MIN_MOVE_TIME = 0.5  # Minimum time to wait between moves
MAX_MOVE_TIME = 2  # Maximum time to wait between moves
API_RATE_LIMIT = 60/15  # 15 requests per minute = 4 seconds between calls
STALEMATE_THRESHOLD = 20  # 20 consecutive moves without mills or captures
MAX_RETRIES = 2  # Maximum number of retries for LLM move generation

# Get API key from environment variable
API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyB59sCEon9MxTlYeJImh9lTSIADNFdY5jU')


class LLM:
    """
    Lasker Morris AI player implementation using Gemini AI 2.0.
    """

    def __init__(self, color: str):
        """
        Initialize AI player.

        Args:
            color: Player color ('blue' or 'orange')
        """
        self.removed_colors = []
        self.color = color
        self.opponent_color = 'orange' if color == 'blue' else 'blue'
        self.board: Dict[str, Optional[str]] = {}
        self.stones_in_hand = {'blue': 10, 'orange': 10}
        self.initialize_board()
        self.valid_points = self._get_valid_points()
        self.adjacent_points = self._get_adjacent_points()

    def initialize_board(self) -> None:
        """Initialize empty game board."""
        # All valid board points
        valid_positions = [
            'a1', 'a4', 'a7',
            'b2', 'b4', 'b6',
            'c3', 'c4', 'c5',
            'd1', 'd2', 'd3', 'd5', 'd6', 'd7',
            'e3', 'e4', 'e5',
            'f2', 'f4', 'f6',
            'g1', 'g4', 'g7'
        ]
        for pos in valid_positions:
            self.board[pos] = None

    def _get_valid_points(self) -> Set[str]:
        """Get all valid board points."""
        return set(self.board.keys())

    def _get_adjacent_points(self) -> Dict[str, List[str]]:
        """Create a mapping of each point to its adjacent points."""
        adjacent = {
            'a1': ['d1', 'a4'],
            'a4': ['a1', 'a7', 'b4'],
            'a7': ['a4', 'd7'],
            'b2': ['d2', 'b4'],
            'b4': ['b2', 'b6', 'a4', 'c4'],
            'b6': ['b4', 'd6'],
            'c3': ['d3', 'c4'],
            'c4': ['c3', 'c5', 'b4'],
            'c5': ['c4', 'd5'],
            'd1': ['a1', 'd2', 'g1'],
            'd2': ['d1', 'd3', 'b2', 'f2'],
            'd3': ['d2', 'c3', 'e3'],
            'd5': ['d6', 'c5', 'e5'],
            'd6': ['d5', 'd7', 'b6', 'f6'],
            'd7': ['d6', 'a7', 'g7'],
            'e3': ['d3', 'e4'],
            'e4': ['e3', 'e5', 'f4'],
            'e5': ['e4', 'd5'],
            'f2': ['d2', 'f4'],
            'f4': ['f2', 'f6', 'e4', 'g4'],
            'f6': ['f4', 'd6'],
            'g1': ['d1', 'g4'],
            'g4': ['g1', 'g7', 'f4'],
            'g7': ['g4', 'd7']
        }
        return adjacent

    def is_mill(self, position: str, color: str) -> bool:
        """
        Check if placing a stone at position forms a mill.

        Args:
            position: Position to check for mill formation
            color: Color of the stone ('blue' or 'orange')

        Returns:
            bool: True if placing a stone forms a mill
        """
        mills = [
            # Vertical mills
            ['a1', 'a4', 'a7'],
            ['b2', 'b4', 'b6'],
            ['c3', 'c4', 'c5'],
            ['d1', 'd2', 'd3'],
            ['d5', 'd6', 'd7'],
            ['e3', 'e4', 'e5'],
            ['f2', 'f4', 'f6'],
            ['g1', 'g4', 'g7'],
            # Horizontal mills
            ['a1', 'd1', 'g1'],
            ['b2', 'd2', 'f2'],
            ['c3', 'd3', 'e3'],
            ['a4', 'b4', 'c4'],
            ['e4', 'f4', 'g4'],
            ['c5', 'd5', 'e5'],
            ['b6', 'd6', 'f6'],
            ['a7', 'd7', 'g7']
        ]

        # Check each possible mill containing this position
        for mill in mills:
            if position in mill:
                # Create a temporary board state to check the mill
                board_copy = self.board.copy()
                board_copy[position] = color

                # Check if all positions in this mill are of the same color
                mill_stones = [board_copy[pos] for pos in mill]
                if all(stone == color for stone in mill_stones):
                    return True
        return False

    def get_valid_moves(self, color: str) -> List[Tuple[str, str, str]]:
        """
        Get list of valid moves from current board state.
        Returns list of tuples (from_pos, to_pos, remove_pos)
        """
        valid_moves = []
        stones_on_board = sum(1 for pos, c in self.board.items() if c == color)
        total_stones = stones_on_board + self.stones_in_hand[color]

        # Phase 1: Placing pieces from hand
        if self.stones_in_hand[color] > 0:
            from_pos = 'h1' if color == 'blue' else 'h2'
            for to_pos in self.valid_points:
                if self.board[to_pos] is None:
                    # Check if move forms a mill
                    self.board[to_pos] = color
                    forms_mill = self.is_mill(to_pos, color)
                    self.board[to_pos] = None

                    if forms_mill:
                        remove_positions = self._get_valid_remove_positions(color)
                        if remove_positions:  # Only add moves if there are stones to remove
                            for remove_pos in remove_positions:
                                valid_moves.append((from_pos, to_pos, remove_pos))
                        else:
                            # If no stones can be normally removed, remove any stone
                            opponent_color = 'orange' if color == 'blue' else 'blue'
                            opponent_stones = [pos for pos, stone in self.board.items() if stone == opponent_color]
                            if opponent_stones:
                                valid_moves.append(
                                    (from_pos, to_pos, opponent_stones[0]))  # Remove the first opponent's stone
                            else:
                                valid_moves.append((from_pos, to_pos, 'r0'))  # If there's no

                    else:
                        valid_moves.append((from_pos, to_pos, 'r0'))

        # Phase 2 & 3: Moving pieces on board
        if stones_on_board > 0:
            for from_pos in self.valid_points:
                if self.board[from_pos] == color:
                    # Get possible destinations
                    if total_stones > 3:
                        # Normal movement to adjacent points
                        possible_to = self.adjacent_points[from_pos]
                    else:
                        # Flying movement to any empty point
                        possible_to = self.valid_points

                    for to_pos in possible_to:
                        if self.board[to_pos] is None:
                            # Check if move forms a mill
                            self.board[from_pos] = None
                            self.board[to_pos] = color
                            forms_mill = self.is_mill(to_pos, color)
                            self.board[to_pos] = None
                            self.board[from_pos] = color

                            if forms_mill:
                                remove_positions = self._get_valid_remove_positions(color)
                                if remove_positions:  # Only add moves if there are stones to remove
                                    for remove_pos in remove_positions:
                                        valid_moves.append((from_pos, to_pos, remove_pos))
                                else:
                                    # If no stones can be normally removed, remove any stone
                                    opponent_color = 'orange' if color == 'blue' else 'blue'
                                    opponent_stones = [pos for pos, stone in self.board.items() if
                                                       stone == opponent_color]
                                    if opponent_stones:
                                        valid_moves.append(
                                            (from_pos, to_pos, opponent_stones[0]))  # Remove the first opponent's stone
                                    else:
                                        valid_moves.append(
                                            (from_pos, to_pos, 'r0'))  # If there's no opponent stone, do nothing
                            else:
                                valid_moves.append((from_pos, to_pos, 'r0'))

        return valid_moves

    def _get_valid_remove_positions(self, color: str) -> List[str]:
        """Get list of opponent's stones that can be removed."""
        opponent_color = 'orange' if color == 'blue' else 'blue'
        opponent_positions = []
        all_in_mill = True

        for pos, stone in self.board.items():
            if stone == opponent_color:
                in_mill = self.is_mill(pos, opponent_color)
                if not in_mill:
                    all_in_mill = False
                    opponent_positions.append(pos)

        # If all opponent's stones are in mills, then all positions are valid
        if all_in_mill:
            opponent_positions = [pos for pos, stone in self.board.items()
                                  if stone == opponent_color]

        return opponent_positions

    def make_move(self, move: Tuple[str, str, str]) -> None:
        """Make a move on the board."""
        from_pos, to_pos, remove_pos = move

        # Handle placing from hand
        if from_pos.startswith('h'):
            color = 'blue' if from_pos == 'h1' else 'orange'
            self.stones_in_hand[color] -= 1
            self.board[to_pos] = color

        else:
            # Handle moving on board
            color = self.board[from_pos]
            self.board[from_pos] = None
            self.board[to_pos] = color

        # Handle removing opponent's stone
        if remove_pos != 'r0':
            removed_color = self.board[remove_pos]
            self.removed_colors.append(removed_color)
            self.board[remove_pos] = None


    def update_board(self, move_str: str) -> None:
        """Update board with opponent's move."""
        from_pos, to_pos, remove_pos = move_str.split()
        self.make_move((from_pos, to_pos, remove_pos))

    def get_text(self,text: str)->str:
        """
        Extract move from LLM response text.
        
        Args:
            text: Raw response from LLM
            
        Returns:
            str: Extracted move or empty string if invalid
        """
        if not isinstance(text, str):
            return ""
        output = ""
        if '(' in text and ')' in text:
            match = re.search(r"\(([^()]+)\)", text)
            if match:
                output = match.group(1)
        else:
            output = text
        return output

    def is_valid_llm_move(self, gemini_move: str) -> str:
        """
        Validate the move returned by Gemini and ensure it adheres to the game rules.
        
        Args:
            gemini_move: Move string from LLM
            
        Returns:
            str: Valid move string or error message starting with 'Invalid'
        """
        move_parts = self.get_text(gemini_move)
        if not move_parts:
            return "Invalid: Empty move"
        move_parts = move_parts.strip().split()

        if len(move_parts) != 3:
            return "Invalid: Move must have exactly 3 parts (from, to, remove)"
            
        from_position, to_position, removal = move_parts
        valid_moves = self.get_valid_moves(self.color)
        
        if not valid_moves:
            return "Invalid: No valid moves available. The game is over."
            
        if tuple(move_parts) in valid_moves:
            return " ".join(move_parts)
            
        if (from_position not in ('h1', 'h2') and (from_position not in self.board)) or to_position not in self.board:
            return f"Invalid: Position {from_position} or {to_position} does not exist"

        if from_position not in ('h1', 'h2') and self.board[from_position] != self.color:
            return f"Invalid: The stone at {from_position} is not {self.color}'s stone"

        if self.board[to_position] is not None:
            return f"Invalid: Target position {to_position} is not empty"
            
        if self.is_mill(to_position, self.color):
            valid_removals = self._get_valid_remove_positions(self.color)
            if removal == "r0" and valid_removals:
                return "Invalid: A mill was formed but no removal was made"
            if removal not in valid_removals and removal != "r0":
                return f"Invalid: Attempt to remove an invalid stone {removal}"
                
        return "Invalid: Move does not follow game rules"

    def get_valid_llm_move(self)->str:
        """
        Get a valid move from Gemini with retries and fallback.
        
        Returns:
            str: A valid move in the format 'from_pos to_pos remove_pos'
        """
        retries = 0
        while retries < MAX_RETRIES:
            try:
                move = self.get_llm_move("" if retries == 0 else f"Previous move was invalid. Attempt {retries + 1}")
                move = self.is_valid_llm_move(move)
                if not move.startswith("Invalid"):
                    return move
                retries += 1
            except Exception as e:
                print(f"Error getting LLM move: {str(e)}", file=sys.stderr)
                retries += 1

        # Fallback to random move if LLM fails
        print("LLM failed to provide valid move, falling back to random move", file=sys.stderr)
        return self.get_random_move()

    def get_random_move(self)-> str:
        """
        Return a random valid move from the list of valid moves.
        
        Returns:
            str: A valid move in the format 'from_pos to_pos remove_pos'
        """
        valid_moves = self.get_valid_moves(self.color)

        if valid_moves:
            move = ' '.join(random.choice(valid_moves))
            return move
        else:
            return "Invalid. No valid moves available. The game is over."

    def get_llm_move(self,hints: str) -> str:
        """
        Get the next move from Gemini given the board state and player color.
        
        Args:
            hints: Additional hints or error messages from previous attempts
            
        Returns:
            str: The move in the format 'from_pos to_pos remove_pos'
        """
        client = genai.Client(api_key=API_KEY)
        valid_positions = [
            'a1', 'a4', 'a7',
            'b2', 'b4', 'b6',
            'c3', 'c4', 'c5',
            'd1', 'd2', 'd3', 'd5', 'd6', 'd7',
            'e3', 'e4', 'e5',
            'f2', 'f4', 'f6',
            'g1', 'g4', 'g7'
        ]
        adjacent = {
            'a1': ['d1', 'a4'],
            'a4': ['a1', 'a7', 'b4'],
            'a7': ['a4', 'd7'],
            'b2': ['d2', 'b4'],
            'b4': ['b2', 'b6', 'a4', 'c4'],
            'b6': ['b4', 'd6'],
            'c3': ['d3', 'c4'],
            'c4': ['c3', 'c5', 'b4'],
            'c5': ['c4', 'd5'],
            'd1': ['a1', 'd2', 'g1'],
            'd2': ['d1', 'd3', 'b2', 'f2'],
            'd3': ['d2', 'c3', 'e3'],
            'd5': ['d6', 'c5', 'e5'],
            'd6': ['d5', 'd7', 'b6', 'f6'],
            'd7': ['d6', 'a7', 'g7'],
            'e3': ['d3', 'e4'],
            'e4': ['e3', 'e5', 'f4'],
            'e5': ['e4', 'd5'],
            'f2': ['d2', 'f4'],
            'f4': ['f2', 'f6', 'e4', 'g4'],
            'f6': ['f4', 'd6'],
            'g1': ['d1', 'g4'],
            'g4': ['g1', 'g7', 'f4'],
            'g7': ['g4', 'd7']
        }
        mills = [
            # Vertical mills
            ['a1', 'a4', 'a7'],
            ['b2', 'b4', 'b6'],
            ['c3', 'c4', 'c5'],
            ['d1', 'd2', 'd3'],
            ['d5', 'd6', 'd7'],
            ['e3', 'e4', 'e5'],
            ['f2', 'f4', 'f6'],
            ['g1', 'g4', 'g7'],
            # Horizontal mills
            ['a1', 'd1', 'g1'],
            ['b2', 'd2', 'f2'],
            ['c3', 'd3', 'e3'],
            ['a4', 'b4', 'c4'],
            ['e4', 'f4', 'g4'],
            ['c5', 'd5', 'e5'],
            ['b6', 'd6', 'f6'],
            ['a7', 'd7', 'g7']
        ]

        rules = (
            "Here is a game, please give me only one move"
            "Game: Lasker Morris (Ten Men's Morris)\n"
            "1. Two players: Blue and Orange. Blue moves first.\n"
            "2. Each player has 10 stones and takes turns to place/move them.\n"
            "3. Stones can be placed on board points labeled as (a1, a3, ... g7).\n"
            "4. A 'mill' is formed when three same-color stones are in a line.\n"
            "5. If a player forms a mill, they can remove an opponent's stone (not in a mill if possible).\n"
            "6. Moves:\n"
            "   - Place a stone from hand.\n"
            "   - Move a stone to an adjacent point.\n"
            "   - If only 3 stones remain, they can 'fly' anywhere.\n"
            "7. Game ends when a player has only 2 stones or no valid moves.\n"
            "8. Illegal moves (e.g., placing on an occupied point) result in an automatic loss.\n"
            "Follow these rules and respond with the best move given the board state.\n"
        
            "### Stone Locations\n"
            "- Stones are either **on the board** or **in the player's hand** (if they haven't been placed yet).\n"
            "- **'h1'** denotes the **blue player's hand**, and **'h2'** denotes the **orange player's hand**.\n"
            "- Players can access only their own hand, not the opponent's hand.\n"
            "- A player **cannot take back** a stone from the board to their hand.\n\n"

            "### Response Format Requirement\n"
            "Your response **must** be structured as follows:\n"
            "1. **Describe the move in natural language**.\n"
            "2. **Follow this with the exact move in parentheses**.\n"
            "3. **Use the following format strictly**:\n"
            "   - (A B C) where:\n"
            "     - **A** = current stone location (e.g., 'h1' or 'h2' for hand, or a board point like 'a4').\n"
            "     - **B** = new location on the board.\n"
            "     - **C** = opponent stone to remove ('r0' if no removal).\n"
            "4. **Examples**:\n"
            "   - 'Move from h1 to d1. This will not form a mill, so no removal is necessary, so (h1 d1 r0).'\n"
            "   - 'Move from e3 to e4, forming a mill. Removing opponent's stone at f4. (e3 e4 f4).'\n"
            "   - 'Move from a4 to b4. No mill is formed. (a4 b4 r0).'\n\n"
            "Return **only the formatted response** without extra explanations.\n"
            
            f"###Board:\n{valid_positions}\n"
            f"###mills:\n{mills}\n"
            f"###adjacent points:\n{adjacent}\n"
            f"###color:\n{self.color}\n"
            f"###stone in hand:\n{self.stones_in_hand}\n"
        
            #f"\n{hints}\n"
            f"Current board state:\n{self.board}\n"
            f"Your color: {self.color}\n"
        )
        response = client.models.generate_content(model="gemini-2.0-flash", contents=rules)
        #print("response",response)
        #print(self.board)
        return response.text


def main():
    """
    Main function to handle game communication.
    Manages the game loop, player initialization, and move processing.
    """
    ai = None
    last_api_call_time = 0  # Track last API call time
    
    try:
        while True:
            try:
                # Read input from referee with timeout
                input_line = input().strip()

                # Check for game end
                if input_line.startswith('END:'):
                    break

                # Initialize AI with assigned color
                if input_line in ['blue', 'orange']:
                    ai = LLM(input_line)
                    if input_line == 'blue':
                        # Blue moves first
                        start_time = time.time()
                        
                        # Ensure we respect API rate limits but with minimal delay
                        time_since_last_call = time.time() - last_api_call_time
                        if time_since_last_call < API_RATE_LIMIT:
                            time.sleep(max(0.1, API_RATE_LIMIT - time_since_last_call))
                        
                        move = ai.get_valid_llm_move()
                        last_api_call_time = time.time()
                        
                        # Calculate remaining time and add minimal delay
                        elapsed_time = time.time() - start_time
                        remaining_time = TIME_LIMIT - elapsed_time - API_CALL_BUFFER
                        
                        if remaining_time > MIN_MOVE_TIME:
                            # Add minimal delay for game flow
                            delay = min(MAX_MOVE_TIME, remaining_time * 0.1)  # Use 10% of remaining time
                            time.sleep(delay)
                            
                        ai.update_board(move)
                        print(move, flush=True)
                else:
                    # Process opponent's move and respond
                    if ai:
                        try:
                            # Update board with opponent's move
                            ai.update_board(input_line)
                            
                            start_time = time.time()
                            
                            # Ensure we respect API rate limits but with minimal delay
                            time_since_last_call = time.time() - last_api_call_time
                            if time_since_last_call < API_RATE_LIMIT:
                                time.sleep(max(0.1, API_RATE_LIMIT - time_since_last_call))
                            
                            # Generate and make our move
                            move = ai.get_valid_llm_move()
                            last_api_call_time = time.time()
                            
                            # Calculate remaining time and add minimal delay
                            elapsed_time = time.time() - start_time
                            remaining_time = TIME_LIMIT - elapsed_time - API_CALL_BUFFER
                            
                            if remaining_time > MIN_MOVE_TIME:
                                # Add minimal delay for game flow
                                delay = min(MAX_MOVE_TIME, remaining_time * 0.1)  # Use 10% of remaining time
                                time.sleep(delay)
                                
                            ai.update_board(move)
                            print(move, flush=True)
                            
                        except Exception as e:
                            print(f"Error processing move: {str(e)}", file=sys.stderr)
                            # Try to make a random move as fallback without delay
                            move = ai.get_random_move()
                            ai.update_board(move)
                            print(move, flush=True)

            except EOFError:
                break
            except Exception as e:
                print(f"Critical error in main loop: {str(e)}", file=sys.stderr)
                sys.exit(1)
    except KeyboardInterrupt:
        print("Game interrupted by user", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()