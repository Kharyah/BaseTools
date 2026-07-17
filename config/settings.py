import logging

from utils import (
    clear_terminal,
    format_header,
    path_name_replace,
    get_app_data_dir
)

logger = logging.getLogger(__name__)

APP_DATA_DIR = get_app_data_dir()
PATH_FILE_JSON = APP_DATA_DIR / "data" / "folders_path.json"
SRT_MODES_JSON = APP_DATA_DIR / "data" / "srt_modes.json"

JSON_FILE_MAP = {
    "path_file": PATH_FILE_JSON,
    "srt_modes": SRT_MODES_JSON
}


def start_logging() -> None:
    """
    Initializes the root logger with two separate file handlers:
    - app.log: Captures all operational info (INFO and above).
    - errors.log: Captures only anomalies and system failures (WARNING+).
    """
    from logging.handlers import RotatingFileHandler

    log_dir = APP_DATA_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    general_log_file = log_dir / "app.log"
    error_log_file = log_dir / "errors.log"

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    if root_logger.handlers:
        root_logger.handlers.clear()

    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # General handler (Overwritten at every execution)
    general_handler = logging.FileHandler(
        general_log_file, mode="w", encoding="utf-8"
    )
    general_handler.setLevel(logging.INFO)
    general_handler.setFormatter(formatter)

    # Alert/Error Handler (Protected against infinite growth)
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=2 * 1024 * 1024,
        backupCount=2,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.WARNING)
    error_handler.setFormatter(formatter)

    # Binds both handlers to the main system logger
    root_logger.addHandler(general_handler)
    root_logger.addHandler(error_handler)


def create_folders_path() -> None:
    """
    Creates the default path configuration JSON file if it does not exist.
    """
    import json
    from pathlib import Path

    PATH_FILE_JSON.parent.mkdir(parents=True, exist_ok=True)

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

    logger.info("Folder_path.json Created sucessful.")


def create_srt_modes_path() -> None:
    """Creates default SRT mode profiles."""
    import json

    SRT_MODES_JSON.parent.mkdir(parents=True, exist_ok=True)

    if not SRT_MODES_JSON.exists():
        srt_modes = {
            "netflix": {
                "max_chars": 42,
                "max_words": 14
            },
            "youtube": {
                "max_chars": 36,
                "max_words": 10
            },
            "vertical_shorts": {
                "max_chars": 20,
                "max_words": 3
            },
            "vertical_shorts_harder": {
                "max_chars": 15,
                "max_words": 2
            }
        }

        with open(SRT_MODES_JSON, "w", encoding="utf-8") as f:
            json.dump(srt_modes, f, indent=4)

    logger.info("Srt_modes.json Created sucessful.")


def read_path(
    json_name: str,
    inner_key: str | None = None
) -> dict | list | str:
    import json

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
    import json
    from collections import deque

    data = read_path(json_name="path_file")
    new_path_str = str(new_path)

    if new_path.exists():
        has_changes = False

        if is_output:
            if data[path_name]["output"] != new_path_str:
                data[path_name]["output"] = new_path_str
                has_changes = True

                logger.info(f"{new_path_str} added in {path_name} output.")

        else:
            inputs_list = data[path_name].setdefault("inputs", [])

            if new_path_str not in inputs_list:
                queue = deque(inputs_list, maxlen=3)
                queue.append(new_path_str)

                data[path_name]["inputs"] = list(queue)
                has_changes = True

                logger.info(f"{new_path_str} added in {path_name} inputs.")

        if has_changes:
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
    from pathlib import Path
    from InquirerPy import inquirer
    from InquirerPy.base.control import Choice

    clear_terminal()
    print(format_header("Select Input Path"))

    paths = read_path(json_name="path_file", inner_key=default)
    choices = [Choice(value=x, name=f"  > {x}") for x in paths["inputs"]]
    choices.append(Choice(value="Another", name="! Select another path."))

    selected = inquirer.select(
        message=f"Select a Default {path_name_replace(default)}:",
        choices=choices
    ).execute()

    return Path.home() if selected == "Another" else Path(selected)


def default_output_path_choice(default: str) -> str:
    """
    Prompts the user via CLI to confirm the current
    output path or choose a new one.

    If a new directory is chosen, it automatically
    updates the system's JSON configuration.

    :param default: The media type key string to look up the output path for.
    :return: The validated target output directory path string.
    """
    from pathlib import Path
    from InquirerPy import inquirer
    from InquirerPy.base.control import Choice

    clear_terminal()
    print(format_header("Select Output Path"))

    output_path_data = read_path(json_name="path_file", inner_key=default)
    current_output = output_path_data["output"]

    selected = inquirer.select(
        message=f"Select the Output {path_name_replace(default)}:",
        choices=[
            Choice(
                value=f"{current_output}",
                name=f"  > {current_output}"
            ),
            Choice(value="Another", name="! Select another path.")
        ]
    ).execute()

    if selected == "Another":
        print(format_header("Select Output Path"))

        final_output = inquirer.filepath(
            message=f"Select the Output {path_name_replace(default)}:",
            default=str(Path.home()),
            only_directories=True
        ).execute()

        final_path = Path(final_output)
        update_path(path_name=default, new_path=final_path, is_output=True)
        return final_path

    final_path = Path(selected)
    update_path(path_name=default, new_path=final_path, is_output=True)
    return final_path
