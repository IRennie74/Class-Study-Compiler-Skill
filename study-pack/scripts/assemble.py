#!/usr/bin/env python3
"""Assemble the unit problem workbook, and refuse to build one that tests untaught material.

Usage: python3 -I assemble.py BUILD_DIR

Reads from BUILD_DIR:
  units.json      [{"n": "1", "title": "...", "lectures": "Lectures L01-L02",
                    "learn": [],              # optional: notes.html sections (<!-- 1 --> markers)
                    "facts": ["...", ...]}, ...]
  notes.html      the concepts notes; each section starts with a marker comment <!-- N -->
  units/uN.html   one file per unit with three marked parts:
                  <!--METHOD-->    one card per problem type:
                                   <div class="ptype" data-m="M1"><h3>Title</h3>
                                     <div class="ask">…</div> <div class="write">…</div>
                                     <div class="explain">…</div> <div class="steps">…</div></div>
                  <!--PRACTICE-->  <div class="q" data-uses="M1 M3"><span class="qn">1.1</span> …
                  <!--SOLUTIONS-->  <div class="sol"><span class="qn">1.1</span> …
  wb_intro.html / wb_outro.html
Writes BUILD_DIR/workbook.html.

Unit order in the PDF (learn first, then practise what was just taught):
  header → list of problem types M1..Mn → key facts → [optional background reading from notes]
  → one card per problem type:  HOW IT'S ASKED (example question, exactly as on the test)
                                → THE ANSWER, WRITTEN EXACTLY LIKE THIS → HOW IT WORKS (full
                                explanation of the concept) → EVERY TIME, DO THIS (checklist)
  → practice (each problem shows "Uses M..") → solutions (new page, same tags)

Coverage check (the build FAILS on any of these):
  * a practice problem without data-uses
  * a problem that uses a method the unit does not define
  * a method that no problem practises
  * practice and solution numbering that don't match
  * a problem-type card missing its example question (div.ask), written answer (div.write)
    or explanation (div.explain)
  * a "learn" section number that is not in notes.html
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


def notes_sections(build: pathlib.Path) -> dict:
    for name in ("notes.html", "guide.html"):
        f = build / name
        if f.exists():
            body = f.read_text().split("</body>")[0]
            pieces = re.split(r"<!-- (\d+) -->", body)
            return {int(pieces[i]): pieces[i + 1] for i in range(1, len(pieces), 2)}
    return {}


def methods_of(method_html: str) -> list:
    """Problem-type cards: <div class="ptype" data-m="M1"><h3>Title</h3> … (legacy: <li data-m> lists)."""
    cards = re.findall(r'<div class="ptype" data-m="(M\d+)">\s*<h3>(.*?)</h3>', method_html, re.S)
    if cards:
        return [(m, re.sub(r"<[^>]+>", "", re.sub(r'<span class="mtag">.*?</span>', "", t)).strip()) for m, t in cards]
    return re.findall(r'<li data-m="(M\d+)"><b>(.*?)</b>', method_html)


def card_errors(n: str, method_html: str) -> list:
    """Every problem-type card must show: the question as asked, the written answer, the explanation."""
    errors = []
    for m, body in re.findall(r'<div class="ptype" data-m="(M\d+)">(.*?)(?=<div class="ptype"|\Z)', method_html, re.S):
        for part, label in (("ask", "how it's asked"), ("write", "the written answer"), ("explain", "how it works")):
            if f'class="{part}"' not in body:
                errors.append(f"unit {n}: card {m} is missing '{label}' (div.{part})")
    return errors


def chip(uses: str) -> str:
    return '<span class="uses">Uses ' + " · ".join(uses.split()) + "</span>"


def check_unit(n: str, methods: list, practice: str, solutions: str) -> list:
    errors = []
    defined = {m for m, _ in methods}
    if not defined:
        errors.append(f"unit {n}: no labelled methods (<li data-m=\"M1\">)")
    qs = re.findall(r'<div class="q"([^>]*)><span class="qn">([^<]+)</span>', practice)
    used = set()
    for attrs, qn in qs:
        mu = re.search(r'data-uses="([^"]*)"', attrs)
        if not mu or not mu.group(1).strip():
            errors.append(f"unit {n}: problem {qn} has no data-uses (which methods does it need?)")
            continue
        for m in mu.group(1).split():
            if m not in defined:
                errors.append(f"unit {n}: problem {qn} uses {m}, which this unit never teaches")
            used.add(m)
    for m in sorted(defined - used, key=lambda x: int(x[1:])):
        errors.append(f"unit {n}: method {m} is taught but never practised")
    sol_ids = re.findall(r'<div class="sol"><span class="qn">([^<]+)</span>', solutions)
    if [q for _, q in qs] != sol_ids:
        errors.append(f"unit {n}: practice {[q for _, q in qs]} vs solutions {sol_ids} differ")
    return errors


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    build = pathlib.Path(sys.argv[1])
    units = json.loads((build / "units.json").read_text())
    notes = notes_sections(build)
    out = [(build / "wb_intro.html").read_text()]
    errors = []
    for u in units:
        n = u["n"]
        parts = unit_parts(build / "units" / f"u{n}.html")
        methods = methods_of(parts["METHOD"])
        errors += check_unit(n, methods, parts["PRACTICE"], parts["SOLUTIONS"])
        errors += card_errors(n, parts["METHOD"])
        learn = u.get("learn", [])
        for sec in learn:
            if sec not in notes:
                errors.append(f"unit {n}: learn section {sec} not found in notes.html")

        uses = dict(
            (qn, re.search(r'data-uses="([^"]*)"', a).group(1))
            for a, qn in re.findall(r'<div class="q"([^>]*)><span class="qn">([^<]+)</span>', parts["PRACTICE"])
            if "data-uses" in a
        )
        practice = re.sub(
            r'(<div class="q"[^>]*><span class="qn">([^<]+)</span>)',
            lambda mo: mo.group(1) + chip(uses.get(mo.group(2), "")) if mo.group(2) in uses else mo.group(1),
            parts["PRACTICE"],
        )
        solutions = re.sub(
            r'(<div class="sol"><span class="qn">([^<]+)</span>)',
            lambda mo: mo.group(1) + chip(uses[mo.group(2)]) if mo.group(2) in uses else mo.group(1),
            parts["SOLUTIONS"],
        )
        n_problems = len(uses)
        out.append(
            f'<div class="pb unit-head"><h1>Unit {n} — {u["title"]}</h1>'
            f'<div class="sub">{u["lectures"]} · {len(methods)} problem types, each: how it\'s asked → '
            f"the answer written out → how it works · then {n_problems} practice problems → worked solutions</div></div>"
        )
        out.append(
            '<div class="objectives"><b>The problem types in this unit (you will learn each one, then practise it):</b><ol class="mlist">'
            + "".join(f'<li data-m="{m}">{t.rstrip(".")}</li>' for m, t in methods)
            + "</ol></div>"
        )
        facts = "".join(f"<li>{f}</li>" for f in u.get("facts", []))
        if facts:
            out.append(f'<div class="note"><b>Key facts for this unit</b><ul>{facts}</ul></div>')
        if learn:
            out.append(f'<div class="learn-head">Background reading: Unit {n}</div>')
            for sec in learn:
                out.append(re.sub(r'<h2 class="pb">', "<h2>", notes.get(sec, "")))
        out.append(parts["METHOD"])
        out.append(
            f'<div class="pb practice-head">Unit {n} practice set: each problem lists the problem types it uses '
            "(M-numbers). Write your answers the way the cards show.</div>"
        )
        out.append(practice)
        out.append(
            f'<div class="pb sol-head">Unit {n} solutions, with the work shown as you should write it</div>'
        )
        out.append(solutions)
    if errors:
        print("COVERAGE CHECK FAILED:")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    out.append((build / "wb_outro.html").read_text())
    (build / "workbook.html").write_text("\n".join(out))
    print(f"workbook.html written ({len(units)} units) — coverage check passed")


if __name__ == "__main__":
    main()
