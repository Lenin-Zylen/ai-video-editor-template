"""Personalise a repo created from the template: channel name and handle.

    python tools/init_channel.py --handle ganeshbuildsai --name "Ganesh" [--keyword AI]

Writes the name and handle into brand/channel.json, retitles README.md, and swaps the example's
placeholder handle. The channel intake (/intake) asks for everything else.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDER = "yourhandle"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--handle", required=True, help="main handle without @")
    p.add_argument("--name", required=True, help="brand or person name")
    p.add_argument("--keyword", help="default comment keyword for CTAs")
    a = p.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9._]+", a.handle):
        sys.exit("handle: letters, digits, dot and underscore only")

    prof_path = ROOT / "brand" / "channel.json"
    prof = json.loads(prof_path.read_text(encoding="utf-8"))
    prof["identity"]["brand_name"] = a.name
    for k, v in prof["handles"].items():
        if not v:
            prof["handles"][k] = None
    prof["handles"]["instagram"] = prof["handles"].get("instagram") or a.handle
    if a.keyword:
        prof["cta"]["default_keyword"] = a.keyword
    prof_path.write_text(json.dumps(prof, indent=2) + "\n", encoding="utf-8")

    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    text = re.sub(r"^# .*", f"# {a.handle}-editor", text, count=1, flags=re.M)
    if "Created from the" not in text:
        text = text.replace("\n", f"\n\nVideos for **{a.name}** (@{a.handle}). Created from the `ai-video-editor-template`.\n", 1)
    readme.write_text(text, encoding="utf-8")

    for f in (ROOT / "examples").rglob("*"):
        if f.is_file() and f.suffix in (".html", ".md", ".json"):
            s = f.read_text(encoding="utf-8")
            if PLACEHOLDER in s or PLACEHOLDER.upper() in s:
                f.write_text(s.replace(PLACEHOLDER.upper(), a.handle.upper()).replace(PLACEHOLDER, a.handle), encoding="utf-8")
    print(f"Personalised for {a.name} (@{a.handle}). Next: /intake in Claude Code.")


if __name__ == "__main__":
    main()
