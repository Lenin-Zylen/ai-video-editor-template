# Brand Rules — STARTER (DRAFT)

These are working defaults from a proven short-form system. They are **not** this channel's brand yet.
The channel intake (`docs/CHANNEL_INTAKE.md`) replaces the colours, fonts, logo, CTA and style with the
channel's own (from `brand/channel.json`, its assets and 3 reference videos), writes `brand/brand-sheet.html`,
and asks for approval. Do not edit a video while this file says DRAFT.

When approved, change the title to `<Channel> — Brand Rules v1 (APPROVED <date>)` and keep a changelog.

## Changelog
- STARTER: copied from the template.

## Locked decisions (filled by the intake)
- Channel name and handle: from `brand/channel.json` → `identity.brand_name`, `handles`.
- CTA: `cta.type`, `cta.default_keyword`, `cta.default_text`.
- Logo: `brand/logo/channel-avatar.png` (round, 240 × 240) and the full logo files in `brand/logo/`.

## Logo
- Use the channel's own files only. Never redraw, recolour, stretch or crop a logo.
- Starter placements: hook label (52 px avatar), top-right watermark from the end of the hook
  (44 px avatar + `@handle`, mono 28 px, muted colour), CTA frame (avatar in the comment box, avatar + handle).
- Product and company logos (OpenAI, Google, …): official marks only (`npx hyperframes media-use resolve --type logo`),
  next to the product's name, never instead of the channel logo.

## Format
- Short form: 1080 × 1920, 30 fps, 9:16. Length 30–60 s.
- Long form: 1920 × 1080, 30 fps, 16:9. Captions at the bottom, chapters, a 1280 × 720 thumbnail.
- Voice master: −14 LUFS integrated, true peak −1 dBTP, loudness range ≤ 4 LU.

## Colour (starter values — the intake replaces them)
| Token | Starter hex | Use |
|---|---|---|
| Ink | `#0D1117` | Main background, caption pill |
| Ink-2 | `#161B22` | Cards |
| Paper | `#EEEBE3` | Light scenes, CTA frame |
| Accent | `#C8F04A` | The one accent: one word or one shape per frame |
| Data | `#7B61FF` | Data and charts only |
| Muted | `#8A8F98` | Labels, muted text, 1 px card borders |
| White | `#FFFFFF` | Caption text, headlines |

Company brands: their own colours and fonts always win.

## Typography (starter: free Google Fonts)
- Display: Archivo 900, width 125, uppercase, tight leading (0.95).
- Captions: Archivo 800, width 112, sentence case.
- UI / body: Inter 500.
- Labels and counters: JetBrains Mono, uppercase, letter-spacing 0.12em.

## Captions
- 2–4 words per chunk, verbatim from the speech; fix spelling by hand. In the spoken language unless the channel asks otherwise.
- Bold display font, 64 px, white on an Ink pill (radius 16 px, 2 px border).
- At most one key word per chunk in the Accent colour. Many chunks have none.
- Short form split scenes: pill on the split line (y = 960). Full-screen graphics: y ≈ 1162. Long form: 100 px above the bottom.
- Entry: 120 ms, scale 0.9 → 1. No exit animation. Captions are an overlay; never reserve a band for them.

## Layout — four frame types (short form)
- **A · Hook (0–2 s):** full-screen title, one Accent word, readable on frame 0 (it is the thumbnail).
- **B · Split (most of the video):** graphic in the top half, the speaker in the bottom half, caption on the split line.
- **C · Full-screen beat:** section cards, stats, and lines where the speaker should not be on screen (voice only).
- **D · CTA (last 3–4 s):** the ask (comment keyword / follow / link) with the channel avatar and handle.
- Signature: a thin Accent progress bar on the top edge and a `02 / 04` step counter during numbered steps.

## Cuts, zooms, pacing
- Remove every pause longer than `production.max_pause_s` in `channel.json` (default 0.1 s), all breaths and filler words.
- Change the top-half graphic every 1.5–2.5 s, synced to a caption chunk.
- First spoken line states the result, not the setup. Structure: Hook → "N things / N ways" → steps → payoff → CTA.
- Punch-in on the face: hard cut 100% ↔ 112% on a key line, about every 6–8 s. No slow zooms.
- Never use a take where the speaker looks down or says a wrong word; ask for another take or cover it with graphics.

## Motion graphics (level from `style.motion`)
- Rich (default): transitions between scenes (wipe + light sweep, zoom-through), animation on every spoken beat,
  UI cards that build piece by piece, count-ups, typed prompts with a caret, cursor clicks, success checks, logos where they fit.
- Entrances 250–350 ms (power3.out), exits 200 ms or a hard cut, group stagger 60–80 ms.
- No idle float or wobble. Hold still 0.3 s before a big reveal.
- Do not copy the reference creators' signature elements. No stock emoji, meme clips or glow effects.

## Music and sound
- Music: from the channel's music policy; low bed without vocals, ≈ −30 LUFS under the voice.
- SFX only on visible actions (click, pop, whoosh, typing, impact on the payoff). Max one sound per second.

## Do not
- Show a caption longer than 4 words, or use the Accent more than once per frame.
- Use anything in `channel.json` → `avoid`.
