import click

from .commands import start_game, start_tictactoe


def create_cli() -> click.Group:
    """Create the main CLI group with all commands"""

    @click.group()
    @click.version_option("0.1.2")
    def cli():
        pass

    cli.add_command(start_game)
    cli.add_command(start_tictactoe)

    return cli
