# cs4341-referee
[![Build and Test](https://github.com/jake-molnia/cs4341-referee/actions/workflows/build.yml/badge.svg)](https://github.com/jake-molnia/cs4341-referee/actions/workflows/build.yml)
[![codecov](https://codecov.io/gh/jake-molnia/cs4341-referee/branch/main/graph/badge.svg)](https://codecov.io/gh/{username}/cs4341-referee)

## Program communication

Here we describe the communication protocol for the Lasker Morris game referee. The game uses a process-based communication method where players interact through standard input/output streams, allowing for implementation in any programming language that supports these basic I/O operations.

### Player Setup

1. Each player must provide an executable command (e.g., `python3 player.py`) that will be used to start their program.

2. Players will be randomly assigned either blue or orange color at the start of the game. The blue player always moves first.

3. The game manager will create two player processes and handle all communication between them.

### Communication Flow

1. Game Initialization:
   - The game manager starts both player processes using their provided commands
   - Players are randomly assigned colors (blue or orange)
   - The blue player receives "blue" as their first input
   - The game begins with the blue player's turn

2. Move Format:
   A move consists of three parts in the format: "A B C" where:
   - A: Current stone location (use 'h1'/'h2' if placing from hand)
   - B: Target board position
   - C: Remove opponent's stone location (use 'r0' if no removal)

   Example moves:
   - `h1 d1 r0` (place new stone at d1, no removal)
   - `d1 d2 e3` (move stone from d1 to d2, remove opponent's stone at e3)

3. Turn Structure:
   - Current player reads opponent's last move (except for first move)
   - Current player calculates and outputs their move
   - Game manager validates the move
   - If valid, the move is sent to the other player
   - If invalid, the current player loses

4. Board Positions:
   - Valid positions are labeled a1 through g7
   - Not all positions are valid (see invalid_fields in code)
   - The board has a 7x7 grid structure with specific valid positions

### Game Rules

1. Initial State:
   - Each player starts with 10 stones in hand
   - The board begins empty
   - Blue player moves first

2. Valid Moves:
   - Players can place stones from their hand using 'h' as source
   - When moving placed stones, must move to adjacent positions unless player has exactly 3 pieces
   - Forming a mill (3 in a row) allows removing an opponent's stone
   - Must remove an opponent's stone when forming a mill

3. Game Ending Conditions:
   - A player loses if they have fewer than 3 pieces total
   - A player loses if they make an invalid move
   - A player loses if they exceed the time limit

### Implementation Notes

1. Player programs should:
   - Read moves from standard input
   - Write moves to standard output
   - Format all moves as described above
   - Handle invalid moves from opponents
   - Track game state internally

2. Common Errors to Avoid:
   - Moving opponent's pieces
   - Moving to invalid positions
   - Moving to occupied positions
   - Not removing stones when forming mills
   - Removing own stones
   - Moving to non-adjacent positions when having more than 3 pieces

3. Visualization:
   - The game manager provides a visual representation of the board
   - Shows current state including:
     - Pieces on board
     - Stones remaining in hand
     - Current player's turn
     - Last move made

### Example Game Sequence

1. Game starts, processes created
2. Blue player receives `blue`
3. Blue player outputs `h1 d1 r0`
4. Orange player receives `orange`
5. Orange player receives `h1 d1 r0`
6. Orange player outputs `h2 g7 r0`
7. Game continues until win condition met

Note: All communication must be precisely formatted. Any deviation from the expected format will result in an invalid move and loss of game.

## Installation

You can install this package directly from GitHub using pip:

```bash
pip install git+https://github.com/jake-molnia/cs4341-referee.git
```

Or install a specific version:

```bash
pip install git+https://github.com/jake-molnia/cs4341-referee.git@v0.1.0
```

## Player Program

Your player program should follow these communication rules to work with the referee:

### Basic Requirements
- Read moves/input from stdin (standard input)
- Write moves/output to stdout (standard output)
- Each message must be on a new line
- Always flush output after writing

### Example Templates

#### Python
```python
import sys

while True:
    game_input = input().strip()  # Read and clean input
    move = "your move logic here"
    print(move, flush=True)  # flush=True is crucial!
```

#### Java

```java
Scanner scanner = new Scanner(System.in);
while (scanner.hasNextLine()) {
    String input = scanner.nextLine();
    String move = "your move logic here";
    System.out.println(move);
    System.out.flush();  // Don't forget to flush!
}
```

#### JavaScript (Node.js)

```javascript
process.stdin.on('data', (input) => {
    const move = "your move logic here";
    console.log(move);  // Node.js auto-flushes console.log
});
```

### Important Notes

- Without flushing, your moves won't be sent to the referee immediately
- Different languages handle buffering differently:
  - Python: Use `print(move, flush=True)`
  - Java: Use `System.out.flush()`
  - C++: Use `cout << move << endl` or `cout.flush()`
  - Node.js: `console.log()` auto-flushes
- Test your program thoroughly to ensure moves are being sent correctly
