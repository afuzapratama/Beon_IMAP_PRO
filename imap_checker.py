#!/usr/bin/env python3
"""
IMAP Login Checker - Interactive Mode
=====================================
Script interaktif untuk testing IMAP login credentials.
Mendukung dua mode: Interactive Menu dan Command Line.

Usage:
    python imap_checker.py              # Interactive mode
    python imap_checker.py --cli ...    # Command line mode
"""

import argparse
import configparser
import imaplib
import os
import re
import signal
import sys
import time
import socks
import validators
from termcolor import colored
from ssl import SSLError
from socket import timeout as socket_timeout


# ==================== HELPER FUNCTIONS ====================

def signal_handler(sign, frame):
    if sign == 2:
        print("\n\n" + yellow("Ctrl+C detected! Exiting..."))
        sys.exit(0)


def green(text):
    return colored(text, "green")


def red(text):
    return colored(text, "red")


def yellow(text):
    return colored(text, "yellow")


def cyan(text):
    return colored(text, "cyan")


def magenta(text):
    return colored(text, "magenta")


def clear_screen():
    os.system('clear' if os.name != 'nt' else 'cls')


def print_banner():
    banner = """
╔══════════════════════════════════════════════════════════╗
║             📧 IMAP LOGIN CHECKER v2.0 📧                ║
║          Interactive Credential Testing Tool             ║
╚══════════════════════════════════════════════════════════╝
    """
    print(cyan(banner))


def email_is_valid(email):
    return re.match(
        r"^[a-zA-Z0-9_+&*-]+(?:\.[a-zA-Z0-9_+&*-]+)*@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,7}$",
        email,
    ) is not None


# ==================== CORE FUNCTIONS ====================

def load_config():
    """Load domains.ini configuration"""
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "domains.ini")
    if not os.path.exists(config_file):
        print(red(f"❌ Config file not found: {config_file}"))
        return None
    
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


def test_single_login(email, password, config, timeout=10, proxy_settings=None, verbose=False):
    """Test single email login"""
    if not email_is_valid(email):
        return False, "Invalid email format"
    
    email_parts = email.lower().split("@")
    account = email_parts[0]
    domain = email_parts[1]
    
    if domain not in config:
        return False, f"Domain '{domain}' not in config"
    
    imap_server = config[domain]["imap"]
    port = int(config[domain]["port"])
    use_ssl = config[domain]["ssl"] == "True"
    
    try:
        # Setup proxy if provided
        if proxy_settings and proxy_settings.get("host"):
            socks.setdefaultproxy(
                socks.PROXY_TYPE_SOCKS5,
                proxy_settings["host"],
                proxy_settings["port"],
                True,
                proxy_settings.get("username"),
                proxy_settings.get("password")
            )
            socks.socket.setdefaulttimeout(30)
            socks.wrapmodule(imaplib)
        
        # Connect to IMAP
        if use_ssl:
            if sys.version_info[1] >= 9:
                connection = imaplib.IMAP4_SSL(imap_server, port=port, timeout=timeout)
            else:
                connection = imaplib.IMAP4_SSL(imap_server, port=port)
        else:
            if sys.version_info[1] >= 9:
                connection = imaplib.IMAP4(imap_server, port=port, timeout=timeout)
            else:
                connection = imaplib.IMAP4(imap_server, port=port)
        
        # Try login
        connection.login(email, password)
        connection.logout()
        return True, "Login successful"
        
    except imaplib.IMAP4.error as e:
        return False, f"Auth failed: {str(e)[:50]}"
    except (SSLError, socket_timeout) as e:
        return False, f"Connection error: {str(e)[:50]}"
    except Exception as e:
        if verbose:
            return False, f"Error: {str(e)[:50]}"
        return False, "Login failed"


