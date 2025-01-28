# Checking and Installing Git

This guide will help you verify and set up Git, which is required to install the CS4341 referee system.

## Checking Git Installation

Open your terminal and run:
```bash
git --version
```

You should see output like:
```
git version 2.39.2
```

## Installing Git

### Windows
1. Download Git from [git-scm.com](https://git-scm.com/download/win)
2. Run the installer
3. Use recommended settings (especially "Git from the command line and also from 3rd-party software")
4. Choose your preferred text editor (VS Code recommended)
5. Select "Use Git from Git Bash only" or "Use Git from the Windows Command Prompt"
6. For line endings, choose "Checkout Windows-style, commit Unix-style"

### macOS
Using Homebrew:
```bash
brew install git
```

Or download from [git-scm.com](https://git-scm.com/download/mac)

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install git
```

## Verifying Installation

After installing, open a new terminal and verify:
```bash
git --version
```

For additional help, consult the [Git documentation](https://git-scm.com/doc) or contact the course staff.