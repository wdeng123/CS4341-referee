LASKER MORRIS GAME - PROJECT SPECIFICATION

PROGRAM COMMUNICATION
This project implements a two-player board game called Lasker Morris where players take turns placing and moving stones on a specialized board. The game uses a simple text-based communication system that allows programs written in different programming languages to play against each other.

PLAYER-REFEREE COMMUNICATION
The referee communicates with player programs like a text conversation:
1. Program Starting:
   - The referee starts each player program
   - The referee can send text messages to each player program
   - Players can read these messages and send text responses back
   - Think of it like a chat where each program must wait for and respond to messages

2. How Messages Work:
   - When the referee sends a message, it appears as text input to your program
   - Your program should read this input (like reading user keyboard input)
   - Your program responds by writing text output (like printing to the screen)
   - Each message must be on its own line (end with Enter/newline)
   - After sending a message, your program needs to ensure it's actually sent (flush the output)

3. Game Flow:
   - At the start, the referee tells each player their color ("blue" or "orange")
   - The orange player waits to receive the blue player's first move
   - Players take turns reading moves and sending their responses
   - Each move must be written as three parts with spaces between:
     * Starting position (either "h1"/"h2" for hand, or the position of your stone)
     * Where you want to place/move the stone
     * Position of opponent's stone to remove (or "r0" if not removing any)
   - Players must respond within 5 seconds

4. Program Cleanup:ª
   - The referee properly closes the communication channels
   - All programs are closed properly when the game ends

   I'll add an example game sequence section with realistic Lasker Morris moves:

EXAMPLE GAME SEQUENCE
**For illustration purposes, here is an example sequence of events that happens in a game between two groups GroupY and GroupZ.**

1. We run the GroupY and GroupZ programs.
2. Referee starts and randomly assigns colors:
   - GroupY gets blue
   - GroupZ gets orange

```
Referee -> GroupY: "blue"
Referee -> GroupZ: "orange"
```

3. Game begins with initial moves:
```
GroupY -> Referee: "h1 d1 r0"        // Blue places first stone at d1
Referee -> GroupZ: "h1 d1 r0"        // Orange receives blue's move
GroupZ -> Referee: "h2 g7 r0"        // Orange places stone at g7
Referee -> GroupY: "h2 g7 r0"        // Blue receives orange's move
```

4. Later in the game - example of forming a mill:
```
GroupY -> Referee: "d1 d2 r0"        // Blue moves stone from d1 to d2, forming a mill with d2-d3-d4
Referee -> GroupZ: "d1 d2 g7"        // Orange receives move, loses stone at g7
GroupZ -> Referee: "h2 f4 r0"        // Orange places new stone from hand
Referee -> GroupY: "h2 f4 r0"        // Blue receives orange's move
```

5. Example of flying move (when player has 3 stones):
```
GroupY -> Referee: "a1 g7 r0"        // Blue flies from a1 to g7 (allowed with 3 stones)
Referee -> GroupZ: "a1 g7 r0"        // Orange receives move
```

6. Example of game ending move:
```
GroupY -> Referee: "g7 d7 f4"        // Blue forms mill and removes orange's second-to-last stone
Referee: "END: GroupY WINS! GroupZ LOSES! GroupZ has fewer than 3 stones!"
```

7. All programs stop running.

REFEREE
A referee program to conduct the game is provided (you don't have to write the referee). The functions of the referee are:

1. Randomly assigning colors (blue or orange) to each player, which determines who goes first
2. Displaying a graphical depiction of the board configuration after each move, including:
   - Current board state with colored stones
   - Number of stones remaining in each player's hand
   - Current player's turn
   - Last move made
3. Managing turns between players and validating moves
4. Timing each player's moves with a 5-second time limit
5. Detecting invalid moves, including:
   - Moving from/to invalid positions
   - Moving opponent's stones
   - Invalid stone removal
   - Incorrect movement patterns
6. Ending the game when win conditions are met:
   - A player has fewer than 3 stones
   - A player makes an invalid move
   - A player exceeds the time limit
   - A player makes an out-of-order move

END GAME CONDITIONS
The possible messages the referee can write at the end of the game are:
END: <winning_groupname> WINS! <losing_groupname> LOSES! <reason>
where reason can be any of the following:
- <losing_groupname> has fewer than 3 stones!
- Time out!
- Invalid move!
- Out-of-order move!

IMPLEMENTATION BENEFITS
This communication approach has several benefits:
1. You can write your player in any programming language that can read input and write output
2. The communication format is simple - just text messages
3. The referee handles all the complex parts of running the programs

If you find any issues or bugs with this referee program, or any deviations from the specifications provided on this webpage, PLEASE report them on the project 1 Slack channel immediately. In such event, we will try to fix any bugs, update the version of the referee program and notify the class.

The process between players and referee continues until either a win condition is met or an invalid move is made. The referee ensures all programs are properly closed and notifies both players of the game's end.

Please note: Your players should not assume that the referee is actively running the game when they start. Your program should be able to wait to receive the color assignment from the referee, and in the case of the orange player also wait to receive the blue player's first move, before start playing.
