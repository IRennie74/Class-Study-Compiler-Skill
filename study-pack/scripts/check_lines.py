#!/usr/bin/env python3
"""Flag <pre> code lines that will wrap awkwardly on a Letter page.

Usage: python3 -I check_lines.py BUILD_DIR
Limits assume the bundled style.css (Menlo ~8.9pt, 15mm margins):
  full width ~95 chars, inside a two-column .two block ~44 chars, inside a table ~40 chars.
Long lines still render (pre-wrap), but splitting them by hand reads better.
"""
import html
import pathlib
import re
import sys

LIMITS = {"full": 95, "two": 44, "table": 40}


def context(before: str) -> str:
    if before.rfind("<table") > before.rfind("</table>"):
        return "table"
    i = before.rfind('<div class="two"')
    if i != -1:
        seg = before[i:]
        if seg.count("<div") > seg.count("</div>"):
            return "two"
    return "full"


def main() -> None:
    build = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    hits = 0
    for f in sorted(build.glob("*.html")) + sorted(build.glob("units/*.html")):
        if f.name in ("mock_test.html", "mock_key.html", "workbook.html"):
            continue
        s = f.read_text()
        for m in re.finditer(r"<pre[^>]*>(.*?)</pre>", s, re.S):
            ctx = context(s[: m.start()])
            text = html.unescape(re.sub(r"<[^>]+>", "", m.group(1)))
            for line in text.split("\n"):
                if len(line) > LIMITS[ctx]:
                    hits += 1
                    print(f"{f.name}: [{ctx} {len(line)}>{LIMITS[ctx]}] {line[:90]}")
    print(f"check_lines: {hits} long line(s)")


if __name__ == "__main__":
    main()
