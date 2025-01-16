import unittest
from unittest.mock import Mock, patch

from src.game.implementation.lasker_morris import LaskerMorris


class TestLaskerMorris(unittest.TestCase):
    @patch("subprocess.Popen")
    def setUp(self, mock_popen) -> None:
        """Set up test environment before each test"""
        # Mock subprocess.Popen
        mock_process = Mock()
        mock_process.stdout.readline.return_value = b"some move\n"
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process

        with patch("random.shuffle") as mock_shuffle:
            # Ensure consistent color assignment for tests
            mock_shuffle.side_effect = lambda x: x
            self.game = LaskerMorris("player1", "player2", visual=False)

        # Mock the players after initialization
        self.game._player1 = Mock()
        self.game._player2 = Mock()
        self.game._player1.color = "blue"
        self.game._player2.color = "orange"
        self.game._player1.is_blue.return_value = True
        self.game._player2.is_blue.return_value = False
        self.game._player1.get_color.return_value = "blue"
        self.game._player2.get_color.return_value = "orange"
        self.game._current_player = self.game._player1

    def test_initialization(self) -> None:
        """Test game initialization"""
        self.assertEqual(self.game.player_hands["blue"], 10)
        self.assertEqual(self.game.player_hands["orange"], 10)
        self.assertEqual(len(self.game.board), 49)  # 7x7 board
        self.assertEqual(len(self.game.invalid_fields), 25)
        self.assertEqual(self.game.current_player.color, "blue")

    @patch("subprocess.Popen")
    def test_make_move_from_hand(self, mock_popen) -> None:
        """Test placing a piece from hand"""
        # Valid move from hand
        self.assertTrue(self.game.make_move("h d1 r0"))
        self.assertEqual(self.game.board["d1"], "blue")
        self.assertEqual(self.game.player_hands["blue"], 9)

    def test_make_move_invalid_format(self) -> None:
        """Test moves with invalid format"""
        self.assertFalse(self.game.make_move("d1"))  # Too few parts
        self.assertFalse(self.game.make_move("d1 d2 r0 extra"))  # Too many parts

    def test_invalid_target_position(self) -> None:
        """Test moves to invalid target positions"""
        self.assertFalse(self.game.make_move("h a2 r0"))  # Invalid field
        self.assertFalse(self.game.make_move("h x1 r0"))  # Non-existent position

    def test_moving_piece_on_board(self) -> None:
        """Test moving a piece already on the board"""
        # Place a piece first
        self.game.make_move("h d1 r0")
        # Move it
        self.assertTrue(self.game.make_move("d1 d2 r0"))
        self.assertIsNone(self.game.board["d1"])
        self.assertEqual(self.game.board["d2"], "blue")

    def test_mill_formation_and_capture(self) -> None:
        """Test forming a mill and capturing opponent's piece"""
        # Setup: Place pieces to form a mill
        self.game.board["d1"] = "blue"
        self.game.board["d2"] = "blue"
        self.game.board["a4"] = "orange"  # Opponent's piece to capture

        # Complete the mill and capture
        self.assertTrue(self.game.make_move("h d3 a4"))
        self.assertIsNone(self.game.board["a4"])  # Captured piece should be removed

    def test_invalid_capture_without_mill(self) -> None:
        """Test attempting to capture without forming a mill"""
        self.game.board["a4"] = "orange"
        self.assertFalse(self.game.make_move("h d1 a4"))  # No mill formed

    def test_flying_rule(self) -> None:
        """Test the flying rule (when player has exactly 3 pieces)"""
        # Setup: Place exactly 3 pieces for blue player
        self.game.board["d1"] = "blue"
        self.game.board["d2"] = "blue"
        self.game.board["d3"] = "blue"
        self.game.player_hands["blue"] = 0

        # Should be able to "fly" to any empty position
        self.assertTrue(self.game.make_move("d1 g7 r0"))

    def test_adjacent_move_requirement(self) -> None:
        """Test requirement to move to adjacent positions when having more than 3 pieces"""
        # Setup: Place 4 pieces
        self.game.board["d1"] = "blue"
        self.game.board["d2"] = "blue"
        self.game.board["d3"] = "blue"
        self.game.board["d5"] = "blue"
        self.game.player_hands["blue"] = 0

        # Try to move to non-adjacent position
        self.assertFalse(self.game.make_move("d1 g7 r0"))
        # Try to move to adjacent position
        self.assertFalse(self.game.make_move("d1 d2 r0"))

        winner = self.game.run_game()
        self.assertEqual(
            winner, self.game._player2
        )  # Orange should win due to invalid move

    def test_switch_player(self) -> None:
        """Test player switching"""
        initial_player = self.game.current_player
        self.game.switch_player()
        self.assertNotEqual(self.game.current_player, initial_player)

    def test_occupied_target_position(self) -> None:
        """Test moving to an occupied position"""
        self.game.board["d1"] = "orange"
        self.assertFalse(self.game.make_move("h d1 r0"))

    def test_empty_hand(self) -> None:
        """Test attempting to place from empty hand"""
        self.game.player_hands["blue"] = 0
        self.assertFalse(self.game.make_move("h d1 r0"))

    def test_remove_own_piece(self) -> None:
        """Test attempting to remove own piece after mill"""
        self.game.board["d1"] = "blue"
        self.game.board["d2"] = "blue"
        self.game.board["d4"] = "blue"
        self.assertFalse(self.game.make_move("h d3 d4"))

    @patch("click.echo")
    @patch("subprocess.Popen")
    def test_visual_display(self, mock_popen, mock_echo) -> None:
        """Test the visual display functionality"""
        game = LaskerMorris("player1", "player2", visual=True)
        game._show_state("h d1 r0")
        mock_echo.assert_called()

    @patch("time.sleep")  # Mock sleep to speed up test
    def test_run_game_invalid_move(self, mock_sleep) -> None:
        """Test game termination on invalid move"""
        self.game.current_player.read.return_value = "invalid move"
        winner = self.game.run_game()
        self.assertEqual(winner, self.game._player2)  # Other player should win


if __name__ == "__main__":
    unittest.main()
