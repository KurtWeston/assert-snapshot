"""Colored diff output formatting and interactive prompts."""

import difflib
from colorama import Fore, Style, init

init(autoreset=True)


def format_diff(expected: str, actual: str) -> str:
    """Generate colored unified diff output."""
    expected_lines = expected.splitlines(keepends=True)
    actual_lines = actual.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        expected_lines,
        actual_lines,
        fromfile='expected',
        tofile='actual',
        lineterm=''
    )
    
    colored_lines = []
    for line in diff:
        if line.startswith('+') and not line.startswith('+++'):
            colored_lines.append(Fore.GREEN + line + Style.RESET_ALL)
        elif line.startswith('-') and not line.startswith('---'):
            colored_lines.append(Fore.RED + line + Style.RESET_ALL)
        elif line.startswith('@@'):
            colored_lines.append(Fore.CYAN + line + Style.RESET_ALL)
        else:
            colored_lines.append(line)
    
    return '\n'.join(colored_lines)


def prompt_update() -> bool:
    """Prompt user to accept or reject snapshot update."""
    while True:
        response = input("\nUpdate snapshot? [y/N]: ").strip().lower()
        if response in ('y', 'yes'):
            return True
        elif response in ('n', 'no', ''):
            return False
        else:
            print("Please enter 'y' or 'n'")
