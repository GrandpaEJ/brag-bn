# /brag-bn

A Claude Code skill that makes a short launch or ad video for your project **with a Bangla voiceover**. It's a thin layer over [/brag](https://github.com/latent-spaces/brag) and runs /brag's full Hyperframes workflow. It changes four things:

- **Voice:** Microsoft Edge neural TTS (`edge-tts`) with Bangladeshi voices, instead of English Kokoro
- **Script:** colloquial Bangla (চলিত ভাষা), numbers written as words, local brands in Bangla script (বিকাশ, নগদ)
- **On-screen text:** Bangla headlines and CTA, taken from your project's own Bangla copy when it has any. The product's real UI stays in whatever language the product shows.
- **Timing:** word-level timestamps from the TTS, so visuals land exactly on the spoken word

## Install

```bash
git clone https://github.com/GrandpaEJ/brag-bn ~/.claude/skills/brag-bn
```

Requirements:

- The /brag plugin: `/plugin marketplace add latent-spaces/brag` then `/plugin install brag@brag`
- Node.js 22+, FFmpeg, and [uv](https://docs.astral.sh/uv/)
- Hyperframes, set up on first run: `npx hyperframes doctor`, `npx hyperframes browser ensure`, `npx hyperframes skills update`

`edge-tts` needs no install: the helper script runs through `uv run --with edge-tts`.

## Use

Inside your project, ask Claude Code:

```text
/brag-bn --format vertical --tone polished --text mixed
```

| Option | Values | Default |
|---|---|---|
| `--voice-id` | `bn-BD-PradeepNeural`, `bn-BD-NabanitaNeural`, `bn-IN-BashkarNeural`, `bn-IN-TanishaaNeural` | `bn-BD-PradeepNeural` |
| `--text` | `bn`, `en`, `mixed` | `mixed` |
| `--rate` | e.g. `+5%`, `-5%` | `+0%` |

All /brag options (`--tone`, `--format`, `--duration`, `--no-music`, `--no-sfx`, `--title`) work too. If a `brag-output/` from an English run already exists, ask for "the Bangla version": the skill reuses that storyboard and changes only the voice, the copy, the fonts and the timings.

## The TTS helper on its own

```bash
uv run --with edge-tts python scripts/bn_tts.py lines.json --out-dir out --voice bn-BD-PradeepNeural
```

`lines.json` is `[{"id": "vo1", "text": "..."}]`. You get one 48 kHz WAV per line and `voiceover.json`, which holds each clip's duration and word timings.

Add `--polish` to run every clip through a light voice chain: a rumble cut, less mud, more presence, a de-esser, gentle compression and a very small room. It adds no delay, so the word timings stay valid. For long narration such as tutorials, `--voice bn-BD-NabanitaNeural --rate -3% --polish` is the cleanest read. Nabanita has noticeably less sibilance than Pradeep.

## A note on edge-tts

`edge-tts` uses Microsoft Edge's read-aloud service. It's free and needs no key, but it isn't an official API, so it can change or rate-limit. For a paid campaign where reliability matters, Azure Speech offers the same neural voices through an official API.
