from enum import Enum

from ...abstract import AbstractPlayer


class PlayerColor(Enum):
    """Enum for valid player colors."""

    BLUE = "blue"
    ORANGE = "orange"


class LaskerPlayer(AbstractPlayer):
    """
    Player class that extends AbstractPlayer to track player color.

    Attributes:
        color: PlayerColor enum representing the player's color (blue or orange)
        process: Subprocess instance for the player program
        command: Shell command to execute player program
    """

    def __init__(
        self, command: str, color: str, log: bool = False, debug: bool = False
    ):
        """
        Initialize player with command and color.

        Args:
            command: Shell command (e.g. "python3 player.py")
            color: Player color, must be either "blue" or "orange"

        Raises:
            ValueError: If color is not "blue" or "orange"
        """
        super().__init__(command, log, debug)

        # Validate and set the color
        try:
            self.color = PlayerColor(color.lower())
        except ValueError:
            raise ValueError(
                f"Invalid color: {color}. Must be either 'blue' or 'orange'"
            )

    def get_color(self) -> str:
        """Return the player's color as a string."""
        return self.color.value

    def is_blue(self) -> bool:
        """Check if player is blue."""
        return self.color == PlayerColor.BLUE

    def is_orange(self) -> bool:
        """Check if player is orange."""
        return self.color == PlayerColor.ORANGE
