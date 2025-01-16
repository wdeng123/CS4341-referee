# Lasker Morris Communication Protocol

This document provides detailed information about the communication protocol used in the Lasker Morris game referee system. The protocol is designed to be language-agnostic, allowing players to be implemented in any programming language that supports standard input/output operations.

## Table of Contents
- [Overview](#overview)
- [Communication Flow](#communication-flow)
- [Message Format](#message-format)
- [Implementation Guidelines](#implementation-guidelines)
- [Language-Specific Examples](#language-specific-examples)
- [Common Issues and Solutions](#common-issues-and-solutions)
- [Testing Your Implementation](#testing-your-implementation)

## Overview

### Key Principles
- Standard I/O based communication
- Text-based message format
- Strict move validation
- Immediate output flushing requirement
- Turn-based synchronization

### Process Architecture
```
[Player 1 Process] <-> [Referee Process] <-> [Player 2 Process]
        ^                     |                     ^
        |                     v                     |
    stdin/stdout         Game Logic            stdin/stdout
```

## Communication Flow

### Game Initialization
1. Referee starts both player processes
2. Players are assigned colors randomly
3. Blue player receives "blue" message
4. Orange player receives "orange" message
5. Blue player makes first move

### Turn Sequence
1. Current player reads opponent's move from stdin
   - First move: Blue player receives no initial move
   - Subsequent moves: Player receives opponent's last move
2. Current player calculates next move
3. Current player writes move to stdout and flushes
4. Referee validates move
   - Valid: Move is sent to opponent
   - Invalid: Current player loses

### Game Termination
- Referee closes player processes when:
  - Win condition is reached
  - Invalid move is made
  - Time limit is exceeded
  - Process error occurs

## Message Format

### Color Assignment
- Input Format: Single word "blue" or "orange"
- Example:
  ```
  blue
  ```

### Move Format
Format: "A B C" where:
- A: Source position
  - `h1`/`h2`: Place from hand (h1 for first player, h2 for second)
  - `a1`-`g7`: Board position for moving existing piece
- B: Target position (a1-g7)
- C: Capture position
  - `r0`: No capture
  - `a1`-`g7`: Position of opponent's piece to remove

Examples:
```
h1 d1 r0    # Place from hand to d1, no capture
d1 d2 e3    # Move from d1 to d2, capture at e3
f4 f6 r0    # Move from f4 to f6, no capture
```

### Board Positions

TODO: Insert image of game state

Invalid positions: a2, a3, a5, a6, b1, b3, b5, b7, etc.

## Implementation Guidelines

### Essential Requirements
1. Read from stdin/standard input
2. Write to stdout/standard output
3. Flush output buffer after each move
4. One move per line
5. Handle invalid opponent moves
6. Track game state internally

### Input/Output Handling
```python
# Correct
print(move, flush=True)  # Python
System.out.println(move); System.out.flush();  # Java
cout << move << endl;  # C++ (endl flushes)

# Incorrect
print(move)  # Python (no flush)
System.out.println(move);  # Java (no flush)
cout << move;  # C++ (no newline or flush)
```

### Move Validation
Player programs should validate:
- Source position exists
- Target position is valid
- Target position is empty
- Move is to adjacent position (unless 3 pieces)
- Capture is required when mill is formed
- Capture position contains opponent's piece

## Language-Specific Examples

### Python
```python
import sys
from typing import Optional

class LaskerPlayer:
    def __init__(self):
        self.color: Optional[str] = None

    def run(self):
        # Read color assignment
        self.color = input().strip()

        while True:
            try:
                # Read opponent's move (if not first move)
                if self.color != "blue":
                    opponent_move = input().strip()

                # Calculate your move
                move = self.calculate_move()

                # Send move
                print(move, flush=True)

            except EOFError:
                break

    def calculate_move(self) -> str:
        # Your move logic here
        return "h1 d1 r0"  # Example move

if __name__ == "__main__":
    player = LaskerPlayer()
    player.run()
```

### Java
```java
import java.util.Scanner;

public class LaskerPlayer {
    private String color;
    private final Scanner scanner;

    public LaskerPlayer() {
        this.scanner = new Scanner(System.in);
    }

    public void run() {
        // Read color assignment
        color = scanner.nextLine().trim();

        while (scanner.hasNextLine()) {
            try {
                // Read opponent's move (if not first move)
                if (!"blue".equals(color)) {
                    String opponentMove = scanner.nextLine().trim();
                }

                // Calculate and send move
                String move = calculateMove();
                System.out.println(move);
                System.out.flush();

            } catch (Exception e) {
                break;
            }
        }
    }

    private String calculateMove() {
        // Your move logic here
        return "h1 d1 r0";  // Example move
    }

    public static void main(String[] args) {
        new LaskerPlayer().run();
    }
}
```

### Node.js
```javascript
const readline = require('readline');

class LaskerPlayer {
    constructor() {
        this.color = null;
        this.rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });
    }

    async run() {
        // Read color assignment
        this.color = await new Promise(resolve => {
            this.rl.once('line', (line) => resolve(line.trim()));
        });

        // Game loop
        this.rl.on('line', (line) => {
            const move = this.calculateMove();
            console.log(move);  // Node.js auto-flushes
        });
    }

    calculateMove() {
        // Your move logic here
        return "h1 d1 r0";  // Example move
    }
}

new LaskerPlayer().run();
```

## Common Issues and Solutions

### Buffer Flushing
Problem: Moves not being received by referee
Solution: Always flush output buffer after writing moves

### Move Timing
Problem: Moves timing out
Solution: Ensure moves are calculated within time limit

### Input Reading
Problem: Missing opponent moves
Solution: Properly handle input stream and EOFError

### Invalid Moves
Problem: Game ending unexpectedly
Solution: Validate moves before sending

## Testing Your Implementation

### Basic Test Script
To run a simple test, simple provide your player for both player 1 and player 2 to the referee and ensure the program doesnt error out.

### Validation Checklist
- [ ] Properly reads color assignment
- [ ] Makes valid first move
- [ ] Reads opponent moves correctly
- [ ] Responds within time limit
- [ ] Handles invalid opponent moves
- [ ] Flushes output properly
- [ ] Terminates cleanly
