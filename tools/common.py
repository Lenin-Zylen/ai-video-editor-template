"""Shared helpers for the editor tools: paths, config, ffmpeg and whisper.cpp lookup.

Works on macOS, Linux and Windows with Python 3.10+ and no extra packages.
Tool locations come from (first match wins):
  1. environment variables FFMPEG, WHISPER_CLI, WHISPER_MODEL
  2. editor.config.json at the repo root (copy editor.config.example.json)
  3. the PATH (ffmpeg, whisper-cli / whisper-cpp)
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def local_config():
    p = ROOT / "editor.config.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def tool(env, key, *names):
    """Find an executable from the env var, editor.config.json, then the PATH."""
    cfg = local_config()
    for cand in (os.environ.get(env), cfg.get(key)):
        if cand and Path(cand).expanduser().exists():
            return str(Path(cand).expanduser())
    for n in names:
        found = shutil.which(n)
        if found:
            return found
    sys.exit(f"{names[0]} not found: set {env} or '{key}' in editor.config.json, or put it on the PATH")


def ffmpeg():
    return tool("FFMPEG", "ffmpeg", "ffmpeg")


def whisper_cli():
    return tool("WHISPER_CLI", "whisper_cli", "whisper-cli", "whisper-cpp")


def whisper_model():
    cfg = local_config()
    m = os.environ.get("WHISPER_MODEL") or cfg.get("whisper_model")
    if not m or not Path(m).expanduser().exists():
        sys.exit("Whisper model not found: set WHISPER_MODEL or 'whisper_model' in editor.config.json "
                 "(ggml-small.en.bin or ggml-medium.en.bin)")
    return str(Path(m).expanduser())


def load_video(config_path):
    """Read projects/<slug>/edit.json and resolve its paths against the repo root."""
    p = Path(config_path)
    if not p.is_absolute():
        p = (Path.cwd() / p).resolve()
    cfg = json.loads(p.read_text(encoding="utf-8"))
    cfg["_path"] = p
    cfg["_project"] = p.parent
    cfg["_raw"] = ROOT / cfg["raw_dir"]
    cfg["_work"] = ROOT / "work" / cfg["slug"]
    cfg["_work"].mkdir(parents=True, exist_ok=True)
    return cfg


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def wav16k(src, dst):
    """Mono 16 kHz WAV for whisper and silence detection (cached)."""
    dst = Path(dst)
    if not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(src), "-ar", "16000", "-ac", "1", str(dst)])
    return dst


def whisper_words(wav, out_base, prompt=None):
    """Word-level transcript: returns [(start, end, word)] and writes <out_base>.csv."""
    cmd = [whisper_cli(), "-m", whisper_model(), "-f", str(wav), "-ml", "1", "-sow",
           "-ocsv", "-of", str(out_base), "-np", "-t", str(os.cpu_count() or 4)]
    if prompt:
        cmd += ["--prompt", prompt]
    run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    import csv
    rows = list(csv.reader(open(f"{out_base}.csv", encoding="utf-8")))[1:]
    return [(int(r[0]) / 1000, int(r[1]) / 1000, r[2].strip()) for r in rows if r[2].strip()]


def duration(path):
    out = subprocess.run([ffmpeg(), "-i", str(path)], capture_output=True, text=True).stderr
    for line in out.splitlines():
        if "Duration:" in line:
            h, m, s = line.split("Duration:")[1].split(",")[0].strip().split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    return 0.0
