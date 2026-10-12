#!/usr/bin/env python3
"""clips.py - candidate Shorts from a podcast transcript, ranked.

    python3 clips.py episode.srt                 # or .vtt, or whisper .json
    python3 clips.py episode.srt --top 8 --min 20 --max 55 --json

A podcast clip has to survive without the conversation around it. This looks for spans (default
20-55 s) that (1) open on a complete thought, not on "y eso...", "pero..." or "and so..." (2) end where
a sentence ends AND the speaker paused, and (3) contain something worth stopping for: a figure, a
question, a turn ("pero", "sin embargo", "but"), a claim with a stake. Spans are scored, overlaps are
dropped, and the best ones are printed with timecodes and their first line.

WHAT IT DOES NOT DO. It does not cut media and it does not write the new first line - the skill does
that (yt-shorts / yt-podcast) and runs it through ../yt-script/hookscore.py. It reads text and
timing only, so it cannot hear laughter, a good pause or a bad audio patch: listen before you cut.
The weights are a heuristic written for this fork and are NOT calibrated on real clips.
English and Spanish.
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "yt-edit"))
sys.path.insert(0, os.path.join(HERE, "..", "yt-script"))
from deadair import load, FILLER_ONLY  # noqa: E402
from hookscore import score as hook_score  # noqa: E402

LABEL = re.compile(r"^\s*(>>+|-|\[?[\w .]{1,24}\]?:)\s*")           # ">> ", "- ", "Marcelo:", "[Speaker 1]:"
CONT = re.compile(r"^(y|e|o|u|pero|entonces|pues|o sea|es decir|eso|esto|ese|esa|aquello|ahí|"
                  r"sin embargo|además|por eso|por lo tanto|también|and|but|so|then|that|this|it|which|because|however|also)\b", re.I)
GREETING = re.compile(r"^(hola|buenas|bienvenid|gracias|hasta|chau|adiós|hello|welcome|thanks|thank you|bye)", re.I)
TURN = re.compile(r"\b(pero|sin embargo|aunque|en cambio|sino que|resulta que|lo curioso|"
                  r"but|however|although|turns out|instead)\b", re.I)
FIGURE = re.compile(r"\d")
TERMINAL = re.compile(r"[.?!…][\"')\]]?\s*$")

def clean(t): return LABEL.sub("", t).strip()

def first_sentence(text):
    m = re.search(r"^(.*?[.?!…])(\s|$)", text)
    return (m.group(1) if m else text)[:200]

def mmss(t):
    t = int(t); return f"{t // 60}:{t % 60:02d}"

def spans(cues, lo, hi):
    n = len(cues)
    for i in range(n):
        prev_ok = i == 0 or TERMINAL.search(cues[i - 1][2]) or cues[i][0] - cues[i - 1][1] >= 0.3
        if not prev_ok or FILLER_ONLY.match(cues[i][2]): continue
        for j in range(i, n):
            dur = cues[j][1] - cues[i][0]
            if dur > hi: break
            end_ok = TERMINAL.search(cues[j][2]) and (j == n - 1 or cues[j + 1][0] - cues[j][1] >= 0.25)
            if dur >= lo and end_ok: yield i, j

def rate(cues, i, j):
    text = " ".join(clean(c[2]) for c in cues[i:j + 1])
    opener = clean(cues[i][2])
    dur = cues[j][1] - cues[i][0]
    words = max(1, len(text.split()))
    fillers = sum(1 for c in cues[i:j + 1] if FILLER_ONLY.match(c[2]))
    s = 40.0
    why = []
    if CONT.match(opener): s -= 35; why.append("opens mid-thought")
    elif GREETING.match(opener): s -= 30; why.append("greeting / sign-off")
    else: s += 8; why.append("opens clean")
    verdict = hook_score(first_sentence(opener + " " + (cues[i + 1][2] if i < j else "")))[1]
    s += (verdict - 50) * 0.35
    if FIGURE.search(text): s += 8; why.append("has a figure")
    if "?" in text: s += 6; why.append("has a question")
    if TURN.search(text): s += 12; why.append("has a turn")
    s -= fillers * 5
    s -= max(0, (words / dur) - 3.6) * 6        # >3.6 words/s reads as a rush, hard to follow
    s += 6 if 28 <= dur <= 48 else 0
    return round(max(0, min(100, s))), text, " | ".join(why), verdict

def main():
    a = sys.argv[1:]
    as_json = "--json" in a; a = [x for x in a if x != "--json"]
    def opt(name, default):
        return float(a[a.index(name) + 1]) if name in a else default
    top, lo, hi = int(opt("--top", 6)), opt("--min", 20), opt("--max", 55)
    path = next((x for k, x in enumerate(a) if not x.startswith("--") and (k == 0 or not a[k - 1].startswith("--"))), None)
    if not path or not os.path.exists(path): print(__doc__); sys.exit(1)
    cues = load(path)
    if len(cues) < 6: print("too few cues - is this a full-episode srt, vtt or whisper json?"); sys.exit(1)
    found = []
    for i, j in spans(cues, lo, hi):
        sc, text, why, v = rate(cues, i, j)
        found.append((sc, i, j, text, why, v))
    found.sort(key=lambda r: -r[0])
    picked = []
    for sc, i, j, text, why, v in found:
        if all(j < pi or i > pj for _, pi, pj, *_ in picked): picked.append((sc, i, j, text, why, v))
        if len(picked) >= top: break
    out = [{"score": sc, "start": round(cues[i][0], 2), "end": round(cues[j][1], 2),
            "seconds": round(cues[j][1] - cues[i][0], 1), "opener": clean(cues[i][2])[:120],
            "why": why, "text": text} for sc, i, j, text, why, v in picked]
    if as_json: print(json.dumps(out, indent=1, ensure_ascii=False)); return
    if not out: print("\n  no span of %.0f-%.0f s opens and ends cleanly - try --min 12 --max 70\n" % (lo, hi)); return
    print(f"\n  {path}   {len(cues)} cues, {len(out)} candidates\n")
    for r in out:
        print(f"  {r['score']:3d}  {mmss(r['start'])} -> {mmss(r['end'])}  ({r['seconds']}s)  {r['why']}")
        print(f"       \"{r['opener']}\"")
    print("\n  Next: write a NEW first line for each one, score it with hookscore.py, and listen before you cut.\n")

if __name__ == "__main__":
    main()
