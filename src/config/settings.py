import json
import logging
import os
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
    
    # FORCE CLEANUP: Removes any ghost handlers created by rogue imports
    if root_logger.handlers:
        root_logger.handlers.clear()
        
    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)

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
        dates = json.load(f)

    return dates[path_name] if path_name != None else dates

def update_path(path_name, new_path):
    path_append = read_path()    
    new_path = str(new_path)

    if new_path not in path_append[path_name]:
        if len(path_append[path_name]) <= 3:
            path_append[path_name].append(new_path)
        else:
            path_append[path_name][0] = new_path

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(path_append, f, indent=4)