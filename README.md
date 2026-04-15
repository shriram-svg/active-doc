# active-doc

A self-organizing markdown document. Write freely — no dates, no checkboxes,
no tagging. The engine scans the text for action verbs, urgency cues, open
loops, dependencies, repetition, and age, then rewrites the file with a
**🔥 Active Focus** section at the top.

Think of it as a continuously-running semantic prioritization layer over
unstructured notes. A cognitive co-processor, not a to-do list.

## Install

Requires **Python 3.8+**. No dependencies.

```bash
git clone https://github.com/shriram-svg/active-doc.git
cd active-doc
```

Or grab just the engine:

```bash
curl -O https://raw.githubusercontent.com/shriram-svg/active-doc/master/engine.py
```

## Quick start

```bash
# 1. Create or pick any markdown file
echo "Need to email Sam. IMPORTANT: ship demo. Waiting on dataset." > mynotes.md

# 2. Run the engine against it
python3 engine.py mynotes.md

# 3. Open mynotes.md — a "🔥 Active Focus" block is now at the top
```

Write freely in the file below the `<!-- active-doc:end -->` marker. Re-run
the engine any time; the focus block is regenerated, your notes are
preserved.

## Usage

```bash
# one-shot
python3 engine.py notes.md

# continuous (re-run every 10s)
python3 engine.py notes.md --watch 10

# surface more items
python3 engine.py notes.md --top 8
```

The engine preserves your full document and only maintains the focus block
between `## 🔥 Active Focus` and the `<!-- active-doc:end -->` marker.

## Signals

| Signal | Examples | Weight |
|---|---|---|
| Action verbs | need to, should, must, follow up, finalize, ship | +3 |
| Urgency | important, ASAP, blocker, deadline, today | +3 |
| Dependency | waiting on, blocked by, depends on | +2 |
| Ownership | I will, we need | +1 |
| Open loop | not sure, unclear, trailing `?` | +1 |
| Emphasis | **bold**, `IMPORTANT`, `!!` | +1 |
| Repetition | same idea appearing N times | +N-1 (cap 3) |
| Age | unresolved for N days | +N (cap 3) |

State (first-seen timestamps) lives in `<file>.state.json` so aging works
across runs.

## Run in the background

**macOS (launchd):** edit the paths in `com.activedoc.engine.plist` to point
at your own `engine.py` and notes file, then:

```bash
cp com.activedoc.engine.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.activedoc.engine.plist
# to stop:
launchctl unload ~/Library/LaunchAgents/com.activedoc.engine.plist
```

**Linux / anywhere:** just use `--watch`:

```bash
nohup python3 engine.py ~/notes.md --watch 10 &
```

**Cron (every minute):**

```
* * * * * /usr/bin/python3 /path/to/engine.py /path/to/notes.md
```

## Roadmap

- LLM-based scoring (replace regex heuristics)
- Embedding-based dedupe (collapse near-duplicate items)
- Dependency graph ("waiting on X" → surface blockers of blockers)
- Decay for items explicitly marked done/resolved
