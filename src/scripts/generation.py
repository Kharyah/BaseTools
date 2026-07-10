import os

from pathlib import Path
from typing import Optional
from config.settings import read_path
from utils import format_divider

import stable_whisper

VALID_FORMATS = [".mp4", ".mp3", ".wav"]


def check_audio_format(file_path: str) -> bool:
    """Checks if the file extension is supported."""
    path = Path(file_path)

    if path.suffix.lower() not in VALID_FORMATS:
        return False
    return True


def get_supported_whisper_languages() -> dict:
    """
    Returns a dictionary of all languages supported by the underlying
    Whisper model used by stable-ts, where keys are language codes (e.g., 'pt')
    and values are the full names (e.g., 'portuguese').
    """
    # Inline import to avoid overhead if this function is not called
    from whisper.tokenizer import LANGUAGES

    # stable-ts re-exports whisper variables, including the LANGUAGES dict
    return LANGUAGES


def generate_custom_split_srt(
    srt_mode: str,
    media_path: str,
    output_path: Optional[str] = None,
    model_size: str = "base",
    language: str = "pt",
) -> None:
    """
    Uses stable-whisper to transcribe and strictly control
    the word/character count per subtitle line. Saves output to target path.
    """

    model = stable_whisper.load_model(model_size)
    srt_all_modes = read_path(json_name="srt_modes", inner_key=srt_mode)
    max_chars = srt_all_modes["max_chars"]
    max_words = srt_all_modes["max_words"]

    print(format_divider())
    print(f"Loading Stable-Whisper model '{model_size}'...")

    print(f"Transcribing: {media_path}...")
    result = model.transcribe(
        media_path,
        language=language,
        # Prevents hallucination loops by treating segments independently
        condition_on_previous_text=False,
        # Disables half-precision to ensure CPU compatibility and stability
        fp16=False
    )

    # If no output path is specified, default to replacing extension with .srt
    if output_path is None:
        output_path = os.path.splitext(media_path)[0] + ".srt"

    # IF the output path is an existing directory,
    # we combine it with the original file's name
    elif os.path.isdir(output_path):
        # Extract just the file name without folder path
        # (e.g., "video_sample.mp4")
        base_name = os.path.basename(media_path)
        # Change extension to .srt (e.g., "video_sample.srt")
        srt_name = os.path.splitext(base_name)[0] + ".srt"
        # Combine the directory with the new srt filename
        output_path = os.path.join(output_path, srt_name)

    print(
        f"Splitting subtitles (Max words: {max_words},"
        f"Max chars: {max_chars})..."
    )

    # Process transcription segments and export directly to SRT format
    (
        result
        .split_by_length(max_chars=max_chars, max_words=max_words)
        # highlight_color=None removes all HTML color tags from the SRT output
        .to_srt_vtt(output_path, word_level=False)
    )

    print(format_divider())
    print(f"Success! Custom SRT saved as: {output_path}")
    print(format_divider())
