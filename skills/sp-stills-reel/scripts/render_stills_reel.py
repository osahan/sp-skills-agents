#!/usr/bin/env python3
"""
render_stills_reel.py — Spice Pilgrim "stills-as-video" social reel renderer.

Turns a set of still photos + captions into a polished vertical/square/wide
social video using PIL (composition) + ffmpeg (Ken Burns motion + crossfades).
Free, deterministic, no AI-video subscription required.

Usage:
    python render_stills_reel.py config.json

See examples/chai_collection.json for the config schema. Key ideas baked in
(learned the hard way — see LEARNINGS.md):

  * FULL-BLEED images. The photo IS the background. Text is a quiet caption
    over a smooth bottom gradient — never a competing block in a separate zone.
  * ONE focal point per beat. "card" beats are text-only (title / CTA);
    "photo" beats are image-first. Separating text moments from image moments
    in TIME is what fixes the "where do I look?" problem.
  * Smooth bottom scrim, darkest at the very bottom, easing to 0 going up.
    (An inverted/short gradient creates a visible hard line — don't.)
  * Slow pacing. ~5.5s holds + ~1.0s dissolves read calm and premium.
  * Per-image crop focus (focus_x) so the subject/tin isn't cropped off when
    a landscape photo is cover-cropped to a tall frame.
  * Brand type: Playfair Display (headings, weight 400 — NEVER bold) +
    Open Sans (body). Copper #9E5F24 is the ONLY accent.

Render reliability note: render each beat to its own clip, THEN stitch. A long
single ffmpeg pass can exceed sandbox time limits; clips are cheap to resume.
"""
import json, os, sys, subprocess, math
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont

