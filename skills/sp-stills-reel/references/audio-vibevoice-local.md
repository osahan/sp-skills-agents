# Local VibeVoice test (Mac) — voiceover for SP reels

> Goal: generate a `vo.wav` from a script, drop it in the reel folder, and let
> `render_stills_reel.py` mix it under music. This doc covers a **local test**;
> automation (n8n/pipeline) is a later step.

## Read this first — what VibeVoice can and can't do (verified from the repo, 2026-06)

- **Cloning *your* voice needs the TTS-1.5B model, whose official inference is
  DISABLED** (Microsoft removed the TTS code after misuse). Cloning today = a
  community fork (unofficial, use at your own risk).
- **The supported model is Realtime-0.5B, which uses PRESET embedded voices only**
  (e.g. `Carter`) — not your voice. Custom voices require contacting their team.
- **English only**, no symbols/code/formulas (pre-normalize text), unstable on
  inputs of ≤3 words, and it does **not** make music/SFX (we add music separately).
- Microsoft: research-only, **not recommended for commercial use without further
  testing**, and **disclose AI use** when publishing. Weigh this for brand audio.

**Recommendation:** use Realtime-0.5B to *test quality/fit* (preset voice). For the
actual brand VO in your voice, **VoiceBox (which you already have) is the safer
bet** unless a community 1.5B fork clones you convincingly.

## Path A — Realtime-0.5B local test (supported; preset voice)

Requires a recent Apple-Silicon Mac (repo verified M4 Pro runs real-time) with
Python 3.10+ and git. From a terminal:

```bash
# 1. Clone + install (no Docker needed on Mac; Docker block in the doc is for NVIDIA)
git clone https://github.com/microsoft/VibeVoice.git
cd VibeVoice
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[streamingtts]"     # downloads deps; model pulls from HF on first run

# 2. Put your script in a text file (English, no symbols, full sentences)
mkdir -p demo/text_examples
printf '%s\n' "Six chais. One slow ritual. Ground the old way, because it matters." \
  > demo/text_examples/sp_chai.txt

# 3. Generate (preset speaker — try a few: Carter, etc.)
python demo/realtime_model_inference_from_file.py \
  --model_path microsoft/VibeVoice-Realtime-0.5B \
  --txt_path demo/text_examples/sp_chai.txt \
  --speaker_name Carter
# -> writes a .wav under the repo's output dir; find it with:  ls -lt **/*.wav
```

Don't want to install anything? The repo's **Colab** runs it on a free GPU:
https://colab.research.google.com/github/microsoft/VibeVoice/blob/main/demo/vibevoice_realtime_colab.ipynb
— run it, download the `.wav`.

## Path B — Your voice via TTS-1.5B (community fork; this is the cloning path)

Official 1.5B inference is disabled, so use the maintained community fork
**`vibevoice-community/VibeVoice`** (it restored `inference_from_file.py` + cloning).
The 1.5B clones a voice from a reference wav placed in `demo/voices/`, matched by
`--speaker_names`.

```bash
# 1. Clone the community fork
git clone https://github.com/vibevoice-community/VibeVoice.git
cd VibeVoice
python3 -m venv .venv && source .venv/bin/activate
pip install -e .                      # if flash-attn fails on Mac, see note below

# 2. Add your reference voice (name it simply — speaker_names matches the filename)
mkdir -p demo/voices
cp "/Users/gagan/Library/CloudStorage/Dropbox/spicepilgrim/social media/chai/voice/gagan_ref.wav" demo/voices/Gagan.wav

# 3. Put the script in a text file
mkdir -p demo/text_examples
cp "/Users/gagan/Library/CloudStorage/Dropbox/spicepilgrim/social media/chai/voice/masala_vo_test.txt" demo/text_examples/sp_masala.txt

# 4. Generate (downloads microsoft/VibeVoice-1.5B weights from HF on first run)
python demo/inference_from_file.py \
  --model_path microsoft/VibeVoice-1.5B \
  --txt_path demo/text_examples/sp_masala.txt \
  --speaker_names Gagan
# -> output .wav lands in the fork's outputs dir; copy it to chai/vo.wav
```

**Mac / reliability notes (verify against the fork's README — flags drift):**
- The 1.5B is heavier than the 0.5B. On Apple Silicon it may need `--device mps`
  or fall back to CPU (slow). `flash-attn` often won't build on Mac — if `pip install`
  fails on it, install without it / use the fork's CPU path.
- If the text file needs a speaker prefix, format lines as `Speaker 1: <text>`.
- **Reliable fallback:** the official **Colab** (free GPU) — generate there, download
  the wav. Fastest way to just *hear* the clone.
- Watermark + "disclose AI" + research-only caveats still apply for brand use.

## Path C — Use VoiceBox (your existing voice) — likely best for brand VO
You already generate Gagan's voice via VoiceBox (id in the film-director skill).
For a single narration line, that's the lowest-risk, on-brand option. Use VibeVoice
only if it clearly beats it.

## Feeding the VO into the reel

Once you have a `vo.wav` (any path above) and optionally a music track, put them in
the reel folder and reference them in the config:

```json
{
  "music": "chai/music/sarangi.mp3",
  "voiceover": "chai/vo.wav",
  "voiceover_start": 0.0,      // seconds; delay VO if it should land later
  "music_gain": 0.22           // music ducks under VO automatically when both present
}
```

Then render — the script mixes VO over a ducked music bed with fades:
```bash
python scripts/render_stills_reel.py myconfig.json
# produces <doc_name>_<fmt>.mp4 (silent) and <doc_name>_<fmt>_audio.mp4 (mixed)
```

## Text prep checklist (avoids VibeVoice failure modes)
- English; spell out symbols/numbers if odd ("N° 02" → "number two").
- Full sentences; avoid ≤3-word clips.
- Keep it short and calm — matches the brand and reduces artifacts.
- If publishing AI VO, add a light disclosure per Microsoft's guidance.
