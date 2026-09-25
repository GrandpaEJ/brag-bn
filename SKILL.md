---
name: brag-bn
description: Bangla version of /brag — a short launch or ad video for the current project with a Bangla voiceover (Microsoft Edge TTS, Bangladeshi voices) and optional Bangla on-screen text. Use when someone says "/brag-bn", asks for a brag, promo, ad or launch video "in Bangla", "Bangla voice", "bangla te video", or wants edge-tts narration on a /brag video.
---

# /brag-bn

The /brag workflow with a Bangla voice. It is a thin layer over the installed `brag:brag` skill. Load that skill and follow its steps 1–4, with the overrides below. Where the two disagree, this file wins. Everything it does not mention (creative laws, tones, audio, Hyperframes handoff, check gate, poster, share copy) stays exactly as /brag says.

Do not edit the /brag plugin itself. It lives in the plugin cache, and `claude plugin update` overwrites it.

## Options

Everything /brag accepts (`--tone`, `--format`, `--duration`, `--no-music`, `--no-sfx`, `--title`), plus:

| Option | Values | Default |
|---|---|---|
| `--voice-id` | any edge-tts Bangla voice | `bn-BD-PradeepNeural` (BD male) |
| `--text` | `bn` (Bangla on screen), `en` (English on screen), `mixed` | `mixed` |
| `--rate` | edge-tts rate, e.g. `+8%`, `-5%` | `+0%` |

Bangla voices: `bn-BD-PradeepNeural` (male), `bn-BD-NabanitaNeural` (female), `bn-IN-BashkarNeural` and `bn-IN-TanishaaNeural` (Kolkata accent; only use them when the user asks).

`mixed` means that headlines, labels and the outro CTA are in Bangla, while the product's real UI stays in whatever language the product actually shows. Never translate a screen the product doesn't translate itself.

## Overrides to /brag

### Dispatch
Narration is always on, so this is the full /brag workflow with `voice.enabled = true`. Never switch to brag-slim; it has no voice.

**Bangla version of an existing cut:** when a finished `brag-output*/` already exists for this project and the user wants it in Bangla, don't redo steps 1–2 from scratch. Copy its `composition/` (without `assets/vo` and `snapshots`) into the new timestamped output dir, keep the storyboard, and change only the voice, the Bangla copy, the fonts and the timings. Write a short `brag-plan.md` that lists the differences.

### Step 1 — Inspect
Also look for the project's own Bangla copy: i18n helpers (`t("English", "বাংলা")`), locale files (`bn.json`, `locales/bn/`), and Bangla meta tags. When the project has a Bangla string for a line, use it verbatim on screen. Its own wording beats a translation.

### Step 2 — Plan: the Bangla voiceover script
Write it under `## Voiceover script` in `brag-plan.md`, one line per scene, in Bangla script:

- Use colloquial standard Bangla (চলিত ভাষা), the way someone in Dhaka would say it in a good ad. No সাধু ভাষা and no word-for-word translation of an English script. Write it in Bangla from the start.
- Keep sentences short, with a comma where a breath goes. Each line must fit its scene.
- **Numbers the voice says are written as Bangla words**, for example একশো টাকা, ষাট সেকেন্ড, দুই জিবি. Digits and symbols like `৳100` or `2GB` get read unpredictably. Digits are fine for on-screen text.
- Write local brands in Bangla script so they're pronounced right: বিকাশ, নগদ, রকেট. Tech words people say in English (সার্ভার, বট, প্যানেল, ডিপ্লয়, কনসোল) are written phonetically in Bangla. For a Latin brand or domain name, write it the way it's spoken: "জিরো বট ডট নেট".
- Don't read out the on-screen text (same rule as /brag). The voice adds the why.
- If the user says it isn't a launch, never use নতুন, চালু হলো, পরিচয় করিয়ে দিচ্ছি, or anything else that means "introducing".
- Bangla takes longer to read: plan **~0.4s per word** of Bangla on-screen text (not /brag's 0.3s), and a floor of 1.5s for any Bangla headline.

### Step 3 — Voice generation (replaces the Kokoro command)
Write the lines to `<output-dir>/work/vo-lines.json` as `[{"id":"vo1","text":"..."}, ...]`, then:

```bash
uv run --with edge-tts python <skill-dir>/scripts/bn_tts.py <output-dir>/work/vo-lines.json \
  --out-dir <output-dir>/composition/assets/vo --voice bn-BD-PradeepNeural --rate +0%
```

This writes `vo1.wav …` (48 kHz) plus `voiceover.json`, which holds each clip's duration and **word timings** (`words: [{text, start, end}]`, seconds from the clip's start).

