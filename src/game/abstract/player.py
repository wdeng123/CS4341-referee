"""
Abstract base class for managing external player processes in a game environment.
Handles subprocess lifecycle and provides basic I/O interface while allowing
subclasses to implement game-specific logic and communication formats.
Includes optional logging of read/write operations.
"""

import shlex
import subprocess
from abc import ABC
from datetime import datetime
from time import sleep
from typing import Optional


class AbstractPlayer(ABC):
    """
    Base player class that manages external process communication.

    Attributes:
        process: Subprocess instance for the player program
        command: Shell command to execute player program
        log: Whether to log the moves
    """

    def __init__(self, command: str, log: bool = False, debug: bool = True):
        """
        Initialize player with command to run their process.

        Args:
            command: Shell command (e.g. "python3 player.py")
            log_reads: If True, log all read operations to log.txt
            log_writes: If True, log all write operations to log.txt
        """
        self.process: Optional[subprocess.Popen] = None
        self.command = command
        self.log = log

    def _log_operation(self, operation: str, data: str) -> None:
        """
        Log an operation to the log file.

        Args:
            operation: Type of operation ('READ' or 'WRITE')
            data: Data being read or written
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        log_entry = f"[{timestamp}] {operation}: {data}\n"
        try:
            with open("log.txt", "a") as log_file:
                log_file.write(log_entry)
        except IOError as e:
            print(f"Warning: Failed to write to log file: {e}")

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
        """
        Write data to player's stdin with newline and flush.

        Args:
            data: String to write to the process
        """
        if self.process and self.process.stdin:
            self.process.stdin.write(f"{data}\n")
            self.process.stdin.flush()
            if self.log:
                self._log_operation("WRITE", data)

    def read(self) -> str:
        """
        Read one line from player's stdout.

        Returns:
            String read from the process output
        """
        if self.process and self.process.stdout:
            data = self.process.stdout.readline().strip()
            if self.log:
                self._log_operation("READ", data)
            return data
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
