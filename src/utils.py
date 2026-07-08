import os
import sys

from InquirerPy.base.control import Choice


def clear_terminal() -> None:
    """Clears the terminal screen based on the Operating System."""
    os.system("cls" if os.name == "nt" else "clear")


def prompt_to_continue() -> None:
    if input("Press Enter to continue or 'q' to exit... ").lower() == "q":
        clear_terminal()
        sys.exit(1)


def create_choice_list(types_list: list) -> list:
    format_list = [Choice(value=x, name=x) for x in types_list]

    return format_list
