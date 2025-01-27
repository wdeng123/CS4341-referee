import unittest
from concurrent.futures import TimeoutError
from unittest.mock import Mock, patch

from src.game.implementation.tictactoe import TicTacToe


class TestTicTacToe(unittest.TestCase):
    @patch("subprocess.Popen")
    def setUp(self, mock_popen):
        """Set up test environment before each test"""
        # Mock subprocess.Popen
        mock_process = Mock()
        mock_process.stdout.readline.return_value = b"a1\n"
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process

        self.game = TicTacToe("player1", "player2", visual=False)

        # Mock the players after initialization
        self.game._player1 = Mock()
        self.game._player2 = Mock()
        self.game._player1.get_symbol.return_value = "X"
        self.game._player2.get_symbol.return_value = "O"
        self.game._player1.is_x.return_value = True
        self.game._player2.is_x.return_value = False
        self.game._current_player = self.game._player1

    # Basic Initialization Tests
    def test_initialization(self):
        """Test game initialization"""
        self.assertEqual(len(self.game.board), 9)  # 3x3 board
        self.assertEqual(self.game.current_player.get_symbol(), "X")
        self.assertTrue(all(value is None for value in self.game.board.values()))
        self.assertEqual(len(self.game.move_history), 0)

    def test_initial_board_positions(self):
        """Test that board positions are correctly initialized"""
        expected_positions = {"a1", "a2", "a3", "b1", "b2", "b3", "c1", "c2", "c3"}
        self.assertEqual(set(self.game.board.keys()), expected_positions)

    # Move Validation Tests
    def test_validate_move_format(self):
        """Test move format validation"""
        valid_moves = ["a1", "b2", "c3"]
        invalid_moves = [
            "",  # Empty move
            "a",  # Too short
            "a11",  # Too long
            "d1",  # Invalid column
            "a4",  # Invalid row
            "aa",  # Invalid format
            "11",  # No column
        ]

        for move in valid_moves:
            is_valid, error = self.game._validate_move_format(move)
            self.assertTrue(is_valid, f"Move {move} should be valid")
            self.assertIsNone(error)

        for move in invalid_moves:
            is_valid, error = self.game._validate_move_format(move)
            self.assertFalse(is_valid, f"Move {move} should be invalid")
            self.assertIsNotNone(error)

    def test_make_move(self):
        """Test making valid and invalid moves"""
        # Test valid move
        self.assertTrue(self.game.make_move("a1"))
        self.assertEqual(self.game.board["a1"], "X")
        self.assertEqual(len(self.game.move_history), 1)

        # Test occupied position
        self.assertFalse(self.game.make_move("a1"))

        # Test invalid position
        self.assertFalse(self.game.make_move("d4"))

    def test_invalid_moves(self):
        """Test various invalid move scenarios"""
        invalid_moves = [
            ("", "Empty move"),
            ("d1", "Invalid column"),
            ("a4", "Invalid row"),
            ("a", "Incomplete move"),
            ("11", "No column"),
            ("aa", "Invalid format"),
            ("a1 b2", "Extra components"),
        ]

        for move, desc in invalid_moves:
            self.assertFalse(
                self.game.make_move(move), f"Move should be invalid: {desc}"
            )

    # Win Condition Tests
    def test_horizontal_wins(self):
        """Test horizontal winning combinations"""
        horizontal_wins = [["a1", "a2", "a3"], ["b1", "b2", "b3"], ["c1", "c2", "c3"]]

        for win in horizontal_wins:
            self.game.board = {pos: None for pos in self.game.board}
            for pos in win:
                self.game.board[pos] = "X"
            winner = self.game.determine_winner()
            self.assertEqual(winner, self.game._player1)

    def test_vertical_wins(self):
        """Test vertical winning combinations"""
        vertical_wins = [["a1", "b1", "c1"], ["a2", "b2", "c2"], ["a3", "b3", "c3"]]

        for win in vertical_wins:
            self.game.board = {pos: None for pos in self.game.board}
            for pos in win:
                self.game.board[pos] = "X"
            winner = self.game.determine_winner()
            self.assertEqual(winner, self.game._player1)

    def test_diagonal_wins(self):
        """Test diagonal winning combinations"""
        diagonal_wins = [["a1", "b2", "c3"], ["a3", "b2", "c1"]]

        for win in diagonal_wins:
            self.game.board = {pos: None for pos in self.game.board}
            for pos in win:
                self.game.board[pos] = "O"
            winner = self.game.determine_winner()
            self.assertEqual(winner, self.game._player2)

    def test_draw_condition(self):
        """Test draw condition when board is full"""
        # Fill board without winning combination
        positions = [
            ("a1", "X"),
            ("a2", "O"),
            ("a3", "O"),
            ("b1", "O"),
            ("b2", "X"),
            ("b3", "X"),
            ("c1", "X"),
            ("c2", "O"),
            ("c3", "O"),
        ]
        for pos, symbol in positions:
            self.game.board[pos] = symbol

        winner = self.game.determine_winner()
        self.assertIsNone(winner)
        self.assertTrue(self.game.is_game_over)

    # Game Flow Tests
    def test_switch_player(self):
        """Test player switching mechanism"""
        initial_player = self.game.current_player
        self.game.switch_player()
        self.assertNotEqual(self.game.current_player, initial_player)
        self.game.switch_player()
        self.assertEqual(self.game.current_player, initial_player)

    def test_move_timeout(self):
        """Test handling of move timeouts"""
        self.game.current_player.read.side_effect = TimeoutError()
        move = self.game._get_move_with_timeout()
        self.assertIsNone(move)

    def test_game_state_tracking(self):
        """Test that game state is properly tracked"""
        moves = ["a1", "b1", "a2", "b2", "a3"]
        for move in moves:
            self.game.make_move(move)
            self.game.switch_player()

        self.assertEqual(len(self.game.move_history), 5)
        self.assertEqual(self.game.move_history, moves)
        self.game.determine_winner()
        self.assertTrue(self.game.is_game_over)  # X wins

    # Complex Game Scenarios
    def test_complete_game_scenario(self):
        """Test a complete game scenario"""
        moves = [
            ("a1", True),  # X plays
            ("b2", True),  # O plays
            ("a2", True),  # X plays
            ("b1", True),  # O plays
            ("a3", True),  # X wins
        ]

        for move, expected_valid in moves:
            self.assertEqual(
                self.game.make_move(move),
                expected_valid,
                f"Unexpected result for move {move}",
            )
            if expected_valid:
                self.game.switch_player()

        winner = self.game.determine_winner()
        self.assertEqual(winner, self.game._player1)
        self.assertTrue(self.game.is_game_over)

    def test_game_end_conditions(self):
        """Test various game end conditions"""
        # Test timeout
        self.game._is_game_over = False
        self.game.current_player.read.side_effect = TimeoutError()
        winner = self.game.run_game()
        self.assertEqual(winner, self.game._player2)
        self.assertTrue(self.game.is_game_over)

        # Test invalid move
        self.game._is_game_over = False
        self.game.current_player.read.return_value = "invalid"
        winner = self.game.run_game()
        self.assertEqual(winner, self.game._player2)
        self.assertTrue(self.game.is_game_over)

    def test_cleanup(self):
        """Test game cleanup"""
        self.game._cleanup_game()
        self.game._player1.stop.assert_called_once()
        self.game._player2.stop.assert_called_once()


if __name__ == "__main__":
    unittest.main()
