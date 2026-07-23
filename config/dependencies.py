import logging

from utils import print_divider

logger = logging.getLogger(__name__)


def check_js_runtime() -> bool:
    """Checks if a valid JavaScript runtime is installed in the environment."""
    import shutil

    # Look for Deno or Node.js executables in the system's PATH
    runtime_deno = shutil.which("deno")
    runtime_node = shutil.which("node")

    # yt-dlp requires a JS runtime to execute deciphering scripts for YT URLs
    if runtime_deno or runtime_node:
        if not runtime_deno:
            logger.warning(
                "Node.js detected instead of Deno. Deno is the recommended"
                "runtime for yt-dlp."
            )

        return True

    display_error()
    return False  # Explicitly return False to block execution in the main loop


def display_error() -> None:
    """
    Displays a CLI error message with instructions to install a JS runtime.
    """
    print("\n" + print_divider(char="=", width=70))
    print("[CRITICAL ERROR] JavaScript Runtime Not Found!")
    print("="*70)
    print("The 'yt-dlp' requires Deno or Node.js installed on your system")
    print("to decrypt and download YouTube videos properly.")
    print("\nHow to resolve this:")
    print("  1. Install Deno (Recommended): https://deno.land")
    print("  2. Or install Node.js: https://nodejs.org")
    print("\nNote: After installation, restart your terminal or IDE.")
    print(print_divider(char="=", width=70) + "\n")

    input("Press enter to continue...")
