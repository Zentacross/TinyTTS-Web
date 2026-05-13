# TinyTTS Web

A minimal browser UI for [**TinyTTS**](https://github.com/tronghieuit/tiny-tts) — the ultra-lightweight (~1.6M params, ~3.4 MB ONNX) English text-to-speech model by [@tronghieuit](https://github.com/tronghieuit).

Type text → pick a voice and speed → click **Generate** → listen or download the resulting `out.wav`.

![TinyTTS Web screenshot](https://raw.githubusercontent.com/Zentacross/TinyTTS-Web/main/Screenshot.png)

---

## Features

- Clean dark UI — textarea, voice picker, speed slider, one button
- **Voice selection**: Male / Female
- **Speed control**: 0.5× – 2.0× with live readout
- **HF token entered in the UI** — never hard-coded; stored only in your browser's `localStorage`
- Built-in HTML5 audio player with download link
- Backend always overwrites a single `out.wav` (no clutter)
- Cache-busted playback so you always hear the latest take
- Pure HTML / CSS / vanilla JS on the frontend — **no npm, no build step**
- Tiny Flask server wrapping the `tiny-tts` Python package

## Stack

| Layer | Tech |
|---|---|
| Model | [`tiny-tts`](https://pypi.org/project/tiny-tts/) (PyPI) |
| Backend | Flask |
| Frontend | HTML + CSS + vanilla JS |

## Requirements

- Python 3.9+
- ~100 MB free disk for the model + deps
- A HuggingFace account + access token (free) — [create one here](https://huggingface.co/settings/tokens)

## Installation

```bash
git clone https://github.com/Zentacross/TinyTTS-Web.git
cd TinyTTS-Web

pip install flask tiny-tts
```

## Run

```bash
python app.py
```

Open <http://localhost:5000>, paste your HuggingFace token into the **HuggingFace token** field, and hit **Generate**. The token is saved in your browser's `localStorage` so you only enter it once per browser.

The TinyTTS model weights are downloaded automatically from HuggingFace on first generation (the token is required for that download).

> ⚠️ The token never touches the repo — it lives in the browser and is sent to your local server only.

## Project structure

```
tinytts-web/
├── app.py          # Flask server: /, /generate, /out.wav
├── index.html      # UI (token, textarea, voice, speed, player)
├── style.css       # Dark theme
├── script.js       # fetch() client + audio player + prefs
├── out.wav         # generated, overwritten on each request (gitignored)
└── README.md
```

## API

### `POST /generate`

```json
{
  "text": "Hello world",
  "hf_token": "hf_xxx",
  "speaker": "MALE",
  "speed": 1.0
}
```

| Field | Type | Default | Notes |
|---|---|---|---|
| `text` | string | — | Required. The text to synthesize. |
| `hf_token` | string | — | Required on first call (used to download the model). |
| `speaker` | `"MALE"` \| `"FEMALE"` | `"MALE"` | Voice to use. |
| `speed` | number | `1.0` | Clamped to `[0.5, 2.0]`. `1.5` = faster, `0.7` = slower. |

Synthesizes speech and writes it to `out.wav`. Returns `{ "ok": true }` on success or `{ "error": "..." }` with a non-200 status on failure.

### `GET /out.wav`

Returns the latest generated audio with `Cache-Control: no-store`.

## Credits

- **Model:** [TinyTTS](https://github.com/tronghieuit/tiny-tts) by [tronghieuit](https://github.com/tronghieuit) — please ⭐ the upstream repo.
- This project is just a thin web wrapper around it.

## License

MIT for this wrapper. The TinyTTS model is distributed under its own license — see the [upstream repository](https://github.com/tronghieuit/tiny-tts).
