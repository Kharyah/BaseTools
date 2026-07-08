import os
import json
import logging

from pathlib import Path
from utils import clear_terminal

from InquirerPy import inquirer
from InquirerPy.base.control import Choice

PATH_FILE_JSON = Path("data/folders_path.json")
SRT_MODES_JSON = Path("data/srt_modes.json")

JSON_FILE_MAP = {
    "path_file": PATH_FILE_JSON,
    "srt_modes": SRT_MODES_JSON
}


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


def start_logging() -> None:
    """
    Initializes the root logger configuration and
    sets up the application log file.

    Creates a 'logs' directory at the project root if it does not exist,
    clears any pre-existing handlers to prevent duplication, and defines
    a standardized format for log entries.
    """

    project_root = get_project_root()
    log_dir = project_root / "logs"
    log_file = log_dir / "app.log"

    log_dir.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # FORCE CLEANUP: Remove existing handlers to prevent duplicate log entries
    if root_logger.handlers:
        root_logger.handlers.clear()

    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # FileHandler Configuration
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)


def create_folders_path() -> None:
    """
    Creates the default path configuration JSON file if it does not exist.

    Initializes the file with standard systemic paths for images, downloads,
    and SRT files formatted to hold recent inputs and the current output.
    """

    if not PATH_FILE_JSON.exists():
        default_paths = {
            "IMAGE_PATH": {
                "inputs": [str(Path.home() / "Pictures")],
                "output": str(Path.home() / "Pictures")
            },
            "DOWNLOAD_PATH": {
                "inputs": [str(Path.home() / "Downloads")],
                "output": str(Path.home() / "Downloads")
            },
            "SRT_PATH": {
                "inputs": [str(Path.home() / "Documents")],
                "output": str(Path.home() / "Documents")
            }
        }
        with open(PATH_FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(default_paths, f, indent=4)
    return None


def read_path(
    json_name: str,
    inner_key: str | None = None
) -> dict | list | str:
    """
    Reads and parses data from a specified project JSON configuration file.

    :param json_name: The target file identifier mapped in JSON_FILE_MAP.
    :param inner_key: Optional specific top-level key to extract from the JSON.
    :return: The complete parsed JSON object or the specific subset requested.
    """
    with open(JSON_FILE_MAP[json_name], "r", encoding="utf-8") as f:
        data = json.load(f)

    return data[inner_key] if inner_key is not None else data


def update_path(
    path_name: str,
    new_path: str,
    is_output: bool = False
) -> None:
    """
    Updates the JSON configuration file with a newly selected directory path.

    Handles separate structures for input history
    (rolling queue capped at 3 paths) and persistent single output directories.

    :param path_name: The media type identifier key (e.g., 'IMAGE_PATH').
    :param new_path: The directory path string to record.
    :param is_output: True if updating the output target,
    False if updating input history.
    """

    data = read_path(json_name="path_file")
    new_path = str(new_path)

    if os.path.exists(new_path):
        if is_output:
            data[path_name]["output"] = new_path

        else:
            target_list = data[path_name]["inputs"]

            if new_path not in target_list:
                # Maintain a maximum of 3 recent input paths
                # using a FIFO queue behavior
                if len(target_list) < 3:
                    target_list.append(new_path)
                else:
                    target_list.pop(0)
                    target_list.append(new_path)

        with open(PATH_FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)


def default_input_path_choice(default: str) -> str:
    """
    Prompts the user via CLI to select a directory
    from their recent input history.

    Provides an option to browse for a completely new path starting from the
    user's home directory.

    :param default: The media type key string to look up history for.
    :return: The selected directory path string.
    """
    path_name = default.replace("_", " ").title()

    clear_terminal()
    print("--- Choice Input Path ---")

    paths = read_path(json_name="path_file", inner_key=default)
    paths_list = [Choice(value=x, name=x) for x in paths["inputs"]]
    paths_list.append(Choice(value="Another", name="> Select another path:"))

    default_path = inquirer.select(
        message=f"Select a Default {path_name}:",
        choices=paths_list
    ).execute()

    path = (
        os.path.expanduser("~")
        if default_path == "Another"
        else default_path
    )
    return path


def default_output_path_choice(default: str) -> str:
    """
    Prompts the user via CLI to confirm the current
    output path or choose a new one.

    If a new directory is chosen, it automatically
    updates the system's JSON configuration.

    :param default: The media type key string to look up the output path for.
    :return: The validated target output directory path string.
    """
    path_name = default.replace("_", " ").title()

    clear_terminal()
    print("--- Choice Output Path ---")

    output_path = read_path(json_name="path_file", inner_key=default)
    output_path_choice = inquirer.select(
        message=f"Select the Output {path_name}:",
        choices=[
            Choice(
                value=f"{output_path['output']}",
                name=f"{output_path['output']}"
            ),
            Choice(value="Another", name="> Select another path:")
        ]
    ).execute()

    if output_path_choice == "Another":
        print("--- Choice Output Path ---")

        final_output_path = inquirer.filepath(
            message=f"Select the Output {path_name}:",
            default=str(os.path.expanduser("~")),
            only_directories=True
        ).execute()

        update_path(
            path_name=default,
            new_path=Path(final_output_path),
            is_output=True
        )
        return final_output_path
    else:
        update_path(
            path_name=default,
            new_path=Path(output_path_choice),
            is_output=True
        )
        return output_path_choice
