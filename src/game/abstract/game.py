"""
Abstract base class for implementing turn-based games between two external player processes.
Handles core game mechanics like player turns and game state while allowing subclasses
to implement specific game rules, move validation, and win conditions. Works in conjunction
with AbstractPlayer to manage process-based players in a game environment.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from .player import AbstractPlayer


class AbstractGame(ABC):
    """
    Abstract base class for implementing turn-based games between two players.
    Manages game state, player turns, and core game mechanics while allowing
    subclasses to implement game-specific rules and logic.

    Attributes:
        _player1: First player instance
        _player2: Second player instance
        _current_player: Reference to player whose turn it is
        _is_game_over: Flag indicating if game has ended
    """

    def __init__(self, player1: AbstractPlayer, player2: AbstractPlayer) -> None:
        """
        Initialize game with two players.

        Args:
            player1: First player instance
            player2: Second player instance
        """
        self._player1 = player1
        self._player2 = player2
        self._current_player = player1
        self._is_game_over = False

    @property
    def current_player(self) -> AbstractPlayer:
        """Get the player whose turn it currently is."""
        return self._current_player

    def switch_player(self) -> None:
        """Switch active turn between players."""
        self._current_player = (
            self._player2 if self._current_player == self._player1 else self._player1
        )

    @property
    def is_game_over(self) -> bool:
        """Check if game has reached an end state."""
        return self._is_game_over

    @abstractmethod
    def initialize_game(self) -> None:
        """
        Set up initial game state.
        Must be implemented by subclasses to establish game-specific starting conditions.
        """
        pass

    @abstractmethod
    def make_move(self, move: Any) -> bool:
        """
        Execute a player's move and update game state.
        Must be implemented by subclasses to handle game-specific move validation and execution.

        Args:
            move: Game-specific move representation

        Returns:
            bool: True if move was valid and executed, False otherwise
        """
        pass

    @abstractmethod
    def determine_winner(self) -> Optional[AbstractPlayer]:
        """
        Check if game has a winner.
        Must be implemented by subclasses to evaluate game-specific win conditions.

        Returns:
            Optional[AbstractPlayer]: Winning player or None if game is ongoing/draw
        """
        pass
