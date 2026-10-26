# ai-video-editor-template

A ready-made AI video editor for one channel: talking-head reels and shorts with captions, motion graphics,
sound effects, music, a cover, and exports for Instagram, YouTube, Facebook and X. Long-form 16:9 is supported too.
You direct it in plain English with **Claude Code**; it edits with **HyperFrames**, **FFmpeg** and **whisper.cpp**.

## Start your own editor (one repo per channel)

1. On GitHub, open this repo and click **Use this template → Create a new repository**.
   Name it after your channel, for example **`ganeshbuildsai-editor`**, and keep it **private**.
   (Or: `gh repo create ganeshbuildsai-editor --private --template Lenin-Zylen/ai-video-editor-template --clone`.)
2. Clone your new repo and open the folder in Claude Code:
   ```bash
   git clone https://github.com/<you>/ganeshbuildsai-editor
   cd ganeshbuildsai-editor
   claude
   ```
   You only need **Claude Code** and **Python 3.10+** installed:

   | OS | Claude Code | Python |
   |---|---|---|
   | macOS | `curl -fsSL https://claude.ai/install.sh \| bash` | `brew install python` |
   | Linux | `curl -fsSL https://claude.ai/install.sh \| bash` | `sudo apt install -y python3` |
   | Windows | `irm https://claude.ai/install.ps1 \| iex` (PowerShell) | `winget install -e --id Python.Python.3.12` |

3. Say hello. The first time, Claude:
   - **sets up the computer** (`/setup`): detects your OS, asks a few questions in one round
     (install now? video language? extras?), installs FFmpeg, whisper.cpp + speech model, Node.js and HyperFrames
     with your OK, and verifies them. Once per computer.
   - **asks about your brand** (`/intake`): company or personal, short or long form, language, platforms, tone,
     motion level, on-camera style, call to action, then one fill-in message for names, handles, website, audience,
     **logo files, colours, fonts, brand guide, other assets**, 3 reference videos, music policy and things to avoid.
     Have your logo (SVG or transparent PNG) and brand colours ready.
   - **builds your brand sheet** from your assets and references, and waits for your approval.
4. Make videos: record with `docs/RECORDING.md`, put the clips in `raw-footages/<slug>/` with the script, and say
   "Edit `<slug>` into a reel. Show me a storyboard first." (or `/new-video <slug>`).

## What is inside

| Path | What |
|---|---|
| `CLAUDE.md` | How Claude works here: setup → intake → brand → edit |
| `tools/` | `setup.py`, `intake.py`, `init_channel.py`, `transcribe_clips.py`, `cut.py`, `captions.py`, `publish.py`, `check_setup.py` (Python, standard library only) |
| `docs/` | `SETUP.md`, `CHANNEL_INTAKE.md`, `WORKFLOW.md`, `RECORDING.md`, `PLATFORMS.md`, `INSTALL.md` (manual install for macOS, Linux, Windows), `GIT.md` (what to commit, what to keep local) |
| `brand/` | `channel.json` (your channel profile, filled by the intake), `BRAND.md` (starter rules until your brand is approved), `logo/`, `assets/` |
| `examples/reel-day03/` | A complete 28 s reel (HyperFrames scenes, captions, transitions, sound effects, cover, `edit.json`) to learn from |
| `.claude/commands/` | `/setup`, `/intake`, `/new-video` |

## Getting template updates later

```bash
git remote add template https://github.com/Lenin-Zylen/ai-video-editor-template
git fetch template
git merge template/main --allow-unrelated-histories   # first time; afterwards just: git merge template/main
```
Your `brand/`, `projects/` and local media are yours; review conflicts in `tools/` and `docs/`.

## Credits and licences
- Fonts: Archivo, Inter, JetBrains Mono (SIL Open Font License).
- Sound effects in the example: Pixabay Content License (`examples/reel-day03/assets/sfx/CREDITS.md`).
- Product logos in the example: theSVG (OpenAI: MIT; Google Calendar, Google Drive: CC0). Use logos only to refer to the product.
