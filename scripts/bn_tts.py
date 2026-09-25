#!/usr/bin/env python3
"""
Generate Bangla voiceover clips with Microsoft Edge's online TTS (edge-tts),
one clip per storyboard line, plus word timings for caption sync.

Usage (run through uv so edge-tts is provisioned on the fly):

    uv run --with edge-tts python bn_tts.py lines.json --out-dir <dir> \
        [--voice bn-BD-PradeepNeural] [--rate +0%] [--pitch +0Hz] [--polish]

--polish runs each clip through a light voice chain (rumble cut, less mud,
more presence, a de-esser, gentle compression and a very small room) so the
raw read-aloud voice sounds less thin. For narration, "--rate -4% --pitch -4Hz
--polish" is a calmer, warmer read than the defaults.

lines.json is a list of {"id": "vo1", "text": "..."} objects, in order.

Writes, for every line:
    <out-dir>/<id>.wav         48 kHz mono PCM (what the composition mounts)
and one manifest:
    <out-dir>/voiceover.json   [{id, text, file, duration, words: [{text, start, end}]}]

Times are seconds from the start of that clip. Exits non-zero, saying why,
when the service cannot be reached: the caller decides what to fall back to.
"""

import argparse
import asyncio
import json
import subprocess
import sys
from pathlib import Path

try:
    import edge_tts
except ImportError:
    sys.exit("edge-tts is not installed. Run this through: uv run --with edge-tts python bn_tts.py ...")

TICKS_PER_SECOND = 10_000_000  # edge-tts reports offsets in 100 ns units

# Adds no delay before the speech, so the word timings stay valid.
POLISH = ",".join([
    "highpass=f=75",
    "equalizer=f=250:t=q:w=1.2:g=-2.5",
    "equalizer=f=3200:t=q:w=1.4:g=2.5",
    "highshelf=f=9000:g=2",
    "deesser=i=0.35",
    "acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2",
    "aecho=0.8:0.5:18|31:0.07|0.04",
])


async def synth(text, voice, rate, pitch, mp3_path):
    comm = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, boundary="WordBoundary")
    words = []
    with open(mp3_path, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start = chunk["offset"] / TICKS_PER_SECOND
                words.append({
                    "text": chunk["text"],
                    "start": round(start, 3),
                    "end": round(start + chunk["duration"] / TICKS_PER_SECOND, 3),
                })
    return words


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    return round(float(out.stdout.strip()), 3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lines", help="JSON list of {id, text}")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--voice", default="bn-BD-PradeepNeural")
    ap.add_argument("--rate", default="+0%")
    ap.add_argument("--pitch", default="+0Hz")
    ap.add_argument("--polish", action="store_true", help="EQ, de-ess, compress and a small room on every clip")
    args = ap.parse_args()

    lines = json.loads(Path(args.lines).read_text(encoding="utf-8"))
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    manifest = []
    for line in lines:
        lid, text = line["id"], line["text"].strip()
        mp3 = out / f"{lid}.mp3"
        wav = out / f"{lid}.wav"
        try:
            words = asyncio.run(synth(text, args.voice, args.rate, args.pitch, mp3))
        except Exception as e:  # network, blocked endpoint, bad voice id
            sys.exit(f"edge-tts failed on {lid}: {type(e).__name__}: {e}")
        if not mp3.exists() or mp3.stat().st_size == 0:
            sys.exit(f"edge-tts returned no audio for {lid}")
        # The composition mixes 48 kHz; convert once here so every clip matches.
        af = ["-af", POLISH] if args.polish else []
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mp3), *af, "-ar", "48000", "-ac", "1", str(wav)], check=True)
        mp3.unlink()
        dur = probe_duration(wav)
        manifest.append({"id": lid, "text": text, "file": wav.name, "duration": dur, "words": words})
        print(f"{lid}\t{dur:.2f}s\t{len(words)} words\t{text}")

    (out / "voiceover.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"total speech {sum(m['duration'] for m in manifest):.2f}s -> {out / 'voiceover.json'}")


if __name__ == "__main__":
    main()
