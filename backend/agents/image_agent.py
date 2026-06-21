"""
agents/image_agent.py
AGENT 1 of 5: Image Agent
Job: take the raw uploaded file (DICOM or PNG/JPG X-ray), normalize it,
and return a clean base64 JPEG that the Detection Agent can send to Roboflow.
"""
import base64
import io
from PIL import Image
import pydicom
from agents.pipeline_state import set_status


def preprocess_scan(file_bytes: bytes, filename: str) -> str:
    """
    Takes raw file bytes, returns a base64-encoded JPEG string.
    Handles both .dcm (DICOM) and normal image formats (.png/.jpg).
    """
    set_status("Image Agent", "active", f"Preprocessing {filename}...")

    try:
        if filename.lower().endswith(".dcm"):
            image = _read_dicom(file_bytes)
        else:
            image = Image.open(io.BytesIO(file_bytes))

        # Standardize: convert to RGB, resize so the model gets a consistent input
        image = image.convert("RGB")
        image.thumbnail((1024, 1024))

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=90)
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")

        set_status("Image Agent", "done", f"Preprocessed {filename} successfully")
        return encoded

    except Exception as e:
        set_status("Image Agent", "error", f"Failed to preprocess {filename}: {e}")
        raise


def _read_dicom(file_bytes: bytes) -> Image.Image:
    """Converts a DICOM (.dcm) file's pixel data into a viewable PIL image."""
    dataset = pydicom.dcmread(io.BytesIO(file_bytes))
    pixel_array = dataset.pixel_array

    # Normalize pixel values to 0-255 range for a standard image
    pixel_array = pixel_array.astype(float)
    pixel_array = (pixel_array - pixel_array.min()) / (pixel_array.max() - pixel_array.min() + 1e-6) * 255.0
    pixel_array = pixel_array.astype("uint8")

    return Image.fromarray(pixel_array)
