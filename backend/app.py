"""Flask API server for StegoVault."""
import io
import base64
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image

from .encryption import encrypt, decrypt
from .embedding import embed, capacity_bits
from .extraction import extract
from .metrics import compute_all
from .histogram import compare_histograms, difference_map, modification_stats
from .analysis import security_report

app = Flask(__name__)
CORS(app)


def _read_image_field(field="image") -> Image.Image:
    f = request.files.get(field)
    if not f:
        raise ValueError(f"missing file field '{field}'")
    return Image.open(f.stream).convert("RGB")


def _img_to_b64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "StegoVault", "version": "2.0"}


@app.post("/api/capacity")
def api_capacity():
    img = _read_image_field()
    return {"capacity_bits": capacity_bits(img), "capacity_bytes": capacity_bits(img) // 8}


@app.post("/api/encode")
def api_encode():
    img = _read_image_field()
    message = request.form.get("message", "")
    password = request.form.get("password", "")
    if not message or not password:
        return {"error": "message and password required"}, 400

    t0 = time.perf_counter()
    blob = encrypt(message, password)
    stego = embed(img, blob, password)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    metrics = compute_all(img, stego)
    mod_stats = modification_stats(img, stego)

    return jsonify({
        "stego_image_b64": _img_to_b64(stego),
        "stats": {
            "message_bytes": len(message.encode("utf-8")),
            "ciphertext_bytes": len(blob),
            "capacity_bits": capacity_bits(img),
            "encoding_ms": round(elapsed_ms, 2),
            **mod_stats,
        },
        "metrics": metrics,
        "security": security_report(password, img, len(blob)),
    })


@app.post("/api/decode")
def api_decode():
    img = _read_image_field()
    password = request.form.get("password", "")
    if not password:
        return {"error": "password required"}, 400
    try:
        t0 = time.perf_counter()
        blob = extract(img, password)
        message = decrypt(blob, password)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        return {"message": message, "decoding_ms": round(elapsed_ms, 2), "key_valid": True}
    except Exception as e:
        return {"error": str(e), "key_valid": False}, 401


@app.post("/api/metrics")
def api_metrics():
    orig = _read_image_field("original")
    stego = _read_image_field("stego")
    return jsonify({
        "metrics": compute_all(orig, stego),
        "modification": modification_stats(orig, stego),
    })


@app.post("/api/histogram")
def api_histogram():
    orig = _read_image_field("original")
    stego = _read_image_field("stego")
    return jsonify(compare_histograms(orig, stego))


@app.post("/api/difference-map")
def api_diff_map():
    orig = _read_image_field("original")
    stego = _read_image_field("stego")
    return jsonify({
        "diff_map_b64": difference_map(orig, stego),
        "modification": modification_stats(orig, stego),
    })


@app.post("/api/security-analysis")
def api_security():
    img = _read_image_field()
    password = request.form.get("password", "")
    payload_bytes = int(request.form.get("payload_bytes", 0))
    return jsonify(security_report(password, img, payload_bytes))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
