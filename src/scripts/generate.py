import os

from pathlib import Path
from typing import Optional
#from whisper.utils import get_writer

VALID_FORMATS = [".mp4", ".mp3", ".wav"]

def check_audio_format(file_path):
    path = Path(file_path)

    if path.suffix.lower() not in VALID_FORMATS:
        return False
    return True

def generate_custom_split_srt(
    media_path: str, 
    output_path: Optional[str] = None,
    model_size: str = "base", 
    language: str = "pt", 
    max_words: int = 3,      # Maximum words per caption line
    max_chars: int = 15      # Maximum characters per caption line
):
    """
    Uses stable-whisper to transcribe and strictly control 
    the word/character count per subtitle line. Saves output to target path.
    """
    import stable_whisper
    
    print(f"Loading Stable-Whisper model '{model_size}'...")
    model = stable_whisper.load_model(model_size)
    
    print(f"Transcribing: {media_path}...")
    result = model.transcribe(
        media_path, 
        language=language,
        condition_on_previous_text=False,
        fp16=False
    )
    
    # If no output path is specified, default to replacing extension with .srt
    if output_path is None:
        output_path = os.path.splitext(media_path)[0] + ".srt"
        
    # IF the output path is an existing directory, we combine it with the original file's name
    elif os.path.isdir(output_path):
        # Extract just the file name without folder path (e.g., "video_sample.mp4")
        base_name = os.path.basename(media_path)
        # Change extension to .srt (e.g., "video_sample.srt")
        srt_name = os.path.splitext(base_name)[0] + ".srt"
        # Combine the directory with the new srt filename
        output_path = os.path.join(output_path, srt_name)
        
    print(f"Splitting subtitles (Max words: {max_words}, Max chars: {max_chars})...")
    
    (
        result
        .split_by_length(max_chars=max_chars, max_words=max_words)
        # highlight_color=None removes all HTML color tags from the SRT output
        .to_srt_vtt(output_path, highlight_color=None)
    )
    
    print(35 * "--")
    print(f"Success! Custom SRT saved as: {output_path}")
    print(35 * "--")