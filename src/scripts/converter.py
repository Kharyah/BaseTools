from pathlib import Path

VALID_FORMATS = [".jpg", ".jpeg", ".png", ".webp"]

def check_format(file_path):
    path = Path(file_path)

    if path.suffix.lower() not in VALID_FORMATS:
        return False
    return True