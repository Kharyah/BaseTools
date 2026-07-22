import logging

from pathlib import Path
from config.settings import read_path
from utils import format_divider

logger = logging.getLogger(__name__)

VALID_FORMATS: set[str] = {".mp4", ".mp3", ".wav"}

_whisper_model_cache = {
    "size": None,
    "instance": None
}


def check_audio_format(file_path: str) -> bool:
    """Checks if the file extension is supported."""
    path = Path(file_path)

    if not path.is_file():
        return False
    return path.suffix.lower() in VALID_FORMATS


def get_supported_whisper_languages() -> dict:
    """Returns a dictionary of all languages supported by the Whisper model."""
    from whisper.tokenizer import LANGUAGES
    return LANGUAGES


def get_supported_whisper_load_models() -> list:
    """Returns a list of all load models supported by the Whisper model."""
    from whisper import available_models
    return [model for model in available_models() if not model.endswith(".en")]


def _get_whisper_model(model_size: str):
    """
    Retrieves the Whisper model instance from cache,
    or loads it if it doesn't exist yet (Lazy Loading Pattern).
    """
    import stable_whisper
    global _whisper_model_cache

    if (
        _whisper_model_cache["size"] == model_size
        and _whisper_model_cache["instance"] is not None
    ):
        logger.info(
            f"Using cached Whisper model instance for size: '{model_size}'"
        )
        return _whisper_model_cache["instance"]

    print(format_divider())
    print(f"[INFO] Loading Whisper model '{model_size}' into memory...")
    print("[INFO] This might take a few seconds on the first run...")

    model = stable_whisper.load_model(model_size)
    _whisper_model_cache["size"] = model_size
    _whisper_model_cache["instance"] = model

    logger.info(
        f"Successfully loaded and cached Whisper model size: '{model_size}'"
    )
    return model


def generate_custom_split_srt(
    srt_mode: str,
    media_path: str,
    output_path: str,
    model_size: str = "base",
    language: str = "pt",
) -> None:
    """
    Transcribes and splits subtitles based on character and word limits
    using pathlib and a cached Whisper model.
    """
    media_path_obj = Path(media_path)
    model = _get_whisper_model(model_size)

    srt_config = read_path(json_name="srt_modes", inner_key=srt_mode)
    max_chars = srt_config["max_chars"]
    max_words = srt_config["max_words"]

    # If no output path is specified, default to replacing extension with .srt
    output_path_obj = Path(output_path)

    if output_path_obj.is_dir():
        final_output = (
            output_path_obj / f"{media_path_obj.stem}_{language}.srt"
        )
    else:
        final_output = output_path_obj

    # Checks if the file already exists
    if final_output.exists():
        print(format_divider())
        print("[INFO] File already exists.")
        print(format_divider())
        return True

    print(f"\n[INFO] Transcribing: {media_path_obj.name}")

    result = model.transcribe(
        str(media_path_obj),
        language=language,
        # Prevents hallucination loops by treating segments independently
        condition_on_previous_text=False,
        # Disables half-precision to ensure CPU compatibility and stability
        fp16=False
    )

    print(
        f"Splitting subtitles (Max words: {max_words},"
        f"Max chars: {max_chars})..."
    )
    final_output.parent.mkdir(parents=True, exist_ok=True)

    # Process transcription segments and export directly to SRT format
    try:
        (
            result
            .split_by_length(max_chars=max_chars, max_words=max_words)
            # highlight_color=None removes all HTML color tags
            # from the SRT output
            .to_srt_vtt(str(final_output), word_level=False)
        )
    except Exception as e:
        # Unexpected crashes are also saved to the log file
        logger.error(f"SRT generation execution failed: {e}")
        print("\n[ERROR] SRT Generation failed. Check logs for details.")

    logger.info("SRT Successfully Generated.")
    print(format_divider())
