# Lasker Morris Game Referee
[![Build and Test](https://github.com/jake-molnia/cs4341-referee/actions/workflows/build.yml/badge.svg)](https://github.com/jake-molnia/cs4341-referee/actions/workflows/build.yml)
[![codecov](https://codecov.io/gh/jake-molnia/cs4341-referee/branch/main/graph/badge.svg)](https://codecov.io/gh/{username}/cs4341-referee)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A Python implementation of a referee for the Lasker Morris board game, designed for programming competitions and AI development.

## Table of Contents
- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Game Rules](#game-rules)
- [Communication Protocol](#communication-protocol)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Features
- 🎮 Complete Lasker Morris game implementation
- 🤖 Process-based player communication
- 🎯 Move validation and game state tracking
- 📊 Visual game state representation
- 🔄 Automatic turn management
- ⏱️ Time limit enforcement
- 🏆 Win condition detection

## Quick Start

```bash
# Install the referee
pip install git+https://github.com/jake-molnia/cs4341-referee.git

# Start a game between two players
lasker-morris start -p1 "python3 player1.py" -p2 "python3 player2.py"
```

## Installation

### Using pip
```bash
# Install latest version
pip install git+https://github.com/jake-molnia/cs4341-referee.git

# Install specific version
pip install git+https://github.com/jake-molnia/cs4341-referee.git@v0.1.0
```

### From source
```bash
git clone https://github.com/jake-molnia/cs4341-referee.git
cd cs4341-referee
pip install -e .
```

## Usage

### Command Line Interface
```bash
# Start a game with visualization
lasker-morris start -p1 "python3 player1.py" -p2 "python3 player2.py" -v

# Start a game without visualization
lasker-morris start -p1 "./player1" -p2 "./player2" --no-visual

# Get help
lasker-morris --help
```

### Python API
```python
from lasker_morris import LaskerMorris

# Create game instance
game = LaskerMorris("python3 player1.py", "python3 player2.py", visual=True)

# Run the game
winner = game.run_game()

# Check winner
if winner:
    print(f"Winner: {winner.get_color()}")
else:
    print("Game ended in a draw")
```

## Game Rules

### Board Layout
The game is played on a 7x7 grid with specific valid positions. The board looks like this:

TODO: Insert picture of game

### Basic Rules
- Players start with 10 stones each
- Blue player moves first
- Stones can be placed from hand or moved on board
- Moving to adjacent positions only (except with 3 pieces)
- Forming 3-in-a-row (mill) allows capturing
- Game ends when a player has fewer than 3 pieces

## Communication Protocol

### Move Format
Moves are formatted as "A B C" where:
- A: Source position ('h1'/'h2' for hand, or board position)
- B: Target position
- C: Capture position ('r0' for no capture)

Example: `h1 d1 r0` or `d1 d2 e3`

### Player Implementation Templates

#### Python
```python
import sys

def main():
    while True:
        game_input = input().strip()
        # Your move logic here
        move = "h1 d1 r0"  # Example move
        print(move, flush=True)

if __name__ == "__main__":
    main()
```

#### Java
```java
import java.util.Scanner;

public class Player {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        while (scanner.hasNextLine()) {
            String input = scanner.nextLine();
            // Your move logic here
            String move = "h1 d1 r0";  // Example move
            System.out.println(move);
            System.out.flush();
        }
    }
}
```

For more templates and details, see [Communication Protocol Documentation](docs/PROTOCOL.md)


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
