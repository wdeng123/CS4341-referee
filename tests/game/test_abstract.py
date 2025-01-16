from typing import Any, Optional, Tuple
from unittest.mock import Mock, patch

import pytest

from src.game.abstract.game import AbstractGame
from src.game.abstract.player import AbstractPlayer


class MockGame(AbstractGame):
    """Mock implementation of AbstractGame for testing"""

    def initialize_game(self) -> None:
        pass

    def make_move(self, move: Any) -> bool:
        return True

    def determine_winner(self) -> Optional[AbstractPlayer]:
        return None if not self._is_game_over else self._player1


class MockPlayer(AbstractPlayer):
    """Mock implementation of AbstractPlayer for testing"""

    def __init__(self, command: str = "python3 mock_player.py") -> None:
        super().__init__(command)


@pytest.fixture
def mock_players() -> Tuple[MockPlayer, MockPlayer]:
    """Fixture providing two mock players"""
    return MockPlayer(), MockPlayer()


@pytest.fixture
def game(mock_players: Tuple[MockPlayer, MockPlayer]) -> MockGame:
    """Fixture providing a mock game instance"""
    player1, player2 = mock_players
    return MockGame(player1, player2)


class TestAbstractPlayer:
    def test_player_initialization(self) -> None:
        """Test player initializes with correct command"""
        command = "python3 test_player.py"
        player = MockPlayer(command)
        assert player.command == command
        assert player.process is None

    @patch("subprocess.Popen")
    def test_player_start(self, mock_popen: Mock) -> None:
        """Test player process starts correctly"""
        player = MockPlayer()
        player.start()
        mock_popen.assert_called_once()
        assert player.process is not None

    @patch("subprocess.Popen")
    def test_player_write(self, mock_popen: Mock) -> None:
        """Test writing to player process"""
        mock_stdin = Mock()
        mock_popen.return_value.stdin = mock_stdin

        player = MockPlayer()
        player.start()
        player.write("test_data")

        mock_stdin.write.assert_called_once_with("test_data\n")
        mock_stdin.flush.assert_called_once()

    @patch("subprocess.Popen")
    def test_player_read(self, mock_popen: Mock) -> None:
        """Test reading from player process"""
        mock_stdout = Mock()
        mock_stdout.readline.return_value = "test_output\n"
        mock_popen.return_value.stdout = mock_stdout

        player = MockPlayer()
        player.start()
        output = player.read()

        assert output == "test_output"
        mock_stdout.readline.assert_called_once()

    @patch("subprocess.Popen")
    def test_player_stop(self, mock_popen: Mock) -> None:
        """Test player process termination"""
        player = MockPlayer()
        player.start()
        player.stop()

        mock_popen.return_value.terminate.assert_called_once()
        assert player.process is None

    @patch("subprocess.Popen")
    def test_player_cleanup(self, mock_popen: Mock) -> None:
        """Test player cleanup on deletion"""
        player = MockPlayer()
        player.start()
        del player
        mock_popen.return_value.terminate.assert_called_once()


class TestAbstractGame:
    def test_game_initialization(
        self, game: MockGame, mock_players: Tuple[MockPlayer, MockPlayer]
    ) -> None:
        """Test game initializes with correct players and state"""
        player1, player2 = mock_players
        assert game._player1 == player1
        assert game._player2 == player2
        assert game.current_player == player1
        assert not game.is_game_over

    def test_switch_player(
        self, game: MockGame, mock_players: Tuple[MockPlayer, MockPlayer]
    ) -> None:
        """Test player turn switching"""
        player1, player2 = mock_players
        assert game.current_player == player1

        game.switch_player()
        assert game.current_player == player2

        game.switch_player()
        assert game.current_player == player1

    def test_game_over_state(self, game: MockGame) -> None:
        """Test game over state management"""
        assert not game.is_game_over
        game._is_game_over = True
        assert game.is_game_over
        assert game.determine_winner() == game._player1

    def test_abstract_methods_implementation(self) -> None:
        """Test that abstract methods must be implemented"""

        class IncompleteGame(AbstractGame):
            pass

        with pytest.raises(TypeError):
            _ = IncompleteGame(MockPlayer(), MockPlayer())

    def test_make_move(self, game: MockGame) -> None:
        """Test move execution"""
        assert game.make_move("test_move") is True

    def test_game_lifecycle(self, game: MockGame) -> None:
        """Test complete game lifecycle"""
        game.initialize_game()
        assert not game.is_game_over
        assert game.current_player == game._player1

        game.make_move("move1")
        game.switch_player()
        assert game.current_player == game._player2

        game._is_game_over = True
        assert game.is_game_over
        assert game.determine_winner() == game._player1
