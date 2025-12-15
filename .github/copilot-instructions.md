# Beon IMAP PRO - Copilot Instructions

## Project Overview

IMAP credential testing utility with interactive and CLI modes. Supports SOCKS5 proxy (including SSH Tunnel) for bypassing IP blocks.

## Architecture

### Main Scripts
- **`imap_checker.py`** - Main script with Interactive Menu & CLI mode (recommended)
- **`imaplogintester.py`** - Legacy basic IMAP tester
- **`imapProxy.py`** - Legacy version with proxy support

### Configuration
- **`domains.ini`** - INI-format mapping of email domains to IMAP server settings:
  ```ini
  [gmail.com]
  imap = imap.gmail.com
  port = 993
  ssl = True
  ```

### Output Structure
```
hasil/
└── YYYY-MM-DD/
    ├── success/
    │   └── success_YYYYMMDD_HHMMSS.txt
    └── failed/
        └── failed_YYYYMMDD_HHMMSS.txt
```

### Input/Output Format
- **Input**: `email:password` per line
- **Output**: Same format, separated into success/failed folders

## Running the Scripts

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install PySocks

# Interactive mode
python imap_checker.py

# CLI mode with SSH Tunnel proxy
ssh -D 1080 -N -C user@server  # Terminal 1
python imap_checker.py --cli -i test.txt -P "localhost:1080" -T 30 -v  # Terminal 2

# CLI flags: -i (input), -o (output), -f (failed), -P (proxy), -T (timeout), -v (verbose)
```

## Key Patterns

### Proxy Handling
- Uses PySocks library for SOCKS5 proxy
- SSH Tunnel recommended: `ssh -D 1080 -N -C user@server`
- Proxy initialized once globally to avoid recursion

### SSL Handling
`ssl` config value is string `"True"` or `"False"` (not boolean). Python 3.9+ uses timeout parameter.

## Code Conventions

- Signal handling for graceful Ctrl+C exit
- Helper functions: `green()`, `red()`, `yellow()`, `cyan()` for colored output
- `get_output_paths()` generates organized folder structure
- File handles flushed immediately after each write
- UTF-8 encoding for all file operations

## Dependencies

- `PySocks` - SOCKS5 proxy support (recommended)
- `SocksiPy_branch` - Legacy SOCKS support
- `termcolor` - Colored terminal output
- `validators` - Domain/IP validation

## Known Issues

- Some commercial proxies (Webshare, 360s5) block IMAP ports
- SSH Tunnel is the most reliable proxy method
- IP can get blocked by mail servers after many failed attempts
