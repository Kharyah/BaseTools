import os

from PIL import Image
from pathlib import Path
from utils import format_divider

# A set of the most common and widely supported image formats
SUPPORTED_FORMATS: set[str] = {
    "JPEG", "JPG", "PNG", "WEBP", "BMP", "GIF", "TIFF", "ICO"
}


def check_image_format(file_path: str) -> bool:
    """Checks if the file extension is supported."""
    path = Path(file_path)

    # Slices off the leading dot to match SUPPORTED_FORMATS
    if path.suffix[1:].upper() not in SUPPORTED_FORMATS:
        return False
    return True


def convert_image_format(
    input_path: str,
    output_dir: str,
    target_format: str
) -> None:
    """
    Converts an image to a target format and saves
    it into the specified output directory.

    :param input_path: Verified path to the source image file.
    :param output_dir: Path directory where the image will be saved.
    :param target_format: The desired image format (e.g., 'PNG', 'JPEG').
    """
    # Normalize format
    target_format = target_format.upper()
    if target_format == "JPG":
        target_format = "JPEG"

    if target_format not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format: '{target_format}'")

    # Extract the base file name without its original extension
    base_name = os.path.splitext(os.path.basename(input_path))[0]

    # Define the correct extension for the output file
    extension = "jpg" if target_format == "JPEG" else target_format.lower()

    # Construct the full final output path automatically
    final_output_path = os.path.join(output_dir, f"{base_name}.{extension}")

    try:
        with Image.open(input_path) as img:
            # JPEG does not support transparency (alpha channel).
            # Convert RGBA/P to RGB to prevent Pillow from raising an OSError.
            if img.mode in ("RGBA", "P") and target_format == "JPEG":
                img = img.convert("RGB")

            # Ensure the output directory exists
            os.makedirs(output_dir, exist_ok=True)

            # Save using the automatically generated full path
            img.save(final_output_path, format=target_format)

    except IOError as e:
        # Wrap the low-level Pillow/OS exception into a clear application error
        raise IOError(f"Failed to process the image conversion: {e}")

    print(format_divider())
    print(f"Image successfully converted to {target_format}.")
    print(f"Saved to: {final_output_path}")
    print(format_divider())