- Scene lengths follow the clip durations (the same rule as /brag: let the voice set the pace). Place each clip in its scene on its own audio track, ~0.15–0.3s after the scene starts.
- Word timings let a key word land with the visual. For example, the headline word appears when the voice says it: global time = clip `data-start` + word `start`. With `--text bn`, burned-in captions can be driven from the same data. Don't guess timings when the data is available.
- Clips carry ~0.5s of trailing silence (visible as `duration` minus the last word's `end`). Scenes may cut into that tail. Time the next scene from the last word's end, not from the clip duration.
- Bangla scripts run long: the first draft of a five-line ad came out 23s of speech. Budget ~2.4 words per second at `+5%`, and total speech ≤ ~20s so the video stays inside 25s.
- If a line runs too long for its scene, rewrite it shorter. Only use `--rate` up to about `+10%` before rewriting, because faster Bangla starts to sound rushed.
- **If edge-tts fails** (offline, blocked, rate-limited), stop and tell the user. Offer to retry or to switch to English Kokoro (the /brag default). Never switch language silently.

### Step 3 — Fonts (Bangla text on screen)
Hyperframes needs every named font shipped locally with `@font-face`. Download the woff2 files into `composition/assets/fonts/` from jsdelivr (fontsource):

- Bangla display and body: **Hind Siliguri** (`@fontsource/hind-siliguri`, subset `bengali`, weights 500/600/700) or **Noto Sans Bengali** (`@fontsource/noto-sans-bengali`, subset `bengali`).
  URL pattern: `https://cdn.jsdelivr.net/npm/@fontsource/<family>@5/files/<family>-bengali-<weight>-normal.woff2`
- Put the Bangla family in the `font-family` stack **even for English-only text**. Inter and most Latin fonts have no `৳`, and without the fallback the taka sign renders in a random system font.
- Bangla typography: line-height ≥ 1.3 for headlines and ≥ 1.5 for body text, because vowel signs and conjuncts clip with tight leading. No negative letter-spacing, and no `text-transform: uppercase` on Bangla (it does nothing, and it breaks eyebrow styles that assume caps). Size Bangla headlines about 10–15% smaller than the English equivalent; Bangla glyphs are taller.
- Confirm the glyphs exist before you rely on them, for example: `uv run --with fonttools --with brotli python -c "from fontTools.ttLib import TTFont; print(0x09F3 in TTFont('<font>.woff2').getBestCmap())"`.

### Step 4 — Deliver
- **Loudness:** Edge voices and the bundled music land around -20 LUFS. While baking the poster frame, normalize the mix to **-14 LUFS, -1.5 dBTP** (two-pass `loudnorm`: measure first, then apply with the measured values). Keep the video stream and the frame count untouched.
- **Re-measure after the AAC encode.** AAC overshoots: a -1.5 dBTP loudnorm has come out at -0.4 dBFS. If `ebur128=peak=true` reports a peak above -1 dBFS, run one more pass with `-c:v copy -af alimiter=limit=0.84:level=false` (≈ -1.5 dBFS). This keeps the baked poster frame and the frame count.
- **`share-copy.txt`:** in Bangla, matching the voiceover's tone, with the domain in Latin. If an English caption would also help, put it in `share-copy-variants.md`.
- Tell the user which voice was used, and that edge-tts goes through Microsoft's unofficial read-aloud endpoint. It's free and needs no key, but it can change or rate-limit. For a paid campaign where reliability matters, Azure Speech has the same neural voices through an official API.

## Environment (first run on a machine)
- `npx hyperframes doctor`. If Chrome is missing, run `npx hyperframes browser ensure`.
- `npx hyperframes skills update` installs the Hyperframes domain skills that /brag step 3 reads.
- `uv` must be on PATH, because the helper script runs through `uv run --with edge-tts`. Kokoro is only needed for the English fallback: `uv venv ~/.cache/hyperframes/kokoro-venv && uv pip install --python ~/.cache/hyperframes/kokoro-venv/bin/python kokoro-onnx soundfile`, then `HYPERFRAMES_PYTHON=~/.cache/hyperframes/kokoro-venv/bin/python`.
