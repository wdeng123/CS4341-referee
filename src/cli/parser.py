import click
from colorama import Fore, Style

from .commands import start_game


def create_cli() -> click.Group:
    """Create the main CLI group with all commands"""

    @click.group()
    def cli():
        click.echo(
            f"{Fore.GREEN}🎮 Welcome to the CS4341-C01 Lasker Morris Referee! 🎲{Style.RESET_ALL}"
        )
        pass

    cli.add_command(start_game)

    return cli
