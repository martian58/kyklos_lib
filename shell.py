import os
import sys
import readline  # For command history and line editing
import subprocess
import threading
import time
from kyklos import Data

class Shell:
    def __init__(self) -> None:
        self.api = Data()
        self.commands = {
            'clear': self.clear_screen,
            'help': self.print_help,
            'status': self.show_status,
            'quit': self.quit_shell,
            'exit': self.quit_shell,
            'account': self.api.print_account_info,
            'min_prices': self.api.print_all_min_prices,
            'free_balances': self.free_balances,
            'min_qty': self.min_qty,
            'convert_to_usd': self.convert_to_usd,
            'min_national': self.min_national,
            'parrot': self.start_parrot_animation
        }
        self.command_history_file = ".kyklos_history"  # To save command history
        self.load_command_history()
        self.display_banner()
        self.parrot_process = None

    def load_command_history(self):
        """Load command history from a file"""
        try:
            readline.read_history_file(self.command_history_file)
        except FileNotFoundError:
            # If history file doesn't exist, continue without loading
            pass

    def save_command_history(self):
        """Save command history to a file"""
        readline.write_history_file(self.command_history_file)

    def display_banner(self):
        banner = """
\033[1;32m██╗  ██╗██╗   ██╗██╗  ██╗██╗      ██████╗ ███████╗
██║ ██╔╝╚██╗ ██╔╝██║ ██╔╝██║     ██╔═══██╗██╔════╝
█████╔╝  ╚████╔╝ █████╔╝ ██║     ██║   ██║███████╗
██╔═██╗   ╚██╔╝  ██╔═██╗ ██║     ██║   ██║╚════██║
██║  ██╗   ██║   ██║  ██╗███████╗╚██████╔╝███████║
╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚══════╝
\033[0m
        """
        print(banner)

    def run(self):
        print("Welcome to Kyklos CLI. Type 'help' for a list of commands.\n")
        try:
            while True:
                command = input("\033[1;32mkyklos> \033[0m").strip()
                self.execute_command(command)
        except (KeyboardInterrupt, EOFError):
            self.quit_shell()

    def execute_command(self, command: str):
        parts = command.split()
        cmd = parts[0] if parts else ""
        args = parts[1:]

        if cmd in self.commands:
            self.commands[cmd](*args)
        else:
            print(f"Unknown command: {cmd}. Type 'help' for a list of commands.")

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def free_balances(self):
        free_balance = self.api.get_free_balances()
        # Check if free_balance is a dictionary
        if isinstance(free_balance, dict):
            print()
            for key, balance in free_balance.items():
                # Format the balance with thousands separators and fixed decimal places
                formatted_balance = "{:,.8f}".format(float(balance))  # 8 decimal places
                print(f"{key}: {formatted_balance}")
        else:
            print("Error: The returned value is not a dictionary.")



    def min_national(self, *args):
        min_value = self.api.get_min_notional_value(args[0])
        print(f"\nMinimum value for {args[0]} is {min_value}\n")

    def min_qty(self, *args):
        if len(args) == 0:
            print("Error: Symbol is required. Usage: min_qty SYMBOL")
            return

        symbol = args[0]
        min_qty = self.api.get_min_quantity_for_order(symbol)

        if min_qty is not None:
            print(f"The minimum quantity for {symbol} is {min_qty}")
        else:
            print(f"Could not retrieve minimum quantity for {symbol}.")

    def convert_to_usd(self, *args):
        if len(args) != 1:
            print("Error: You must provide an argument in the format SYMBOL:AMOUNT, e.g., BTC:0.001")
            return

        try:
            symbol, amount_str = args[0].split(":")
            amount = float(amount_str)
        except ValueError:
            print("Error: Invalid format. Use SYMBOL:AMOUNT, e.g., BTC:0.001")
            return

        price_in_usd = self.api.get_crypto_price_in_usd(symbol)

        if price_in_usd is not None:
            value_in_usd = price_in_usd * amount
            print(f"{amount:.8f} {symbol} is worth ${value_in_usd:.7f} USD")
        else:
            print(f"Error: Could not retrieve price for {symbol}.")

    def print_help(self):
        help_text = """
        Available commands:
        clear              - Clear the screen
        help               - Print this help message
        status             - Show the current status of the application
        quit               - Exit the shell
        exit               - Exit the shell
        account            - Get account information
        min_prices         - Get min prices
        free_balances      - Get free balances
        min_qty            - Get min quantity for a symbol
        convert_to_usd     - Convert crypto to USD, Usage: convert_to_usd SYMBOL:AMOUNT
        min_national       - Display the minimum national value for a symbol
        parrot             - Display live parrot animation
        """
        print(help_text)

    def show_status(self):
        print("Application status: Running")

    def quit_shell(self):
        print("Exiting shell. Goodbye!")
        self.save_command_history()  # Save command history on exit
        if self.parrot_process:
            self.parrot_process.terminate()  # Terminate the curl process if it's running
        sys.exit()

    def start_parrot_animation(self, *args):
        if self.parrot_process and self.parrot_process.poll() is None:
            print("Parrot animation is already running.")
            return

        # Run 'curl parrot.live' in a subprocess
        self.parrot_process = subprocess.Popen(
            ['curl', 'parrot.live'],
            stdout=sys.stdout,
            stderr=subprocess.STDOUT
        )

if __name__ == '__main__':
    shell = Shell()
    shell.run()
