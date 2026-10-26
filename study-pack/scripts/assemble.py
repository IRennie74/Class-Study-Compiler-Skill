#!/usr/bin/env python3
"""Assemble the unit problem workbook.

Usage: python3 -I assemble.py BUILD_DIR

Reads from BUILD_DIR:
  units.json      [{"n": "1", "title": "...", "lectures": "L01-L02", "facts": ["...", ...]}, ...]
  units/uN.html   one file per unit with three marked parts:
                  <!--METHOD--> method + show-your-work model + deck box
                  <!--PRACTICE--> practice problems (div.q with span.qn)
                  <!--SOLUTIONS--> worked solutions (div.sol) + checklist
  wb_intro.html   opening of the document (doctype, head, cover, how-to-use, rules)
  wb_outro.html   mixed review set + closing </body></html>
Writes BUILD_DIR/workbook.html
"""
import json
import pathlib
import re
import sys


def unit_parts(path: pathlib.Path) -> dict:
    text = path.read_text()
    chunks = re.split(r"<!--(METHOD|PRACTICE|SOLUTIONS)-->", text)
    parts = {chunks[i]: chunks[i + 1] for i in range(1, len(chunks), 2)}
    missing = {"METHOD", "PRACTICE", "SOLUTIONS"} - parts.keys()
    if missing:
        sys.exit(f"{path.name}: missing marker(s) {sorted(missing)}")
    return parts


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    build = pathlib.Path(sys.argv[1])
    units = json.loads((build / "units.json").read_text())
    out = [(build / "wb_intro.html").read_text()]
    for u in units:
        parts = unit_parts(build / "units" / f"u{u['n']}.html")
        n_problems = parts["PRACTICE"].count('class="qn"')
        n_solutions = parts["SOLUTIONS"].count('class="qn"')
        if n_problems != n_solutions:
            print(f"WARNING unit {u['n']}: {n_problems} problems but {n_solutions} solutions")
        facts = "".join(f"<li>{f}</li>" for f in u["facts"])
        out.append(
            f'<div class="pb unit-head"><h1>Unit {u["n"]} — {u["title"]}</h1>'
            f'<div class="sub">{u["lectures"]} · {n_problems} practice problems · '
            f"full worked solutions follow the practice set</div></div>"
        )
        out.append(
            '<div class="note"><b>Key facts you need for these problems</b>'
            f"<ul>{facts}</ul></div>"
        )
        out.append(parts["METHOD"])
        out.append(
            f'<div class="practice-head">Unit {u["n"]} practice set: do these on paper, '
            "showing your work as in the model above</div>"
        )
        out.append(parts["PRACTICE"])
        out.append(
            f'<div class="pb sol-head">Unit {u["n"]} solutions, with the work shown '
            "as you should write it</div>"
        )
        out.append(parts["SOLUTIONS"])
    out.append((build / "wb_outro.html").read_text())
    (build / "workbook.html").write_text("\n".join(out))
    print(f"workbook.html written ({len(units)} units)")


if __name__ == "__main__":
    main()
