import os
import sys

from pathlib import Path
from InquirerPy.base.control import Choice

TERMINAL_WIDTH = 40  # Global terminal styling constant


def get_project_root(anchor: str = "requirements.txt") -> Path:
    """
    Finds the project root directory by traversing
    upwards from the current file.

    :param anchor: The filename used as a landmark
    to identify the root directory.
    :return: A Path object pointing to the root
    directory or the current parent.
    """
    current_path = Path(__file__).resolve()

    # Traverse upwards through parent directories
    # to find the project root anchor
    for parent in [current_path] + list(current_path.parents):
        if (parent / anchor).exists():
            return parent
    return current_path.parent


def clear_terminal() -> None:
    """Clears the terminal screen based on the Operating System."""
    os.system("cls" if os.name == "nt" else "clear")


def prompt_to_continue() -> None:
    """Create a follow-up or exit question."""
    if input("Press Enter to continue or 'q' to exit... ").lower() == "q":
        clear_terminal()
        sys.exit(1)


def path_name_replace(path_name: str) -> str:
    return path_name.replace("_", " ").title()


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
