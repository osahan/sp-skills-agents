---
name: sp-stills-reel
description: >
  Produce polished Spice Pilgrim "stills-as-video" social reels — turning a set
  of product/dish photos plus short captions into a branded vertical/square/wide
  video (Ken Burns motion, crossfades, editorial captions), for free, with no AI
  video subscription. Use this whenever Gagan/Dolly want a social video, reel,
  Instagram/TikTok/YouTube short, "slideshow video", product showcase, or chai/
  spice/tea video built from photos — even if they don't say "stills-as-video."
  Also trigger when iterating on an existing SP reel (pacing, captions, fonts,
  crop, music) or when asked to render an SP reel in multiple aspect ratios. Do
  NOT use for AI-generated footage (Veo/Sora/HeyGen) or for editing existing
  filmed video — this skill animates still photos.
---

# Spice Pilgrim — Stills-as-Video Reel

Turn still photos + captions into a branded social video. PIL composes each
frame; ffmpeg adds slow Ken Burns motion and crossfades. Everything runs locally
and free — no per-minute AI-video cost. The render logic lives in
`scripts/render_stills_reel.py`; you drive it with a small JSON config.

**Before doing anything, read `references/brand-design-system.md`** for the exact
fonts and colors, and skim `LEARNINGS.md` for hard-won lessons. After you finish,
you MUST update `LEARNINGS.md` (see "Self-improvement protocol" below) — that is
what keeps this skill getting better.

## The design philosophy (why it looks professional, not amateur)

These principles were learned by getting it wrong first. Honor them:

1. **The photo is the background — full bleed.** Never box the image into a zone
   with text in a separate zone. Two equal regions create competing focal points
   and the viewer doesn't know where to look.
2. **One focal point per beat, separated in time.** Title and call-to-action are
   their own **text-only "card" beats** (charcoal background, copper glow).
   Product beats are **image-first**, with text demoted to a small caption over a
   gradient. So a "read this" moment never fights a "look at this" moment.
3. **Smooth bottom scrim.** Darkest at the very bottom, easing to transparent
   going up over a long band. A short/inverted gradient makes a visible hard
   line — avoid it.
4. **Slow, calm pacing.** ~5.5s holds, ~1.0s dissolves. Premium reads unhurried.
   When in doubt, lengthen.
5. **Editorial caption lockup.** tracked copper overline → Playfair headline
   (Title Case, weight 400) → hairline copper rule → small Open Sans descriptor →
   index (`02 / 06`). This hierarchy is most of what makes it look designed.
6. **Crop to keep the subject.** Landscape product shots have the tin off-center;
   set `focus_x` per photo (0=left … 1=right) so the tin isn't cropped off a tall
   frame. ~0.74 for right-biased jars.
7. **Brand discipline.** Playfair Display headings (never bold) + Open Sans body.
   Copper `#9E5F24` is the only accent. (Full tokens in the reference file.)

## Workflow

1. **Gather inputs.** You need photos and (optionally) a music track as *files* —
   the sandbox can't fetch image binaries or synthesize audio. Have the user drop
   them into a folder (e.g. `social media/<topic>/`). Brand fonts
   (`PlayfairDisplay-Regular.ttf`, `OpenSans-Regular.ttf`, `OpenSans-Bold.ttf`)
   should live in a `fonts/` dir; without them the script uses stand-ins and says
   so — fine for drafts, swap in real fonts for the final.
2. **Inspect the photos** (Read them) and choose the best shot per item. Note
   where the subject sits to set `focus_x`. Keep the set visually consistent
   (similar surfaces/lighting).
3. **Write a config** modeled on `examples/chai_collection.json`: a `card` opener,
   one `photo` beat per product, a `card` closer (CTA). Keep captions short and in
   brand voice; headline = product name in Title Case.
4. **Render** (renders each beat to a clip, then stitches — resumable):
   ```bash
   python scripts/render_stills_reel.py myconfig.json
   ```
   Start with 9:16 to validate, then add `1x1` and `16x9` to `formats` for native
   multi-format masters. (Render formats natively from the source — do NOT resize
   a finished 9:16 in Canva; that crops the subject. Canva is only for optional
   branded sticker/overlay polish afterward.)
5. **Verify visually.** Extract a few frames with ffmpeg and Read them — check
   focal clarity, no hard scrim line, subject in frame, caption legibility,
   spelling. Fix and re-render.
6. **Deliver** to the user's folder and present the files.

## Config quick reference

See `examples/chai_collection.json` for the full schema. Fields:
`doc_name`, `output_dir`, `formats` (`9x16`/`1x1`/`16x9`), `font_dir`,
`fallback_font_dir`, `audio` (path or null), `transition`, `transition_dur`,
and `beats[]`. Each beat: `type` (`card`|`photo`), `overline`, `headline`
(`\n` allowed), `desc`, `index`, `image` (photo beats), `focus_x`, `dur`.

## Audio (music + voiceover)
The renderer mixes optional `music` (full bed if alone, auto-ducked under VO when
both present) and `voiceover` (laid on top, optional `voiceover_start` delay), each
with fades — set them in the config. Audio must arrive as **files** (the sandbox
can't synthesize). For generating a voiceover locally (VibeVoice on a Mac, its real
limitations, and why VoiceBox may be the better brand-VO choice), see
`references/audio-vibevoice-local.md`. For music, generate a few signature tracks
once (Suno/MusicFX) and reuse them — don't regenerate per video.

## Known environment constraints (don't relearn these)
- **No web binary fetch / no TTS / no music gen** in the sandbox — audio & images
  come in as files; the script only *mixes* provided audio.
- **Time limits:** keep renders chunked (clips then stitch). The script already
  renders at 1× + ffmpeg upscale and quarter-res card glow to stay fast. If a long
  render risks timing out, render the beat clips, then run only the stitch.

## Self-improvement protocol (required)

This skill is meant to get better with use. After each invocation:

1. **Append a dated entry to `LEARNINGS.md`** — what you made, what worked, what
   broke, any new user preference (e.g. preferred hold length, caption voice,
   favored transition, a music track they liked). Be concrete.
2. **Promote stable lessons.** If a lesson has held up across a few reels, edit it
   into this `SKILL.md` (or `references/`) so future runs get it by default, and
   note in `LEARNINGS.md` that it was promoted.
3. **Bundle repeated work.** If you find yourself writing the same helper or doing
   the same manual step repeatedly, add it to `scripts/` and reference it here.
4. **Keep brand truth synced.** If fonts/colors change, reconcile with
   `brain/spice-pilgrim/design/design.md` and update `references/brand-design-system.md`.

Because installed skills run read-only, "self-improvement" means editing the
**source copy in this repo** (`~/sites/osahan/sp-skills-agents/...`) and
reinstalling — the LEARNINGS log is the durable memory between runs.
