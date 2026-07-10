import os
import sys

from InquirerPy.base.control import Choice

TERMINAL_WIDTH = 40  # Global terminal styling constant


def clear_terminal() -> None:
    """Clears the terminal screen based on the Operating System."""
    os.system("cls" if os.name == "nt" else "clear")


def prompt_to_continue() -> None:
    """Create a follow-up or exit question."""
    if input("Press Enter to continue or 'q' to exit... ").lower() == "q":
        clear_terminal()
        sys.exit(1)


def create_choice_list(types_list: list) -> list:
    """Create a list for choices in the InquirerPy in a practical way."""
    format_list = [Choice(value=x, name=f"  > {x}") for x in types_list]
    return format_list


def format_header(title: str, width: int = TERMINAL_WIDTH) -> str:
    """Generates a centered header with hyphen padding."""
    return f" {title} ".center(width, "-")


def format_divider(char: str = "-", width: int = TERMINAL_WIDTH) -> str:
    """Generates a clean dividing line with the same width as the headers."""
    return char * width
