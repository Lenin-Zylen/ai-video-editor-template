"""First-time setup helper for the editor. Claude runs this during /setup (see docs/SETUP.md).

    python tools/setup.py status            # is setup done on this computer? (exit 0 = done)
    python tools/setup.py detect            # JSON: OS, package managers, tools, RAM, disk
    python tools/setup.py plan              # install commands for every missing tool, for this OS
    python tools/setup.py model [--size small.en] [--dir PATH]   # download a whisper.cpp model
    python tools/setup.py whisper-windows [--dir PATH]          # Windows: download + unzip whisper.cpp
    python tools/setup.py ffmpeg-windows [--dir PATH]           # Windows without winget: download FFmpeg
    python tools/setup.py write-config      # write editor.config.json from what is found
    python tools/setup.py done              # verify everything, then write the .setup-done marker

Standard library only, so it runs before anything else is installed (Python 3.10+).
"""
import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER = ROOT / ".setup-done"
CONFIG = ROOT / "editor.config.json"
HOME = Path.home()
TOOLS_DIR = HOME / "ai-editor-tools"        # default place for downloaded tools and models
MODEL_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-{size}.bin"
MODEL_MB = {"base.en": 142, "small.en": 466, "medium.en": 1500, "small": 466, "medium": 1500}
FFMPEG_WIN_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
WHISPER_RELEASES = "https://api.github.com/repos/ggml-org/whisper.cpp/releases?per_page=20"


# ---------- detection ----------

def os_name():
    s = platform.system()
    return {"Darwin": "macos", "Windows": "windows"}.get(s, "linux" if s == "Linux" else s.lower())


def run_out(cmd, timeout=60):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (r.stdout or r.stderr).strip()
    except Exception:  # noqa: BLE001
        return ""


def which(*names):
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    return None


def linux_distro():
    p = Path("/etc/os-release")
    if not p.exists():
        return ""
    info = dict(l.split("=", 1) for l in p.read_text().splitlines() if "=" in l)
    return info.get("ID", "").strip('"') + " " + info.get("VERSION_ID", "").strip('"')


def ram_gb():
    try:
        if os_name() == "windows":
            import ctypes

            class MS(ctypes.Structure):
                _fields_ = [("l", ctypes.c_ulong), ("load", ctypes.c_ulong), ("total", ctypes.c_ulonglong),
                            ("avail", ctypes.c_ulonglong)] + [(f"x{i}", ctypes.c_ulonglong) for i in range(5)]
            m = MS()
            m.l = ctypes.sizeof(MS)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
            return round(m.total / 2**30, 1), round(m.avail / 2**30, 1)
        if os_name() == "macos":
            return round(int(run_out(["sysctl", "-n", "hw.memsize"])) / 2**30, 1), None
        mem = dict(l.split(":", 1) for l in Path("/proc/meminfo").read_text().splitlines())
        kb = lambda k: int(mem[k].split()[0])
        return round(kb("MemTotal") / 2**20, 1), round(kb("MemAvailable") / 2**20, 1)
    except Exception:  # noqa: BLE001
        return None, None


def config():
    return json.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}


def find_whisper():
    cfg = config().get("whisper_cli")
    if cfg and Path(cfg).expanduser().exists():
        return str(Path(cfg).expanduser())
    p = which("whisper-cli", "whisper-cpp")
    if p:
        return p
    exe = "whisper-cli.exe" if os_name() == "windows" else "whisper-cli"
    for base in (TOOLS_DIR / "whisper", HOME / "whisper.cpp" / "build" / "bin", HOME / ".claude" / "tools" / "whisper",
                 Path("C:/tools/whisper")):
        for f in base.rglob(exe) if base.exists() else []:
            return str(f)
    return None


def find_models():
    cfg = config().get("whisper_model")
    found = [cfg] if cfg and Path(cfg).expanduser().exists() else []
    for base in (TOOLS_DIR / "models", HOME / "whisper-models", HOME / "whisper.cpp" / "models",
                 HOME / ".claude" / "tools" / "whisper" / "models", Path("C:/tools/whisper/models")):
        if base.exists():
            found += [str(f) for f in sorted(base.glob("ggml-*.bin"))]
    return list(dict.fromkeys(str(Path(f).expanduser().resolve()) for f in found))


def find_ffmpeg():
    cfg = config().get("ffmpeg")
    if cfg and Path(cfg).expanduser().exists():
        return str(Path(cfg).expanduser())
    p = which("ffmpeg")
    if p:
        return p
    exe = "ffmpeg.exe" if os_name() == "windows" else "ffmpeg"
    for base in (TOOLS_DIR / "ffmpeg", HOME / ".claude" / "tools" / "ffmpeg", Path("C:/tools/ffmpeg")):
        for f in base.rglob(exe) if base.exists() else []:
            return str(f)
    return None


