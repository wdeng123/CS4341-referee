# cs4341-referee

[![Build and Test](https://github.com/jake-molnia/cs4341-referee/actions/workflows/build.yml/badge.svg)](https://github.com/jake-molnia/cs4341-referee/actions/workflows/build.yml)
[![codecov](https://codecov.io/gh/jake-molnia/cs4341-referee/branch/main/graph/badge.svg)](https://codecov.io/gh/{username}/cs4341-referee)

TODO: Write README

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
