import os

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from pathlib import Path

# TODO - Remember to call functions from converter, downloader and generate
from scripts.converter import check_format
from config import create_folders_path, read_path, update_path

def file_path_choice():
    os.system("cls" if os.name == "nt" else "clear")
    print("--- Choice Image ---")

    paths = read_path("IMAGE_PATH")
    paths_list = [Choice(value=x, name=x) for x in paths]
    paths_list.append(Choice(value="Another", name="> Choice another path."))
 
    default_path = inquirer.select(
        message="Choice a Default Path!",
        choices=paths_list
    ).execute()

    current_path_directory = default_path if default_path != "Another" else os.path.expanduser("~")

    while True:
        file_path = inquirer.filepath(
            message="Choice the Image File!",
            default=str(current_path_directory),
            validate=check_format
        ).execute()

        if not file_path:
            break
            
        if os.path.isfile(file_path):
            return file_path

        elif os.path.isdir(file_path):
            current_path_directory = file_path
            os.system("cls" if os.name == "nt" else "clear")

def media_downloader():
    print("--- Media Downloader ---")
    file_path = file_path_choice()

def image_converter():
    print("--- Image Converter ---")
    file_path = file_path_choice()

    types_list = ["PNG", "JPEG", "JPG", "WEBP"]
    file_format_list = [Choice(value=x, name=x) for x in types_list]
    file_format_list.append(Choice(value="Return", name="Return"))

    file_format = inquirer.select(
        message="Choice The File Format:",
        choices=file_format_list
    ).execute()

    if file_format == "Return":
        os.system("cls" if os.name == "nt" else "clear")
    else:        
        new_path = Path(file_path)
        update_path(path_name="IMAGE_PATH", new_path=new_path.parent)

        # TODO - Create the system to convert the image and save it in the right folder. 
        # TODO - Maybe think about configuring to save to the same path or if the user chooses another path.

def srt_generator():
    pass

def main():
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

        os.system("cls" if os.name == "nt" else "clear")

if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    create_folders_path() # Creating/checking the json file

    main()

    # TODO - Check if the code arguments are good -> Setup it if not
    # TODO - Check if main.py and config.py is good to be in src and if scripts its a good name
    # TODO - Setup download def and str_generator.
    # str generator -> choice file, choice default modes and call fuction
    # download -> choice folder to save -> input the url -> choice mode (mp3, wav or mp4) always download in best format.