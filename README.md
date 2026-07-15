# 🛠️ BaseTools

A powerful and interactive Command Line Interface (CLI) application built in Python to centralize utility scripts that I use in my daily life.

---

## 🚀 Key Features

* **Media Downloader:** Fast audio/video downloading from YouTube and other platforms (powered by `yt-dlp`).
* **Image Converter:** Seamless format conversion (PNG, JPG, WEBP, BMP, etc.) using `Pillow`.
* **SRT Subtitle Generator:** Automatic transcription and translation with smart segmentation (powered by `stable-whisper`).

---

## 📦 How to Use (No Python Required)

The easiest way to run **BaseTools** is by downloading the pre-compiled version for Windows:

1. Go to the [Releases](https://github.com/Kharyah/BaseTools/releases) page.
2. Download the latest **`basetools-windows-vX.Y.Z.zip`** file.
3. Extract the ZIP archive anywhere on your computer.
4. **Choose your preferred way to run:**
   * **Easy Way:** Double-click the `basetools.bat` file. A terminal window will open, launching the application automatically.
   * **Terminal Way (Global):** If you want to type `basetools` from any terminal directory, move the `basetools.exe` to a permanent folder and add that folder to your system's **`PATH`** environment variable.

### ⚠️ External Requirements
Since this tool relies on command-line utilities for heavy media processing, make sure you have these installed on your system:
* **FFmpeg** (Required for processing audio and downloads)
* **Deno** or **Node.js** (Required by `yt-dlp` to parse streaming URLs)
