"""
Abstract base class for managing external player processes in a game environment.
Handles subprocess lifecycle and provides basic I/O interface while allowing
subclasses to implement game-specific logic and communication formats.
Includes optional logging of read/write operations.
"""

import shlex
import subprocess
import sys
import threading
from abc import ABC
from collections import deque
from datetime import datetime
from time import sleep
from typing import IO, Deque, Optional


class AbstractPlayer(ABC):
    """
    Base player class that manages external process communication.

    Attributes:
        process: Subprocess instance for the player program
        command: Shell command to execute player program
        log: Whether to log the moves
        forward_output: Whether to forward subprocess output
    """

    def __init__(
        self,
        command: str,
        log: bool = False,
        forward_output: bool = False,
        stdout: Optional[IO[str]] = sys.stdout,
        stderr: Optional[IO[str]] = sys.stdin,
    ):
        """
        Initialize player with command to run their process.

        Args:
            command: Shell command (e.g. "python3 player.py")
            log: If True, log all read/write operations to log.txt
            forward_output: If True, forward subprocess output
            stdout: Output stream for stdout (defaults to None)
            stderr: Output stream for stderr (defaults to None)
        """
        self.process: Optional[subprocess.Popen] = None
        self.command = command
        self.log = log
        self.forward_output = forward_output
        self.stdout = stdout
        self.stderr = stderr
        self._stdout_thread: Optional[threading.Thread] = None
        self._stderr_thread: Optional[threading.Thread] = None
        self._output_queue: Deque[str] = deque()
        self._queue_lock = threading.Lock()
        self._stop_event = threading.Event()

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
        self._stop_event.clear()
        self.process = subprocess.Popen(
            shlex.split(self.command),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if self.process:
            # Always start stdout processing thread
            self._stdout_thread = threading.Thread(
                target=self._process_output,
                args=(self.process.stdout, self.stdout),
                daemon=True,
            )
            self._stdout_thread.start()

            # Start stderr thread if needed
            if self.stderr is not None:
                self._stderr_thread = threading.Thread(
                    target=self._process_output,
                    args=(self.process.stderr, self.stderr),
                    daemon=True,
                )
                self._stderr_thread.start()

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
        Read one line from the output queue.

        Returns:
            String read from the process output
        """
        # Try to get a line from the queue
        while True:
            with self._queue_lock:
                if self._output_queue:
                    data = self._output_queue.popleft().strip()
                    if self.log:
                        self._log_operation("READ", data)
                    return data

            # If queue is empty and process is dead, return empty string
            if not self.process or self.process.poll() is not None:
                return ""

            # Small sleep to prevent busy waiting
            sleep(0.001)

    def _process_output(self, pipe: IO[str], target: Optional[IO[str]]) -> None:
        """
        Process output from pipe, storing in queue and optionally forwarding.
        """
        try:
            while not self._stop_event.is_set():
                line = pipe.readline()
                if not line:
                    break

                # Store in queue for read() method
                with self._queue_lock:
                    self._output_queue.append(line)

                # Forward if requested
                if self.forward_output and target:
                    try:
                        target.write(line)
                        target.flush()
                        if self.log:
                            self._log_operation("FORWARD", line.strip())
                    except (ValueError, IOError):
                        break

        except (ValueError, IOError):
            pass

    def stop(self) -> None:
        """Terminate the player process safely and cleanup resources."""
        self._stop_event.set()

        if self.process:
            try:
                # First terminate the process
                self.process.terminate()

                # Then close pipes
                if self.process.stdin:
                    self.process.stdin.close()
                if self.process.stdout:
                    self.process.stdout.close()
                if self.process.stderr:
                    self.process.stderr.close()

                # Wait for processing threads to finish
                if self._stdout_thread:
                    self._stdout_thread.join(timeout=0.1)
                if self._stderr_thread:
                    self._stderr_thread.join(timeout=0.1)

                try:
                    self.process.wait(timeout=0.1)
                except subprocess.TimeoutExpired:
                    self.process.kill()

            except ProcessLookupError:
                pass
            finally:
                self.process = None
                self._stdout_thread = None
                self._stderr_thread = None
                self._output_queue.clear()

    def __del__(self):
        """Ensure process cleanup on deletion."""
        self.stop()
