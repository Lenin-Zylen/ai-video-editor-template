---
description: Start a new video edit from raw-footages/<slug> (takes, cut, storyboard, captions, draft, cover, publish)
---

Start a new video: `$ARGUMENTS` (the slug, e.g. `day04-sonnet`; ask for it if missing).

1. Check `.setup-done` and `python tools/intake.py status`; finish setup or the intake first if needed.
   Check that `brand/BRAND.md` is approved (not DRAFT).
2. Read `brand/BRAND.md`, `brand/channel.json`, `docs/WORKFLOW.md`, and the script in `raw-footages/<slug>/`.
   If the folder mixes clips from different videos, ask which ones belong to this video.
3. Create `projects/<slug>` with HyperFrames (portrait for short form, landscape for long form), copy fonts,
   logos and sound effects from `examples/reel-day03/assets/` and `brand/logo/`, and write `projects/<slug>/edit.json`.
4. `python tools/transcribe_clips.py projects/<slug>/edit.json`, pick the best take for every script line,
   show the take list, then `python tools/cut.py projects/<slug>/edit.json`.
5. Build the scenes and the storyboard; stop and wait for approval.
6. Captions (`python tools/captions.py`), `npx hyperframes check`, snapshots, a draft render to `exports/<slug>/drafts/`.
7. After the person's notes: cover, music, then `python tools/publish.py projects/<slug>/edit.json`.