def detect():
    osn = os_name()
    npx = which("npx.cmd", "npx")
    total, avail = ram_gb()
    hf = run_out([npx, "hyperframes", "--version"], 180) if npx else ""
    tools = {
        "python": {"path": sys.executable, "version": platform.python_version(), "ok": sys.version_info >= (3, 10)},
        "git": {"path": which("git"), "version": run_out(["git", "--version"]) if which("git") else ""},
        "node": {"path": which("node"), "version": run_out(["node", "--version"]) if which("node") else ""},
        "ffmpeg": {"path": find_ffmpeg()},
        "whisper_cli": {"path": find_whisper()},
        "whisper_models": find_models(),
        "hyperframes": {"version": hf.splitlines()[-1] if hf else ""},
        "yt_dlp": {"path": which("yt-dlp")},
        "gh": {"path": which("gh")},
    }
    node_major = int(re.findall(r"v(\d+)", tools["node"]["version"])[0]) if tools["node"]["version"] else 0
    tools["node"]["ok"] = node_major >= 18
    return {
        "os": osn,
        "os_version": platform.mac_ver()[0] if osn == "macos" else (linux_distro() if osn == "linux" else platform.version()),
        "arch": platform.machine(),
        "apple_silicon": osn == "macos" and platform.machine() == "arm64",
        "nvidia_gpu": bool(which("nvidia-smi")),
        "ram_gb_total": total, "ram_gb_free": avail,
        "disk_gb_free_here": round(shutil.disk_usage(ROOT).free / 2**30, 1),
        "package_managers": [m for m in ("brew", "apt", "dnf", "pacman", "winget", "choco", "scoop") if which(m)],
        "tools": tools,
        "setup_done": MARKER.exists(),
        "config_file": str(CONFIG) if CONFIG.exists() else None,
    }


# ---------- install plan ----------

def missing(d):
    t = d["tools"]
    out = []
    if not t["git"]["path"]:
        out.append("git")
    if not t["node"]["ok"]:
        out.append("node")
    if not t["ffmpeg"]["path"]:
        out.append("ffmpeg")
    if not t["whisper_cli"]["path"]:
        out.append("whisper")
    if not t["whisper_models"]:
        out.append("whisper_model")
    if not t["hyperframes"]["version"]:
        out.append("hyperframes")
    if not t["yt_dlp"]["path"]:
        out.append("yt_dlp (optional)")
    return out


def plan(d):
    osn, pms = d["os"], d["package_managers"]
    steps = {}
    if osn == "macos":
        brew = "brew" in pms
        if not brew:
            steps["homebrew"] = ['/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"']
        steps.update({
            "git": ["brew install git"], "node": ["brew install node@22", "brew link --overwrite node@22"],
            "ffmpeg": ["brew install ffmpeg"], "whisper": ["brew install whisper-cpp   # gives `whisper-cli`"],
            "yt_dlp (optional)": ["brew install yt-dlp"]})
    elif osn == "linux":
        pm = "apt" if "apt" in pms else ("dnf" if "dnf" in pms else ("pacman" if "pacman" in pms else "apt"))
        inst = {"apt": "sudo apt update && sudo apt install -y", "dnf": "sudo dnf install -y", "pacman": "sudo pacman -S --needed"}[pm]
        steps.update({
            "git": [f"{inst} git"],
            "node": ["curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash",
                     "export NVM_DIR=\"$HOME/.nvm\" && . \"$NVM_DIR/nvm.sh\" && nvm install 22"],
            "ffmpeg": [f"{inst} ffmpeg"],
            "whisper": [f"{inst} {'build-essential' if pm == 'apt' else 'gcc-c++ make'} cmake",
                        "git clone --depth 1 https://github.com/ggml-org/whisper.cpp ~/whisper.cpp",
                        "cmake -S ~/whisper.cpp -B ~/whisper.cpp/build -DCMAKE_BUILD_TYPE=Release"
                        + (" -DGGML_CUDA=1" if d["nvidia_gpu"] else ""),
                        "cmake --build ~/whisper.cpp/build -j --config Release   # binary: ~/whisper.cpp/build/bin/whisper-cli"],
            "yt_dlp (optional)": [f"{inst} pipx && pipx install yt-dlp"]})
    else:  # windows
        if "winget" in pms:
            steps.update({
                "git": ["winget install -e --id Git.Git"], "node": ["winget install -e --id OpenJS.NodeJS.LTS"],
                "ffmpeg": ["winget install -e --id Gyan.FFmpeg"],
                "yt_dlp (optional)": ["winget install -e --id yt-dlp.yt-dlp"]})
        elif "choco" in pms:   # needs an Administrator terminal
            steps.update({
                "git": ["choco install -y git"], "node": ["choco install -y nodejs-lts"],
                "ffmpeg": ["choco install -y ffmpeg"], "yt_dlp (optional)": ["choco install -y yt-dlp"]})
        elif "scoop" in pms:
            steps.update({
                "git": ["scoop install git"], "node": ["scoop install nodejs-lts"],
                "ffmpeg": ["scoop install ffmpeg"], "yt_dlp (optional)": ["scoop install yt-dlp"]})
        else:
            steps.update({
                "git": ["Download and run https://git-scm.com/download/win (default options)"],
                "node": ["Download and run the Node.js 22 LTS installer from https://nodejs.org"],
                "ffmpeg": ["python tools/setup.py ffmpeg-windows"],
                "yt_dlp (optional)": ["python -m pip install --user yt-dlp"]})
        steps["whisper"] = ["python tools/setup.py whisper-windows"]
    steps["whisper_model"] = ["python tools/setup.py model --size small.en   # 466 MB; medium.en = 1.5 GB, better on strong accents"]
    steps["hyperframes"] = ["npm install -g hyperframes", "npx hyperframes skills update   # Claude Code skills for video work"]
    need = missing(d)
    return {"os": osn, "missing": need, "steps": {k: v for k, v in steps.items() if k in need or k == "homebrew"},
            "after": ["python tools/setup.py write-config", "python tools/setup.py done"]}


