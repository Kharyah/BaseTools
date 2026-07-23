import logging

from pathlib import Path
from utils import print_divider

logger = logging.getLogger(__name__)

# A set of the most common and widely supported image formats
SUPPORTED_FORMATS: set[str] = {
    "JPEG", "JPG", "PNG", "WEBP", "BMP", "GIF", "TIFF", "ICO"
}


def check_image_format(file_path: str) -> bool:
    """Checks if the file extension is supported."""
    path = Path(file_path)

    if not path.is_file():
        return False

    suffix = path.suffix.lstrip(".").upper()
    return suffix in SUPPORTED_FORMATS


def convert_image_format(
    input_path: str,
    output_dir: str,
    target_format: str
) -> bool:
    """
    Converts an image to a target format and saves
    it into the specified output directory.

    :param input_path: Verified path to the source image file.
    :param output_dir: Path directory where the image will be saved.
    :param target_format: The desired image format (e.g., 'PNG', 'JPEG').
    """
    from PIL import Image

    # Normalize format
    target_format = target_format.upper()
    if target_format == "JPG":
        target_format = "JPEG"

    if target_format not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format: '{target_format}'")

    input_path_obj = Path(input_path)
    output_dir_obj = Path(output_dir)

    base_name = input_path_obj.stem
    extension = "jpg" if target_format == "JPEG" else target_format.lower()
    final_output_path = output_dir_obj / f"{base_name}.{extension}"

    try:
        with Image.open(input_path) as img:
            # JPEG does not support transparency (alpha channel).
            # Convert RGBA/P to RGB to prevent Pillow from raising an OSError.
            if img.mode in ("RGBA", "P") and target_format == "JPEG":
                img = img.convert("RGB")

            # Ensure the output directory exists
            output_dir_obj.mkdir(parents=True, exist_ok=True)

            # Checks if the file already exists
            if final_output_path.exists():
                print_divider()
                print("[INFO] File already exists.")
                print_divider()
                return True

            img.save(final_output_path, format=target_format)

    except IOError as e:
        # Wrap the low-level Pillow/OS exception into a clear application error
        raise IOError(f"Failed to process the image conversion: {e}")

    logger.info("Image converted successfully.")

    print_divider()
    print(f"Image successfully converted to {target_format}.")
    print(f"Saved to: {final_output_path}")
    print_divider()
