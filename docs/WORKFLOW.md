# Workflow: from raw clips to four platforms

This workspace makes short vertical videos (1080 × 1920) for Instagram, YouTube Shorts, Facebook Reels and X.
Claude Code does the editing. You give it footage, the script and your decisions.

Read `brand/BRAND.md` first. Every edit follows it.

## Folder map

`python tools/setup.py done` creates the workspace folders at the end of setup.
`python tools/setup.py folders --slug <slug>` creates the folders for one video.
Most of these folders are git-ignored, so a fresh clone does not have them until you run these commands.
What goes into git: `docs/GIT.md`.

```
<repo>/
├── brand/                  brand rules, channel.json, logo, assets              git
├── tools/                  editor scripts (Python, standard library only)       git
├── docs/                   workflow, setup, recording, platforms, git rules     git
├── examples/reel-day03/    the example reel to learn from                        git
├── .claude/commands/       /setup, /intake, /new-video                           git
├── references/             reference reels for the brand
│   ├── <id>/<id>.info.json     metadata (title, channel, counts)                 git
│   ├── <id>/*.mp4              the video                                         local
│   └── _analysis/<id>/         cuts.txt, transcript.srt, words.srt, sheet.jpg, frames/   git
├── raw-footages/<slug>/    camera clips and the script for one video             local
├── projects/<slug>/        one HyperFrames project per video                     git (no media)
│   ├── edit.json, index.html, hyperframes.json, package.json, STORYBOARD.md
│   ├── compositions/           one HTML file per scene, captions.html
│   ├── boards/                 storyboard.html (boards/stills/redo/ is local)
│   ├── cover/                  index.html, cover.png, assets/logos/ (cover/shot/ is local)
│   └── assets/
│       ├── fonts/, logos/, screens/    small files                               git
│       ├── sfx/, music/, meme/         audio and video clips                     local
│       ├── cut.mp4                     written by tools/cut.py                    local
│       └── transcript.json             generated                                  local
├── work/<slug>/            scratch: WAVs, clips/ word times, the cut, the master local
├── exports/<slug>/         drafts/, then instagram/, youtube/, facebook/, x/     local
├── renders/                other renders                                          local
├── editor.config.json      tool paths for this computer                           local
└── .setup-done             setup marker for this computer                         local
```

Put the screenshots for a video in `assets/screens/`, sound effects in `assets/sfx/`, music in `assets/music/`
(with a `CREDITS.md`), and meme or stock clips in `assets/meme/` (with a `CREDITS.md`).
Keep downloads and captures in `work/<slug>/` until you pick the final file.

## The steps

1. **Put the footage in its own folder.** `raw-footages/<slug>/` (for example `day04-sonnet`). One video per folder.
   Put the script PDF next to it.
2. **Create the project.** Ask Claude: "New video `<slug>` from `raw-footages/<slug>` with this script."
   Claude runs `npx hyperframes init projects/<slug> --example blank --resolution portrait`,
   runs `python tools/setup.py folders --slug <slug>` to add the video folders (see the folder map),
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
