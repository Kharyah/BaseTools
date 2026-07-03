import os

from PIL import Image
from pathlib import Path

# A set of the most common and widely supported image formats
SUPPORTED_FORMATS: Set[str] = {
    "JPEG", "JPG", "PNG", "WEBP", "BMP", "GIF", "TIFF", "ICO"
}

def check_image_format(file_path):
    path = Path(file_path)

    if path.suffix[1:].upper() not in SUPPORTED_FORMATS:
        return False
    return True

def convert_image_format(input_path: str, output_dir: str, target_format: str) -> None:
    """
    Converts an image to a target format and saves it into the specified output directory.
    Automatically extracts the original file name and applies the new extension.
    
    :param input_path: Verified path to the source image file.
    :param output_dir: Path to the target directory where the image will be saved.
    :param target_format: The desired image format (e.g., 'PNG', 'JPEG', 'WEBP').
    """
    # 1. Normalize format
    target_format = target_format.upper()
    if target_format == "JPG":
        target_format = "JPEG"

    if target_format not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format: '{target_format}'")

    # 2. Extract the base file name without its original extension
    # Example: "C:/Images/photo.png" -> "photo"
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    
    # 3. Define the correct extension for the output file
    extension = "jpg" if target_format == "JPEG" else target_format.lower()
    
    # 4. Construct the full final output path automatically
    # Example: "C:/Users/Usuario/Downloads" + "photo" + ".jpg"
    final_output_path = os.path.join(output_dir, f"{base_name}.{extension}")

    try:
        with Image.open(input_path) as img:
            # Handle alpha channel transparency for JPEG conversion
            if img.mode in ("RGBA", "P") and target_format == "JPEG":
                img = img.convert("RGB")
            
            # Ensure the output directory exists
            os.makedirs(output_dir, exist_ok=True)
                
            # Save using the automatically generated full path
            img.save(final_output_path, format=target_format)
            
    except IOError as e:
        raise IOError(f"Failed to process the image conversion: {e}")
    
    print(35 * "--")
    print(f"Image successfully converted to {target_format}.")
    print(f"Saved to: {final_output_path}")
    print(35 * "--")