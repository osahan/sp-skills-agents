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

## Open questions / next ideas (not yet validated)
- Per-blend spin-off reels (one product each) from the same config — likely a `--only <index>` flag.
- Music: settle on 1–2 signature royalty-free tracks so reels feel like a series.
- Try a subtle film grain + a 1s hold of silence at the end (echoes the Pilgrim Film grammar) for hero pieces.
