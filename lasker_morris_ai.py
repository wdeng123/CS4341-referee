"""
Lasker Morris AI player implementation using minimax algorithm with alpha-beta pruning.
"""

import sys
from typing import Dict, List, Optional, Tuple, Set

class LaskerMorrisAI:
    """
    AI player for Lasker Morris using minimax algorithm with alpha-beta pruning.
    """
    def __init__(self, color: str):
        """
        Initialize AI player.
        
        Args:
            color: Player color ('blue' or 'orange')
        """
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
        """Check if placing a stone at position forms a mill."""
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

        for mill in mills:
            if position in mill:
                if all(self.board.get(pos) == color for pos in mill):
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
                    original_value = self.board[to_pos]
                    self.board[to_pos] = color
                    forms_mill = self.is_mill(to_pos, color)
                    self.board[to_pos] = original_value

                    if forms_mill:
                        remove_positions = self._get_valid_remove_positions(color)
                        for remove_pos in remove_positions:
                            valid_moves.append((from_pos, to_pos, remove_pos))
                    else:
                        valid_moves.append((from_pos, to_pos, 'r0'))

        # Phase 2 & 3: Moving pieces on board
        else:
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
                                    for remove_pos in remove_positions:
                                        valid_moves.append((from_pos, to_pos, remove_pos))

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
            opponent_positions = [pos for pos, stone in self.valid_points
                               if self.board.items() == opponent_color]

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
            self.board[remove_pos] = None



    def undo_move(self, move: Tuple[str, str, str]) -> None:
        """Undo a move on the board."""
        from_pos, to_pos, remove_pos = move

        #test
        opponent_color = 'orange' if from_pos == 'h1' else 'blue'


        # Restore removed stone if any
        if remove_pos != 'r0':
            self.board[remove_pos] = opponent_color

        # Handle placing from hand
        if from_pos.startswith('h'):
            color = 'blue' if from_pos == 'h1' else 'orange'
            self.stones_in_hand[color] += 1
            self.board[to_pos] = None
        else:
            # Handle moving on board
            color = self.board[to_pos]
            self.board[to_pos] = None
            self.board[from_pos] = color


    def evaluate_board(self) -> int:
        """
        Evaluate current board state.
        Returns positive score for favorable positions, negative for unfavorable.
        """
        # Count stones
        ai_stones = sum(1 for _, stone in self.board.items() if stone == self.color)
        ai_stones += self.stones_in_hand[self.color]
        
        opp_stones = sum(1 for _, stone in self.board.items() if stone == self.opponent_color)
        opp_stones += self.stones_in_hand[self.opponent_color]

        # Count mills
        ai_mills = self._count_mills(self.color)
        opp_mills = self._count_mills(self.opponent_color)

        # Count potential mills (two stones in line)
        ai_potential = self._count_potential_mills(self.color)
        opp_potential = self._count_potential_mills(self.opponent_color)

        # Winning/losing conditions
        if opp_stones <= 2:
            return 1000
        if ai_stones <= 2:
            return -1000

        # Combine factors with weights
        score = (ai_stones - opp_stones) * 10
        score += (ai_mills - opp_mills) * 50
        score += (ai_potential - opp_potential) * 30

        return score

    def _count_mills(self, color: str) -> int:
        """Count number of mills for given color."""
        mills = 0
        counted_positions = set()

        for pos in self.valid_points:
            if self.board[pos] == color and pos not in counted_positions:
                if self.is_mill(pos, color):
                    mills += 1
                    # Add all positions in this mill to counted set
                    for mill in self._get_mills_containing(pos):
                        if all(self.board[p] == color for p in mill):
                            counted_positions.update(mill)

        return mills

    def _count_potential_mills(self, color: str) -> int:
        """Count number of potential mills (two stones in line) for given color."""
        potential = 0
        for mill in self._get_all_possible_mills():
            stones = sum(1 for pos in mill if self.board[pos] == color)
            empty = sum(1 for pos in mill if self.board[pos] is None)
            if stones == 2 and empty == 1:
                potential += 1
        return potential

    def _get_mills_containing(self, position: str) -> List[List[str]]:
        """Get all possible mills containing the given position."""
        mills = [
            ['a1', 'a4', 'a7'], ['b2', 'b4', 'b6'], ['c3', 'c4', 'c5'],
            ['d1', 'd2', 'd3'], ['d5', 'd6', 'd7'], ['e3', 'e4', 'e5'],
            ['f2', 'f4', 'f6'], ['g1', 'g4', 'g7'],
            ['a1', 'd1', 'g1'], ['b2', 'd2', 'f2'], ['c3', 'd3', 'e3'],
            ['a4', 'b4', 'c4'], ['e4', 'f4', 'g4'], ['c5', 'd5', 'e5'],
            ['b6', 'd6', 'f6'], ['a7', 'd7', 'g7']
        ]
        return [mill for mill in mills if position in mill]

    def _get_all_possible_mills(self) -> List[List[str]]:
        """Get all possible mill combinations on the board."""
        return [
            ['a1', 'a4', 'a7'], ['b2', 'b4', 'b6'], ['c3', 'c4', 'c5'],
            ['d1', 'd2', 'd3'], ['d5', 'd6', 'd7'], ['e3', 'e4', 'e5'],
            ['f2', 'f4', 'f6'], ['g1', 'g4', 'g7'],
            ['a1', 'd1', 'g1'], ['b2', 'd2', 'f2'], ['c3', 'd3', 'e3'],
            ['a4', 'b4', 'c4'], ['e4', 'f4', 'g4'], ['c5', 'd5', 'e5'],
            ['b6', 'd6', 'f6'], ['a7', 'd7', 'g7']
        ]

    def minimax(self, depth: int, is_maximizing: bool, alpha: float = float('-inf'), 
                beta: float = float('inf')) -> Tuple[int, Optional[Tuple[str, str, str]]]:
        """
        Minimax algorithm implementation with alpha-beta pruning.
        
        Args:
            depth: Current depth in game tree
            is_maximizing: True if maximizing player's turn
            alpha: Best value that maximizer can guarantee
            beta: Best value that minimizer can guarantee
        
        Returns:
            Tuple of (best score, best move)
        """
        if depth == 0:
            return self.evaluate_board(), None

        color = self.color if is_maximizing else self.opponent_color
        valid_moves = self.get_valid_moves(color)

        if not valid_moves:
            return -1000 if is_maximizing else 1000, None

        best_move = None
        if is_maximizing:
            best_score = float('-inf')
            for move in valid_moves:
                self.make_move(move)
                score, _ = self.minimax(depth - 1, False, alpha, beta)
                self.undo_move(move)

                if score > best_score:
                    best_score = score
                    best_move = move

                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
        else:
            best_score = float('inf')
            for move in valid_moves:
                self.make_move(move)
                score, _ = self.minimax(depth - 1, True, alpha, beta)
                self.undo_move(move)

                if score < best_score:
                    best_score = score
                    best_move = move

                beta = min(beta, best_score)
                if beta <= alpha:
                    break

        return best_score, best_move

    def get_best_move(self) -> str | tuple[str, str, str]:
        """Get best move using minimax algorithm with alpha-beta pruning."""
        _, best_move = self.minimax(4, True)  # Adjust depth based on performance
        if best_move:
            #return f"{best_move[0]} {best_move[1]} {best_move[2]}"
            return f"{best_move[0]} {best_move[1]} {best_move[2]}"
        return self.get_valid_moves(self.color)[0]

    def update_board(self, move_str: str) -> None:
        """Update board with opponent's move."""
        from_pos, to_pos, remove_pos = move_str.split()

        self.make_move((from_pos, to_pos, remove_pos))


def main():
    """Main function to handle game communication."""
    ai = None
    
    while True:
        try:
            # Read input from referee
            input_line = input().strip()
            
            # Initialize AI with assigned color
            if input_line in ['blue', 'orange']:
                ai = LaskerMorrisAI(input_line)
                if input_line == 'blue':
                    # Blue moves first
                    move = ai.get_best_move()
                    ai.update_board(move)
                    print(move, flush=True)
            else:
                # Process opponent's move and respond
                if ai:
                    if input_line.startswith('END:'):
                        break
                    ai.update_board(input_line)
                    move = ai.get_best_move()
                    ai.update_board(move)
                    print(move, flush=True)
                    
        except EOFError:
            break

if __name__ == "__main__":
    main() 