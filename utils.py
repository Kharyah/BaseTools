from pathlib import Path

TERMINAL_WIDTH = 60  # Global terminal styling constant


def get_app_data_dir() -> Path:
    """
    Returns the absolute path to the application's dedicated data directory.
    """
    return Path.home() / ".basetools"


def clear_terminal() -> None:
    """Clears the terminal screen based on the Operating System."""
    import os

    os.system("cls" if os.name == "nt" else "clear")


def prompt_to_continue() -> None:
    """Create a follow-up or exit question."""
    import sys

    choice = input(
        "Press Enter to continue or 'q' to exit... "
    ).strip().lower()

    if choice == "q":
        clear_terminal()
        print("BaseTools was closed!")
        sys.exit(0)

        return False
    return True


def path_name_replace(path_name: str) -> str:
    return path_name.replace("_", " ").title()


def print_header(title: str, width: int = TERMINAL_WIDTH) -> print:
    """Generates a centered header with hyphen padding."""
    return print(f" {title} ".center(width, "-"))


def print_divider(char: str = "-", width: int = TERMINAL_WIDTH) -> print:
    """Generates a clean dividing line with the same width as the headers."""
    return print(char * width)
