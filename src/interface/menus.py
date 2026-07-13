import logging

from pathlib import Path
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from scripts.converter import check_image_format, convert_image_format
from scripts.downloader import check_url, download_media
from config.dependencies import check_js_runtime

from utils import (
    clear_terminal,
    prompt_to_continue,
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


def path_media_choice(initial_path: str, media_type: str) -> str:
    logger.info("Started Path Media Select.")
    print(format_header("Select Path"))

    current_path_directory = initial_path
    check_media_format = FUNCTIONS_FORMAT_CHECK_CALL[media_type]

    while True:
        file_path_str = inquirer.filepath(
            message=f"Select the {path_name_replace(media_type)} File:",
            default=str(current_path_directory),
            validate=check_media_format
        ).execute()

        file_path = Path(file_path_str)

        if file_path.is_file():
            update_path(path_name=media_type, new_path=file_path.parent)
            return file_path

        elif file_path.is_dir():
            current_path_directory = file_path
            clear_terminal()


def media_downloader() -> None:
    logger.info("Started Media Downloader Logic.")

    if not check_js_runtime():
        return

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

            if not prompt_to_continue():
                return

    choices = [Choice(value=x, name=f"  > {x}") for x in ["mp3", "mp4", "wav"]]
    choices.append(Choice(value="Return", name="! Return"))

    file_format = inquirer.select(
        message="Select The File Format (It'll be the best quality possible):",
        choices=choices
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
    logger.info("Started Image Converter Logic.")
    print(format_header("Image Converter"))

    output_path = default_output_path_choice("IMAGE_PATH")
    input_path_base = default_input_path_choice("IMAGE_PATH")

    file_path = path_media_choice(
        initial_path=input_path_base,
        media_type="IMAGE_PATH"
    )

    formats = ["JPEG", "JPG", "PNG", "WEBP", "BMP", "GIF", "TIFF", "ICO"]
    choices = [Choice(value=x, name=f"  > {x}") for x in formats]
    choices.append(Choice(value="Return", name="! Return."))

    file_format = inquirer.select(
        message="Select The File Format:",
        choices=choices
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
    logger.info("Started Srt Generator Logic.")
    print(format_header("SRT Generator"))

    output_path = default_output_path_choice("SRT_PATH")
    input_path_base = default_input_path_choice("SRT_PATH")

    file_path = path_media_choice(
        initial_path=input_path_base,
        media_type="SRT_PATH"
    )

    modes = list(read_path(json_name="srt_modes"))
    choices = [Choice(value=x, name=f"  > {x}") for x in modes.keys()]
    choices.append(Choice(value="Return", name="! Return."))

    mode_choice = inquirer.select(
        message="Select the SRT mode:",
        choices=choices,
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
