from enum import Enum

from ...abstract import AbstractPlayer


class PlayerSymbol(Enum):
    """Enum for valid player symbols."""

    X = "BLUE"
    O = "ORANGE"


class TicTacToePlayer(AbstractPlayer):
    """
    Player class that extends AbstractPlayer to track player symbol.

    Attributes:
        symbol: PlayerSymbol enum representing the player's symbol (X or O)
        process: Subprocess instance for the player program
        command: Shell command to execute player program
    """

    def __init__(self, command: str, symbol: str, log: bool = False):
        """
        Initialize player with command and symbol.

        Args:
            command: Shell command (e.g. "python3 player.py")
            symbol: Player symbol, must be either "X" or "O"

        Raises:
            ValueError: If symbol is not "X" or "O"
        """
        super().__init__(command, log)

        # Validate and set the symbol
        try:
            self.symbol = PlayerSymbol(symbol.upper())
        except ValueError:
            raise ValueError(
                f"Invalid symbol: {symbol}. Must be either 'blue' or 'orange'"
            )

    def get_symbol(self) -> str:
        """Return the player's symbol as a string."""
        return self.symbol.value

    def is_x(self) -> bool:
        """Check if player is X."""
        return self.symbol == PlayerSymbol.X

    def is_o(self) -> bool:
        """Check if player is O."""
        return self.symbol == PlayerSymbol.O
