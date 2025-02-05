"""
TicTacToe AI player implementation using minimax algorithm.
"""

import sys
from typing import Dict, List, Optional, Tuple

class TicTacToeAI:
    """
    AI player for Tic-tac-toe using minimax algorithm.
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
        self.initialize_board()

    def initialize_board(self) -> None:
        """Initialize empty game board."""
        for col in 'abc':
            for row in '123':
                self.board[f"{col}{row}"] = None

    def get_valid_moves(self) -> List[str]:
        """Get list of valid moves from current board state."""
        return [pos for pos, val in self.board.items() if val is None]

    def make_move(self, position: str, color: str) -> None:
        """Make a move on the board."""
        self.board[position] = color

    def undo_move(self, position: str) -> None:
        """Undo a move on the board."""
        self.board[position] = None

    def is_winner(self, color: str) -> bool:
        """Check if specified color has won."""
        win_combinations = [
            # Rows
            ["a1", "b1", "c1"],
            ["a2", "b2", "c2"],
            ["a3", "b3", "c3"],
            # Columns
            ["a1", "a2", "a3"],
            ["b1", "b2", "b3"],
            ["c1", "c2", "c3"],
            # Diagonals
            ["a1", "b2", "c3"],
            ["a3", "b2", "c1"],
        ]

        for combo in win_combinations:
            if all(self.board[pos] == color for pos in combo):
                return True
        return False

    def is_board_full(self) -> bool:
        """Check if board is full."""
        return all(val is not None for val in self.board.values())

    def evaluate_board(self) -> int:
        """
        Evaluate current board state.
        Returns:
            100 if AI wins
            -100 if opponent wins
            0 for draw or ongoing game
        """
        if self.is_winner(self.color):
            return 100
        elif self.is_winner(self.opponent_color):
            return -100
        return 0

    def minimax(self, depth: int, is_maximizing: bool) -> Tuple[int, Optional[str]]:
        """
        Minimax algorithm implementation.
        
        Args:
            depth: Current depth in game tree
            is_maximizing: True if maximizing player's turn
        
        Returns:
            Tuple of (best score, best move)
        """
        if self.is_winner(self.color):
            return 100, None
        elif self.is_winner(self.opponent_color):
            return -100, None
        elif self.is_board_full():
            return 0, None

        valid_moves = self.get_valid_moves()
        
        if is_maximizing:
            best_score = float('-inf')
            best_move = None
            
            for move in valid_moves:
                self.make_move(move, self.color)
                score, _ = self.minimax(depth + 1, False)
                self.undo_move(move)
                
                if score > best_score:
                    best_score = score
                    best_move = move
                    
            return best_score, best_move
        else:
            best_score = float('inf')
            best_move = None
            
            for move in valid_moves:
                self.make_move(move, self.opponent_color)
                score, _ = self.minimax(depth + 1, True)
                self.undo_move(move)
                
                if score < best_score:
                    best_score = score
                    best_move = move
                    
            return best_score, best_move

    def get_best_move(self) -> str:
        """Get best move using minimax algorithm."""
        _, best_move = self.minimax(0, True)
        return best_move if best_move else self.get_valid_moves()[0]

    def update_board(self, move: str, color: str) -> None:
        """Update board with opponent's move."""
        self.board[move] = color

def main():
    """Main function to handle game communication."""
    ai = None
    
    while True:
        try:
            # Read input from referee
            input_line = input().strip()
            
            # Initialize AI with assigned color
            if input_line in ['blue', 'orange']:
                ai = TicTacToeAI(input_line)
                if input_line == 'blue':
                    # Blue moves first
                    move = ai.get_best_move()
                    ai.update_board(move, ai.color)
                    print(move, flush=True)
            else:
                # Process opponent's move and respond
                if ai:
                    ai.update_board(input_line, ai.opponent_color)
                    move = ai.get_best_move()
                    ai.update_board(move, ai.color)
                    print(move, flush=True)
                    
        except EOFError:
            break

if __name__ == "__main__":
    main() 