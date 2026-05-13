"""
TinyTTS web app — basic Flask server.

Run:
    pip install flask tiny_tts
    python app.py

Then open http://localhost:5000

The HuggingFace token is supplied from the browser (stored in your
browser's localStorage) — it is never hard-coded here.
"""
import os
import threading
from flask import Flask, request, jsonify, send_from_directory, send_file

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(BASE_DIR, "out.wav")

app = Flask(__name__, static_folder=None)

_tts = None
_tts_lock = threading.Lock()


def get_tts(hf_token: str):
    """Lazily build (and cache) the TinyTTS model.

    The token must be set in the environment BEFORE importing tiny_tts so
    its internal HuggingFace download picks it up.
    """
    global _tts
    with _tts_lock:
        if _tts is None:
            if not hf_token:
                raise RuntimeError("HF_TOKEN is required on first generation.")
            os.environ["HF_TOKEN"] = hf_token
            os.environ["HUGGINGFACE_HUB_TOKEN"] = hf_token
            from tiny_tts import TinyTTS  # imported lazily
            _tts = TinyTTS()
        return _tts


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/style.css")
def style():
    return send_from_directory(BASE_DIR, "style.css")


@app.route("/script.js")
def script():
    return send_from_directory(BASE_DIR, "script.js")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    hf_token = (data.get("hf_token") or "").strip() or os.environ.get("HF_TOKEN", "")
    speaker = (data.get("speaker") or "MALE").upper()
    if speaker not in ("MALE", "FEMALE"):
        speaker = "MALE"
    try:
        speed = float(data.get("speed", 1.0))
    except (TypeError, ValueError):
        speed = 1.0
    speed = max(0.5, min(2.0, speed))

    if not text:
        return jsonify({"error": "Text is required."}), 400
    if not hf_token:
        return jsonify({"error": "HF token is required."}), 400

    try:
        tts = get_tts(hf_token)
        # tiny-tts speak() supports speed and (per CLI) speaker.
        try:
            tts.speak(text, output_path=OUTPUT_PATH, speed=speed, speaker=speaker)
        except TypeError:
            # Older versions may not accept `speaker` kwarg.
            tts.speak(text, output_path=OUTPUT_PATH, speed=speed)
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": str(exc)}), 500
    return jsonify({"ok": True})


@app.route("/out.wav")
def out_wav():
    if not os.path.exists(OUTPUT_PATH):
        return jsonify({"error": "No audio yet."}), 404
    response = send_file(OUTPUT_PATH, mimetype="audio/wav", conditional=False)
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
