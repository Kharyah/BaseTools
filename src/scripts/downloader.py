import yt_dlp
import logging

from utils import format_divider

logger = logging.getLogger(__name__)

silent_yt_logger = logging.getLogger("yt_dlp_silent")
silent_yt_logger.setLevel(logging.CRITICAL)


def check_url(url: str) -> bool:
    """Checks if the URL is valid and reachable by yt-dlp."""
    ydl_opts = {
        "simulate": True,
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "logger": silent_yt_logger
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=False)
            return True
    except yt_dlp.utils.DownloadError as exc:
        logger.warning(f"URL validation failed: {exc}")
        return False
    except Exception as exc:
        logging.error(f"Error checking URL: {exc}")
        return False


class DownloadLogger:
    """
    Redirects yt-dlp internal messages to Python's logging system.
    """
    def debug(self, msg):
        # The progressive download bar outputs via debug.
        # We pass (do nothing) so it doesn't flood our log file.
        pass

    def warning(self, msg):
        # Sends warnings directly to the app.log file
        logging.warning(f"[yt-dlp] {msg}")

    def error(self, msg):
        # Sends critical errors directly to the app.log file
        logging.error(f"[yt-dlp] {msg}")


def show_progress_percentage(d: dict) -> None:
    """Calculates and displays only the download percentage in the CLI."""
    if d.get("status") == "downloading":
        print(
            f"Downloading Progress: {d.get('_percent_srt', '0.0%')}", end="\r"
        )


def get_yt_dlp_options(output_path: str, file_type: str) -> dict:
    """
    Generates the yt-dlp download configuration dictionary.

    :param output_path: Path directory where the media will be saved.
    :param file_type: The desired media format (e.g., 'WAV', 'MP3', 'MP4').
    """

    ydl_opts = {
        'outtmpl': str(output_path / "%(title)s.%(ext)s"),
        'logger': DownloadLogger(),
        'progress_hooks': [show_progress_percentage],
    }

    if file_type.lower() == 'mp4':
        ydl_opts["format"] = (
            "bestvideo[ext=mp4]+bestaudio[ext=m4a]/"
            "best[ext=mp4]/"
            "best"
        )
    elif file_type.lower() in ['mp3', 'wav']:
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': file_type.lower(),
            'preferredquality': '0',
        }]
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

    return ydl_opts


def download_media(url: str, output_path: str, file_type: str) -> bool:
    """
    Downloads the requested media using the fetched yt-dlp configuration.

    :param url: The target media URL.
    :param output_path: The directory path where the file will be saved.
    :param file_type: The desired media file format.
    """
    output_path.mkdir(parents=True, exist_ok=True)

    try:
        ydl_opts = get_yt_dlp_options(output_path, file_type)

        print(format_divider())
        print("[INFO] Extracting metadata and initiating download...")
        print(f"[INFO] Target Format: {file_type.upper()} (Best Quality)")
        print(f"[INFO] Destination: {output_path}\n")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        logger.info("Media downloaded successfully.")
        print("\n[SUCCESS] Download completed successfully!")
        print(format_divider())
        return True

    except Exception as e:
        # Unexpected crashes are also saved to the log file
        logger.error(f"Download execution failed: {e}")
        print("\n[ERROR] Download failed. Check logs for details.")
        return False
