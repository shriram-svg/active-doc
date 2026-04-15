#!/usr/bin/env python3
"""Active Doc engine.

Reads a markdown file, scores each line for action-intent / urgency,
and rewrites the file with a "🔥 Active Focus" section at the top.

No dates required. No checkboxes required. Meaning is inferred from text.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

FOCUS_HEADER = "## 🔥 Active Focus"
DIVIDER = "<!-- active-doc:end -->"

ACTION_PAT = re.compile(
    r"\b(need to|needs to|should|must|have to|follow[- ]?up|finalize|"
    r"decide|build|send|ship|write|fix|review|schedule|talk to|reach out|"
    r"call|email|draft|plan|kick off|launch|migrate|investigate)\b",
    re.I,
)
URGENCY_PAT = re.compile(
    r"\b(important|asap|urgent|critical|priority|risk|risky|blocker|"
    r"blocking|time[- ]sensitive|deadline|overdue|today|tonight|tomorrow)\b",
    re.I,
)
OPEN_LOOP_PAT = re.compile(r"\b(not sure|unclear|unresolved|tbd|open question|todo)\b", re.I)
WAITING_PAT = re.compile(r"\b(waiting on|depends on|blocked by|pending)\b", re.I)
OWNERSHIP_PAT = re.compile(r"\b(i (?:will|need|should|have to)|we (?:will|need|should|have to))\b", re.I)
EMPHASIS_PAT = re.compile(r"(\*\*[^*]+\*\*|!{2,}|\bIMPORTANT\b|\bNOTE\b)")


def score_line(line: str, frequency: int = 1) -> int:
    s = 0
    if ACTION_PAT.search(line):
        s += 3
    if URGENCY_PAT.search(line):
        s += 3
    if WAITING_PAT.search(line):
        s += 2
    if OWNERSHIP_PAT.search(line):
        s += 1
    if OPEN_LOOP_PAT.search(line) or line.rstrip().endswith("?"):
        s += 1
    if EMPHASIS_PAT.search(line):
        s += 1
    if frequency > 1:
        s += min(frequency - 1, 3)
    return s


def normalize(line: str) -> str:
    core = re.sub(r"[^a-z0-9 ]", " ", line.lower())
    core = re.sub(r"\s+", " ", core).strip()
    return core


def line_key(line: str) -> str:
    return hashlib.md5(normalize(line).encode()).hexdigest()[:12]


def strip_existing_focus(text: str) -> str:
    if FOCUS_HEADER in text:
        parts = text.split(DIVIDER, 1)
        if len(parts) == 2:
            return parts[1].lstrip("\n")
        # Fallback: remove from header to first ---
        idx = text.find(FOCUS_HEADER)
        tail = text[idx:]
        m = re.search(r"\n---+\n", tail)
        if m:
            return text[idx + m.end():]
    return text


def extract_candidates(body: str) -> list[str]:
    out = []
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        line = re.sub(r"^[-*+]\s+", "", line)
        line = re.sub(r"^\d+\.\s+", "", line)
        line = re.sub(r"^\[[ xX]\]\s+", "", line)
        if len(line) < 4:
            continue
        out.append(line)
    return out


def rank(lines: list[str], top_n: int, state: dict) -> list[tuple[str, int]]:
    freq = Counter(line_key(l) for l in lines)
    now = datetime.now(timezone.utc).isoformat()
    seen = state.setdefault("seen", {})

    scored: dict[str, tuple[str, int]] = {}
    for line in lines:
        key = line_key(line)
        first_seen = seen.setdefault(key, now)
        # Aging: boost if first seen > 1 day ago and still present
        try:
            age_days = (datetime.now(timezone.utc) - datetime.fromisoformat(first_seen)).days
        except ValueError:
            age_days = 0
        age_bonus = min(age_days, 3)

        s = score_line(line, frequency=freq[key]) + age_bonus
        if s <= 0:
            continue
        # Dedupe: keep highest-scoring instance per normalized key
        if key not in scored or s > scored[key][1]:
            scored[key] = (line, s)

    # Prune seen entries no longer present
    present = {line_key(l) for l in lines}
    for stale in list(seen.keys()):
        if stale not in present:
            del seen[stale]

    ranked = sorted(scored.values(), key=lambda x: x[1], reverse=True)
    return ranked[:top_n]


def render(ranked: list[tuple[str, int]]) -> str:
    if not ranked:
        return f"{FOCUS_HEADER}\n\n_No action signals detected yet._\n\n{DIVIDER}\n\n"
    lines = [FOCUS_HEADER, ""]
    for i, (text, s) in enumerate(ranked, 1):
        lines.append(f"{i}. {text}  _(score {s})_")
    lines.append("")
    lines.append(f"{DIVIDER}")
    lines.append("")
    return "\n".join(lines) + "\n"


def process(path: Path, state_path: Path, top_n: int = 5) -> None:
    text = path.read_text()
    body = strip_existing_focus(text)
    candidates = extract_candidates(body)

    state = {}
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text())
        except json.JSONDecodeError:
            state = {}

    ranked = rank(candidates, top_n, state)
    new_text = render(ranked) + body.lstrip("\n")

    if new_text != text:
        path.write_text(new_text)

    state_path.write_text(json.dumps(state, indent=2))


def main() -> int:
    ap = argparse.ArgumentParser(description="Bubble action items to the top of a markdown doc.")
    ap.add_argument("file", nargs="?", default="notes.md", help="Markdown file to process")
    ap.add_argument("--top", type=int, default=5, help="How many items to surface")
    ap.add_argument("--watch", type=float, default=0, help="Re-run every N seconds (0 = one-shot)")
    ap.add_argument("--state", default=None, help="State file (default: <file>.state.json)")
    args = ap.parse_args()

    path = Path(args.file).expanduser().resolve()
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 1
    state_path = Path(args.state).expanduser().resolve() if args.state else path.with_suffix(path.suffix + ".state.json")

    if args.watch > 0:
        while True:
            process(path, state_path, args.top)
            time.sleep(args.watch)
    else:
        process(path, state_path, args.top)
    return 0


if __name__ == "__main__":
    sys.exit(main())
