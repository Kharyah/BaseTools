import json
from pathlib import Path

JSON_FILE = Path("data/folders_path.json")

def create_folders_path():
    global JSON_FILE

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