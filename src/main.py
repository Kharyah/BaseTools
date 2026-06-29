from config.settings import start_logging

start_logging()

import os
import sys
import logging

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from pathlib import Path

from scripts.converter import check_image_format
from scripts.generate import check_audio_format
from scripts.downloader import check_url, download_media
from config.depedences import check_js_runtime
from config.settings import create_folders_path, read_path, update_path

def clear_terminal():
    """Clears the terminal screen based on the Operating System."""
    os.system("cls" if os.name == "nt" else "clear")

def prompt_to_continue():
    if input("Press Enter to continue or 'q' to exit... ").lower() == "q":
        return True
    return False

def create_choice_list(types_list: list):
    format_list = [Choice(value=x, name=x) for x in types_list]

    return format_list

def path_image_choice(path):
    print("--- Choice Path ---")
    current_path_directory = path

    while True:
        file_path = inquirer.filepath(
            message="Choice the Image File!",
            default=str(current_path_directory),
            validate=check_image_format
        ).execute()

        if not file_path:
            break
            
        if os.path.isfile(file_path):
            return file_path

        elif os.path.isdir(file_path):
            current_path_directory = file_path
            clear_terminal()
    return current_path_directory

def path_audio_choice(path):
    current_path_directory = path

    while True:
        file_path = inquirer.filepath(
            message="Choice the Audio File!",
            default=str(current_path_directory),
            validate=check_audio_format
        ).execute()

        if not file_path:
            break
            
        if os.path.isfile(file_path):
            return file_path

        elif os.path.isdir(file_path):
            current_path_directory = file_path
            clear_terminal()
    return current_path_directory

def default_path_choice(default: str):
    path_name = default.replace("_", " ").title()

    clear_terminal()
    print("--- Choice Path ---")

    paths = read_path(default)
    paths_list = [Choice(value=x, name=x) for x in paths]
    paths_list.append(Choice(value="Another", name="> Choice another path."))
 
    default_path = inquirer.select(
        message=f"Choice a Default {path_name}!",
        choices=paths_list
    ).execute()

    functions_call = {
        "Download Path": None,
        "Image Path": path_image_choice,
        "Str Path": None
    }

    action_fuction = functions_call.get(path_name)
    return action_fuction(os.path.expanduser("~") if default_path == "Another" else default_path)

def media_downloader():
    if not check_js_runtime:
        return None

    file_path = default_path_choice("DOWNLOAD_PATH")
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
            
            if prompt_to_continue():
                clear_terminal()
                sys.exit(1)
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
        download_media(url=checked_url, output_path=file_path, file_type=file_format)
        prompt_to_continue()

def image_converter():
    print("--- Image Converter ---")
    file_path = default_path_choice("IMAGE_PATH")

    file_format_list = create_choice_list(["PNG", "JPEG", "JPG", "WEBP"])
    file_format_list.append(Choice(value="Return", name="Return"))

    file_format = inquirer.select(
        message="Choice The File Format:",
        choices=file_format_list
    ).execute()

    if file_format == "Return":
        clear_terminal()
    else:
        update_path(path_name="IMAGE_PATH", new_path=Path(file_path))

def srt_generator():
    print("--- SRT Generator ---")
    file_path = default_path_choice("SRT_PATH")

    srt_mode = create_choice_list([])
    srt_mode.append(Choice(value="Return", name="Return"))

    if srt_mode == "Return":
        clear_terminal()
    else:


        update_path(path_name="IMAGE_PATH", new_path=Path(file_path).parent)
        audio_file = path_audio_choice()
        

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
    #logging.info("Fuctions 'create_folder_path' execute successful.")

    main()

    # TODO - Check if the code arguments are good -> Setup it if not
    # TODO - Check if main.py and config.py is good to be in src and if scripts its a good name
    # TODO - Setup download def and str_generator.
    # str generator -> choice file, choice default modes and call fuction
    # download -> choice folder to save -> input the url -> choice mode (mp3, wav or mp4) always download in best format.