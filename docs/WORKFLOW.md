# Workflow: from raw clips to four platforms

This workspace makes short vertical videos (1080 × 1920) for Instagram, YouTube Shorts, Facebook Reels and X.
Claude Code does the editing. You give it footage, the script and your decisions.

Read `brand/BRAND.md` first. Every edit follows it.

## Folder map

| Folder | What is in it | In git? |
|---|---|---|
| `brand/` | Brand rules, brand sheet, logo | yes |
| `tools/` | The editor scripts (Python, no extra packages) | yes |
| `docs/` | This workflow, recording checklist, platform specs | yes |
| `template/` | Starter kit to set up a new channel | yes |
| `projects/<slug>/` | One HyperFrames project per video: `edit.json`, scenes, cover | yes (no media) |
| `raw-footages/<slug>/` | Camera clips for one video | no |
| `references/` | Reference reels for the brand | no |
| `work/<slug>/` | Scratch: WAVs, transcripts, the cut, the master | no |
| `exports/<slug>/` | Finished files per platform | no |

## The steps

1. **Put the footage in its own folder.** `raw-footages/<slug>/` (for example `day04-sonnet`). One video per folder.
   Put the script PDF next to it.
2. **Create the project.** Ask Claude: "New video `<slug>` from `raw-footages/<slug>` with this script."
   Claude runs `npx hyperframes init projects/<slug> --example blank --resolution portrait`,
   copies the fonts, logos and sound effects from `examples/reel-day03/assets/` and `brand/logo/`, and writes `projects/<slug>/edit.json`.
3. **Transcribe and pick takes.**
   ```
   python tools/transcribe_clips.py projects/<slug>/edit.json
   ```
   Claude compares each take with the script and fills `"takes"` in `edit.json` (clip, start, end per line).
   You approve or correct the takes ("use clip X from 1:22 to 1:27").
4. **Cut.**
   ```
   python tools/cut.py projects/<slug>/edit.json
   ```
   This removes every pause longer than `max_pause` (default 0.1 s) and reports any that are left.
5. **Storyboard and scenes.** Claude builds the scenes in `projects/<slug>/compositions/`, poses the
   storyboard (`boards/storyboard.html`) and waits for your go.
6. **Captions.**
   ```
   python tools/captions.py projects/<slug>/edit.json
   ```
7. **Check and draft.** `npx hyperframes check`, snapshots, then a draft render
   (`npx hyperframes render -q draft -o exports/<slug>/drafts/<slug>_DRAFT.mp4`). You review; give all notes in one pass.
8. **Cover.** Claude builds `projects/<slug>/cover/index.html` (hook headline, your face, handle chip).
9. **Publish.**
   ```
   python tools/publish.py projects/<slug>/edit.json
   ```
   Renders the final, the cover, masters the audio to -14 LUFS and writes `exports/<slug>/{instagram,youtube,facebook,x}/`.

## What makes it fast

- Script PDF and one folder per video from the start.
- Good recording habits (see `docs/RECORDING.md`).
- Music chosen once: tracks in `assets/music/` of an earlier project, or the HeyGen catalog.
- All review notes in one message, with timestamps.