# ----------------------------- font resolution -----------------------------
# Priority: explicit path -> font_dir/<google name> -> fallback_dir look-alike -> DejaVu
GOOGLE = {
    "head": "PlayfairDisplay-Regular.ttf",
    "body": "OpenSans-Regular.ttf",
    "body_bold": "OpenSans-Bold.ttf",
}
FALLBACK = {  # decent stand-ins if the real brand fonts aren't present
    "head": ["Lora-Regular.ttf", "PlayfairDisplay-Regular.ttf", "DejaVuSerif.ttf"],
    "body": ["WorkSans-Regular.ttf", "OpenSans-Regular.ttf", "DejaVuSans.ttf"],
    "body_bold": ["WorkSans-Bold.ttf", "OpenSans-Bold.ttf", "DejaVuSans-Bold.ttf"],
}
DEJAVU = {
    "head": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "body": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "body_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}

def resolve_font(role, cfg):
    explicit = (cfg.get("fonts") or {}).get(role)
    if explicit and os.path.exists(explicit):
        return explicit, False
    for d in [cfg.get("font_dir"), cfg.get("fallback_font_dir")]:
        if d and os.path.exists(os.path.join(d, GOOGLE[role])):
            return os.path.join(d, GOOGLE[role]), False
    for d in [cfg.get("fallback_font_dir")]:
        if d:
            for cand in FALLBACK[role]:
                if os.path.exists(os.path.join(d, cand)):
                    return os.path.join(d, cand), True  # stand-in
    if os.path.exists(DEJAVU[role]):
        return DEJAVU[role], True
    raise SystemExit(f"No font found for '{role}'. Provide fonts.{role} or font_dir in config.")

# ----------------------------- image helpers -----------------------------
def cover(img, w, h, fx=0.5):
    r = max(w / img.width, h / img.height)
    n = img.resize((int(img.width * r), int(img.height * r)))
    x = int(round((n.width - w) * fx)); y = (n.height - h) // 2
    return n.crop((x, y, x + w, y + h))

def base_photo(path, W, H, fx, dim):
    src = Image.open(path).convert("RGB")
    return ImageEnhance.Brightness(cover(src, W, H, fx)).enhance(dim)

def base_card(W, H, char, copper):
    im = Image.new("RGB", (W, H), tuple(char))
    q = 4; gw, gh = W // q, H // q
    g = Image.new("L", (gw, gh), 0)
    ImageDraw.Draw(g).ellipse([gw*0.2, gh*0.3, gw*0.8, gh*0.7], fill=70)
    g = g.filter(ImageFilter.GaussianBlur(60)).resize((W, H))
    return Image.composite(Image.new("RGB", (W, H), tuple(copper)), im, g)

def tracked(d, pos, t, font, fill, tr, sh=True):
    x, y = pos
    for c in t:
        if sh: d.text((x+2, y+2), c, font=font, fill=(0, 0, 0, 150))
        d.text((x, y), c, font=font, fill=tuple(fill)+(255,)); x += d.textlength(c, font=font) + tr
def twidth(d, t, font, tr):
    return sum(d.textlength(c, font=font) + tr for c in t) - (tr if t else 0)

def overlay_photo(W, H, ov, hl, desc, idx, F, C):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); px = im.load()
    band = int(H * 0.58)
    for yy in range(band):                       # darkest at very bottom -> smooth fade up (no hard line)
        frac = (band - yy) / band
        a = int(210 * frac ** 1.8)
        for xx in range(W): px[xx, H-1-yy] = (8, 5, 3, a)
    d = ImageDraw.Draw(im); L = int(W * 0.075)
    f_ov = ImageFont.truetype(F["body_bold"], int(W*0.028)); f_de = ImageFont.truetype(F["body"], int(W*0.033))
    hs = int(W*0.095)
    while max(d.textlength(x, font=ImageFont.truetype(F["head"], hs)) for x in hl.split("\n")) > W*0.86 and hs > int(W*0.06): hs -= 3
    f_hl = ImageFont.truetype(F["head"], hs); lines = hl.split("\n")
    blk = int(W*0.028*1.6) + len(lines)*int(hs*1.08) + int(W*0.05) + int(W*0.033*1.4)
    y = int(H*0.88) - blk
    tracked(d, (L, y), ov, f_ov, C["copper"], int(W*0.011)); y += int(W*0.028*1.7)
    for ln in lines:
        d.text((L+2, y+3), ln, font=f_hl, fill=(0,0,0,160)); d.text((L, y), ln, font=f_hl, fill=tuple(C["white"])+(255,)); y += int(hs*1.08)
    y += int(W*0.012); d.line([L, y, L+int(W*0.12), y], fill=tuple(C["copper"])+(255,), width=3); y += int(W*0.028)
    tracked(d, (L, y), desc, f_de, C["soft"], int(W*0.003))
    if idx:
        f_ix = ImageFont.truetype(F["body_bold"], int(W*0.026)); iw = twidth(d, idx, f_ix, int(W*0.006))
        tracked(d, (W-L-iw, int(H*0.905)), idx, f_ix, C["copper"], int(W*0.006))
    return im

