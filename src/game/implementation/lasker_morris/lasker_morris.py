import random
import time
from typing import Dict, Optional, Set

import click
from colorama import Fore, Style

from ...abstract import AbstractGame
from .lasker_player import LaskerPlayer


class LaskerMorris(AbstractGame):
    """
    Implementation of Lasker Morris game.
    Manages game state including board, player hands, and move validation.
    """

    # TODO: Make random colorselection a flag

    def __init__(self, player1_command: str, player2_command: str, visual: bool = True):
        """
        Initialize game with player commands and randomly assign colors.

        Args:
            player1_command: Shell command for first player
            player2_command: Shell command for second player
        """
        # Randomly assign colors to players
        colors = ["blue", "orange"]
        random.shuffle(colors)

        # Create players with assigned colors
        player1 = LaskerPlayer(player1_command, colors[0])
        player2 = LaskerPlayer(player2_command, colors[1])

        # Initialize parent class
        super().__init__(player1, player2)

        # Initialize game state
        self.board: Dict[str, Optional[str]] = {}  # Maps position to player color
        self.player_hands: Dict[str, int] = {"blue": 10, "orange": 10}
        self.invalid_fields: Set[str] = {
            "a2",
            "a3",
            "a5",
            "a6",
            "b1",
            "b3",
            "b5",
            "b7",
            "c1",
            "c2",
            "c6",
            "c7",
            "d4",
            "e1",
            "e2",
            "e6",
            "e7",
            "f1",
            "f3",
            "f5",
            "f7",
            "g2",
            "g3",
            "g5",
            "g6",
        }
        self.visual = visual
        self.initialize_game()

    def initialize_game(self) -> None:
        """Initialize game board and start player processes."""
        # Initialize empty board (1-7, a-g)
        for num in range(1, 8):
            for letter in "abcdefg":
                position = f"{letter}{num}"
                self.board[position] = None

        # Start player processes
        self._player1.start()
        self._player2.start()

        # Ensure blue player goes first
        self._current_player = (
            self._player1 if self._player1.is_blue() else self._player2
        )

        # Send current player staring command
        self._current_player.write("blue")

    def make_move(self, move: str) -> bool:
        """
        Execute a player's move if valid.

        Args:
            move: String in format "A B C" where:
                A: Current stone location (or hand 'h')
                B: Target board location
                C: Remove opponent's stone location or 'r0'

        Returns:
            bool: True if move was valid and executed
        """
        try:
            # Parse move
            parts = move.strip().split()
            if len(parts) != 3:
                return False

            source, target, remove = parts

            # Validate move
            if not self._is_valid_move(source, target, remove):
                return False

            # Execute move
            self._execute_move(source, target, remove)

            if self.visual:
                self._show_state(move)

            return True

        except Exception:
            return False

    def _is_valid_move(self, source: str, target: str, remove: str) -> bool:
        """
        Validate move according to game rules with descriptive error messages.

        Args:
            source: Starting position of stone ('h' if from hand)
            target: Target position for stone placement/movement
            remove: Position of opponent's stone to remove ('r0' if none)

        Returns:
            bool: True if move is valid according to game rules
        """
        # Validate target position
        if target in self.invalid_fields or target not in self.board:
            click.echo(
                f"\n{Fore.RED}Invalid move: Target position {target} does not exist on the board{Style.RESET_ALL}"
            )
            return False
        if self.board[target] is not None:
            click.echo(
                f"\n{Fore.RED}Invalid move: Target position {target} is already occupied{Style.RESET_ALL}"
            )
            click.echo(self.board[target])
            return False

        # Validate source position
        if source != "h":  # If moving a stone (not from hand)
            if source in self.invalid_fields or source not in self.board:
                click.echo(
                    f"\n{Fore.RED}Invalid move: Source position {source} does not exist on the board{Style.RESET_ALL}"
                )
                return False
            if self.board[source] != self._current_player.color:
                click.echo(
                    f"\n{Fore.RED}Invalid move: {self._current_player.color} player tried to move opponent's stone from {source}{Style.RESET_ALL}"
                )
                return False
            # Check if player has exactly 3 pieces for flying rule
            if (
                self._count_player_pieces(self._current_player.color) > 3
            ):  # Only enforce adjacent moves if more than 3 pieces
                if not self._check_corret_step(source, target):
                    click.echo(
                        f"""\n{Fore.RED}Invalid move: Cannot move from {source} to {target} -
                        must move to adjacent position when you have more than 3 pieces{Style.RESET_ALL}"""
                    )
                    return False

        elif self.player_hands[self._current_player.get_color()] <= 0:
            click.echo(
                f"\n{Fore.RED}Invalid move: {self._current_player.color} player has no stones left in hand{Style.RESET_ALL}"
            )
            return False

        # Validate remove position
        if remove != "r0":  # If removing opponent's stone
            if remove in self.invalid_fields or remove not in self.board:
                click.echo(
                    f"\n{Fore.RED}Invalid move: Cannot remove stone - position {remove} does not exist on the board{Style.RESET_ALL}"
                )
                return False
            if self.board[remove] is None:
                click.echo(
                    f"\n{Fore.RED}Invalid move: Cannot remove stone - position {remove} is empty{Style.RESET_ALL}"
                )
                return False
            if self.board[remove] == self.current_player.color:
                click.echo(
                    f"\n{Fore.RED}Invalid move: {self._current_player.color} player tried to remove their own stone at {remove}{Style.RESET_ALL}"
                )
                return False
            if not self._is_mill(source, target):
                click.echo(
                    f"\n{Fore.RED}Invalid move: Cannot remove opponent's stone - move does not form a mill{Style.RESET_ALL}"
                )
                return False
        else:  # If not removing any stone
            if self._is_mill(source, target):
                click.echo(
                    f"\n{Fore.RED}Invalid move: Must remove an opponent's stone after forming a mill{Style.RESET_ALL}"
                )
                return False

        return True

    def _is_mill(self, source: str, target: str) -> bool:
        """
        Check if placing a stone at target position forms a mill.

        Args:
            source: Starting position of the stone (or 'h' if from hand)
            target: Target position where stone is placed

        Returns:
            bool: True if move forms a mill, False otherwise
        """
        # Get the color of the current player
        color = self.current_player.color

        # Define possible mill combinations (each list represents positions that form a mill)
        mills = [
            # Horizontal mills
            ["a1", "a4", "a7"],
            ["b2", "b4", "b6"],
            ["c3", "c4", "c5"],
            ["d1", "d2", "d3"],
            ["d5", "d6", "d7"],
            ["e3", "e4", "e5"],
            ["f2", "f4", "f6"],
            ["g1", "g4", "g7"],
            # Vertical mills
            ["a1", "d1", "g1"],
            ["b2", "d2", "f2"],
            ["c3", "d3", "e3"],
            ["a4", "b4", "c4"],
            ["e4", "f4", "g4"],
            ["c5", "d5", "e5"],
            ["b6", "d6", "f6"],
            ["a7", "d7", "g7"],
        ]

        # Check each possible mill combination
        for mill in mills:
            if target in mill:  # Only check mills that include the target position
                # Count stones of current player's color in this mill combination
                stones_in_mill = 0
                for pos in mill:
                    if pos == target:  # Count the target position
                        stones_in_mill += 1
                    elif (
                        pos != source and self.board[pos] == color
                    ):  # Count existing stones
                        stones_in_mill += 1

                # If all three positions in the mill are occupied by player's stones
                if stones_in_mill == 3:
                    return True

        return False

    def _check_corret_step(self, source: str, target: str) -> bool:
        """
        Check if a move from source to target is to a neighboring position.

        Args:
            source: Starting position of the stone
            target: Target position where stone will move

        Returns:
            bool: True if target is a neighbor of source, False otherwise
        """
        # Define adjacent positions for each valid board position
        neighbors = {
            "a1": ["a4", "d1", "a4"],
            "a4": ["a1", "a7", "b4"],
            "a7": ["a4", "d7"],
            "b2": ["b4", "d2"],
            "b4": ["b2", "b6", "a4", "c4"],
            "b6": ["b4", "d6"],
            "c3": ["c4", "d3"],
            "c4": ["c3", "c5", "b4"],
            "c5": ["c4", "d5"],
            "d1": ["a1", "d2", "g1"],
            "d2": ["b2", "d1", "d3", "f2"],
            "d3": ["c3", "d2", "e3"],
            "d5": ["c5", "d6", "e5"],
            "d6": ["b6", "d5", "d7", "f6"],
            "d7": ["a7", "d6", "g7"],
            "e3": ["d3", "e4"],
            "e4": ["e3", "e5", "f4"],
            "e5": ["d5", "e4"],
            "f2": ["d2", "f4"],
            "f4": ["e4", "f2", "f6", "g4"],
            "f6": ["d6", "f4"],
            "g1": ["d1", "g4"],
            "g4": ["f4", "g1", "g7"],
            "g7": ["d7", "g4"],
        }

        # If either position is invalid, return False
        if source not in neighbors or target not in neighbors:
            return False

        # Check if target is in the list of neighbors for the source position
        return target in neighbors[source]

    def _count_player_pieces(self, color: str) -> int:
        """
        Count total number of pieces a player has on the board.

        Args:
            color: Player color to count pieces for

        Returns:
            int: Total number of pieces on board
        """
        return (
            sum(1 for pos in self.board.values() if pos == color)
            + self.player_hands[color]
        )

    def _execute_move(self, source: str, target: str, remove: str) -> None:
        """Execute a validated move."""
        current_color = self._current_player.get_color()

        # Handle move from hand
        if source == "h":
            self.player_hands[current_color] -= 1
        else:
            self.board[source] = None

        # Place stone on target
        self.board[target] = current_color

        # Handle removal if specified
        if remove != "r0":
            self.board[remove] = None

    def _show_state(self, move: Optional[str] = None) -> None:
        """Show game state if visualization is enabled."""
        # Calculate number of lines to clear (1 for each row of the board + fixed lines)
        num_lines = 7  # board rows
        num_lines += 13  # fixed lines (move, turn, "Board:", coordinate row, blank lines, hands header, 2 hand states)

        # Move cursor up and clear lines
        if hasattr(self, "_previous_draw"):
            click.echo("\033[J")  # Clear from cursor to end of screen
            click.echo(f"\033[{num_lines}A")  # Move cursor up
        self._previous_draw = True

        if move:
            click.echo(f"\nMove: {move}")

        current_color = self._current_player.get_color()
        color_code = Fore.BLUE if current_color == "blue" else Fore.YELLOW
        click.echo(f"\n{color_code}{current_color}'s turn{Style.RESET_ALL}    ")

        # Show board
        click.echo("\nBoard:")
        for num in range(1, 8):
            row = ""
            for letter in "abcdefg":
                pos = f"{letter}{num}"
                if pos in self.invalid_fields:
                    row += "  "
                elif self.board.get(pos) is None:
                    row += ". "
                else:
                    color = Fore.BLUE if self.board[pos] == "blue" else Fore.YELLOW
                    row += f"{color}●{Style.RESET_ALL} "
            click.echo(f"{num} {row}")
        click.echo("  a b c d e f g")

        # Show hands
        click.echo("\nStones in hand:")
        click.echo(f"{Fore.BLUE}Blue: {self.player_hands['blue']}{Style.RESET_ALL} ")
        click.echo(
            f"{Fore.YELLOW}Orange: {self.player_hands['orange']}{Style.RESET_ALL} "
        )

    def determine_winner(self) -> Optional[LaskerPlayer]:
        """
        Check win conditions.
        Game ends if a player has fewer than 2 pieces total.
        """
        for player in [self._player1, self._player2]:
            color = player.get_color()
            total_pieces = self._count_player_pieces(color)
            if total_pieces < 3:
                self._is_game_over = True
                return self._player2 if player == self._player1 else self._player1
        return None

    def run_game(self) -> Optional[LaskerPlayer]:
        """Main game loop."""

        while not self.is_game_over:
            # Get current player's move
            move = self.current_player.read()

            # Validate and execute move
            if not self.make_move(move):
                self._is_game_over = True
                # End player processes
                self._player1.stop()
                self._player2.stop()
                return (
                    self._player2
                    if self.current_player == self._player1
                    else self._player1
                )

            # Write move to other player
            other_player = (
                self._player2 if self.current_player == self._player1 else self._player1
            )
            other_player.write(move)

            # Check for winner
            winner = self.determine_winner()
            if winner:
                return winner

            # Switch turns
            self.switch_player()

            time.sleep(2)  # Pauses for 2 seconds

        return None
