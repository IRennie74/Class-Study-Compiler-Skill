# Class Study Compiler Skill — my multiple-PDF study method for Claude Code

This is how I study for tests. I put all the course materials for a test in one folder: lecture slides, the instructor's practice problems and solutions, revision videos. Claude turns that folder into **five PDFs**:

| # | PDF | What I use it for |
|---|-----|-------------------|
| 1 | **Mock Test** | A full practice test of original, test-style questions. It's longer than the real thing, so every question type the instructor uses shows up. There are boxes for my work. |
| 2 | **Mock Test — Answers** | The same test with every answer in red and a short "Why" explaining the method. |
| 3 | **Unit Problem Workbook** | The main one. It assumes I know **nothing**: it starts with a **Unit 0 "Start here"** that teaches the background the course takes for granted, and every unit opens with a plain-language **words and symbols** glossary. Then, for every type of problem: **how it's asked** (an example exactly as on the test) → **what I'm looking at** (every part and symbol of the question explained) → **the answer, written exactly how I should write it** → **how it works** (the full concept: what, why, diagrams, traps) → a checklist. Then 8–12 practice problems per unit, each tagged with the problem types it uses, and fully worked solutions on the next page. It ends with a mixed review set. The build refuses to produce a workbook that skips any of this. |
| 4 | **Complete Master Reference** | Everything in one place: notes from every lecture, how the instructor solves problems, every official practice problem solved, problem types, traps, reference tables, glossary, self-test, exam checklist. Written so I can review it **or hand it to another AI** that then knows the whole course. |
| 5 | **Concepts Notes** | Topic-by-topic explanations with worked examples and a cheat sheet. |

Tests are about solving problems, so most of the pack is problems with worked, show-your-work solutions. The notes support the problems, not the other way round.

## Using it

The repo is **Class Study Compiler Skill**; the skill inside it is called `study-pack`. Install it once (below), open Claude Code in the folder with the course materials, and say:

```
/study-pack
```

or just "make me a study pack for this". It will:

1. **Inventory** the folder (PDFs, practice decks, zipped videos). It asks if a lecture seems to be missing, and if I add files halfway through, it folds them in.
2. **Extract** everything: PDF text, page images for image-only slides, and frames and contact sheets from revision videos, so it can see the instructor's handwritten working.
3. **Study** the material: it splits topics into units, catalogues the instructor's problem types, and learns the instructor's way of showing work.
4. **Write** original problems and solutions, **verifying every answer**.
5. **Build** the PDFs with headless Chrome, check the layout, and drop them in `Study_Pack/`.

## Install

```bash
git clone https://github.com/IRennie74/Class-Study-Compiler-Skill.git
```

```bash
cd Class-Study-Compiler-Skill && ./install.sh
```

That copies `study-pack/` into `~/.claude/skills/study-pack`. Requirements: macOS or Linux with `poppler` (pdftotext, pdftoppm), `ffmpeg`, Python 3, and Google Chrome, Edge or Chromium. On a Mac:

```bash
brew install poppler ffmpeg
```

## What's in the repo

```
study-pack/                  the skill (what gets installed)
  SKILL.md                   the workflow Claude follows
  references/pdf-set.md      exact spec of each of the five PDFs
  references/problem-writing.md   how problems & show-your-work solutions are written and verified
  scripts/extract.sh         materials → text, page images, video frames/contact sheets
  scripts/assemble.py        units.json + units/*.html → workbook.html
  scripts/build.sh           HTML → the five PDFs (headless Chrome) + layout check
  scripts/check_lines.py     flags code lines that would wrap badly
  scripts/contact_sheet.sh   one image of every page, for a quick visual check
  templates/                 style.css, mock/unit/workbook templates
examples/cisc221/            a complete real build (Queen's CISC 221, x86-64 machine-level programming)
install.sh
```

`examples/cisc221` holds the HTML sources of the first pack made this way: a 13-page mock and its 17-page key, a 59-page workbook with 76 problems, a 28-page master reference and 22 pages of notes. To rebuild it:

```bash
./study-pack/scripts/build.sh examples/cisc221 /tmp/cisc221_pack CISC221
```
