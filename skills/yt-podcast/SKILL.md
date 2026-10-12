---
name: yt-podcast
description: >-
  Plan, record and repurpose a conversational video podcast in Spanish (or
  bilingual Spanish/Guarani/English): the episode brief, the cold open, the
  question arc, the close, and the clips, chapters and package afterwards.
  Use for "episodio de podcast", "guia de entrevista", "preparar un
  episodio", "preguntas para el invitado", "sacar clips del episodio",
  "podcast en video".
---

# yt-podcast

A podcast is not a script read aloud. It is a **conversation with a shape**. `yt-script` writes a
monologue; this writes the structure that lets two people talk without wandering, and then mines the
recording for everything a viewer will actually find.

Read `~/.claude/youtube/voice.md` first (template: `templates/voice.es.md`). If it does not exist,
ask for a transcript of an episode or three, infer the register (tuteo, voseo, usted), and write it.
If the user runs more than one project, confirm WHICH profile applies before writing anything.
Never invent a figure, a quote or a source; if a number would help and is not in hand, ask for it.

## Three modes

### 1. BRIEF - before recording

Ask for: the topic in one sentence, who the guest is (or "solo"), and the one thing a viewer should
know after the episode that they did not before. Then produce:

1. **The promise** - one sentence, the title's job. Not "hablamos de X": what the viewer gets.
2. **Cold open** (30-60 s, recorded LAST from the best moment, or written first if it cannot be
   found). Five options built from [the 21 hook formulas](../yt-script/hooks.json), scored with
   `../yt-script/hookscore.py`; show the top two with their panels. A podcast hook is a *line the
   guest will say*, so quote the guest's position, not the host's summary.
3. **The arc, in 5-7 questions**, each with a purpose:
   - the easy opener (gets the guest talking, 1 question)
   - the claim (what do they believe that others do not)
   - the pressure question (the hardest fair one - a podcast without one is a press release)
   - the concrete (ask for a case, a number, a date: "¿cuándo fue la última vez que...?")
   - the turn (where it complicates), and the close (what would you tell someone starting today)
   Every question is open, short, and one idea. Add a **follow-up** under each: "¿por qué?",
   "¿me da un ejemplo?", "¿y qué costó eso?". The follow-ups carry the episode.
4. **A no-go list**: topics the guest asked to avoid, and claims neither side can back up.
5. **Housekeeping**: length target, number of voices, intro (keep it under 20 s), single closing ask.

### 2. LIVE - while recording (a short card, not a script)

Give the host a half-page: the promise, the five questions, the three follow-ups, and a reminder of
the two rules that ruin most episodes: **do not ask the next question until the guest finishes**, and
**if the answer was vague, ask for the example before moving on.**

### 3. REPURPOSE - after recording

Take the transcript (`.srt`, `.vtt` or whisper `.json`) and run the tools in this order:

```bash
python3 ../yt-edit/deadair.py episode.srt           # dead air, filler, retakes (Spanish + English)
python3 clips.py episode.srt --top 8                # candidate Shorts, ranked
python3 ../yt-chapters/chapters.py episode.srt      # chapters, validated against YouTube's rules
python3 ../yt-package/title.py --title "..." --thumb "..."
```

Then, with the user:

- **Clips**: for each of the top candidates, write a NEW first line (the original assumes the
  conversation around it), score it with `hookscore.py`, add different on-screen text, and name the
  loop point. `clips.py` reads text and timing only - it cannot hear laughter, audio problems or a
  good pause, and it cannot tell a complete answer from a reply to the previous sentence. Listen
  before you cut. See `../yt-shorts/SKILL.md` for the writing rules.
- **Chapters**: retitle every draft line in the user's words; the tool gives topic words, not titles.
- **Title and thumbnail** as one pairing: a guest's face plus three words is the usual thumbnail;
  the title must say what the thumbnail does not.
- **Description**: `../yt-seo/SKILL.md`, adding guest name, links and the chapter block.

## Rules that are specific to conversations

- **The guest's consent is part of the process.** Do not clip, caption or title a guest in a way
  that changes what they meant. A clip must not turn a qualified answer into a flat claim. If a
  trimmed answer loses its qualification, restore the qualification or drop the clip.
- **Attribute.** Name the guest in every clip title or caption; do not present their claim as yours.
- **Do not sharpen into false certainty.** Hook formulas reward flat statements; a guest who said
  "creo que" did not say "es así". Keep the hedge, or pick another moment.
- **Guarani**: use it where the user asks for it and verify any phrase with `traductor-guarani`.
  Do not guess spellings, and do not translate quotes from a guest without telling the user.
- **Institutional use**: if this brief is for an institutional channel (e.g. INAPP), the guest, topic
  and final cut may need an authority's approval first. Produce the draft; do not treat it as cleared.

## What to hand back

- BRIEF: promise, two scored cold opens, the question arc with follow-ups, the no-go list.
- REPURPOSE: the clip table (time, score, new first line, on-screen text), the chapter block, three
  title/thumbnail pairings, and the description.

## The gate

Nothing here publishes. This skill writes and you publish. Every output ends in a block the user
copies, and the last line of every run is the question: **ship it, or change it?**
