---
description: First-time setup of the video editor on this computer (detect, ask, install, verify)
---

Run the first-time setup for this video editor. Follow `docs/SETUP.md` exactly:

1. Check Python, then run `python tools/setup.py detect` and `python tools/setup.py plan`.
2. Summarise the computer and what is missing in 3–5 short lines.
3. Ask the setup questions in one AskUserQuestion round (install now, speech model, extras). Skip questions that do not apply.
4. Install what is missing with the person's OK. Commands that need a password or Administrator rights: ask the person to run them (they can type `!` and the command).
5. Run `python tools/setup.py write-config` and `python tools/setup.py done`.
6. Tell the person setup is complete and what to do next.

$ARGUMENTS
