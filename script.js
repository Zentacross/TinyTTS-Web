const $text = document.getElementById("text");
const $btn = document.getElementById("generate");
const $status = document.getElementById("status");
const $playerWrap = document.getElementById("player-wrap");
const $player = document.getElementById("player");
const $download = document.getElementById("download");
const $token = document.getElementById("hf-token");
const $speaker = document.getElementById("speaker");
const $speed = document.getElementById("speed");
const $speedVal = document.getElementById("speed-val");

const TOKEN_KEY = "tinytts.hf_token";
const SPEAKER_KEY = "tinytts.speaker";
const SPEED_KEY = "tinytts.speed";

// Restore prefs
$token.value = localStorage.getItem(TOKEN_KEY) || "";
$speaker.value = localStorage.getItem(SPEAKER_KEY) || "MALE";
$speed.value = localStorage.getItem(SPEED_KEY) || "1";
$speedVal.textContent = `${Number($speed.value).toFixed(2)}×`;

$token.addEventListener("change", () => localStorage.setItem(TOKEN_KEY, $token.value.trim()));
$speaker.addEventListener("change", () => localStorage.setItem(SPEAKER_KEY, $speaker.value));
$speed.addEventListener("input", () => {
  $speedVal.textContent = `${Number($speed.value).toFixed(2)}×`;
  localStorage.setItem(SPEED_KEY, $speed.value);
});

function setStatus(msg, isError = false) {
  $status.textContent = msg;
  $status.classList.toggle("error", isError);
}

$btn.addEventListener("click", async () => {
  const text = $text.value.trim();
  const hf_token = $token.value.trim();
  if (!text) return setStatus("Please enter some text.", true);
  if (!hf_token) return setStatus("Please enter your HuggingFace token.", true);

  localStorage.setItem(TOKEN_KEY, hf_token);

  $btn.disabled = true;
  setStatus("Generating audio...");

  try {
    const res = await fetch("/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text,
        hf_token,
        speaker: $speaker.value,
        speed: parseFloat($speed.value),
      }),
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);

    const url = `/out.wav?t=${Date.now()}`;
    $player.src = url;
    $download.href = url;
    $playerWrap.hidden = false;
    setStatus("Ready. Press play to listen.");

    try { await $player.play(); } catch { /* autoplay blocked */ }
  } catch (err) {
    setStatus(err.message || "Something went wrong.", true);
  } finally {
    $btn.disabled = false;
  }
});
