import json
import logging
import os

from pathlib import Path
from utils import clear_terminal

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from pathlib import Path

JSON_FILE = Path("data/folders_path.json")

def get_project_root(anchor: str = "requirements.txt") -> Path:
    """Finds the project root directory by looking for an anchor file."""
    current_path = Path(__file__).resolve()
    for parent in [current_path] + list(current_path.parents):
        if (parent / anchor).exists():
            return parent
    return current_path.parent

def start_logging():
    project_root = get_project_root()
    log_dir = project_root / "logs"
    log_file = log_dir / "app.log"
    
    log_dir.mkdir(parents=True, exist_ok=True)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # FORCE CLEANUP: Remove handlers existentes para evitar duplicidade
    if root_logger.handlers:
        root_logger.handlers.clear()
        
    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configura APENAS o FileHandler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    
    root_logger.addHandler(file_handler)

def create_folders_path():
    if not JSON_FILE.exists():
        default_paths = {
            "IMAGE_PATH": [
                str(Path.home() / "Pictures"),
            ],
            "DOWNLOAD_PATH": [
                str(Path.home() / "Downloads"),
            ],
            "STR_PATH": [
                str(Path.home() / "Documents")
            ]
        }

        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(default_paths, f, indent=4)
    return None

def read_path(path_name: str = None):
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return data[path_name] if path_name is not None else data

def update_path(path_name: str, new_path: str, is_output: bool = False):
    data = read_path()
    new_path = str(new_path)
    
    if os.path.exists(new_path):
        if is_output:
            data[path_name]["output"] = new_path

        else:
            target_list = data[path_name]["inputs"]
            
            if new_path not in target_list:
                if len(target_list) < 3:
                    target_list.append(new_path)
                else:
                    target_list.pop(0)
                    target_list.append(new_path)
                    
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

def default_input_path_choice(default: str):
    path_name = default.replace("_", " ").title()

    clear_terminal()
    print("--- Choice Input Path ---")

    paths = read_path(default)
    paths_list = [Choice(value=x, name=x) for x in paths["inputs"]]
    paths_list.append(Choice(value="Another", name="> Choice another path."))
 
    default_path = inquirer.select(
        message=f"Choice a Default {path_name}:",
        choices=paths_list
    ).execute()

    path = os.path.expanduser("~") if default_path == "Another" else default_path
    return path

def default_output_path_choice(default: str):
    path_name = default.replace("_", " ").title()

    clear_terminal()
    print("--- Choice Output Path ---")

    output_path = read_path(default)
    output_path_choice = inquirer.select(
        message=f"Choice the Output {path_name}:",
        choices=[
            Choice(value=f"{output_path["output"]}", name=f"{output_path["output"]}"),
            Choice(value="Another", name="> Choice another path.")
        ]
    ).execute()

    if output_path_choice == "Another":
        print("--- Choice Output Path ---")

        final_output_path = inquirer.filepath(
            message=f"Choice the Output {path_name}:",
            default=str(os.path.expanduser("~")),
            only_directories=True
        ).execute()

        update_path(path_name=default, new_path=Path(final_output_path), is_output=True)
        return final_output_path
    else:
        update_path(path_name=default, new_path=Path(output_path_choice), is_output=True)
        return output_path_choice