# ---------- downloads ----------

def download(url, dst, label):
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_suffix(dst.suffix + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": "ai-editor-setup"})
    with urllib.request.urlopen(req) as r, open(tmp, "wb") as f:
        total = int(r.headers.get("Content-Length") or 0)
        done, step = 0, 0
        while chunk := r.read(1 << 20):
            f.write(chunk)
            done += len(chunk)
            if total and done * 10 // total > step:
                step = done * 10 // total
                print(f"  {label}: {done * 100 // total}%", flush=True)
    tmp.replace(dst)
    return dst


def cmd_model(a):
    dst = Path(a.dir or TOOLS_DIR / "models") / f"ggml-{a.size}.bin"
    if dst.exists():
        print(f"already there: {dst}")
    else:
        print(f"downloading ggml-{a.size}.bin (~{MODEL_MB.get(a.size, '?')} MB) -> {dst}")
        download(MODEL_URL.format(size=a.size), dst, a.size)
    print(dst)


def cmd_whisper_windows(a):
    base = Path(a.dir or TOOLS_DIR / "whisper")
    req = urllib.request.Request(WHISPER_RELEASES, headers={"User-Agent": "ai-editor-setup"})
    releases = json.loads(urllib.request.urlopen(req).read())
    asset = next((x for r in releases for x in r.get("assets", []) if x["name"] == "whisper-bin-x64.zip"), None)
    if not asset:
        sys.exit("no whisper-bin-x64.zip found in recent whisper.cpp releases; see docs/SETUP.md for the manual steps")
    z = download(asset["browser_download_url"], base / "whisper-bin-x64.zip", "whisper.cpp")
    with zipfile.ZipFile(z) as f:
        f.extractall(base)
    z.unlink()
    exe = next(base.rglob("whisper-cli.exe"))
    print(exe)


def cmd_ffmpeg_windows(a):
    base = Path(a.dir or TOOLS_DIR / "ffmpeg")
    z = download(FFMPEG_WIN_URL, base / "ffmpeg.zip", "ffmpeg")
    with zipfile.ZipFile(z) as f:
        f.extractall(base)
    z.unlink()
    print(next(base.rglob("ffmpeg.exe")))


# ---------- config and marker ----------

def cmd_write_config(a):
    d = detect()
    cfg = config()
    t = d["tools"]
    if t["ffmpeg"]["path"]:
        cfg["ffmpeg"] = t["ffmpeg"]["path"].replace("\\", "/")
    if t["whisper_cli"]["path"]:
        cfg["whisper_cli"] = t["whisper_cli"]["path"].replace("\\", "/")
    models = t["whisper_models"]
    if models and not cfg.get("whisper_model"):
        pick = next((m for m in models if "medium.en" in m), None) or next((m for m in models if "small.en" in m), models[-1])
        cfg["whisper_model"] = pick.replace("\\", "/")
    CONFIG.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(cfg, indent=2))


def cmd_done(a):
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "check_setup.py")])
    if r.returncode != 0:
        sys.exit("setup is not complete; fix the MISSING lines above, then run this again")
    d = detect()
    MARKER.write_text(json.dumps({"os": d["os"], "os_version": d["os_version"], "tools": d["tools"]}, indent=2),
                      encoding="utf-8")
    print(f"setup done -> {MARKER.name}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    sub.add_parser("detect")
    sub.add_parser("plan")
    m = sub.add_parser("model")
    m.add_argument("--size", default="small.en", choices=sorted(MODEL_MB))
    m.add_argument("--dir")
    for name in ("whisper-windows", "ffmpeg-windows"):
        sub.add_parser(name).add_argument("--dir")
    sub.add_parser("write-config")
    sub.add_parser("done")
    a = p.parse_args()
    if a.cmd == "status":
        print("SETUP DONE" if MARKER.exists() else "SETUP NEEDED: run the first-time setup (docs/SETUP.md, or /setup)")
        sys.exit(0 if MARKER.exists() else 1)
    if a.cmd == "detect":
        print(json.dumps(detect(), indent=2))
    elif a.cmd == "plan":
        print(json.dumps(plan(detect()), indent=2))
    else:
        {"model": cmd_model, "whisper-windows": cmd_whisper_windows, "ffmpeg-windows": cmd_ffmpeg_windows,
         "write-config": cmd_write_config, "done": cmd_done}[a.cmd](a)


if __name__ == "__main__":
    main()
