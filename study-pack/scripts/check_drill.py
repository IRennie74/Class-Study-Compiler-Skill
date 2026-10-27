#!/usr/bin/env python3
"""Check the Q&A drill (drill.html): every question must be followed by its full answer.

Usage: python3 -I check_drill.py BUILD_DIR      (exit 1 on any problem)

Each <div class="qa"> must contain, in order: div.qq (the question), then div.ans with
p.look ("What you're looking at"), a <pre> worked answer, and p.why ("Why").
The drill must have Part A/B/C section heads (div.secthead) and at least 15 questions.
"""
import pathlib
import re
import sys

MIN_QUESTIONS = 15


def main() -> None:
    build = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    f = build / "drill.html"
    errors = []
    if not f.exists():
        sys.exit("DRILL CHECK FAILED:\n  - drill.html is missing (PDF 6, the Q&A drill, is required)")
    s = f.read_text()
    blocks = re.split(r'<div class="qa(?: big)?">', s)[1:]
    if len(blocks) < MIN_QUESTIONS:
        errors.append(f"only {len(blocks)} questions (need at least {MIN_QUESTIONS})")
    if s.count('class="secthead') < 3:
        errors.append("needs Part A / B / C section heads ordered by likelihood (div.secthead)")
    for b in blocks:
        num = re.search(r'<span class="qnum">([^<]+)</span>', b)
        name = num.group(1) if num else "?"
        q = b.find('class="qq"')
        a = b.find('class="ans"')
        if q == -1 or a == -1 or a < q:
            errors.append(f"{name}: needs the question (div.qq) followed by its answer (div.ans)")
            continue
        ans = b[a:]
        look, pre, why = ans.find('class="look"'), ans.find("<pre"), ans.find('class="why"')
        if look == -1:
            errors.append(f"{name}: answer is missing 'What you're looking at' (p.look)")
        if pre == -1:
            errors.append(f"{name}: answer is missing the worked answer (<pre>)")
        if why == -1:
            errors.append(f"{name}: answer is missing 'Why' (p.why)")
        if -1 not in (look, pre, why) and not (look < pre < why):
            errors.append(f"{name}: answer parts must be in order: look → worked answer → why")
    if errors:
        print("DRILL CHECK FAILED:")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    print(f"drill check passed ({len(blocks)} questions)")


if __name__ == "__main__":
    main()
