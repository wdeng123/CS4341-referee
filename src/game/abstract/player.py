"""
Abstract base class for managing external player processes in a game environment.
Handles subprocess lifecycle and provides basic I/O interface while allowing
subclasses to implement game-specific logic and communication formats.
"""

import shlex
import subprocess
from abc import ABC
from time import sleep
from typing import Optional


class AbstractPlayer(ABC):
    """
    Base player class that manages external process communication.

    Attributes:
        process: Subprocess instance for the player program
        command: Shell command to execute player program
    """

    def __init__(self, command: str):
        """
        Initialize player with command to run their process.

        Args:
            command: Shell command (e.g. "python3 player.py")
        """
        self.process: Optional[subprocess.Popen] = None
        self.command = command

    def start(self) -> None:
        """Start the player's subprocess with pipes for communication."""
        self.process = subprocess.Popen(
            shlex.split(self.command),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def write(self, data: str) -> None:
        """Write data to player's stdin with newline and flush."""
        if self.process and self.process.stdin:
            self.process.stdin.write(f"{data}\n")
            self.process.stdin.flush()

    def read(self) -> str:
        """Read one line from player's stdout."""
        if self.process and self.process.stdout:
            return self.process.stdout.readline().strip()
        return ""

    def stop(self) -> None:
        """Terminate the player process safely and cleanup resources."""
        sleep(0.25)
        if self.process:
            try:
                # First attempt graceful termination first closing the pipes and then the process
                if self.process.stdin:
                    self.process.stdin.close()
                if self.process.stdout:
                    self.process.stdout.close()
                if self.process.stderr:
                    self.process.stderr.close()

                self.process.terminate()

                # Wait for a short time for process to terminate
                try:
                    self.process.wait(timeout=1.0)
                except subprocess.TimeoutExpired:
                    # If process doesn't terminate gracefully, force kill it
                    self.process.kill()
                    self.process.wait(timeout=1.0)
            except ProcessLookupError:
                # Process already terminated
                pass
            finally:
                # Note we close the process
                self.process = None

    def __del__(self):
        """Ensure process cleanup on deletion."""
        self.stop()
