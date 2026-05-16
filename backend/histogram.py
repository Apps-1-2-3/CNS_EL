"""RGB histogram + difference map generation."""
import io
import base64
import numpy as np
from PIL import Image


def rgb_histograms(img: Image.Image) -> dict:
    arr = np.array(img.convert("RGB"))
    out = {}
    for i, ch in enumerate(("r", "g", "b")):
        hist, _ = np.histogram(arr[..., i], bins=256, range=(0, 256))
        out[ch] = hist.astype(int).tolist()
    return out


def compare_histograms(original: Image.Image, stego: Image.Image) -> dict:
    return {
        "original": rgb_histograms(original),
        "stego": rgb_histograms(stego),
        "bins": list(range(256)),
    }


def difference_map(original: Image.Image, stego: Image.Image, amplify: int = 64) -> str:
    """Return PNG (base64) where modified pixels are highlighted bright red."""
    a = np.array(original.convert("RGB"), dtype=np.int16)
    b = np.array(stego.convert("RGB"), dtype=np.int16)
    diff = np.any(a != b, axis=2)  # H x W bool

    out = np.zeros_like(a, dtype=np.uint8)
    # grayscale base of original at low brightness
    gray = (0.3 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2]).astype(np.uint8) // 3
    out[..., 0] = gray; out[..., 1] = gray; out[..., 2] = gray
    # highlight changed pixels
    out[diff] = [255, 40, 80]

    img = Image.fromarray(out, "RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def modification_stats(original: Image.Image, stego: Image.Image) -> dict:
    a = np.array(original.convert("RGB"), dtype=np.int16)
    b = np.array(stego.convert("RGB"), dtype=np.int16)
    pixel_diff = np.any(a != b, axis=2)
    total = pixel_diff.size
    modified = int(pixel_diff.sum())
    channel_changes = int(np.sum(a != b))
    return {
        "total_pixels": int(total),
        "modified_pixels": modified,
        "modified_percent": round(100.0 * modified / total, 4),
        "channel_bit_flips": channel_changes,
    }
