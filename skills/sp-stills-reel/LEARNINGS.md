# LEARNINGS — sp-stills-reel

> This is the skill's memory. **Append a dated entry every time the skill is used**
> with anything that worked, broke, or surprised you. When a lesson has proven
> itself across a few uses, fold it into `SKILL.md` (or `references/`) and note
> here that it was promoted. This is how the skill improves itself over time.

Entry format:
```
## YYYY-MM-DD — short title
- Context: what was being made
- Learned: the insight
- Action: what changed in the skill (or "logged only")
```

---

## 2026-06-27 — Initial creation (chai "Six Chais, One Ritual" reel)
- **Context:** First stills-as-video reel — 6 chai blends + title/CTA cards, vertical-first, later all 3 formats.
- **Learned (design):**
  - The killer mistake was **two competing focal zones** — a boxed photo up top + a separate text block below. Viewer didn't know where to look. Fix that won: **full-bleed photo + caption over a gradient**, and **separate text-only cards** for title/CTA so text moments and image moments never compete (separation in *time*).
  - The bottom scrim must be **darkest at the very bottom, easing to 0 going up**. An inverted/short gradient creates a visible **hard line**. Use a long band (~0.58·H) and a gentle power curve (~^1.8).
  - **Pacing:** first pass at ~2.2s/slide felt amateur and rushed. ~5.5s holds + ~1.0s dissolves read calm/premium. Users will ask for *more* time, not less.
  - **Crop focus matters:** landscape product shots have the tin off-center (often right). Center-cropping to 9:16 cut the tin off. A per-image `focus_x` (≈0.74 for right-biased jars) keeps the subject in frame.
  - **Typography is 80% of "professional."** Generic system font + flat centered same-size caps = amateur. The editorial lockup (tracked copper overline → Playfair headline → hairline copper rule → small descriptor → index/wordmark) is what made it look designed.
- **Learned (brand):** Fonts are **Playfair Display (400, never bold) + Open Sans**; **copper #9E5F24 is the only accent**. Pulled from the vault design doc, which was itself extracted live from the Shopify theme. Always reconcile to `brain/spice-pilgrim/design/design.md`.
- **Learned (environment / ops):**
  - TTS voiceover and music generation are **network-blocked in the sandbox** — audio must arrive as a provided file; the skill only *mixes* it.
  - Can't fetch image **binaries** from the web (only page text) — user drops photos into a folder.
  - Brand font files weren't installed and apt needs root — **fonts must be supplied** (drop .ttf in a fonts dir). Until then, Lora/Work Sans are acceptable stand-ins.
  - **Render reliability:** a single long ffmpeg pass (or a heavy PIL blur on a 2× canvas) blows past the ~45s sandbox shell limit, and background processes can be killed before the final stitch. Mitigations now baked into the script: render at 1× and upscale 1.3× in ffmpeg for zoom headroom (not 2× PIL), compute card glow at quarter-res, render each beat to its own clip, then stitch separately (clips are cheap to resume).
- **Action:** All of the above are implemented in `scripts/render_stills_reel.py` and documented in `SKILL.md` / `references/brand-design-system.md`.

## 2026-06-27 — Audio layer + VibeVoice reality check
- **Context:** Adding voiceover + music to the chai reel; user wants VibeVoice (their voice) and prefers to automate, but chose to test locally first.
- **Learned (verified from the official repo):**
  - **VibeVoice voice-cloning (TTS-1.5B) is officially DISABLED** (code removed after misuse). Cloning your own voice now needs a community fork (unofficial).
  - The **supported Realtime-0.5B uses PRESET embedded voices only** — not your voice. Good for testing quality; runs real-time on Apple Silicon (repo cites M4 Pro).
  - English-only, no symbols/music, unstable on ≤3-word inputs; Microsoft labels it research-only and asks for AI disclosure. Real considerations for *branded* audio.
  - Net: for the actual brand VO, **VoiceBox (already in hand) is the lower-risk path**; reserve VibeVoice for testing or if a community fork clones convincingly.
- **Action:** Extended `render_stills_reel.py` to mix `music` + `voiceover` (auto-duck music under VO, fades, `voiceover_start` offset). Added `references/audio-vibevoice-local.md` (Mac quickstart + the limitations above). Music best practice: generate a few signature tracks once and reuse, not per-video.

## 2026-06-28 — First voiced hero piece (Masala "The Promise") + clean-photo mode
- **Context:** Built a single-blend VO-driven hero reel with Gagan's real voice (VibeVoice 1.5B community fork).
- **Learned (worked):**
  - **VibeVoice voice cloning succeeds — but only with a REAL recording.** First attempt cloned the *VoiceBox sample* (itself synthetic) → accent came out Americanized/wrong. Re-cloning from a fresh 40s phone recording of Gagan's natural voice fixed the accent. Lesson: clone from genuine speech, never from another synthetic clip.
  - **VibeVoice gotchas confirmed:** script needs a `Speaker 1:` prefix or it errors ("No valid speaker scripts"); strip em-dashes/odd symbols; runs on Apple-Silicon MPS fine for ~30s clips.
  - **Hero-piece grammar ≠ showcase grammar.** For VO-driven films, photos should be **clean full-bleed (no captions)** so text doesn't fight the narration — the voice carries it; brand text only on the closing card. Added a clean-photo path to the renderer: a photo beat with no overline/headline/desc/index now renders a subtle cinematic **vignette** instead of the caption lockup.
  - **Audio mixing works end-to-end:** `voiceover` muxed over the silent reel, durations matched (31s video / 30.8s VO).
- **Process win:** reference-prep recipe = convert to mono 24kHz, trim leading/trailing silence, `loudnorm I=-16` → clean clip for any cloner.
- **Action:** clean-photo/vignette mode added to `scripts/render_stills_reel.py`; VibeVoice `Speaker 1:` + real-reference lessons added to `references/audio-vibevoice-local.md` context. Still open: music bed + real Playfair/Open Sans fonts before the final multi-format render.

## 2026-06-28 — Ken Burns jitter fix + resumable renders
- **Symptom:** slow zoom "shakes"/steps, most visible at 1:1.
- **Cause:** ffmpeg `zoompan` rounds pan x/y to integer pixels each frame → visible stepping during slow zooms.
- **Fix:** render zoompan on a supersampled canvas (`supersample` config, e.g. 2×) then downscale to final — integer steps become sub-pixel → smooth glide. Added `supersample` (float) to config; default 2. Downscale uses bilinear (lanczos was ~too slow per-frame here).
- **Cost caveat (sandbox-specific):** zoompan on a large canvas is slow (~30–37s for one 9s clip at ~1.6×). The Cowork bash sandbox kills processes at ~45s, so a single supersampled tall-format clip may not finish in one call. **On a normal machine (e.g. the user's Mac) there's no such cap — supersample=2 renders all formats smoothly in one run.**
- **Mitigation added:** renders are now **resumable** — each clip writes atomically (`.tmp` → `os.replace`) and existing clips are skipped, so re-invoking the script continues where it left off. This makes long renders survive the sandbox's 45s kills (call repeatedly until the final mp4 appears).
- **Practical guidance:** in-sandbox, use `supersample: 1.0` for quick drafts; bump to `2` for finals (ideally rendered where there's no time cap). 1:1 benefits most from the fix.

## Open questions / next ideas (not yet validated)
- Per-blend spin-off reels (one product each) from the same config — likely a `--only <index>` flag.
- Music: settle on 1–2 signature royalty-free tracks so reels feel like a series.
- Try a subtle film grain + a 1s hold of silence at the end (echoes the Pilgrim Film grammar) for hero pieces.
