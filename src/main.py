from config.settings import start_logging

start_logging()

import os
import sys
import logging

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from pathlib import Path

from scripts.converter import check_image_format, convert_image_format
from scripts.generate import check_audio_format, generate_custom_split_srt
from scripts.downloader import check_url, download_media
from config.depedences import check_js_runtime

from config.settings import create_folders_path, default_input_path_choice, default_output_path_choice, update_path
from utils import clear_terminal, prompt_to_continue, create_choice_list

def path_media_choice(path, media_type):
    print("--- Choice Path ---")
    current_path_directory = path
    function_name = media_type.replace("_", " ").title()
    
    functions_format_check_call = {
        "Image Path": check_image_format,
        "Srt Path": check_audio_format
    }

    check_media_format = functions_format_check_call[function_name]

    while True:
        file_path = inquirer.filepath(
            message=f"Choice the {function_name} File!",
            default=str(current_path_directory),
            validate=check_media_format
        ).execute()

        if os.path.isfile(file_path):
            update_path(path_name=media_type, new_path=Path(file_path).parent)
            return file_path

        elif os.path.isdir(file_path):
            current_path_directory = file_path
            clear_terminal()

def media_downloader():
    if not check_js_runtime:
        return None

    output_path = default_output_path_choice("DOWNLOAD_PATH")
    checked_url = None

    while True:
        clear_terminal()
        print("--- Media Downloader ---")
        url = str(input("Enter a URL: "))
        
        if check_url(url):
            checked_url = url
            break
        else:
            print("Error: Invalid URL or not supported by yt-dlp. Try again.")
            
            prompt_to_continue()
            continue

    file_format_list = create_choice_list(["mp3", "mp4", "wav"])
    file_format_list.append(Choice(value="Return", name="Return"))

    file_format = inquirer.select(
        message="Choice The File Format (It will be the best quality possible):",
        choices=file_format_list
    ).execute()
    
    if file_format == "Return":
        clear_terminal()
    else:
        download_media(url=checked_url, output_path=output_path, file_type=file_format)
        prompt_to_continue()

def image_converter():
    print("--- Image Converter ---")
    output_path = default_output_path_choice("IMAGE_PATH")
    file_path = path_media_choice(path=default_input_path_choice("IMAGE_PATH"), media_type="IMAGE_PATH")

    file_format_list = create_choice_list(["JPEG", "JPG", "PNG", "WEBP", "BMP", "GIF", "TIFF", "ICO"])
    file_format_list.append(Choice(value="Return", name="Return"))

    file_format = inquirer.select(
        message="Choice The File Format:",
        choices=file_format_list
    ).execute()

    if file_format == "Return":
        clear_terminal()
    else:
        convert_image_format(input_path=file_path, output_dir=output_path, target_format=file_format)
        prompt_to_continue()

def srt_generator():
    print("--- SRT Generator ---")
    output_path = default_output_path_choice("SRT_PATH")
    file_path = path_media_choice(path=default_input_path_choice("SRT_PATH"), media_type="SRT_PATH")

    srt_mode = create_choice_list(["Exemple1", "Exemple2"]) # TODO - add whisper modes
    srt_mode.append(Choice(value="Return", name="Return"))

    if srt_mode == "Return":
        clear_terminal()
    else:
        # TODO - Create a error check.
        # TODO - Create default max_words and max_chars choices.
        # TODO - Create default mode choices.
        # TODO - Create language choice.

        generate_custom_split_srt(
            media_path=file_path,
            output_path=output_path,
            model_size="base",
            language="pt",
        )

        prompt_to_continue()
        
def main():
    clear_terminal()

    call_functions = {
        "Media Downloader": media_downloader,
        "Image Converter": image_converter,
        "Srt Generator": srt_generator
    }

    choices_values = ["Media Downloader", "Image Converter", "Srt Generator", "Exit"]
    choices_texts = ["1. Downloader Media with yt-dlp.", "2. Converter Images.", "3. Generator srt files.", "4. Exit"]
    choices_list = [Choice(value=x, name=y) for x, y in zip(choices_values, choices_texts)]

    while True:
        user_choice = inquirer.select(
            message="Select Tool!",
            choices=choices_list,
            default="Media Downloader"
        ).execute()

        if user_choice in call_functions.keys():
            call_functions[user_choice]()

        else:
            print("Closing...")
            break

        clear_terminal()

if __name__ == "__main__":
    clear_terminal()
    create_folders_path() # Creating/checking the json file

    main()