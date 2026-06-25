import yt_dlp

def check_url(url: str):
    ydl_opts = {
        "simulate": True,
        "quiet": True,
        "extract_flat": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.extract_info(url, download=False)
            return True
        except Exception:
            return False