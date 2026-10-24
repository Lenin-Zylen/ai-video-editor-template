---
description: Collect or update the brand and channel details (brand type, formats, language, logo, assets, style, CTA)
---

Run the channel intake in `docs/CHANNEL_INTAKE.md`:

1. Run `python tools/intake.py status` and read `brand/channel.json`. Ask only for missing fields
   (or for the fields the person wants to change).
2. Round 1 and Round 2 with AskUserQuestion (4 questions each), then the Round 3 fill-in message.
3. Save the answers to `brand/channel.json`, copy their logo and assets into `brand/`, pick the whisper model
   for their language, then run `python tools/intake.py render` and `python tools/intake.py status`.
4. If `brand/BRAND.md` is a DRAFT, build the brand sheet from their references and assets and ask for approval.
5. Summarise what changes in the edits because of their answers.

$ARGUMENTS
