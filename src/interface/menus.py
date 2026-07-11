import os
import logging

from pathlib import Path
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from scripts.converter import check_image_format, convert_image_format
from scripts.downloader import check_url, download_media
from config.depedences import check_js_runtime

from utils import (
    clear_terminal,
    prompt_to_continue,
    create_choice_list,
    format_header,
    format_divider,
    path_name_replace
)


from scripts.generation import (
    check_audio_format,
    generate_custom_split_srt,
    get_supported_whisper_languages
)

from config.settings import (
    default_input_path_choice,
    default_output_path_choice,
    update_path,
    read_path
)

logger = logging.getLogger(__name__)

FUNCTIONS_FORMAT_CHECK_CALL = {
    "IMAGE_PATH": check_image_format,
    "SRT_PATH": check_audio_format
}


def path_media_choice(path: str, media_type: str) -> str:
    logging.info("Started Path Media Select.")

    print(format_header("Select Path"))

    current_path_directory = path
    check_media_format = FUNCTIONS_FORMAT_CHECK_CALL[media_type]

    while True:
        file_path = inquirer.filepath(
            message=f"Select the {path_name_replace(media_type)} File:",
            default=str(current_path_directory),
            validate=check_media_format
        ).execute()

        if os.path.isfile(file_path):
            update_path(path_name=media_type, new_path=Path(file_path).parent)
            return file_path

        # If a directory is selected, update the current
        # path to allow nested browsing.
        elif os.path.isdir(file_path):
            current_path_directory = file_path
            clear_terminal()


def media_downloader() -> None:
    logging.info("Started Media Downloader Logic.")

    # Guard clause: Ensure JavaScript runtime is available
    # before invoking yt-dlp.
    if not check_js_runtime():
        return None

    output_path = default_output_path_choice("DOWNLOAD_PATH")
    checked_url = None

    while True:
        clear_terminal()
        print(format_header("Media Downloader"))

        url = input("Enter a URL: ")

        if check_url(url):
            checked_url = url
            break
        else:
            print("Error: Invalid URL or not supported by yt-dlp. Try again.")
            print(format_divider())

            prompt_to_continue()
            continue

    file_format_list = create_choice_list(["mp3", "mp4", "wav"])
    file_format_list.append(Choice(value="Return", name="! Return"))

    file_format = inquirer.select(
        message="Select The File Format (It'll be the best quality possible):",
        choices=file_format_list
    ).execute()

    if file_format == "Return":
        clear_terminal()
    else:
        download_media(
            url=checked_url,
            output_path=output_path,
            file_type=file_format
        )
        prompt_to_continue()


def image_converter() -> None:
    logging.info("Started Image Converter Logic.")

    print(format_header("Image Converter"))
    output_path = default_output_path_choice("IMAGE_PATH")

    # Map media types to their respective validator functions
    file_path = path_media_choice(
        path=default_input_path_choice("IMAGE_PATH"),
        media_type="IMAGE_PATH"
    )

    file_format_list = create_choice_list(
        ["JPEG", "JPG", "PNG", "WEBP", "BMP", "GIF", "TIFF", "ICO"]
    )
    file_format_list.append(Choice(value="Return", name="! Return."))

    file_format = inquirer.select(
        message="Select The File Format:",
        choices=file_format_list
    ).execute()

    if file_format == "Return":
        clear_terminal()
    else:
        convert_image_format(
            input_path=file_path,
            output_dir=output_path,
            target_format=file_format
        )
        prompt_to_continue()


def srt_generator() -> None:
    logging.info("Started Srt Generator Logic.")

    print(format_header("SRT Generator"))
    output_path = default_output_path_choice("SRT_PATH")

    # Map media types to their respective validator functions
    file_path = path_media_choice(
        path=default_input_path_choice("SRT_PATH"),
        media_type="SRT_PATH"
    )

    srt_all_modes = read_path(json_name="srt_modes")
    srt_mode = create_choice_list(list(srt_all_modes.keys()))
    srt_mode.append(Choice(value="Return", name="! Return."))

    mode_choice = inquirer.select(
        message="Select the SRT mode:",
        choices=srt_mode,
    ).execute()

    if mode_choice == "Return":
        clear_terminal()
    else:
        whisper_languages = get_supported_whisper_languages().items()

        # Sort supported languages alphabetically by name
        # for better UX in the selection menu.
        lg_choice = sorted([
                Choice(value=code, name=f"  > {name.title()}")
                for code, name in whisper_languages
            ], key=lambda x: x.name
        )

        language_choice = inquirer.select(
            message="Select the language:",
            choices=lg_choice
        ).execute()

        generate_custom_split_srt(
            srt_mode=mode_choice,
            media_path=file_path,
            output_path=output_path,
            model_size="base",
            language=language_choice,
        )

        prompt_to_continue()
