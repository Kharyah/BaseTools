import yt_dlp
import os
import logging

logger = logging.getLogger("Downloader")

class MyQuietLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

def check_url(url: str) -> bool:
    ydl_opts = {
        "simulate": True,
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "logger": MyQuietLogger(),
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=False)
            return True
            
    except Exception as exc:
        logging.error(f"Error checking URL: {exc}")
        return False

logging.basicConfig(
    filename='app.log',
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DownloadLogger:
    """Redirects yt-dlp internal messages to Python's logging system instead of the terminal."""
    def debug(self, msg):
        # The progressive download bar outputs via debug. 
        # We pass (do nothing) so it doesn't flood our log file.
        pass

    def warning(self, msg):
        # Sends warnings directly to the app.log file
        logging.warning(f"[yt-dlp WARNING] {msg}")

    def error(self, msg):
        # Sends critical errors directly to the app.log file
        logging.error(f"[yt-dlp ERROR] {msg}")


def get_yt_dlp_options(output_path: str, file_type: str) -> dict:
    outtmpl_path = os.path.join(output_path, '%(title)s.%(ext)s')

    ydl_opts = {
        'outtmpl': outtmpl_path,
        'remote_components': 'ejs:github',
        'quiet': False,             # Keep False so the default download progress bar still shows up
        'no_warnings': True,        # Prevents yt-dlp from printing warnings to stderr/terminal
        'logger': DownloadLogger(), # Binds our custom logger to intercept messages
    }

    if file_type.lower() == 'mp4':
        ydl_opts['format'] = 'bestvideo+bestaudio/best'
        ydl_opts['merge_output_format'] = 'mp4'
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
    os.makedirs(output_path, exist_ok=True)
    
    try:
        ydl_opts = get_yt_dlp_options(output_path, file_type)
        
        print(f"\n[INFO] Extracting metadata and initiating download...")
        print(f"[INFO] Target Format: {file_type.upper()} (Best Quality)")
        print(f"[INFO] Destination: {output_path}\n")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        print(f"\n[SUCCESS] Download completed successfully!")
        return True
        
    except Exception as e:
        # Unexpected crashes are also saved to the log file
        logging.error(f"Critical failure in download_media: {e}", exc_info=True)
        print(f"\n[ERROR] Download failed. Check 'app.log' for details.")
        return False