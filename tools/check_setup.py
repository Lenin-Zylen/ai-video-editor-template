"""Check that this computer has everything the editor needs.

    python tools/check_setup.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402


def version(cmd):
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return (out.stdout or out.stderr).strip().splitlines()[0]
    except Exception as e:  # noqa: BLE001
        return f"ERROR {e}"


def main():
    ok = True
    rows = [("python", sys.version.split()[0], sys.version_info >= (3, 10))]
    for name, finder in (("ffmpeg", common.ffmpeg), ("whisper-cli", common.whisper_cli), ("whisper model", common.whisper_model)):
        try:
            rows.append((name, finder(), True))
        except SystemExit as e:
            rows.append((name, str(e), False))
    for exe, args in (("node", ["--version"]), ("git", ["--version"]), ("yt-dlp", ["--version"])):
        path = shutil.which(exe)
        rows.append((exe, version([path, *args]) if path else "not on PATH", bool(path)))
    npx = shutil.which("npx.cmd") or shutil.which("npx")
    rows.append(("hyperframes", version([npx, "hyperframes", "--version"]) if npx else "npx not found", bool(npx)))
    for name, detail, good in rows:
        ok &= good or name == "yt-dlp"
        print(f"{'OK ' if good else 'MISSING'}  {name:<14} {detail}")
    print("\nAll required tools found." if ok else "\nInstall the MISSING tools (see template/README.md).")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
