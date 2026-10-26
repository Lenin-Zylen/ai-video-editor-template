# First-time setup (runbook for Claude)

Run this once per computer, before any editing. It is done when `.setup-done` exists at the repo root
(`python tools/setup.py status` exits 0). The marker is local and is not in git, so every new computer
runs setup once.

The person may not be technical. Detect first, ask only what you cannot detect, and ask everything in
**one** question round. Explain each install in one plain sentence. Never install without their OK.

---

## Step 0 — Python

`tools/setup.py` needs Python 3.10+. Check with `python --version` (or `python3 --version`, or `py --version` on Windows).
If it is missing, ask the person to install it first:

| OS | Command |
|---|---|
| macOS | `brew install python` (no Homebrew? `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`) |
| Ubuntu / Debian | `sudo apt update && sudo apt install -y python3 python3-pip` |
| Fedora | `sudo dnf install -y python3` |
| Windows | `winget install -e --id Python.Python.3.12`, or the installer from python.org (tick "Add python.exe to PATH") |

Use `python3` instead of `python` on macOS and Linux if `python` is not found.

## Step 1 — Detect

```
python tools/setup.py detect
python tools/setup.py plan
```
`detect` reports the OS, package managers, RAM, free disk and every tool. `plan` lists the missing tools
with the install commands for this OS. Summarise the result for the person in 3–5 short lines:
what the computer is, what is already installed, what is missing.

If `plan` shows nothing missing, skip to Step 4.

## Step 2 — Ask (one round, with the AskUserQuestion tool)

Ask only the questions that apply:

1. **Install now?** "I need to install: <missing list>. Install them now?"
   Options: *Yes, install everything (recommended)* · *Show me the commands, I will run them* · *Skip the optional tools*.
2. **Video language** (picks the speech model; skip if `brand/channel.json` already has `language.whisper_model`
   and that model is on the computer): "Which language will your videos be spoken in?"
   *English (small.en, 466 MB)* · *English with a strong accent (medium.en, 1.5 GB)* ·
   *Another language or a mix, e.g. Tamil + English (small, multilingual, 466 MB)* ·
   *Another language, best accuracy (medium, multilingual, 1.5 GB)*.
   Write the answer to `brand/channel.json` → `language.spoken` and `language.whisper_model`.
3. **Extras** (multi-select, all optional):
   *yt-dlp: download reference reels* · *HeyGen CLI: music catalog (needs a HeyGen account)* ·
   *Remotion: code videos in React*.
4. **Low resources warning** (only if RAM is under 8 GB or free disk under 10 GB): tell them renders may be slow
   or fail, and suggest closing apps. This is a statement, not a question.

## Step 3 — Install

Run the commands from `plan` in order: package manager (Homebrew on macOS) → git → node → ffmpeg → whisper → model → hyperframes.

- **Commands that need a password or Administrator rights** (`sudo ...`, `choco ...`, installer windows):
  do not run them yourself. Ask the person to run them in their own terminal, or in Claude Code
  by typing `!` followed by the command. Wait for them to say it is done.
- **Commands without a password** (`brew`, `winget`, `npm install -g`, `python tools/setup.py ...`): run them yourself.
- **Downloads done by the helper** (from official sources only):
  - `python tools/setup.py model --size small.en` → Hugging Face `ggerganov/whisper.cpp`
  - `python tools/setup.py whisper-windows` → the newest `whisper-bin-x64.zip` from github.com/ggml-org/whisper.cpp releases
  - `python tools/setup.py ffmpeg-windows` → gyan.dev FFmpeg essentials (only if there is no winget, choco or scoop)
  They save into `~/ai-editor-tools/` unless the person chose another folder (`--dir`).
- **HyperFrames:** `npm install -g hyperframes`, then `npx hyperframes skills update` (installs the Claude Code skills
  for video work; tell the person to restart Claude Code afterwards so the skills load).
- **Windows PATH:** programs installed with winget or choco are on the PATH only in new terminals.
  If `detect` still misses them, that is fine: `write-config` stores the full paths.
- **Linux whisper.cpp** is built from source (about 5 minutes). With an NVIDIA GPU the plan adds `-DGGML_CUDA=1`;
  if that build fails, rebuild without it.
- If a step fails, show the last lines of the error, fix the cause (missing build tools, no permission, no network),
  and continue. Do not loop on the same failing command.

Optional extras, only if chosen:
- yt-dlp: the plan's `yt_dlp` command.
- HeyGen CLI: point them to https://developers.heygen.com/cli; they run `heygen auth login --oauth` themselves.
- Remotion: nothing global; later `npx create-video@latest` in a project (on Windows with Docker, pass `--port=3123`).

## Step 4 — Configure and verify

```
python tools/setup.py write-config     # writes editor.config.json with the found paths
python tools/setup.py done             # runs tools/check_setup.py, creates the folders, then writes .setup-done
```
`done` also creates the workspace folders that git does not carry: `raw-footages/`, `references/_analysis/`,
`work/`, `exports/`, `renders/` (folder map: `docs/WORKFLOW.md`). To create them again, run `python tools/setup.py folders`.
`done` refuses to write the marker while something required is missing. Fix it and run it again.

Then add a line to the memory (if memory is available): the OS, where the tools live, the whisper model.

## Step 5 — Hand over

Tell the person, in short lines:
- setup is complete and will not run again on this computer;
- what was installed and where;
- the next step. Run `python tools/intake.py status`: if the channel details are missing, continue straight
  into the channel intake (`docs/CHANNEL_INTAKE.md`) in the same session. Otherwise: put clips in
  `raw-footages/<slug>/` with the script and ask for an edit.

## Re-running

To run setup again (new computer, broken install): delete `.setup-done`, or type `/setup`.
