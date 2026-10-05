from PIL import Image
import io


ALLOWED_TYPES = {"image/jpeg", "image/png", "image/jpg", "image/webp"}


def validate_image(content_type: str) -> bool:
    """Return True if the MIME type is an allowed image format."""
    return content_type in ALLOWED_TYPES


def read_image_bytes(file) -> bytes:
    """Read all bytes from an uploaded file object."""
    return file.read()


def bytes_to_pil(file_bytes: bytes) -> Image.Image:
    """Convert raw bytes → PIL Image in RGB mode."""
    return Image.open(io.BytesIO(file_bytes)).convert("RGB")