def process_file(input_file, output_file, failed_file, config, timeout, sleep_time, proxy_settings, verbose, show_successes_only):
    """Process credential file"""
    if not os.path.exists(input_file):
        print(red(f"❌ Input file not found: {input_file}"))
        return
    
    # Count total lines
    with open(input_file, "r", encoding="utf-8") as f:
        total_lines = sum(1 for line in f if line.strip() and ":" in line)
    
    print(f"\n📁 Processing: {cyan(input_file)}")
    print(f"📊 Total credentials: {yellow(str(total_lines))}")
    print(f"⏱️  Timeout: {timeout}s | Sleep: {sleep_time}s")
    if proxy_settings and proxy_settings.get("host"):
        print(f"🔒 Proxy: {proxy_settings['host']}:{proxy_settings['port']}")
    print("-" * 50)
    
    success_handle = None
    failed_handle = None
    
    try:
        if output_file:
            success_handle = open(output_file, "a", encoding="utf-8")
        if failed_file:
            failed_handle = open(failed_file, "a", encoding="utf-8")
        
        count_all = 0
        count_ok = 0
        count_fail = 0
        
        with open(input_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or ":" not in line:
                    continue
                
                parts = line.split(":", 1)
                email = parts[0].lower()
                password = parts[1]
                
                count_all += 1
                success, msg = test_single_login(email, password, config, timeout, proxy_settings, verbose)
                
                if success:
                    count_ok += 1
                    status = green("✓ SUCCESS")
                    if success_handle:
                        success_handle.write(f"{email}:{password}\n")
                        success_handle.flush()
                    if not show_successes_only or success:
                        print(f"[{count_all}/{total_lines}] {email} | {status}")
                else:
                    count_fail += 1
                    status = red("✗ FAILED")
                    if failed_handle:
                        failed_handle.write(f"{email}:{password}\n")
                        failed_handle.flush()
                    if not show_successes_only:
                        print(f"[{count_all}/{total_lines}] {email} | {status}")
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
        
        print("\n" + "=" * 50)
        print(f"📊 RESULTS: {green(str(count_ok))} success | {red(str(count_fail))} failed | Total: {count_all}")
        if output_file:
            print(f"💾 Success saved to: {cyan(output_file)}")
        if failed_file:
            print(f"💾 Failed saved to: {cyan(failed_file)}")
            
    finally:
        if success_handle:
            success_handle.close()
        if failed_handle:
            failed_handle.close()


# ==================== INTERACTIVE MODE ====================

class InteractiveMode:
    def __init__(self):
        self.config = load_config()
        self.proxy_settings = {
            "host": None,
            "port": None,
            "username": None,
            "password": None
        }
        self.settings = {
            "timeout": 10,
            "sleep_time": 0,
            "verbose": False,
            "show_successes_only": False
        }
        self.input_file = None
        self.output_file = "success.txt"
        self.failed_file = "failed.txt"
    
    def run(self):
        if not self.config:
            print(red("Failed to load config. Exiting."))
            return
        
        while True:
            self.show_menu()
            choice = input(cyan("\n➤ Select option: ")).strip()
            
            if choice == "1":
                self.set_input_file()
            elif choice == "2":
                self.set_output_files()
            elif choice == "3":
                self.configure_proxy()
            elif choice == "4":
                self.configure_settings()
            elif choice == "5":
                self.test_single()
            elif choice == "6":
                self.start_checking()
            elif choice == "7":
                self.show_supported_domains()
            elif choice == "8":
                self.show_current_config()
            elif choice == "0" or choice.lower() == "q":
                print(yellow("\n👋 Goodbye!"))
                break
            else:
                print(red("Invalid option!"))
            
            input(yellow("\nPress Enter to continue..."))
    
    def show_menu(self):
        clear_screen()
        print_banner()
        
        # Show current status
        print(magenta("─" * 50))
        print(f" 📄 Input File  : {cyan(self.input_file or 'Not set')}")
        print(f" 💾 Output File : {cyan(self.output_file)}")
        print(f" 🔒 Proxy       : {cyan(self.proxy_settings['host'] + ':' + str(self.proxy_settings['port']) if self.proxy_settings['host'] else 'Not set')}")
        print(magenta("─" * 50))
        
        print("""
  [1] 📄 Set Input File (email:password list)
  [2] 💾 Set Output Files
  [3] 🔒 Configure Proxy (SOCKS5)
  [4] ⚙️  Settings (timeout, sleep, verbose)
  [5] 🧪 Test Single Login
  [6] 🚀 START CHECKING
  [7] 📋 Show Supported Domains
  [8] 📊 Show Current Configuration
  [0] 🚪 Exit
        """)
    
    def set_input_file(self):
        print(yellow("\n=== SET INPUT FILE ==="))
        print("Enter path to file containing email:password (one per line)")
        
        # List txt files in current directory
        txt_files = [f for f in os.listdir(".") if f.endswith(".txt")]
        if txt_files:
            print(f"\nAvailable .txt files: {', '.join(txt_files)}")
        
        path = input(cyan("File path: ")).strip()
        if os.path.exists(path):
            self.input_file = path
            with open(path, "r") as f:
                lines = sum(1 for line in f if line.strip() and ":" in line)
            print(green(f"✓ File set! Contains {lines} credentials."))
        else:
            print(red(f"❌ File not found: {path}"))
    
    def set_output_files(self):
        print(yellow("\n=== SET OUTPUT FILES ==="))
        print(f"Current success file: {self.output_file}")
        print(f"Current failed file: {self.failed_file}")
        
        success = input(cyan("Success output file (Enter to keep): ")).strip()
        if success:
            self.output_file = success
        
        failed = input(cyan("Failed output file (Enter to keep): ")).strip()
        if failed:
            self.failed_file = failed
        
        print(green("✓ Output files updated!"))
    
    def configure_proxy(self):
        print(yellow("\n=== CONFIGURE SOCKS5 PROXY ==="))
        print("Leave empty to disable proxy\n")
        
        host = input(cyan("Proxy Host (e.g., 127.0.0.1): ")).strip()
        if not host:
            self.proxy_settings = {"host": None, "port": None, "username": None, "password": None}
            print(yellow("Proxy disabled."))
            return
        
        port = input(cyan("Proxy Port (e.g., 1080): ")).strip()
        username = input(cyan("Username (optional): ")).strip()
        password = input(cyan("Password (optional): ")).strip()
        
        self.proxy_settings = {
            "host": host,
            "port": int(port) if port else 1080,
            "username": username if username else None,
            "password": password if password else None
        }
        print(green(f"✓ Proxy configured: {host}:{port}"))
    
    def configure_settings(self):
        print(yellow("\n=== SETTINGS ==="))
        print(f"Current: timeout={self.settings['timeout']}s, sleep={self.settings['sleep_time']}s, verbose={self.settings['verbose']}")
        
        timeout = input(cyan(f"Timeout in seconds [{self.settings['timeout']}]: ")).strip()
        if timeout:
            self.settings["timeout"] = int(timeout)
        
        sleep = input(cyan(f"Sleep between checks [{self.settings['sleep_time']}]: ")).strip()
        if sleep:
            self.settings["sleep_time"] = float(sleep)
        
        verbose = input(cyan("Verbose mode? (y/n): ")).strip().lower()
        if verbose == "y":
            self.settings["verbose"] = True
        elif verbose == "n":
            self.settings["verbose"] = False
        
        success_only = input(cyan("Show successes only? (y/n): ")).strip().lower()
        if success_only == "y":
            self.settings["show_successes_only"] = True
        elif success_only == "n":
            self.settings["show_successes_only"] = False
        
        print(green("✓ Settings updated!"))
    
    def test_single(self):
        print(yellow("\n=== TEST SINGLE LOGIN ==="))
        email = input(cyan("Email: ")).strip()
        password = input(cyan("Password: ")).strip()
        
        if not email or not password:
            print(red("Email and password required!"))
            return
        
        print(yellow("\nTesting..."))
        success, msg = test_single_login(
            email, password, self.config,
            self.settings["timeout"],
            self.proxy_settings,
            True
        )
        
        if success:
            print(green(f"\n✓ SUCCESS! {msg}"))
        else:
            print(red(f"\n✗ FAILED: {msg}"))
    
    def start_checking(self):
        if not self.input_file:
            print(red("❌ Please set input file first!"))
            return
        
        print(yellow("\n=== STARTING CREDENTIAL CHECK ==="))
        confirm = input(cyan("Continue? (y/n): ")).strip().lower()
        if confirm != "y":
            return
        
        process_file(
            self.input_file,
            self.output_file,
            self.failed_file,
            self.config,
            self.settings["timeout"],
            self.settings["sleep_time"],
            self.proxy_settings,
            self.settings["verbose"],
            self.settings["show_successes_only"]
        )
    
    def show_supported_domains(self):
        print(yellow("\n=== SUPPORTED EMAIL DOMAINS ==="))
        domains = list(self.config.sections())
        
        # Group by provider
        print(f"\nTotal: {len(domains)} domains\n")
        for i, domain in enumerate(sorted(domains), 1):
            imap = self.config[domain]["imap"]
            ssl = "SSL" if self.config[domain]["ssl"] == "True" else "Plain"
            print(f"  {i:3}. {domain:25} → {imap:30} [{ssl}]")
    
    def show_current_config(self):
        print(yellow("\n=== CURRENT CONFIGURATION ==="))
        print(f"""
  Input File     : {self.input_file or 'Not set'}
  Output File    : {self.output_file}
  Failed File    : {self.failed_file}
  
  Proxy Host     : {self.proxy_settings['host'] or 'Disabled'}
  Proxy Port     : {self.proxy_settings['port'] or '-'}
  Proxy Username : {self.proxy_settings['username'] or '-'}
  Proxy Password : {'*' * len(self.proxy_settings['password']) if self.proxy_settings['password'] else '-'}
  
  Timeout        : {self.settings['timeout']} seconds
  Sleep Time     : {self.settings['sleep_time']} seconds
  Verbose        : {self.settings['verbose']}
  Success Only   : {self.settings['show_successes_only']}
        """)


# ==================== CLI MODE ====================

def cli_mode():
    parser = argparse.ArgumentParser(
        prog="imap_checker.py",
        description="IMAP Login Checker - Test email credentials",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python imap_checker.py                                    # Interactive mode
  python imap_checker.py --cli -i data.txt -o success.txt   # CLI mode
  python imap_checker.py --cli -i data.txt -P 127.0.0.1:1080 -U user -W pass
        """
    )
    
    parser.add_argument("--cli", action="store_true", help="Use command line mode")
    parser.add_argument("-i", "--input", help="Input file with email:password")
    parser.add_argument("-o", "--output", help="Output file for successful logins")
    parser.add_argument("-f", "--failed", help="Output file for failed logins")
    parser.add_argument("-P", "--proxy", help="SOCKS5 proxy (host:port)")
    parser.add_argument("-U", "--proxy-user", help="Proxy username")
    parser.add_argument("-W", "--proxy-pass", help="Proxy password")
    parser.add_argument("-t", "--sleep", type=float, default=0, help="Sleep between tests (seconds)")
    parser.add_argument("-T", "--timeout", type=int, default=10, help="Connection timeout (seconds)")
    parser.add_argument("-s", "--success-only", action="store_true", help="Show successes only")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # If no CLI flag, run interactive mode
    if not args.cli:
        return False
    
    # CLI mode requires input file
    if not args.input:
        print(red("Error: --input file required in CLI mode"))
        parser.print_help()
        sys.exit(1)
    
    config = load_config()
    if not config:
        sys.exit(1)
    
    # Parse proxy
    proxy_settings = {"host": None, "port": None, "username": None, "password": None}
    if args.proxy:
        parts = args.proxy.split(":")
        proxy_settings["host"] = parts[0]
        proxy_settings["port"] = int(parts[1]) if len(parts) > 1 else 1080
        proxy_settings["username"] = args.proxy_user
        proxy_settings["password"] = args.proxy_pass
    
    print_banner()
    process_file(
        args.input,
        args.output,
        args.failed,
        config,
        args.timeout,
        args.sleep,
        proxy_settings,
        args.verbose,
        args.success_only
    )
    
    return True


# ==================== MAIN ====================

def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    # Try CLI mode first
    if cli_mode():
        return
    
    # Otherwise run interactive mode
    interactive = InteractiveMode()
    interactive.run()


if __name__ == "__main__":
    main()
