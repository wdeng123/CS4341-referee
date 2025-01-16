from pathlib import Path
from typing import Optional

import click
from colorama import Fore, Style, init

from ..game import LaskerMorris

# Initialize colorama for Windows compatibility
init()


@click.command(name="start")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to TOML configuration file",
)
@click.option(
    "--player1", "-p1", prompt="Enter Player 1 command", help="Command to run Player 1."
)
@click.option(
    "--player2", "-p2", prompt="Enter Player 2 command", help="Command to run Player 2."
)
@click.option(
    "--visual/--no-visual",
    "-v/-nv",
    default=True,
    help="Enable/disable game visualization",
)
def start_game(
    config: Optional[Path], player1: str, player2: str, visual: bool
) -> None:
    """🎮 Start a new game of Lasker Morris!"""
    try:
        game = LaskerMorris(player1, player2, visual)
        click.echo(f"\n{Fore.GREEN}Starting new game!{Style.RESET_ALL}")
        winner = game.run_game()

        if winner:
            color_code = Fore.BLUE if winner.get_color() == "blue" else Fore.YELLOW
            click.echo(
                f"\n{color_code}Game over! Winner: {winner.get_color()}{Style.RESET_ALL}"
            )
        else:
            click.echo(f"\n{Fore.GREEN}Game over! Draw!{Style.RESET_ALL}")

    except Exception as e:
        click.echo(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
        raise click.Abort()
