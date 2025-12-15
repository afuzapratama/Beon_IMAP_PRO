# Beon IMAP PRO - Copilot Instructions

## Project Overview

IMAP credential testing utility with two main scripts for validating email login credentials against IMAP servers. Supports SOCKS5 proxy routing for anonymized testing.

## Architecture

### Main Scripts
- **`imaplogintester.py`** - Basic IMAP login tester with proxy support (`hostname:port:username:password` format)
- **`imapProxy.py`** - Enhanced version with separate proxy auth flags (`-U`/`-W`) and failed login output (`-f`)

### Configuration
- **`domains.ini`** - INI-format mapping of email domains to IMAP server settings:
  ```ini
  [gmail.com]
  imap = imap.gmail.com
  port = 993
  ssl = True
  ```

### Input/Output Format
- **Input**: `email:password` per line (e.g., `user@gmail.com:mypassword`)
- **Output**: Successful logins written to output file in same format

## Key Patterns

### Email Domain Resolution
Domain extracted from email, looked up in `domains.ini` sections. Missing domains trigger warnings but continue processing.

### Proxy Configuration Differences
```bash
# imaplogintester.py - combined format
-P "host:port:username:password"

# imapProxy.py - separate flags
-P "host:port" -U username -W password
```

### SSL Handling
`ssl` config value is string `"True"` or `"False"` (not boolean). Python version detection for timeout parameter (3.9+).

## Running the Scripts

```bash
# Install dependencies
pip install -r requirements.txt

# Basic usage
python imaplogintester.py -i test.txt -o results.txt -v

# With proxy (imapProxy.py)
python imapProxy.py -i test.txt -o success.txt -f failed.txt -P "proxy:1080" -U user -W pass

# Common flags: -s (successes only), -t (sleep time), -T (timeout), -v (verbose)
```

## Dependencies

- `SocksiPy_branch` - SOCKS proxy support (note: `imapProxy.py` uses `socks.setdefaultproxy`, `imaplogintester.py` uses `socks.set_default_proxy`)
- `termcolor` - Colored terminal output
- `validators` - Domain/IP validation

## Adding New Email Domains

Add section to `domains.ini`:
```ini
[newdomain.com]
imap = imap.newdomain.com
port = 993
ssl = True
```

## Code Conventions

- Signal handling for graceful Ctrl+C exit
- Helper functions: `green()`, `red()`, `yellow()` for colored output
- `email_is_valid()` regex validation before processing
- File handles flushed immediately after each successful write
- UTF-8 encoding used for all file operations

## Known Limitations (from TODOs)

- No validation of `domains.ini` file format
- Single-threaded processing (no multithreading implemented)
- `backup/` contains test data files, not production code
