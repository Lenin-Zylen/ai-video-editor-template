"""Channel intake helper (see docs/CHANNEL_INTAKE.md).

    python tools/intake.py status   # which required details are missing (exit 0 = complete)
    python tools/intake.py render   # write brand/CHANNEL.md from brand/channel.json
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "brand" / "channel.json"
TEMPLATE = next((p for p in (ROOT / "tools" / "channel.template.json",
                                ROOT / "template" / "channel.template.json") if p.exists()), None)

# (path in channel.json, question to ask). A field counts as answered when it is not null / empty,
# or when it is the string "skip" or "none" (the person chose to leave it out).
REQUIRED = [
    ("identity.brand_type", "Company or personal brand?"),
    ("identity.brand_name", "Brand / channel name"),
    ("identity.on_camera", "Who is on camera (name, title)?"),
    ("audience.who", "Who is the audience?"),
    ("formats.short_form", "Short form (Reels/Shorts)?"),
    ("formats.long_form", "Long form (YouTube 16:9)?"),
    ("language.spoken", "Spoken language(s)"),
    ("language.whisper_model", "Speech model for that language"),
    ("handles", "At least one handle"),
    ("assets.logo", "Logo file (or 'none')"),
    ("assets.colors", "Brand colours (or 'none')"),
    ("style.references", "3 reference videos (or 'skip')"),
    ("style.tone", "Tone"),
    ("style.motion", "Motion level"),
    ("style.on_camera", "On camera: talking head / faceless / screen / mix"),
    ("cta.type", "Call to action type"),
    ("assets.music.policy", "Music policy"),
]


def get(d, path):
    for k in path.split("."):
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def answered(v):
    if v is None:
        return False
    if isinstance(v, bool):
        return True
    if isinstance(v, str):
        return v.strip() != ""
    if isinstance(v, list):
        return any(answered(x) for x in v)
    if isinstance(v, dict):
        return any(answered(x) for x in v.values())
    return True


def load():
    if PROFILE.exists():
        return json.loads(PROFILE.read_text(encoding="utf-8"))
    return json.loads(TEMPLATE.read_text(encoding="utf-8")) if TEMPLATE else {}


def status():
    p = load()
    missing = [(k, q) for k, q in REQUIRED if not answered(get(p, k))]
    if not PROFILE.exists():
        print("NO PROFILE: brand/channel.json does not exist; run the channel intake (docs/CHANNEL_INTAKE.md, or /intake)")
    elif missing:
        print(f"INTAKE INCOMPLETE: {len(missing)} detail(s) missing; ask only these:")
    else:
        flag = "" if p.get("intake_complete") else ' (set "intake_complete": true)'
        print("INTAKE COMPLETE" + flag)
    for k, q in missing:
        print(f"  - {k}: {q}")
    sys.exit(0 if PROFILE.exists() and not missing else 1)


def line(v):
    if isinstance(v, list):
        return ", ".join(line(x) for x in v if answered(x)) or "—"
    if isinstance(v, dict):
        parts = [f"{k}: {line(x)}" for k, x in v.items() if answered(x)]
        return "; ".join(parts) or "—"
    if isinstance(v, bool):
        return "yes" if v else "no"
    return str(v) if answered(v) else "—"


def render():
    p = load()
    out = [f"# Channel profile — {p.get('identity', {}).get('brand_name') or 'unnamed'}", "",
           "Generated from `brand/channel.json` by `python tools/intake.py render`. Edit the JSON, not this file.", "",
           f"Intake complete: {line(p.get('intake_complete'))} · updated: {line(p.get('updated'))}", ""]
    for section, data in p.items():
        if section in ("intake_complete", "updated") or not isinstance(data, dict):
            continue
        out.append(f"## {section.replace('_', ' ').capitalize()}")
        for k, v in data.items():
            out.append(f"- **{k.replace('_', ' ')}**: {line(v)}")
        out.append("")
    if answered(p.get("notes")):
        out += ["## Notes", str(p["notes"]), ""]
    (ROOT / "brand" / "CHANNEL.md").write_text("\n".join(out), encoding="utf-8")
    print("wrote brand/CHANNEL.md")


if __name__ == "__main__":
    {"status": status, "render": render}.get(sys.argv[1] if len(sys.argv) > 1 else "status", status)()
