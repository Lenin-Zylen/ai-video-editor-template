# Install the tools (manual)

You do not need this page if Claude sets up your computer (open the repo in Claude Code; it runs `/setup`
the first time, see `docs/SETUP.md`). Use it if you prefer to install everything yourself.

You need about 30–45 minutes and about 5 GB of free disk space.

Everybody needs: **Git**, **Node.js 22 LTS**, **Python 3.10+**, **FFmpeg**, **whisper.cpp** with an English model,
the **HyperFrames** CLI and **Claude Code**. **yt-dlp** is needed only to download reference reels.

### macOS (Homebrew)

```bash
# Homebrew first, if missing: https://brew.sh
brew install git node@22 python ffmpeg yt-dlp whisper-cpp
npm install -g hyperframes
mkdir -p ~/whisper-models
curl -L -o ~/whisper-models/ggml-small.en.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en.bin
curl -fsSL https://claude.ai/install.sh | bash        # Claude Code
```
Homebrew's whisper-cpp installs the `whisper-cli` command. If `node` is not found, run `brew link node@22`.

### Linux (Ubuntu / Debian)

```bash
sudo apt update
sudo apt install -y git python3 python3-pip pipx ffmpeg build-essential cmake curl
# Node.js 22 with nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc && nvm install 22
npm install -g hyperframes
pipx install yt-dlp
# whisper.cpp from source
git clone https://github.com/ggml-org/whisper.cpp ~/whisper.cpp
cmake -S ~/whisper.cpp -B ~/whisper.cpp/build && cmake --build ~/whisper.cpp/build -j --config Release
sh ~/whisper.cpp/models/download-ggml-model.sh small.en     # saves ~/whisper.cpp/models/ggml-small.en.bin
curl -fsSL https://claude.ai/install.sh | bash             # Claude Code
```
The whisper binary is `~/whisper.cpp/build/bin/whisper-cli`.
HyperFrames renders with headless Chrome; if a render fails on a minimal server, run `npx hyperframes doctor`.

### Windows 10 / 11

With winget (PowerShell):
```powershell
winget install Git.Git OpenJS.NodeJS.LTS Python.Python.3.12 Gyan.FFmpeg yt-dlp.yt-dlp
npm install -g hyperframes
irm https://claude.ai/install.ps1 | iex      # Claude Code
```
If winget is missing, install Git, Node.js 22 LTS and Python 3.12 from their websites,
and download FFmpeg from https://www.gyan.dev/ffmpeg/builds/ (essentials build).

whisper.cpp on Windows:
1. Open https://github.com/ggml-org/whisper.cpp/releases and download `whisper-bin-x64.zip`
   from the newest release that has files (CPU build).
2. Unzip it, for example to `C:\tools\whisper\`. The program is `Release\whisper-cli.exe`.
3. Download the model into `C:\tools\whisper\models\`:
   https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en.bin

### All systems: optional extras
- Better transcripts for strong accents: `ggml-medium.en.bin` (1.5 GB) from the same Hugging Face page.
- Music catalog: install the HeyGen CLI (https://developers.heygen.com/cli) and run `heygen auth login --oauth`.
  Without it, use CC0 tracks (for example from freesound.org via openverse.org) in `assets/music/`.
- Remotion (only if you want to code videos in React): `npx create-video@latest`.

## Point the tools at your programs

Copy `editor.config.example.json` to `editor.config.json` and set `ffmpeg`, `whisper_cli` and `whisper_model`
(leave a key out if the program is on the PATH). Then:

```bash
python tools/check_setup.py           # every required tool found?
npx hyperframes skills update         # Claude Code skills for video work (restart Claude Code after)
python tools/setup.py done            # marks this computer as set up (.setup-done)
```
