#!/usr/bin/env python3
"""Count repetition in a screen's visible text.

Pipe in the text of one screen (from a browser page-text tool, or copied by
hand). Prints the word count, the full sentences, lines and sentences that
appear more than once, phrases of three or more words repeated inside lines,
and glance-level precision such as the year and long time zone names.

The output is a list of leads for the ledger. Confirm each one on the rendered
screen, because the same words can sit in two different contexts. Single-word
repeats, such as a title in the breadcrumb and the heading, fall below the
phrase length, so the ledger has to catch those.

Usage:
  python3 -I repeat_scan.py < screen.txt
  python3 -I repeat_scan.py --min-words 4 < screen.txt
"""

import argparse
import re
import sys
from collections import Counter

WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'’-]*")
# A sentence is a run of at least five words that starts with a capital and
# ends in a full stop, question mark or exclamation mark. Chips and labels do
# not qualify.
SENTENCE_RE = re.compile(r"[A-Z][^.!?\n]{20,}?[.!?](?=\s|$)")
ZONE_RE = re.compile(r"\b(?:Africa|America|Asia|Atlantic|Australia|Europe|Pacific)/[A-Za-z_]+\b")
YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
TIME_RE = re.compile(r"\b\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm)\b")


def norm(line):
    return " ".join(w.lower() for w in WORD_RE.findall(line))


def report(title, counter, least=2):
    rows = sorted(((v, n) for v, n in counter.items() if n >= least), key=lambda r: (-r[1], r[0]))
    print(f"{title}: {len(rows)}")
    for value, n in rows:
        print(f"  {n}x  {value}")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--min-words", type=int, default=3)
    parser.add_argument("--max-words", type=int, default=12)
    args = parser.parse_args()

    text = sys.stdin.read()
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    print(f"words: {len(WORD_RE.findall(text))}")

    sentences = [s.strip() for s in SENTENCE_RE.findall(text) if len(s.split()) >= 5]
    print(f"sentences: {len(sentences)}")
    for s in dict.fromkeys(sentences):
        print(f"  - {s}")

    # A sentence repeated on every row of a list is the commonest finding, so
    # count whole sentences and whole lines before looking at fragments.
    repeated_sentences = report("repeated sentences", Counter(sentences))
    repeated_lines = report(
        "repeated lines", Counter(ln for ln in lines if len(WORD_RE.findall(ln)) >= args.min_words)
    )
    covered = {norm(v) for v, _ in repeated_sentences + repeated_lines}

    # Phrases stay inside one line, and the longest repeat wins: a shorter
    # phrase that sits inside a found one, or inside a repeated sentence or
    # line, is not reported again.
    found = []
    line_words = [norm(ln).split() for ln in lines]
    for size in range(args.max_words, args.min_words - 1, -1):
        counts = Counter(
            " ".join(ws[i : i + size]) for ws in line_words for i in range(len(ws) - size + 1)
        )
        for phrase, n in counts.items():
            if n > 1 and not any(phrase in longer for longer, _ in found) and not any(
                phrase in c for c in covered
            ):
                found.append((phrase, n))
    report("repeated phrases", dict(found))

    # Precision a glance does not need counts from its first appearance.
    report("long time zone names", Counter(ZONE_RE.findall(text)), least=1)
    report("years", Counter(YEAR_RE.findall(text)), least=1)
    report("repeated times", Counter(TIME_RE.findall(text)))


if __name__ == "__main__":
    main()
