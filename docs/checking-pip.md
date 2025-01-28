# Checking and Installing pip

This guide will help you verify and set up pip, Python's package installer, which is required for the CS4341 referee system.

## Checking pip Installation

1. Open your terminal and run:
   ```bash
   pip --version
   # or
   pip3 --version
   ```

2. You should see output like:
   ```
   pip 23.1.2 from /usr/local/lib/python3.10/site-packages/pip (python 3.10)
   ```

## Installing pip

### Windows
1. pip usually comes with Python installation. If missing:
   ```bash
   python -m ensurepip --upgrade
   ```
   
### macOS/Linux
```bash
python3 -m ensurepip --upgrade
# or
sudo apt install python3-pip  # Ubuntu/Debian
brew install pip  # macOS with Homebrew
```

## Upgrading pip

It's recommended to keep pip updated:
```bash
python -m pip install --upgrade pip
# or
pip install --upgrade pip
```

## Multiple Python Versions
If you have multiple Python versions:
1. Use the specific version's pip:
   ```bash
   python3.10 -m pip install <package>
   ```
2. Or use virtual environments (recommended):
   ```bash
   python -m venv myenv
   source myenv/bin/activate  # Unix/macOS
   myenv\Scripts\activate     # Windows
   pip install <package>
   ```

## Verifying Installation

After adding to PATH or installing, verify with:
```bash
pip --version
cs4341-referee --help  # After installing the referee
```

For additional help, consult the [pip documentation](https://pip.pypa.io/en/stable/installation/) or contact the course staff.