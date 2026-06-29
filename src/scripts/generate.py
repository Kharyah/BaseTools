from pathlib import Path

VALID_FORMATS = [".mp4", ".mp3", ".wav"]

def check_audio_format(file_path):
    path = Path(file_path)

    if path.suffix.lower() not in VALID_FORMATS:
        return False
    return True