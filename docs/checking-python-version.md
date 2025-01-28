# Checking Your Python Version

This guide will help you verify that you have Python 3.9 or higher installed on your system, which is required to run the CS4341 referee system.

## Command Line Method

1. Open your terminal (Command Prompt on Windows, Terminal on macOS/Linux)

2. Run one of these commands:
   ```bash
   python --version
   # or
   python3 --version
   ```

3. You should see output like:
   ```
   Python 3.10.8
   ```
   Make sure the version number is 3.10.0 or higher.

## Checking in Python

You can also check your version from within Python:

1. Open Python in interactive mode:
   ```bash
   python
   # or
   python3
   ```

2. Run this code:
   ```python
   import sys
   print(sys.version)
   ```

3. You'll see detailed version information like:
   ```
   3.10.8 (main, Oct 13 2022, 10:17:43) [Clang 14.0.0 (clang-1400.0.29.102)]
   ```

## Installing or Updating Python

If you don't have Python 3.9+ installed:

### Windows
1. Visit the [Python Downloads page](https://www.python.org/downloads/)
2. Download the latest Python 3 installer
3. Run the installer, making sure to check "Add Python to PATH"

### macOS
Using Homebrew:
```bash
brew install python@3.12
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3.12
```

## Multiple Python Versions

If you have multiple Python versions installed:

1. You can specify the version explicitly:
   ```bash
   python3.9 --version
   python3.10 --version
   ```

2. Consider using virtual environments to manage different Python versions:
   ```bash
   # Create a virtual environment with specific Python version
   python3.10 -m venv myenv

   # Activate it
   source myenv/bin/activate  # On Unix/macOS
   myenv\Scripts\activate     # On Windows
   ```

## Troubleshooting

If you see an error like "python not found" or get a version lower than 3.10:

1. Make sure Python is properly installed
2. Check if Python is added to your system's PATH
3. Try using `python3` instead of `python`
4. On Windows, try using `py -3` or `py -3.10`

For additional help, consult the [Python Installation Guide](https://docs.python.org/3/using/index.html) or contact the course staff.
