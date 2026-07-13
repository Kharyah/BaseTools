import logging

from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from utils import clear_terminal
from interface.menus import media_downloader, image_converter, srt_generator

from config.settings import (
    create_folders_path,
    create_srt_modes_path,
    start_logging
)

logger = logging.getLogger(__name__)

CALL_FUNCTIONS_MAIN = {
    "Media Downloader": media_downloader,
    "Image Converter": image_converter,
    "Srt Generator": srt_generator
}
MENU_CHOICES = (
    Choice(value="Media Downloader", name="  > Download Media with yt-dlp."),
    Choice(value="Image Converter", name="  > Convert Images."),
    Choice(value="Srt Generator", name="  > Generate srt files."),
    Choice(value="Exit", name="! Exit.")
)


def main() -> None:
    while True:
        clear_terminal()
        user_choice = inquirer.select(
            message="Select Tool:",
            choices=MENU_CHOICES,
            default="Media Downloader"
        ).execute()

        if user_choice in CALL_FUNCTIONS_MAIN.keys():
            CALL_FUNCTIONS_MAIN[user_choice]()

        else:
            print("Closing...")
            break


if __name__ == "__main__":
    start_logging()
    create_folders_path()
    create_srt_modes_path()

    logger.info("Application context initiated successfully.")
    main()
