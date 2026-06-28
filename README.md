# sp-skills-agents

Spice Pilgrim's own library of **skills** and **agents** — reusable, self-improving
workflows for the brand. Each skill captures hard-won learnings so future sessions
(Cowork, Claude Code, claude.ai) start with full context instead of re-deriving it.

## Layout

```
sp-skills-agents/
├── skills/
│   └── sp-stills-reel/        # stills-as-video social reels (PIL + ffmpeg)
│       ├── SKILL.md
│       ├── scripts/           # render_stills_reel.py (config-driven renderer)
│       ├── references/        # brand-design-system.md (fonts/colors)
│       ├── examples/          # example configs (chai_collection.json)
│       └── LEARNINGS.md       # the skill's memory — append after every use
└── agents/
    └── video-head/            # orchestrator: owns SP social video end-to-end
        ├── AGENT.md
        └── LEARNINGS.md
```

## The self-improving convention

Every skill here carries a `LEARNINGS.md`. The rule: **append a dated entry every
time the skill is used**, and periodically promote stable lessons into the
`SKILL.md` body. Installed skills run read-only, so improvements are made to the
**source copy in this repo** and reinstalled; the LEARNINGS log is the durable
memory between runs.

## Skills

| Skill | What it does | Status |
|---|---|---|
| `sp-stills-reel` | Photos + captions → branded multi-format social video, free | active (v1) |

## Agents

| Agent | What it does | Status |
|---|---|---|
| `video-head` | Orchestrates SP social video end-to-end (concept→script→render→captions→QA→deliver); delegates to sub-roles; uses `sp-stills-reel` | active (v1) |

## Requirements

- Python 3 with Pillow (`pip install pillow`)
- `ffmpeg` / `ffprobe` on PATH
- Brand fonts (Playfair Display, Open Sans) — drop `.ttf` files in a `fonts/` dir
- Brand design source of truth: `brain/spice-pilgrim/design/design.md`
