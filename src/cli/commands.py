import click
from colorama import Fore, Style, init

from ..config import Config, LaskerConfig, TicTacToeConfig
from ..game import LaskerMorris, TicTacToe

# Initialize colorama for Windows compatibility
init()


@click.command(name="laskermorris")
@click.option(
    "--player1", "-p1", prompt="Enter Player 1 command", help="Command to run Player 1."
)
@click.option(
    "--player2", "-p2", prompt="Enter Player 2 command", help="Command to run Player 2."
)
@click.option(
    "--visual/--no-visual",
    "-v/-nv",
    default=LaskerConfig.DEFAULT_VIS,
    help="Enable/disable game visualization",
)
@click.option(
    "--random-assignment/--no-random-assignment",
    "-r/-nr",
    default=LaskerConfig.DEFAULT_RAND,
    help="Enable/disable random selection of first player",
)
@click.option(
    "--timeout",
    "-t",
    type=int,
    default=LaskerConfig.GAME_TIMEOUT,
    help="Timeout in seconds for each player's move",
)
@click.option(
    "--port",
    type=int,
    default=Config.DEFAULT_WEB_PORT,
    help="Port the webserver for visualization gets hosted on",
)
@click.option(
    "--log/--no-log",
    "-l/-nl",
    default=LaskerConfig.DEFAULT_LOG,
    help="Enable/disable logging all communication",
)
@click.option(
    "--debug/--no-debug",
    "-d/-nd",
    default=LaskerConfig.DEFAULT_DEBUG,
    help="Enable/disable debug output",
)
def start_game(
    player1: str,
    player2: str,
    visual: bool,
    random_assignment: bool,
    timeout: int,
    port: int,
    log: bool,
    debug: bool,
) -> None:
    """🎮 Start a new game of Lasker Morris!"""
    try:
        game = LaskerMorris(
            player1_command=player1,
            player2_command=player2,
            visual=visual,
            select_rand=random_assignment,
            timeout=timeout,
            debug=debug,
            logging=log,
            port=port,
            print_board=debug
        )
        winner = game.run_game()

        if winner:
            color_code = Fore.BLUE if winner.get_color() == "blue" else Fore.YELLOW
            click.echo(f"\n{color_code}Game over! Winner: {winner.get_color()}{Style.RESET_ALL}")
        else:
            click.echo(f"\n{Fore.GREEN}Game over! Draw!{Style.RESET_ALL}")

        # Keep webserver running if visualization is enabled
        if visual:
            click.echo(
                f"\n{Fore.YELLOW}Press <CTRL>+C to exit visualization{Style.RESET_ALL}"
            )
            try:
                while True:
                    pass
            except KeyboardInterrupt:
                pass

    except Exception as e:
        click.echo(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
        raise click.Abort()


@click.command(name="tictactoe")
@click.option(
    "--player", "-p", prompt="Enter Player command", help="Command to run Player."
)
@click.option(
    "--player2", "-p2", required=False, help="Command to run Player 2 (optional)."
)
@click.option(
    "--visual/--no-visual",
    "-v/-nv",
    default=TicTacToeConfig.DEFAULT_VIS,
    help="Enable/disable game visualization",
)
@click.option(
    "--random-assignment/--no-random-assignment",
    "-r/-nr",
    default=TicTacToeConfig.DEFAULT_RAND,
    help="Enable/disable random assignment of X/O symbols",
)
@click.option(
    "--timeout",
    "-t",
    type=int,
    default=TicTacToeConfig.GAME_TIMEOUT,
    help="Timeout in seconds for each player's move",
)
@click.option(
    "--log/--no-log",
    "-l/-nl",
    default=TicTacToeConfig.DEFAULT_LOG,
    help="Enable/disable logging all communication",
)
@click.option(
    "--debug/--no-debug",
    "-d/-nd",
    default=TicTacToeConfig.DEFAULT_DEBUG,
    help="Enable/disable debug output",
)
@click.option(
    "--port",
    type=int,
    default=Config.DEFAULT_WEB_PORT,
    help="Port the webserver for visualization gets hosted on",
)
def start_tictactoe(
    player: str,
    player2: str | None,
    visual: bool,
    random_assignment: bool,
    timeout: int,
    log: bool,
    debug: bool,
    port: int,
) -> None:
    """🎮 Start a new game of TicTacToe!

    Players take turns placing X's and O's on a 3x3 grid.
    First player to get three in a row (horizontally, vertically, or diagonally) wins!
    """
    try:
        # Check for optinal second player
        if not player2:
            player2 = player

        # Initialize game
        game = TicTacToe(
            player1_command=player,
            player2_command=player2,
            visual=visual,
            random_assignment=random_assignment,
            move_timeout=timeout,
            enable_logging=log,
            debug=debug,
            port=port,
        )

        # Run game and get winner
        winner = game.run_game()

        # Display game result
        if winner:
            color_code = Fore.BLUE if winner.get_symbol() == "X" else Fore.YELLOW
            click.echo(f"\n{color_code}Game over! Winner: Player {winner.get_symbol()}{Style.RESET_ALL}")
        else:
            click.echo(f"\n{Fore.GREEN}Game over! It's a draw!{Style.RESET_ALL}")

        # Keep webserver running if visualization is enabled
        if visual:
            click.echo(f"\n{Fore.YELLOW}Press <CTRL>+C to exit visualization{Style.RESET_ALL}")
            try:
                while True:
                    pass
            except KeyboardInterrupt:
                pass

    except Exception as e:
        click.echo(f"\n{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        raise click.Abort()
    finally:
        # Ensure proper cleanup
        if "game" in locals():
            game._cleanup_game()
