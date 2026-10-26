# AI video editor — instructions for Claude

This repo edits videos for **one channel**: the one in `brand/channel.json` (personal or company brand).
Short form (Reels, Shorts, TikTok, 9:16) and long form (YouTube, 16:9) for Instagram, YouTube, Facebook, X and more.
It was created from the `ai-video-editor-template` repo.

## FIRST: is this computer set up? (check at the start of every session)
- If the file `.setup-done` does **not** exist at the repo root, this computer has not been set up.
  Before you do anything else (even if the person asks for an edit), say so in one line and run the
  first-time setup in `docs/SETUP.md`: detect the system, ask the setup questions in one round,
  install the missing tools with the person's OK, then `python tools/setup.py done`.
- If `.setup-done` exists, setup is complete: never ask the setup questions again.
  Run `/setup` only when the person asks or a tool is broken.

## SECOND: do we know the brand and the channel? (right after setup, or before the first edit)
- Run `python tools/intake.py status`. If it is not complete, run the channel intake in
  `docs/CHANNEL_INTAKE.md` before planning any video: company or personal brand, short or long form,
  language, platforms, logo and brand assets, colours, fonts, references, tone, motion level, CTA, music, things to avoid.
  Ask only for the missing details. `/intake` runs it again on request.
- `brand/channel.json` is the source of truth for these details; `brand/CHANNEL.md` is its readable copy.
- When the intake has the channel name, update the title of `README.md` to `<handle>-ai-editor` and this repo's
  description if the person wants (`python tools/init_channel.py --handle <handle> --name "<name>"` does it).

## THIRD: the brand rules
- `brand/BRAND.md` starts as a STARTER (DRAFT). The intake builds the channel's own brand sheet
  (`brand/brand-sheet.html` + `brand/BRAND.md`) from its assets and references and asks for approval.
  **Do not edit a video while BRAND.md says DRAFT.**
- After approval: read `brand/BRAND.md`, `brand/channel.json` and `brand/CHANNEL.md` before every edit and follow them.
  Do not change the brand rules without the person's approval; if a request conflicts with a rule, name the rule and ask.

## How to make a video
Follow `docs/WORKFLOW.md` (or `/new-video <slug>`). In short:
1. Footage in `raw-footages/<slug>/`, script next to it. One video per folder; ask if a folder mixes videos.
2. `npx hyperframes init projects/<slug> --example blank --resolution portrait` (or `landscape` for long form);
   write `projects/<slug>/edit.json` (see `examples/reel-day03/edit.json`).
3. `python tools/transcribe_clips.py` → pick takes against the script → `python tools/cut.py` → scenes and storyboard →
   `python tools/captions.py` → `npx hyperframes check`, snapshots, draft → cover → `python tools/publish.py`.
4. Match the script cut by cut. Captions are verbatim; on-screen prompts and quotes use the script's exact wording.
5. Show a storyboard before building and a draft before the final. Ask for all notes in one pass.

## Default editing rules (change them in channel.json / BRAND.md)
- Cut every pause longer than `production.max_pause_s` (default 0.1 s); report any that remain.
- Pick takes by checking each one: no looking down, no wrong words, no stray "okay"; ask for the clip and timecode
  when unsure, or cover the line with full-screen graphics (voice only).
- Snap every cut to the frame grid (tools/cut.py does) so captions stay in sync.
- Use the speech model from `language.whisper_model` (multilingual for non-English or mixed speech).
- Motion follows `style.motion`. Sound effects only on visible actions. Music from `assets.music.policy`.
- Check rendered files: duration, no pauses over the limit, loudness −14 LUFS, frames inside the safe areas (`docs/PLATFORMS.md`).

## Folders
- Folder map: `docs/WORKFLOW.md`. Setup creates the workspace folders; `python tools/setup.py folders --slug <slug>`
  creates the folders for one video. Run it again if a fresh clone misses a git-ignored folder.
- Do not commit a video file or an audio file. Full rules and checks: `docs/GIT.md`.
- In git: `brand/`, `tools/`, `docs/`, `examples/`, `projects/` (code and small assets only), `.claude/commands/`,
  reference metadata (`references/**/*.info.json`, `references/_analysis/`).
- Local only: `raw-footages/`, `work/`, `exports/`, `renders/`, `editor.config.json`, `.setup-done`,
  all video and audio under `projects/` and `references/`.

## Tools
- ffmpeg and whisper.cpp paths: `editor.config.json` (written by `python tools/setup.py write-config`) or the PATH.
- HyperFrames renders the videos (`npx hyperframes ...`); load its skills (`/hyperframes`) before writing compositions.
- Remotion (optional): if port 3000 is busy (Docker often uses it), pass `--port=3123`; keep Remotion projects in short paths.
