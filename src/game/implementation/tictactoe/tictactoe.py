import random
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Dict, List, Optional, Tuple

import click
from colorama import Fore, Style

from ....config import Config, TicTacToeConfig
from ...abstract import AbstractGame
from .tictactoe_player import TicTacToePlayer
from .web import TicTacToeWeb


class TicTacToe(AbstractGame):
    """
    Implementation of Tic-tac-toe game.
    Manages game state including board and move validation.
    """

    VALID_COLUMNS = set("abc")
    VALID_ROWS = set("123")

    def __init__(
        self,
        player1_command: str,
        player2_command: str,
        visual: bool = TicTacToeConfig.DEFAULT_VIS,
        random_assignment: bool = TicTacToeConfig.DEFAULT_RAND,
        move_timeout: int = TicTacToeConfig.GAME_TIMEOUT,
        enable_logging: bool = TicTacToeConfig.DEFAULT_LOG,
        debug: bool = TicTacToeConfig.DEFAULT_DEBUG,
        port: int = Config.DEFAULT_WEB_PORT,
    ):
        """
        Initialize game with player commands and game settings.

        Args:
            player1_command: Shell command for first player
            player2_command: Shell command for second player
            visual: Whether to show visual board state
            random_assignment: Whether to randomly assign X/O symbols
            move_timeout: Timeout in seconds for each player's move
            enable_logging: Whether to log all communication
            debug: Whether to show debug information
        """
        self.move_timeout = move_timeout
        self.debug = debug
        self.enable_logging = enable_logging
        self.port = port

        # Initialize players with randomly assigned colors
        colors = ["blue", "orange"]
        if random_assignment:
            random.shuffle(colors)

        # Create players with assigned symbols
        player1 = TicTacToePlayer(
            player1_command, colors[0], self.enable_logging)
        player2 = TicTacToePlayer(
            player2_command, colors[1], self.enable_logging)

        super().__init__(player1, player2)

        self.board: Dict[str, Optional[str]] = {}
        self.visual = visual
        self.web = TicTacToeWeb(self) if visual else None
        self.move_history: List[str] = []
        self.initialize_game()

    def initialize_game(self) -> None:
        """Initialize game board and start player processes."""
        # Initialize empty board (1-3, a-c)
        self.board = {
            f"{col}{row}": None for col in self.VALID_COLUMNS for row in self.VALID_ROWS
        }

        self._player1.start()
        self._player2.start()

        if self.visual and self.web:
            self.web.start_web_server(self.port)

        # Ensure X player goes first
        self._current_player = self._player1 if self._player1.is_x() else self._player2
        self._current_player.write("blue")
        other_player = (
            self._player2 if self._current_player == self._player1 else self._player1
        )
        other_player.write("orange")

    def _validate_move_format(self, move: str) -> Tuple[bool, Optional[str]]:
        """
        Validate move format.

        Args:
            move: String representing board position (e.g. "a1")

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        move = move.strip().lower()

        if len(move) != 2:
            return False, f"Invalid move format: {move}. Must be in format 'a1'"

        col, row = move[0], move[1]

        if col not in self.VALID_COLUMNS:
            return (
                False,
                f"Invalid column: {col}. Must be one of: {', '.join(sorted(self.VALID_COLUMNS))}",
            )

        if row not in self.VALID_ROWS:
            return (
                False,
                f"Invalid row: {row}. Must be one of: {', '.join(sorted(self.VALID_ROWS))}",
            )

        return True, None

    def make_move(self, move: str) -> bool:
        """
        Execute a player's move if valid.

        Args:
            move: String representing board position (e.g. "a1")

        Returns:
            bool: True if move was valid and executed
        """
        try:
            # Validate move format
            is_valid, error_msg = self._validate_move_format(move)
            if not is_valid:
                click.echo(f"\n{Fore.RED}{error_msg}{Style.RESET_ALL}")
                return False

            move = move.lower()
            # Check if position is available
            if not self._is_valid_move(move):
                return False

            # Execute move
            self._execute_move(move)
            self.move_history.append(move)

            if self.debug:
                self._show_state(move)

            return True

        except Exception as e:
            click.echo(f"\n{Fore.RED}Error processing move: {str(e)}{Style.RESET_ALL}")
            return False

    def _is_valid_move(self, position: str) -> bool:
        """
        Validate move according to game rules.

        Args:
            position: Board position (e.g. "a1")

        Returns:
            bool: True if move is valid
        """
        if position not in self.board:
            click.echo(
                f"\n{Fore.RED}Invalid move: Position {position} does not exist on the board{Style.RESET_ALL}"
            )
            return False

        if self.board[position] is not None:
            click.echo(
                f"\n{Fore.RED}Invalid move: Position {position} is already occupied{Style.RESET_ALL}"
            )
            return False

        return True

    def _execute_move(self, position: str) -> None:
        """Execute a validated move."""
        self.board[position] = self._current_player.get_symbol()

        if self.visual and self.web:
            self.web.update_history(position)

    def _check_winner(self) -> Optional[str]:
        """
        Check for winning combinations.

        Returns:
            Optional[str]: Winning symbol (X/O) or None if no winner
        """
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
            values = [self.board[pos] for pos in combo]
            if (None not in values) and (len(set(values)) == 1):
                return values[0]
        return None

    def _is_board_full(self) -> bool:
        """Check if the board is completely filled."""

        if all(value is not None for value in self.board.values()):
            self._is_game_over = True
            return True
        return False

    def determine_winner(self) -> Optional[TicTacToePlayer]:
        """
        Check win conditions and determine game outcome.
        Returns:
            Optional[TicTacToePlayer]: Winning player or None for draw
        """
        winning_symbol = self._check_winner()

        if winning_symbol:
            self._is_game_over = True
            return (
                self._player1
                if self._player1.get_symbol() == winning_symbol
                else self._player2
            )

        return None

    def _get_move_with_timeout(self) -> Optional[str]:
        """
        Get a move from the current player with timeout.

        Returns:
            Optional[str]: The move if received within timeout, None if timeout occurred
        """
        with ThreadPoolExecutor(max_workers=1) as executor:
            try:
                future = executor.submit(self.current_player.read)
                return future.result(timeout=self.move_timeout)
            except TimeoutError:
                click.echo(
                    f"\n{Fore.RED}Move timeout: Player {self.current_player.get_symbol()} "
                    f"took too long to respond{Style.RESET_ALL}"
                )
                return None

    def run_game(self) -> Optional[TicTacToePlayer]:
        """Main game loop."""
        while not self.is_game_over:
            move = self._get_move_with_timeout()

            if move is None:  # Timeout occurred
                self._is_game_over = True
                winner = (
                    self._player2
                    if self.current_player == self._player1
                    else self._player1
                )
                message = f"END: {winner.get_symbol()} WINS! {self.current_player.get_symbol()} LOSES! Time out!"
                if self.visual:
                    self.web.end_message = message
                self._cleanup_game()
                return winner

            if not self.make_move(move):
                self._is_game_over = True
                winner = (
                    self._player2
                    if self.current_player == self._player1
                    else self._player1
                )
                message = f"END: {winner.get_symbol()} WINS! {self.current_player.get_symbol()} LOSES! Invalid move {move}!"
                if self.visual:
                    self.web.end_message = message
                self._cleanup_game()
                return winner

            # Write move to other player
            other_player = (
                self._player2 if self.current_player == self._player1 else self._player1
            )
            other_player.write(move)
            # Check for winner or draw
            winner = self.determine_winner()
            if winner is not None:
                message = f"END: {winner.get_symbol()} WINS! {other_player.get_symbol()} LOSES! Three in a row!"
                if self.visual:
                    self.web.end_message = message
                self._cleanup_game()
                return winner
            elif self._is_board_full():
                message = "Draw!"
                if self.visual:
                    self.web.end_message = message
                self._cleanup_game()
                return None

            self.switch_player()

        return None

    def _cleanup_game(self) -> None:
        """Clean up game resources."""
        self._player1.stop()
        self._player2.stop()
