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

    # Basic Initialization Tests
    def test_initialization(self) -> None:
        """Test game initialization"""
        self.assertEqual(self.game.player_hands["blue"], 10)
        self.assertEqual(self.game.player_hands["orange"], 10)
        self.assertEqual(len(self.game.board), 49)  # 7x7 board
        self.assertEqual(len(self.game.invalid_fields), 25)
        self.assertEqual(self.game.current_player.color, "blue")

    # Game State Tracking Tests
    def test_game_state_tracking(self) -> None:
        """Test that game history and state tracking works correctly"""
        # Make several moves and verify history
        self.game.make_move("h1 d1 r0")
        self.game.make_move("h2 d2 r0")
        self.game.make_move("h1 d3 r0")

        self.assertEqual(len(self.game.game_history), 2)
        self.assertEqual(len(self.game.board_states), 2)
        self.assertEqual(len(self.game.hand_states), 2)

        # Verify last state
        last_state = self.game.game_history[-1]
        self.assertEqual(last_state["move"], "h1 d3 r0")
        self.assertEqual(last_state["player"], "blue")

    # Move Validation Tests
    def test_make_move_from_hand(self) -> None:
        """Test placing a piece from hand"""
        self.assertTrue(self.game.make_move("h1 d1 r0"))
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

    def test_invalid_move_variants(self) -> None:
        """Test various invalid move scenarios"""
        invalid_moves = [
            ("h3 d1 r0", "Invalid hand"),
            ("h1 x9 r0", "Invalid target"),
            ("h1 d1 x9", "Invalid remove"),
            ("d1 d1 r0", "Same source and target"),
            ("h1 d1 d1", "Remove from target position"),
            ("", "Empty move"),
            ("h1 d1", "Incomplete move"),
            ("h1 d1 r0 extra", "Extra components"),
        ]

        for move, desc in invalid_moves:
            self.assertFalse(
                self.game.make_move(move), f"Move should be invalid: {desc}"
            )

    def test_occupied_target_position(self) -> None:
        """Test moving to an occupied position"""
        self.game.board["d1"] = "orange"
        self.assertFalse(self.game.make_move("h d1 r0"))

    def test_empty_hand(self) -> None:
        """Test attempting to place from empty hand"""
        self.game.player_hands["blue"] = 0
        self.assertFalse(self.game.make_move("h d1 r0"))

    # Mill and Capture Tests
    def test_mill_formation_and_capture(self) -> None:
        """Test forming a mill and capturing opponent's piece"""
        # Setup: Place pieces to form a mill
        self.game.board["d1"] = "blue"
        self.game.board["d2"] = "blue"
        self.game.board["a4"] = "orange"  # Opponent's piece to capture

        # Complete the mill and capture
        self.assertTrue(self.game.make_move("h1 d3 a4"))
        self.assertIsNone(self.game.board["a4"])  # Captured piece should be removed

    def test_invalid_capture_without_mill(self) -> None:
        """Test attempting to capture without forming a mill"""
        self.game.board["a4"] = "orange"
        self.assertFalse(self.game.make_move("h d1 a4"))  # No mill formed

    def test_remove_own_piece(self) -> None:
        """Test attempting to remove own piece after mill"""
        self.game.board["d1"] = "blue"
        self.game.board["d2"] = "blue"
        self.game.board["d4"] = "blue"
        self.assertFalse(self.game.make_move("h d3 d4"))

    def test_mill_combinations(self) -> None:
        """Test all possible mill combinations"""
        # Test horizontal mills
        horizontal_mills = [
            ["a1", "a4", "a7"],
            ["b2", "b4", "b6"],
            ["c3", "c4", "c5"],
            ["d1", "d2", "d3"],
            ["d5", "d6", "d7"],
            ["e3", "e4", "e5"],
            ["f2", "f4", "f6"],
            ["g1", "g4", "g7"],
        ]

        for mill in horizontal_mills:
            self.game.board = {pos: None for pos in self.game.board}  # Reset board
            # Set up first two positions
            self.game.board[mill[0]] = "blue"
            self.game.board[mill[1]] = "blue"
            # Verify mill formation with third position
            self.assertTrue(self.game._is_mill("h1", mill[2]))

        # Test vertical mills
        vertical_mills = [
            ["a1", "d1", "g1"],
            ["b2", "d2", "f2"],
            ["c3", "d3", "e3"],
            ["a4", "b4", "c4"],
            ["e4", "f4", "g4"],
            ["c5", "d5", "e5"],
            ["b6", "d6", "f6"],
            ["a7", "d7", "g7"],
        ]

        for mill in vertical_mills:
            self.game.board = {pos: None for pos in self.game.board}
            self.game.board[mill[0]] = "blue"
            self.game.board[mill[1]] = "blue"
            self.assertTrue(self.game._is_mill("h1", mill[2]))

    # Movement Rule Tests
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

    # Game Flow Tests
    def test_switch_player(self) -> None:
        """Test player switching"""
        initial_player = self.game.current_player
        self.game.switch_player()
        self.assertNotEqual(self.game.current_player, initial_player)

    def test_timeout_handling(self) -> None:
        """Test handling of move timeouts"""
        # Simply raise TimeoutError immediately
        self.game.current_player.read.side_effect = TimeoutError

        # No real timing involved
        move = self.game._get_move_with_timeout()
        self.assertIsNone(move)

        # Verify timeout messages were sent
        self.game._player1.write.assert_called_once()
        self.game._player2.write.assert_called_once()

    def test_oscillation_detection(self) -> None:
        """Test detection of oscillating moves"""
        # Simulate oscillating moves
        moves = [
            {"move": "d1 d2 r0", "player": "blue", "board": {}, "hands": {}},
            {"move": "e1 e2 r0", "player": "orange", "board": {}, "hands": {}},
            {"move": "d2 d1 r0", "player": "blue", "board": {}, "hands": {}},
            {"move": "e2 e1 r0", "player": "orange", "board": {}, "hands": {}},
            {"move": "d1 d2 r0", "player": "blue", "board": {}, "hands": {}},
            {"move": "e1 e2 r0", "player": "orange", "board": {}, "hands": {}},
            {"move": "d2 d1 r0", "player": "blue", "board": {}, "hands": {}},
            {"move": "e2 e1 r0", "player": "orange", "board": {}, "hands": {}},
        ]

        self.game.game_history = moves
        self.assertTrue(self.game._is_oscillating_moves())

        # Test non-oscillating moves
        moves = [
            {"move": "d1 d2 r0", "player": "blue", "board": {}, "hands": {}},
            {"move": "e1 e2 r0", "player": "orange", "board": {}, "hands": {}},
            {"move": "d2 d3 r0", "player": "blue", "board": {}, "hands": {}},
            {"move": "e2 e3 r0", "player": "orange", "board": {}, "hands": {}},
        ]

        self.game.game_history = moves
        self.assertFalse(self.game._is_oscillating_moves())

    # Game End Tests
    def test_win_conditions(self) -> None:
        """Test various win conditions"""
        # Test win by reducing opponent pieces
        self.game.board = {pos: None for pos in self.game.board}
        self.game.board["d1"] = "orange"
        self.game.board["d2"] = "orange"
        self.game.player_hands["orange"] = 0

        winner = self.game.determine_winner()
        self.assertEqual(winner, self.game._player1)

        # Test draw by oscillation
        moves = [{"move": "d1 d2 r0", "player": "blue", "board": {}, "hands": {}}] * 8
        self.game.game_history = moves
        self.game._is_oscillating_moves = Mock(return_value=True)

        winner = self.game.determine_winner()
        self.assertIsNone(winner)
        self.assertTrue(self.game._is_game_over)

    def test_game_state_persistence(self) -> None:
        """Test that game state is properly maintained across moves"""
        # Initial state verification
        self.assertEqual(self.game.player_hands["blue"], 10)
        self.assertEqual(self.game.player_hands["orange"], 10)

        # Make series of moves
        moves = [("h1 d1 r0", "blue"), ("h2 d2 r0", "orange"), ("h1 d3 r0", "blue")]

        for move, color in moves:
            self.game.make_move(move)
            self.game.switch_player()

        # Verify final state
        self.assertEqual(self.game.player_hands["blue"], 8)
        self.assertEqual(self.game.player_hands["orange"], 9)
        self.assertEqual(self.game.board["d1"], "blue")
        self.assertEqual(self.game.board["d2"], "orange")
        self.assertEqual(self.game.board["d3"], "blue")

    @patch("click.echo")
    def test_visual_display(self, mock_echo) -> None:
        """Test the visual display functionality"""
        self.game._show_state("h1 d1 r0")
        mock_echo.assert_called()

        # Test display with different board states
        self.game.board["d1"] = "blue"
        self.game.board["d2"] = "orange"
        self.game._show_state("d1 d3 r0")
        mock_echo.assert_called()

        # Test display with empty board
        self.game.board = {pos: None for pos in self.game.board}
        self.game._show_state()
        mock_echo.assert_called()

    def test_piece_counting(self) -> None:
        """Test accurate counting of player pieces in various scenarios"""
        # Test initial count
        self.assertEqual(self.game._count_player_pieces("blue"), 10)
        self.assertEqual(self.game._count_player_pieces("orange"), 10)

        # Test after placing pieces
        self.game.board["d1"] = "blue"
        self.game.board["d2"] = "blue"
        self.game.player_hands["blue"] = 8
        self.assertEqual(self.game._count_player_pieces("blue"), 10)

        # Test when pieces are captured
        self.game.board["d2"] = None
        self.assertEqual(self.game._count_player_pieces("blue"), 9)

        # Test at minimum playable pieces
        self.game.board = {pos: None for pos in self.game.board}
        self.game.board["d1"] = "blue"
        self.game.board["d2"] = "blue"
        self.game.board["d3"] = "blue"
        self.game.player_hands["blue"] = 0
        self.assertEqual(self.game._count_player_pieces("blue"), 3)

    def test_complex_game_scenarios(self) -> None:
        """Test complex game scenarios involving multiple moves and captures"""
        # Setup a complex board state
        self.game.board["d1"] = "blue"
        self.game.board["d2"] = "blue"
        self.game.board["e3"] = "orange"
        self.game.board["e4"] = "orange"
        self.game.board["e5"] = "orange"
        self.game.player_hands["blue"] = 8
        self.game.player_hands["orange"] = 7

        # Test mill formation with capture
        self.assertTrue(self.game.make_move("h1 d3 e3"))
        self.assertIsNone(self.game.board["e3"])  # Verify capture

        # Test opponent's response forming another mill
        self.game.switch_player()
        self.assertTrue(self.game.make_move("h2 e3 d3"))
        self.assertIsNone(self.game.board["d3"])  # Verify capture

        # Test moving out of and back into mill position
        self.game.switch_player()
        self.assertTrue(self.game.make_move("d1 a1 r0"))
        self.game.switch_player()
        self.assertTrue(self.game.make_move("e3 d3 r0"))

    def test_edge_case_scenarios(self) -> None:
        """Test edge cases and boundary conditions"""
        # Test moving the last piece when at exactly 3 pieces
        self.game.board = {pos: None for pos in self.game.board}
        self.game.board["d1"] = "blue"
        self.game.board["d2"] = "blue"
        self.game.board["d3"] = "blue"
        self.game.player_hands["blue"] = 0
        self.game.player_hands["orange"] = 0

        # Should allow flying with exactly 3 pieces
        self.assertTrue(self.game.make_move("d1 g7 r0"))

        # Test attempting to move with 2 pieces (should trigger game end)
        self.game.board["d2"] = None
        winner = self.game.determine_winner()
        self.assertEqual(winner, self.game._player2)

        # Test maximum possible mills in one position
        self.game.board = {pos: None for pos in self.game.board}
        self.game.board["d1"] = "blue"
        self.game.board["d2"] = "blue"
        self.game.board["g1"] = "blue"
        self.game.board["a1"] = "blue"
        self.game.board["a4"] = "orange"
        # Moving to d3 should form two mills simultaneously
        self.game.player_hands["blue"] = 1
        self.assertTrue(self.game.make_move("h1 d3 a4"))

    def test_move_validation_edge_cases(self) -> None:
        """Test edge cases in move validation"""
        # Test moves with various invalid formats
        invalid_moves = [
            "h1 d1",  # Missing remove part
            "h1",  # Missing target and remove
            "h1 d1 r0 extra",  # Extra components
            "H1 D1 R0",  # Upper case
            "h1d1r0",  # No spaces
            "h1 d1 ",  # Trailing space without remove
        ]

        for move in invalid_moves:
            self.assertFalse(
                self.game.make_move(move), f"Move should be invalid: {move}"
            )

        # Test moves with invalid but similar-looking positions
        invalid_positions = [
            "h1 a0 r0",  # Row 0 doesn't exist
            "h1 a8 r0",  # Row 8 doesn't exist
            "h1 h1 r0",  # Column h doesn't exist
            "h1 1a r0",  # Reversed format
            "h1 aa r0",  # Invalid column
            "h1 11 r0",  # Invalid format
        ]

        for move in invalid_positions:
            self.assertFalse(
                self.game.make_move(move), f"Move should be invalid: {move}"
            )

    def test_game_end_by_invalid_move(self) -> None:
        """Test game ending when a player makes an invalid move"""
        # Setup player to return invalid move
        self.game.current_player.read.return_value = "invalid move"

        # Run game and verify winner
        winner = self.game.run_game()
        self.assertEqual(winner, self.game._player2)

        # Verify game ended with correct messages
        self.assertTrue(self.game._is_game_over)
        self.game._player1.write.assert_called()
        self.game._player2.write.assert_called()

    def test_game_end_by_timeout(self) -> None:
        """Test game ending when a player's move times out"""
        self.game._is_game_over = False
        self.game.current_player.read.side_effect = TimeoutError

        # Run game and verify winner
        winner = self.game.run_game()
        self.assertEqual(winner, self.game._player2)
        self.assertTrue(self.game._is_game_over)

    def test_game_end_by_insufficient_pieces(self) -> None:
        """Test game ending when a player has insufficient pieces to continue"""
        # Setup board state with insufficient pieces for orange
        self.game._is_game_over = False
        self.game.board = {pos: None for pos in self.game.board}
        self.game.board["d1"] = "orange"
        self.game.board["d2"] = "orange"
        self.game.player_hands["orange"] = 0

        # Check winner determination
        winner = self.game.determine_winner()
        self.assertEqual(winner, self.game._player1)

        # Verify game state
        self.assertTrue(self.game._is_game_over)
        total_pieces = self.game._count_player_pieces("orange")
        self.assertTrue(total_pieces < 3)

    def test_game_end_by_oscillation_draw(self) -> None:
        """Test game ending in a draw due to repetitive moves"""
        # Setup oscillating move pattern
        self.game._is_game_over = False
        self.game.game_history = [
            {"move": "d1 d2 r0", "player": "blue", "board": {}, "hands": {}},
            {"move": "e1 e2 r0", "player": "orange", "board": {}, "hands": {}},
            {"move": "d2 d1 r0", "player": "blue", "board": {}, "hands": {}},
            {"move": "e2 e1 r0", "player": "orange", "board": {}, "hands": {}},
            {"move": "d1 d2 r0", "player": "blue", "board": {}, "hands": {}},
            {"move": "e1 e2 r0", "player": "orange", "board": {}, "hands": {}},
            {"move": "d2 d1 r0", "player": "blue", "board": {}, "hands": {}},
            {"move": "e2 e1 r0", "player": "orange", "board": {}, "hands": {}},
            {"move": "d1 d2 r0", "player": "blue", "board": {}, "hands": {}},
            {"move": "e1 e2 r0", "player": "orange", "board": {}, "hands": {}},
            {"move": "d2 d1 r0", "player": "blue", "board": {}, "hands": {}},
            {"move": "e2 e1 r0", "player": "orange", "board": {}, "hands": {}},
        ]

        # Check winner determination
        winner = self.game.determine_winner()

        # Verify draw conditions
        self.assertIsNone(winner)  # Draw should return None
        self.assertTrue(self.game._is_game_over)
        self.game._player1.write.assert_called()
        self.game._player2.write.assert_called()
