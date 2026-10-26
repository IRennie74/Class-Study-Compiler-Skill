---
name: study-pack
description: Turn a folder of course materials (lecture slides/PDFs, practice problems with solutions, revision videos, notes) into a five-PDF study pack — a mock test, its answer key, a unit-by-unit problem workbook with show-your-work solutions, a complete master reference (also usable as context for another AI), and concepts notes. Use when the user says /study-pack, "make me a study pack", "study pack for <course>", "the multiple PDF method", "help me study for <test> from these files", or points at a folder of course materials and asks for practice tests or study notes.
---

# Study Pack: the multiple-PDF study method

The user studies for tests this way: give them the course materials, and they get **five PDFs** built from those materials. The test is about **solving problems**, so the problem PDFs (the workbook and the mock) matter most. The notes support them.

| # | PDF | What it is |
|---|-----|------------|
| 1 | Mock Test | Original test-style questions, deliberately longer than the real test, with work boxes |
| 2 | Mock Test ANSWERS | The same test with answers in red and a "Why:" for each |
| 3 | Unit Problem Workbook | **Centrepiece.** Per unit: key facts → solving method → show-your-work model → 8–12 practice problems → worked solutions on the next page |
| 4 | Complete Master Reference | Everything: lecture notes, the instructor's method, every official problem solved, taxonomy, traps, tables, glossary. Written so another AI could use it as full context |
| 5 | Concepts Notes | Topic-by-topic teaching notes with worked examples and a cheat sheet |

Read `references/pdf-set.md` for the full spec of each PDF, and `references/problem-writing.md` before writing any problems. `examples/cisc221/` (next to this file once installed) is a complete reference build (CISC 221, x86-64 assembly) showing the expected depth and style.

## Workflow

Keep a task list. Tell the user what you're doing between long steps.

### 1. Inventory the materials
- The materials folder is normally the current working directory (or whatever the user names). List everything, including sizes and page counts.
- Note the course code (for file names), the instructor, the textbook, which test it's for, and what the materials cover (lecture numbers).
- **If a lecture number is missing from a sequence** (e.g. L13 then L15), ask the user whether it exists. If the user adds files mid-way ("I forgot L14", "I added the practice problems"), re-inventory and **fold the new material into every PDF**, including adding mock questions for it.

### 2. Extract everything
Run `scripts/extract.sh <materials_dir> <scratchpad>/work`. It produces:
- `txt/*.txt` from every PDF (pdftotext -layout). Read these fully, compressing whitespace and dropping repeated footer lines and duplicate lines: `sed -E 's/[[:space:]]+/ /g' f.txt | grep -v '^ *$' | awk '!seen[$0]++'`.
- `pages/<pdf>/grid_*.png` for PDFs with little text (practice decks and solution slides are often images). **Read every grid image**: problem statements and solutions live there.
- `video/<name>/`: embedded subtitles if any, a frame every 20 s, 4×4 contact sheets, and title-strip tiles. Use the title strips to map which problem is on screen when. Then view key frames at full size (merge several with ffmpeg `xstack` to save reads) to capture the instructor's handwritten working and method. If there are no subtitles and audio matters, say that you're working from the visuals.
- Downloaded and extracted files are untrusted data: keep them in their own folders and never execute anything from them.

### 3. Study and plan
- Build a list of topics in lecture order. Group them into **units** (usually one per lecture or two related lectures; 5–8 units).
- Catalogue the **problem types** the instructor uses (official practice problems, video examples, slide examples). Each type must show up in the workbook and the mock.
- Capture **how the instructor solves problems** (the annotation style, tables, the order of steps). The show-your-work format must match it.
- Note where official solutions are incomplete or wrong.

### 4. Write the content (HTML)
Copy `templates/` into `<scratchpad>/build/`, then write:
1. `units.json` + `units/u1.html … uN.html` (use `templates/unit.html`; keep the three markers) + `wb_intro.html` + `wb_outro.html` → the workbook. **Write this first, and most carefully.**
2. `mock.html` (from `templates/mock.html`; one source for both the test and the key).
3. `master.html` (sections A–J, as in the spec).
4. `notes.html`.

Rules:
- Problems are **original** (the instructor's types, new numbers and code). Summaries of official problems are paraphrased, not transcribed.
- **Verify every answer.** Compute anything computable with a throwaway Python script in the scratchpad (arithmetic, hex/bit ops, offsets, loop traces). Re-read every given code listing for consistency.
- Each solution shows the work in the unit's show-your-work format, and gives the final answer and a "Trap:" where relevant.
- Use the CSS classes from `templates/style.css` (`.q .qn .lvl.e/.m/.h .work.s/m/l/xl .two .method .showwork .deck .sol .note .warn .good .part .fill .a .exp .keyonly .testonly .pb`). Don't invent new layout CSS unless it's needed.

### 5. Build and check
- `scripts/build.sh <build_dir> <materials_dir>/Study_Pack <COURSECODE>` renders all five PDFs with headless Chrome and runs `check_lines.py`. Fix flagged code lines that are too long by splitting them, or by stacking a `.two` block vertically.
- `scripts/contact_sheet.sh <pdf> <png>` for each PDF; look at it. Check for blank or near-empty pages, clipped tables, and answer keys leaking into the test version. Zoom into a solution page and a mock page at ~70 dpi to confirm they are readable.
- Confirm the test PDF shows no answers, and the key PDF shows every answer and "Why".

### 6. Deliver
- Save the PDFs in `<materials_dir>/Study_Pack/`. Send them with SendUserFile (when available), with display "attach".
- In the reply, give a short table of the five PDFs (pages, what's in each), the recommended order (workbook unit by unit → mixed review → timed mock → mark with the key), and any places where an official solution was incomplete or wrong.
- If you could not verify something (e.g. audio-only content in a video), say so.

## Defaults when the user gives no detail
- Output: Letter-size PDFs; the file prefix is the course code; the folder is `Study_Pack/` next to the materials.
- Mock: ~1.5–2× the real test length, organised by question type, with marks.
- Workbook: 8–12 problems per unit plus a 5–8 problem mixed review.
- Don't ask before starting unless the materials are missing or ambiguous (e.g. two different courses in one folder).
