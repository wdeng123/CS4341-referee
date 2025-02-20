import random
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Dict, Optional, Set

import click
from colorama import Fore, Style

from ....config import Config, LaskerConfig
from ...abstract import AbstractGame
from .lasker_player import LaskerPlayer
from .web.lasker_web import LaskerMorrisWeb


class LaskerMorris(AbstractGame):
    """Implementation of Lasker Morris game. Manages game state including board, player hands, and move validation."""

    def __init__(
        self,
        player1_command: str,
        player2_command: str,
        visual: bool = LaskerConfig.DEFAULT_VIS,
        select_rand: bool = LaskerConfig.DEFAULT_RAND,
        timeout: int = LaskerConfig.GAME_TIMEOUT,
        debug: bool = LaskerConfig.DEFAULT_DEBUG,
        logging: bool = LaskerConfig.DEFAULT_LOG,
        port: int = Config.DEFAULT_WEB_PORT,
        print_board: bool = LaskerConfig.PRINT_BOARD
    ):
        """Initialize game with player commands and game settings.

        Args:
            player1_command: Shell command for first player
            player2_command: Shell command for second player
            visual: Enable visualization if True
            select_rand: Randomly assign colors if True
            timeout: Move timeout in seconds
            debug: Enable debug output if True
            logging: Enable logging if True
        """
        self.move_timeout = timeout + 0.5
        self.game_history = []
        self.board_states = []
        self.hand_states = []
        self.debug = debug
        self.port = port
        self.prin_board = print_board
        self.moves_without_taking = 0

        # Initialize players with randomly assigned colors
        colors = ["blue", "orange"]
        if select_rand:
            random.shuffle(colors)

        player1 = LaskerPlayer(player1_command, colors[0], logging, debug)
        player2 = LaskerPlayer(player2_command, colors[1], logging, debug)
        super().__init__(player1, player2)

        # Initialize game state
        self.board: Dict[str, Optional[str]] = {}
        self.player_hands: Dict[str, int] = {
            "blue": LaskerConfig.HAND_SIZE,
            "orange": LaskerConfig.HAND_SIZE,
        }

        # Define invalid board positions
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
        self.web = LaskerMorrisWeb(self)
        self.initialize_game()

    def initialize_game(self) -> None:
        """Initialize empty game board and start player processes."""
        # Initialize empty board positions
        for num in range(1, 8):
            for letter in "abcdefg":
                self.board[f"{letter}{num}"] = None

        # Start player processes and web server
        self._player1.start()
        self._player2.start()

        if self.visual:
            self.web.start_web_server(self.port)

        # Ensure blue player goes first
        self._current_player = (
            self._player1 if self._player1.is_blue() else self._player2
        )
        self._current_player.write("blue")
        other_player = (
            self._player2 if self._current_player == self._player1 else self._player1
        )
        other_player.write("orange")

    def make_move(self, move: str) -> bool:
        """Execute a player's move if valid.

        Args:
            move: String in format "A B C" where:
                A: Current stone location (or hand 'h')
                B: Target board location
                C: Remove opponent's stone location or 'r0'

        Returns:
            bool: True if move was valid and executed
        """
        try:
            parts = move.strip().split()
            if len(parts) != 3:
                return False

            source, target, remove = parts
            if not self._is_valid_move(source, target, remove):
                return False

            self._execute_move(source, target, remove)

            if self.prin_board:
                self._show_state(move)

            return True
        except Exception:
            return False

    def _has_valid_moves(self, player_color: str) -> bool:
        """Check if the given player has any valid moves available.

        Args:
            player_color: Color of the player to check ('blue' or 'orange')

        Returns:
            bool: True if the player has at least one valid move available
        """
        # If player has pieces in hand, they can always make a move
        if self.player_hands[player_color] > 0:
            # Check if there's at least one empty valid position
            for pos in self.board:
                if pos not in self.invalid_fields and self.board[pos] is None:
                    return True
            return False

        # Get all pieces of the player
        player_pieces = [pos for pos, color in self.board.items() if color == player_color]

        # Check if player has exactly 3 pieces (can move to any empty position)
        if len(player_pieces) == 3:
            for pos in self.board:
                if pos not in self.invalid_fields and self.board[pos] is None:
                    return True
        else:
            # Check if any piece can move to an adjacent empty position
            for piece_pos in player_pieces:
                neighbors = {
                    "a1": ["a4", "d1"],
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

                if piece_pos in neighbors:
                    for neighbor in neighbors[piece_pos]:
                        if self.board[neighbor] is None:
                            return True
        return False

    def _is_valid_move(self, source: str, target: str, remove: str) -> bool:
        """Validate move according to game rules.

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
            return False

        # Validate source position
        if source in ["h1", "h2"]:
            # Validate hand moves
            is_player1 = self._current_player.get_color() == "blue"
            correct_hand = "h1" if is_player1 else "h2"

            if source != correct_hand:
                click.echo(
                    f"\n{Fore.RED}Invalid move: Player tried to use opponent's hand ({source}){Style.RESET_ALL}"
                )
                return False

            if self.player_hands[self._current_player.get_color()] <= 0:
                click.echo(
                    f"\n{Fore.RED}Invalid move: {self._current_player.get_color()} player has no stones left in hand{Style.RESET_ALL}"
                )
                return False
        else:
            # Validate board moves
            if source in self.invalid_fields or source not in self.board:
                click.echo(
                    f"\n{Fore.RED}Invalid move: Source position {source} does not exist on the board{Style.RESET_ALL}"
                )
                return False

            if self.board[source] != self._current_player.get_color():
                click.echo(
                    f"\n{Fore.RED}"
                    f"Invalid move: {self._current_player.get_color()} player "
                    f"tried to move opponent's stone from {source}"
                    f"{Style.RESET_ALL}"
                )
                return False

            # Check adjacent moves rule (except when player has exactly 3 pieces)
            if self._count_player_pieces(self._current_player.get_color()) > 3:
                if not self._check_corret_step(source, target):
                    click.echo(
                        f"\n{Fore.RED}"
                        f"Invalid move: Cannot move from {source} to {target} - "
                        f"must move to adjacent position when you have more than 3 pieces"
                        f"{Style.RESET_ALL}"
                    )
                    return False

        # Validate remove position
        if remove != "r0":
            self.moves_without_taking = 0
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

            if self.board[remove] == self._current_player.get_color():
                click.echo(
                    f"\n{Fore.RED}"
                    f"Invalid move: {self._current_player.get_color()} player "
                    f"tried to remove their own stone at {remove}"
                    f"{Style.RESET_ALL}"
                )
                return False

            if not self._is_mill(source, target):
                click.echo(
                    f"\n{Fore.RED}Invalid move: Cannot remove opponent's stone - move does not form a mill{Style.RESET_ALL}"
                )
                return False
        elif self._is_mill(source, target):
            click.echo(
                f"\n{Fore.RED}Invalid move: Must remove an opponent's stone after forming a mill{Style.RESET_ALL}"
            )
            return False
        else:
            # Track every move without taking a piece
            self.moves_without_taking += 1

        return True

    def _is_mill(self, source: str, target: str) -> bool:
        """Check if placing a stone at target position forms a mill.

        Args:
            source: Starting position of the stone (or 'h' if from hand)
            target: Target position where stone is placed

        Returns:
            bool: True if move forms a mill
        """
        color = self._current_player.get_color()

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

        for mill in mills:
            if target in mill:
                stones_in_mill = 0
                for pos in mill:
                    if pos == target:
                        stones_in_mill += 1
                    elif pos != source and self.board[pos] == color:
                        stones_in_mill += 1

                if stones_in_mill == 3:
                    return True

        return False

    def _check_corret_step(self, source: str, target: str) -> bool:
        """Check if a move from source to target is to a neighboring position.

        Args:
            source: Starting position of the stone
            target: Target position where stone will move

        Returns:
            bool: True if target is a neighbor of source
        """
        neighbors = {
            "a1": ["a4", "d1"],
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

        return (
            source in neighbors and target in neighbors and target in neighbors[source]
        )

    def _count_player_pieces(self, color: str) -> int:
        """Count total number of pieces a player has on the board.

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
        """Execute a validated move and update game state."""
        current_color = self._current_player.get_color()

        # Update board state
        if source in ["h1", "h2"]:
            self.player_hands[current_color] -= 1
        else:
            self.board[source] = None

        self.board[target] = current_color

        if remove != "r0":
            self.board[remove] = None

        # Record move history
        move_data = {
            "move": f"{source} {target} {remove}",
            "player": current_color,
            "board": self.board.copy(),
            "hands": self.player_hands.copy(),
        }
        self.game_history.append(move_data)
        self.board_states.append(self.board.copy())
        self.hand_states.append(self.player_hands.copy())

    def _is_oscillating_moves(self) -> bool:
        """Check if players are making repetitive moves with no strategic progress."""
        if len(self.game_history) < 6:
            return False

        blue_moves = []
        orange_moves = []

        for move_data in self.game_history[-8:]:
            source, target, remove = move_data["move"].split()
            if source not in ["h1", "h2"]:
                if move_data["player"] == "blue":
                    blue_moves.append((source, target, remove))
                else:
                    orange_moves.append((source, target, remove))

        def check_oscillation(moves):
            if len(moves) < 4:
                return False

            for i in range(len(moves) - 3):
                move1, move2, move3, move4 = moves[i: i + 4]

                basic_pattern = (
                    move1[0] == move2[1]
                    and move1[1] == move2[0]
                    and move3[0] == move4[1]
                    and move3[1] == move4[0]
                )

                repeating_pattern = (
                    move1[0] == move3[0]
                    and move1[1] == move3[1]
                    and move2[0] == move4[0]
                    and move2[1] == move4[1]
                )

                no_captures = all(
                    move[2] == "r0" for move in [move1, move2, move3, move4]
                )

                if basic_pattern and repeating_pattern and no_captures:
                    return True

            return False

        return check_oscillation(blue_moves) and check_oscillation(orange_moves)

    def _show_state(self, move: Optional[str] = None) -> None:
        """Display current game state if visualization is enabled."""

        click.echo("-------------------------------------------------")
        if move:
            click.echo(f"Move: {move}")

        current_color = self._current_player.get_color()
        color_code = Fore.BLUE if current_color == "blue" else Fore.YELLOW
        click.echo(f"{color_code}{current_color}'s turn{Style.RESET_ALL}")

        # Display board
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

        # Display stones in hand
        click.echo("\nStones in hand:")
        click.echo(f"{Fore.BLUE}Blue: {self.player_hands['blue']}{Style.RESET_ALL}")
        click.echo(
            f"{Fore.YELLOW}Orange: {self.player_hands['orange']}{Style.RESET_ALL}"
        )
        click.echo("-------------------------------------------------")

    def determine_winner(self) -> Optional[LaskerPlayer]:
        """Check win conditions and return winner if game is over."""
        # Check for draw condition
        if self.moves_without_taking >= 20:
            self._is_game_over = True
            message = "Draw!"
            click.echo(message)
            if self.visual:
                self.web.end_message = message
            self._player1.write(message)
            self._player2.write(message)
            self._player1.stop()
            self._player2.stop()
            return None

        # Check if any player has fewer than 3 pieces
        for player in [self._player1, self._player2]:
            color = player.get_color()
            if self._count_player_pieces(color) < 3:
                self._is_game_over = True
                return self._player1 if player == self._player2 else self._player2

        return None

    def _get_move_with_timeout(self) -> Optional[str]:
        """Get a move from the current player with timeout.

        Returns:
            str: The move if received within timeout, None if timeout occurred
        """
        with ThreadPoolExecutor(max_workers=1) as executor:
            try:
                future = executor.submit(self._current_player.read)
                return future.result(timeout=self.move_timeout)
            except TimeoutError:
                winner_color = (
                    self._player2.get_color()
                    if self._current_player == self._player1
                    else self._player1.get_color()
                )
                loser_color = self._current_player.get_color()
                message = f"END: {winner_color} WINS! {loser_color} LOSES! Time out!"
                if self.visual:
                    self.web.end_message = message
                self._player1.write(message)
                self._player2.write(message)
                click.echo(
                    f"\n{Fore.RED}Move timeout: Player {self._current_player.get_color()} took too long to respond{Style.RESET_ALL}"
                )

                return None

    def run_game(self) -> Optional[LaskerPlayer]:
        """Main game loop."""
        while not self.is_game_over:

            # Check for immoblilzation
            if not self._has_valid_moves(self._current_player.get_color()):
                self._is_game_over = True
                winner = self._player2 if self._current_player == self._player1 else self._player1
                winner_color = winner.get_color()
                loser_color = self._current_player.get_color()
                message = f"END: {winner_color} WINS! {loser_color} LOSES! No valid moves available!"
                if self.visual:
                    self.web.end_message = message
                self._player1.write(message)
                self._player2.write(message)
                self._player1.stop()
                self._player2.stop()
                return winner

            # Get and validate current player's move
            move = self._get_move_with_timeout()
            if not move or not self.make_move(move):
                self._is_game_over = True
                winner_color = (
                    self._player2.get_color()
                    if self._current_player == self._player1
                    else self._player1.get_color()
                )
                loser_color = self._current_player.get_color()
                message = f"END: {winner_color} WINS! {loser_color} LOSES! Invalid move {move}!"
                if self.visual:
                    self.web.end_message = message
                self._player1.write(message)
                self._player2.write(message)
                self._player1.stop()
                self._player2.stop()

                return (
                    self._player2
                    if self._current_player == self._player1
                    else self._player1
                )

            # Send move to other player
            other_player = (
                self._player2
                if self._current_player == self._player1
                else self._player1
            )
            other_player.write(move)

            # Check for winner
            winner = self.determine_winner()
            if winner:
                winner_color = (
                    self._player2.get_color()
                    if self._current_player == self._player2
                    else self._player1.get_color()
                )
                loser_color = (
                    self._player2.get_color()
                    if self._current_player == self._player1
                    else self._player1.get_color()
                )
                message = (
                    f"END: {winner_color} WINS! {loser_color} LOSES! Ran out of pieces!"
                )
                if self.visual:
                    self.web.end_message = message
                self._player1.write(message)
                self._player2.write(message)
                self._player1.stop()
                self._player2.stop()

                return winner

            self.switch_player()

        return None
