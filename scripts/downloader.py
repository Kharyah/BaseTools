import logging

from utils import print_divider
from pathlib import Path

logger = logging.getLogger(__name__)

silent_yt_logger = logging.getLogger("yt_dlp_silent")
silent_yt_logger.setLevel(logging.CRITICAL)


class DownloadLogger:
    def debug(self, msg):
        logger.debug(f"[yt-dlp-debug] {msg}")
        if msg.startswith("[download]"):
            return  # Safety exit for progressive bar logs

    def warning(self, msg):
        # Sends warnings directly to the app.log file
        logger.warning(f"[yt-dlp] {msg}")

    def error(self, msg):
        # Sends critical errors directly to the app.log file
        logger.error(f"[yt-dlp] {msg}")


def check_url(url: str) -> tuple[bool, bool]:
    """
    Validates if the URL is reachable and checks if it represents a playlist.

    :param url: The target URL to check.
    :return: A tuple containing (is_valid, is_playlist).
    """
    import yt_dlp

    ydl_opts = {
        "simulate": True,
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "logger": silent_yt_logger
    }

    # Print a checking status to the user
    print("[INFO] Checking URL status... Please wait.", end="\r", flush=True)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract metadata without downloading
            info = ydl.extract_info(url, download=False)

            # Clear the "Checking..." line in the console
            print(" " * 50, end="\r")

            if not info:
                return False, False

            # Check if the extracted entity is a playlist
            is_playlist = info.get("_type") == "playlist"
            return True, is_playlist

    except yt_dlp.utils.DownloadError as exc:
        print(" " * 50, end="\r")
        logger.warning(f"URL validation failed: {exc}")
        return False, False
    except Exception as exc:
        print(" " * 50, end="\r")
        logging.error(f"Error checking URL: {exc}")
        return False, False


def show_progress_percentage(d: dict) -> None:
    """
    Displays the current download progress percentage and video title.
    """
    if d.get("status") != "downloading":
        return

    # 1. Extract percentage string with a basic calculation fallback
    percent_str = d.get("_percent_str")
    if not percent_str:
        total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
        downloaded = d.get("downloaded_bytes", 0)
        percent_str = (
            f"{(downloaded / total) * 100:.1f}%" if total > 0 else "0.0%"
        )

    percent_str = percent_str.strip()

    # 2. Extract metadata
    info = d.get("info_dict", {})
    title = info.get("title", "Unknown Title")
    idx = info.get("playlist_index")
    total_entries = info.get("n_entries")

    # 3. Truncate title using slicing (safe for standard strings)
    if len(title) > 40:
        title = f"{title[:37]}..."

    # 4. Format string using f-strings based on playlist presence
    if idx is not None and total_entries is not None:
        prefix = f"[Video {idx}/{total_entries}]"
    else:
        prefix = "[Downloading]"

    output = f"{prefix} {title} -> {percent_str}"

    # 5. Flush terminal line using ljust to clear trailing remnants
    print(f"\r{output.ljust(100)}", end="", flush=True)


def get_yt_dlp_options(output_path: str, file_type: str) -> dict:
    """
    Generates the yt-dlp download configuration dictionary.

    :param output_path: Path directory where the media will be saved.
    :param file_type: The desired media format (e.g., 'WAV', 'MP3', 'MP4').
    """

    ydl_opts = {
        'outtmpl': str(output_path / "%(title)s [%(id)s].%(ext)s"),
        'logger': DownloadLogger(),
        'progress_hooks': [show_progress_percentage],
        'quiet': True,
        'no_warnings': True,
        'noprogress': True,
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


def media_exists(
    output_path: Path,
    video_id: str,
    file_type: str
) -> bool:
    """
    Checks whether a media file with the same video ID and
    format already exists.

    :param output_path: Directory where downloaded media files are stored.
    :param video_id: Unique identifier of the video source.
    :param file_type: Desired media format to check (e.g., MP3, WAV, MP4).
    :return: True if a matching media file exists, otherwise False.
    """

    expected_ext = file_type.lower()

    return any(
        video_id in file.name
        and file.suffix.lower() == f".{expected_ext}"
        for file in output_path.iterdir()
        if file.is_file()
    )


def download_media(url: str, output_path: str, file_type: str) -> bool:
    """
    Downloads the requested media using the fetched yt-dlp configuration.

    :param url: The target media URL.
    :param output_path: The directory path where the file will be saved.
    :param file_type: The desired media file format.
    """
    import yt_dlp

    output_path.mkdir(parents=True, exist_ok=True)

    try:
        ydl_opts = get_yt_dlp_options(output_path, file_type)

        print_divider()
        print("[INFO] Extracting metadata and initiating download...")
        print(f"[INFO] Target Format: {file_type.upper()} (Best Quality)")
        print(f"[INFO] Destination: {output_path}\n")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Checks if the file already exists
            if media_exists(output_path, info["id"], file_type):
                print_divider()
                print("[INFO] File already exists.")
                print_divider()
                return True

            ydl.download([url])

        print("\n[SUCCESS] Download completed successfully!")
        print_divider()
        return True

    except Exception as e:
        # Unexpected crashes are also saved to the log file
        logger.error(f"Download execution failed: {e}")
        print("\n[ERROR] Download failed. Check logs for details.")
        return False
