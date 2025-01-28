from flask import jsonify, render_template

from ....abstract import WebGame


class LaskerMorrisWeb(WebGame):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.end_message = None

    def get_game_state_json(self):
        game_data = {
            "board": self.game.board,
            "playerHands": self.game.player_hands,
            "currentPlayer": self.game.current_player.get_color(),
            "isGameOver": self.game.is_game_over,
            "invalidFields": list(self.game.invalid_fields),
            "history": {
                "moves": self.game.game_history,
                "boards": self.game.board_states,
                "hands": self.game.hand_states,
            },
            "endMessage": self.end_message if self.game.is_game_over else None,
        }
        return jsonify(game_data)

    def get_index(self):
        """Render template with game state data"""
        game_data = {
            "board": self.game.board,
            "playerHands": self.game.player_hands,
            "currentPlayer": self.game.current_player.get_color(),
            "isGameOver": self.game.is_game_over,
            "invalidFields": list(self.game.invalid_fields),
            "history": {
                "moves": self.game.game_history,
                "boards": self.game.board_states,
                "hands": self.game.hand_states,
            },
            "endMessage": self.end_message if self.game.is_game_over else None,
        }
        return render_template("./lasker_morris/index.html", game_data=game_data)
