# Channel intake (runbook for Claude)

The intake collects everything about the brand and the videos before the first edit, so the first video
is right the first time. Answers go to `brand/channel.json` (machine-readable) and `brand/CHANNEL.md`
(human-readable, written by `python tools/intake.py render`).

**When:** right after the first-time computer setup (`docs/SETUP.md`), or at the start of the first video
edit if `python tools/intake.py status` reports missing fields. Ask only for fields that are still missing.
Never repeat questions that already have answers. `/intake` runs it again on request.

Keep it short for the person: three rounds, about 5 minutes. Tell them at the start:
"Before your first video I need some details about your brand. Three quick rounds."

---

## Round 1 — choices (AskUserQuestion, 4 questions)

1. **Brand type** — "Is this channel for a company or for personal branding?"
   *Personal brand* · *Company brand* · *Both: a founder speaking for the company*
2. **Video format** — "What will we edit?" (multi-select)
   *Short form: Reels, Shorts, TikTok (9:16)* · *Long form: YouTube videos (16:9)* · *Clips cut from long videos*
3. **Language** — "Which language will the videos be spoken in?"
   *English* · *Tamil* · *Hindi* · *A mix (for example Tamil + English)* (Other → they type it)
4. **Motion level** — "How much motion graphics?"
   *Rich: graphics on every beat, transitions, sound effects (recommended)* · *Balanced* · *Minimal: captions and a few cards*

## Round 2 — choices (AskUserQuestion, 4 questions)

1. **Platforms** (multi-select) — *Instagram* · *YouTube* · *Facebook* · *X / LinkedIn / TikTok (type which)*
2. **Tone** (multi-select) — *Energetic* · *Calm expert* · *Premium / corporate* · *Playful*
3. **On camera** — *Talking head* · *Faceless (graphics + voice)* · *Screen recordings / demos* · *A mix*
4. **Call to action** — *Comment a keyword to get a link* · *Follow for more* · *Link in bio / website* · *Book a call / lead magnet*

## Round 3 — one fill-in message

Send this block and ask them to fill in what they know and write "skip" for the rest:

```
Brand / channel name:
Person(s) on camera (name, title):
Handles (Instagram / YouTube / Facebook / X / LinkedIn / TikTok):
Website or main link:
One-line tagline or what the channel is about:
Industry / niche:
Audience (who, beginner or expert, which countries):
Logo files (paths or "attached"):          ← SVG or transparent PNG; light and dark versions if you have them
Headshot or avatar photo (path):
Brand colours (hex, e.g. #0D1117):
Brand fonts:
Brand guide / other assets (paths: intro, outro, lower thirds, product screenshots):
3 reference videos you like (links):
Music: royalty-free only / my own licensed tracks / HeyGen catalog:
Series name and numbering (e.g. "Day 03"), posting days:
Video length you want (short: seconds, long: minutes):
Default comment keyword or CTA text:
Words, competitors or colours to avoid; legal disclaimers:
Who approves the videos:
Anything else:
```

## After the answers

1. Write the answers into `brand/channel.json` (keep its structure; use `null` for "skip").
   Set `language.whisper_model`:
   - English only → `small.en` (or `medium.en` for strong accents);
   - any other language or a mix → the multilingual `small` or `medium` (never a `.en` model).
   If that model is not on the computer, offer `python tools/setup.py model --size <model>`.
2. **Assets:** copy every file they gave into `brand/assets/` (logos into `brand/logo/`). Check each logo:
   SVG or PNG with transparency, readable on dark and light. Make the round avatar
   (`brand/logo/channel-avatar.png`, 240 × 240) from the headshot or logo mark if there is none.
   Never redraw a logo; if a file is missing or low quality, say so and continue.
3. Run `python tools/intake.py render` (writes `brand/CHANNEL.md`) and `python tools/intake.py status`.
   When nothing required is missing, set `"intake_complete": true` and `"updated"` to today's date.
4. **Brand sheet:** if `brand/BRAND.md` is still a DRAFT, build the brand now: download the reference videos
   with yt-dlp into `references/`, study them (fonts, colours, captions, cuts, zooms, pacing, motion, music, sound),
   and write a brand sheet that uses the channel's own colours, fonts and logo — the channel's own, not a copy.
   Show it and wait for approval. Company brands: their existing colours and fonts win over anything from the references.
5. Summarise in 4–6 lines what you will do differently because of their answers
   (format and canvas, language and captions, motion level, CTA, platforms).

## How the answers change the edit

| Answer | Effect |
|---|---|
| Short form | 1080 × 1920, split layout, captions on the split line, cover 9:16, exports per platform |
| Long form | 1920 × 1080, captions at the bottom (`"captions": {"position": "bottom"}` in edit.json), chapters, a 1280 × 720 thumbnail |
| Language not English / mixed | multilingual whisper model; captions in the spoken language unless they want English captions; check every caption by hand |
| Company brand | their colours, fonts and logo rules first; product logos only where accurate; legal lines in the CTA if required |
| Personal brand | the person's face, avatar and handle carry the brand; more on-camera time |
| Motion: minimal | captions + a few cards; no full-screen graphics unless asked |
| Faceless | full-screen graphics with voice; stock or generated visuals per scene |
| CTA type | the end card and the last caption |
| Music policy | where music comes from (CC0 only, their tracks, HeyGen) |
| Avoid list | checked before every storyboard and every render |
