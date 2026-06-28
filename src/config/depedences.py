import shutil
import sys

def check_js_runtime():
    runtime_deno = shutil.which("deno")
    runtime_node = shutil.which("node")
    
    if runtime_deno or runtime_node:
        return True
    exibir_erro_e_sair()

def display_error():
    print("\n" + "="*70)
    print("[CRITICAL ERROR] JavaScript Runtime Not Found!")
    print("="*70)
    print("The 'yt-dlp' package requires Deno or Node.js installed on your system")
    print("to decrypt and download YouTube videos properly.")
    print("\nHow to resolve this:")
    print("  1. Install Deno (Recommended): https://deno.land")
    print("  2. Or install Node.js: https://nodejs.org")
    print("\nNote: After installation, restart your terminal or IDE.")
    print("="*70 + "\n")

    input("Press enter to continue...")