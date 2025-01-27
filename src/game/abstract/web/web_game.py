import threading
from abc import ABC, abstractmethod

from click import echo
from flask import Flask
from flask_cors import CORS


class WebGame(ABC):
    """Abstract base class for web-enabled games"""

    def __init__(self):
        self.app = Flask(__name__, template_folder="../../../web/templates/")
        CORS(self.app)
        self.game_history = []
        # Register routes
        self.app.route("/")(self.get_index)
        self.app.route("/game-state")(self.get_game_state_json)

    @abstractmethod
    def get_game_state_json(self):
        """Return current game state as JSON"""
        pass

    @abstractmethod
    def get_index(self):
        """Return game index.html"""
        pass

    def start_web_server(self, port=8000):
        """Start production server using Waitress"""
        from waitress import serve

        url = f"http://localhost:{port}"
        echo(f"\n🎮 Game visualization available at: 🌐 {url}")
        threading.Thread(
            target=lambda: serve(self.app, host="0.0.0.0", port=port), daemon=True
        ).start()
