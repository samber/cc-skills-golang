#!/usr/bin/env python3
"""Flag markdown prose paragraphs longer than the sentence cap documented in CLAUDE.md."""

import argparse
import re
import sys

# Matches the "≤ 3 sentences per prose paragraph" budget in CLAUDE.md > Token budgets.
MAX_SENTENCES = 3

# Enough of the paragraph to identify it in an editor without flooding the terminal.
PREVIEW_CHARS = 80

FENCE_RE = re.compile(r"^\s*(```|~~~)")
LIST_ITEM_RE = re.compile(r"^\s*([-*+]\s|\d+[.)]\s)")
SENTENCE_END_RE = re.compile(r"[.!?](?=\s|$)")

# These abbreviations end in a period followed by a space, so the sentence heuristic
# would read them as sentence ends and flag paragraphs that are already within the cap.
ABBREVIATION_RE = re.compile(r"\b(?:e\.g|i\.e|etc|vs|cf|approx|resp)\.(?=\s)")


def blank_out_code_blocks(lines):
    """Replace fenced-code lines with empty ones, preserving line numbering."""
    result = []
    inside = False
    for line in lines:
        if FENCE_RE.match(line):
            inside = not inside
            result.append("")
            continue
        result.append("" if inside else line)
    return result


def paragraphs(lines):
    block = []
    start = 0
    for number, line in enumerate(lines, start=1):
        if line.strip():
            if not block:
                start = number
            block.append(line)
        elif block:
            yield start, block
            block = []
    if block:
        yield start, block


def is_prose(block):
    first = block[0].lstrip()
    if first.startswith("#") or first.startswith(">") or first.startswith("<"):
        return False
    if LIST_ITEM_RE.match(block[0]):
        return False
    for line in block:
        stripped = line.strip()
        if stripped.startswith("|") or stripped.count("|") >= 2:
            return False
        if set(stripped) <= set("-:| ") and "---" in stripped:
            return False
    return True


def count_sentences(text):
    count = len(SENTENCE_END_RE.findall(ABBREVIATION_RE.sub("", text)))
    # A paragraph ending without terminal punctuation still holds one sentence.
    return count if count else 1


def check_file(path):
    try:
        with open(path, encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    except OSError as error:
        print(f"skipping {path}: {error}", file=sys.stderr)
        return None

    flagged = 0
    for start, block in paragraphs(blank_out_code_blocks(lines)):
        if not is_prose(block):
            continue
        text = " ".join(line.strip() for line in block)
        sentences = count_sentences(text)
        if sentences > MAX_SENTENCES:
            flagged += 1
            preview = text[:PREVIEW_CHARS]
            print(
                f"{path}:{start}: paragraph has {sentences} sentences "
                f'(max {MAX_SENTENCES}): "{preview}..."'
            )
    return flagged


def main():
    parser = argparse.ArgumentParser(
        description="Warn about markdown prose paragraphs over the sentence cap."
    )
    parser.add_argument("files", nargs="+", help="markdown files to check")
    args = parser.parse_args()

    total = 0
    checked = 0
    for path in args.files:
        flagged = check_file(path)
        if flagged is None:
            continue
        checked += 1
        total += flagged

    print(f"{total} paragraph(s) flagged across {checked} file(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