def overlay_vignette(W, H):
    """Clean cinematic vignette for caption-less 'film' beats (VO-driven pieces).
    Subtle edge darkening, transparent center — lets the photo + voiceover carry."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    v = Image.new("L", (W, H), 0)
    ImageDraw.Draw(v).ellipse([-W*0.15, -H*0.10, W*1.15, H*1.10], fill=255)
    v = v.filter(ImageFilter.GaussianBlur(int(min(W, H) * 0.18)))
    dark = Image.new("RGBA", (W, H), (6, 4, 3, 90))
    return Image.composite(Image.new("RGBA", (W, H), (0, 0, 0, 0)), dark, v)

def overlay_card(W, H, ov, hl, desc, F, C):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f_ov = ImageFont.truetype(F["body_bold"], int(W*0.030)); f_de = ImageFont.truetype(F["body"], int(W*0.036))
    hs = int(W*0.135)
    while max(d.textlength(x, font=ImageFont.truetype(F["head"], hs)) for x in hl.split("\n")) > W*0.84 and hs > int(W*0.07): hs -= 3
    f_hl = ImageFont.truetype(F["head"], hs); lines = hl.split("\n")
    total = int(W*0.030*1.7) + len(lines)*int(hs*1.1) + int(W*0.06) + int(W*0.036*1.4)
    y = (H - total)//2
    ow = twidth(d, ov, f_ov, int(W*0.013)); tracked(d, ((W-ow)//2, y), ov, f_ov, C["copper"], int(W*0.013), sh=False); y += int(W*0.030*1.8)
    for ln in lines:
        lw = d.textlength(ln, font=f_hl); d.text(((W-lw)//2, y), ln, font=f_hl, fill=tuple(C["white"])+(255,)); y += int(hs*1.1)
    y += int(W*0.018); d.line([(W-int(W*0.10))//2, y, (W+int(W*0.10))//2, y], fill=tuple(C["copper"])+(255,), width=3); y += int(W*0.03)
    dw = twidth(d, desc, f_de, int(W*0.004)); tracked(d, ((W-dw)//2, y), desc, f_de, C["soft"], int(W*0.004), sh=False)
    return im

# ----------------------------- render -----------------------------
FORMATS = {"9x16": (1080, 1920), "1x1": (1080, 1080), "16x9": (1920, 1080)}

def run(cmd): subprocess.run(cmd, check=True)

def render_format(cfg, fmt, F, C):
    W, H = FORMATS[fmt]; FPS = 30
    name = cfg["doc_name"]; out_dir = cfg.get("output_dir", os.getcwd())
    wd = os.path.join("/tmp", f"sp_reel_{name}_{fmt}"); os.makedirs(wd, exist_ok=True)
    T = float(cfg.get("transition_dur", 1.0)); trans = cfg.get("transition", "fade")
    beats = cfg["beats"]; clips = []; durs = []
    SS = float(cfg.get("supersample", 2))   # render Ken Burns at SSx, then downscale -> kills zoompan pixel-step jitter
    WS, HS = int(round(W * SS)), int(round(H * SS))
    for i, b in enumerate(beats):
        dur = float(b.get("dur", 5.6 if b["type"] == "photo" else 3.8)); durs.append(dur)
        cp = f"{wd}/c{i}.mp4"
        if os.path.exists(cp) and os.path.getsize(cp) > 20000:
            clips.append(cp); continue          # resume: this clip is already rendered
        if b["type"] == "photo":
            base = base_photo(b["image"], WS, HS, float(b.get("focus_x", 0.5)), float(cfg.get("photo_dim", 0.96)))
            has_text = any(b.get(k) for k in ("overline", "headline", "desc", "index"))
            if has_text:
                txt = overlay_photo(W, H, b.get("overline", ""), b.get("headline", ""), b.get("desc", ""), b.get("index", ""), F, C)
            else:  # clean cinematic beat (no caption) — for VO-driven films
                txt = overlay_vignette(W, H)
        else:
            base = base_card(WS, HS, C["char"], C["copper"])
            txt = overlay_card(W, H, b.get("overline", ""), b["headline"], b.get("desc", ""), F, C)
        bp = f"{wd}/b{i}.png"; base.save(bp); tp = f"{wd}/t{i}.png"; txt.save(tp)
        zin = "zoom+0.0006" if i % 2 == 0 else "if(eq(on,1),1.07,zoom-0.0006)"
        # zoompan runs on the SSx canvas (integer pan rounding is sub-pixel at final res), then lanczos downscale = smooth glide
        vf = (f"[0:v]zoompan=z='min({zin},1.08)':d={int(dur*FPS)}:"
              f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={WS}x{HS}:fps={FPS},"
              f"scale={W}:{H}:flags=bilinear[bg];"
              f"[1:v]format=rgba,fade=t=in:st=0:d=0.6:alpha=1[tx];[bg][tx]overlay=0:0,format=yuv420p[v]")
        tmp = f"{wd}/c{i}.tmp.mp4"               # atomic write: a killed render never leaves a corrupt clip
        run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", bp, "-loop", "1", "-i", tp,
             "-filter_complex", vf, "-map", "[v]", "-t", str(dur), "-r", str(FPS),
             "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20", "-pix_fmt", "yuv420p", tmp])
        os.replace(tmp, cp)
        clips.append(cp)
    # xfade chain
    ins = []
    for c in clips: ins += ["-i", c]
    fc = ""; prev = "0:v"; total = durs[0]
    for i in range(1, len(clips)):
        off = total - T; fc += f"[{prev}][{i}:v]xfade=transition={trans}:duration={T}:offset={off:.3f}[x{i}];"; prev = f"x{i}"; total += durs[i] - T
    fc = fc.rstrip(";")
    silent = os.path.join(out_dir, f"{name}_{fmt}.mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", fc, "-map", f"[{prev}]",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", silent])
    mux_audio(cfg, silent, out_dir, name, fmt, total)
    print(f"  wrote {silent} ({total:.1f}s)")

def mux_audio(cfg, silent, out_dir, name, fmt, total):
    """Mix optional music (bed) + voiceover into the silent reel.
    - music: full-volume bed if alone; ducked under VO if both present.
    - voiceover: laid on top, optionally delayed by voiceover_start seconds.
    Both get gentle fades. Output length tracks the video (-shortest)."""
    music = cfg.get("music") or cfg.get("audio")
    vo = cfg.get("voiceover")
    music = music if (music and os.path.exists(music)) else None
    vo = vo if (vo and os.path.exists(vo)) else None
    if not music and not vo:
        return
    outp = os.path.join(out_dir, f"{name}_{fmt}_audio.mp4")
    fout = max(0.0, total - 2)
    ins = ["-i", silent]
    if music:
        ins += ["-i", music]
    if vo:
        ins += ["-i", vo]
    music_idx = 1 if music else None
    vo_idx = (2 if music else 1) if vo else None
    music_gain = float(cfg.get("music_gain", 0.22 if vo else 1.0))
    vo_start = float(cfg.get("voiceover_start", 0.0))
    parts = []
    if music:
        parts.append(f"[{music_idx}:a]volume={music_gain},afade=t=in:st=0:d=1.5,afade=t=out:st={fout:.2f}:d=2[m]")
    if vo:
        delay = int(vo_start * 1000)
        parts.append(f"[{vo_idx}:a]adelay={delay}|{delay},afade=t=in:st={vo_start:.2f}:d=0.3[v]")
    if music and vo:
        parts.append("[m][v]amix=inputs=2:duration=first:normalize=0[a]")
        amap = "[a]"
    elif music:
        amap = "[m]"
    else:
        amap = "[v]"
    run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", ";".join(parts),
         "-map", "0:v", "-map", amap, "-c:v", "copy", "-c:a", "aac", "-shortest", outp])
    tag = "music+VO" if (music and vo) else ("music" if music else "VO")
    print(f"  wrote {outp} (with {tag})")

def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: render_stills_reel.py config.json")
    cfg = json.load(open(sys.argv[1]))
    # resolve fonts once
    F = {}; standin = False
    for role in ("head", "body", "body_bold"):
        p, s = resolve_font(role, cfg); F[role] = p; standin = standin or s
    print(f"fonts: head={os.path.basename(F['head'])} body={os.path.basename(F['body'])}"
          f"{'  [STAND-IN — drop real brand fonts for final]' if standin else ''}")
    dC = {"copper": [158, 95, 36], "white": [255, 255, 255], "char": [18, 18, 18], "soft": [236, 232, 226]}
    C = {**dC, **(cfg.get("colors") or {})}
    for fmt in cfg.get("formats", ["9x16"]):
        print(f"[{fmt}]"); render_format(cfg, fmt, F, C)

if __name__ == "__main__":
    main()
