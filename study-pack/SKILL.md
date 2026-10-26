---
name: study-pack
description: Turn a folder of course materials (lecture slides/PDFs, practice problems with solutions, revision videos, notes) into a five-PDF study pack — a mock test, its answer key, a unit-by-unit problem workbook with show-your-work solutions, a complete master reference (also usable as context for another AI), and concepts notes. Use when the user says /study-pack, "make me a study pack", "study pack for <course>", "the multiple PDF method", "help me study for <test> from these files", or points at a folder of course materials and asks for practice tests or study notes.
---

# Study Pack: the multiple-PDF study method

The user studies for tests this way: give them the course materials, and they get **five PDFs** built from those materials. The test is about **solving problems**, so the problem PDFs (the workbook and the mock) matter most. The notes support them.

**How the user learns (non-negotiable).** For every problem type, show them **(1) the problem exactly as it will be asked**, then **(2) the answer to that example, written exactly the way they should write it**, then **(3) a real explanation of the whole concept** (what it is, why it works, how, with diagrams and traps; never just a list of rules), then **(4) a short checklist**. Only after that come the practice problems. Every practice problem must be solvable from the cards before it, and shows which cards it uses ("Uses M2 · M5"). `assemble.py` enforces both rules and fails the build otherwise. Showing facts without explaining them is a failure mode the user called out explicitly.

| # | PDF | What it is |
|---|-----|------------|
| 1 | Mock Test | Original test-style questions, deliberately longer than the real test, with work boxes |
| 2 | Mock Test ANSWERS | The same test with answers in red and a "Why:" for each |
| 3 | Unit Problem Workbook | **Centrepiece.** Per unit, one card per problem type: **how it's asked** (an example exactly as on the test) → **the answer, written exactly like this** → **how it works** (a full explanation of the concept) → **every time, do this**. Then 8–12 practice problems, each tagged with the cards it uses → worked solutions on the next page |
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
- **Plan each unit before writing any problem:** list its problem types, then its methods M1…Mn (one per type, including the "write the code" direction, "why" questions, edge cases and tricks), then which notes sections teach them.

### 4. Write the content (HTML)
Copy `templates/` into `<scratchpad>/build/`, then write:
1. `notes.html`: one section per topic, each starting with a `<!-- N -->` marker (the workbook can include sections as optional background reading).
2. `units.json` + `units/u1.html … uN.html` (use `templates/unit.html`: one **problem-type card** per type, `div.ptype data-m="M1"` containing `div.ask`, `div.write`, `div.explain` and `div.steps`; every problem is `div.q data-uses="M1 M3"`) + `wb_intro.html` + `wb_outro.html` → the workbook. **Write this most carefully.** For each card:
   - **ask**: a new example in the instructor's exact format (wording, tables, code layout, blanks);
   - **write**: its complete answer, laid out as the student should write it;
   - **explain**: teach the concept properly: what it is, why it works (the mechanism), the rules with reasons, a diagram where it helps, the traps, and a link to the lecture or official example. Aim for several paragraphs, not bullet fragments.
   Then do the **audit pass**: for each problem, ask "could a student who has read only this unit's cards solve this?" If not, add a card, or move the problem. `"learn"` in units.json can optionally add notes sections as background reading.
3. `mock.html` (from `templates/mock.html`; one source for both the test and the key). Every question must map to a workbook unit's method, and the scoring guide maps each Part to the unit to redo.
4. `master.html` (sections A–J, as in the spec).

Rules:
- Problems are **original** (the instructor's types, new numbers and code). Summaries of official problems are paraphrased, not transcribed.
- **Verify every answer.** Compute anything computable with a throwaway Python script in the scratchpad (arithmetic, hex/bit ops, offsets, loop traces). Re-read every given code listing for consistency.
- Each solution shows the work in the unit's show-your-work format, and gives the final answer and a "Trap:" where relevant.
- Use the CSS classes from `templates/style.css` (`.q .qn .lvl.e/.m/.h .work.s/m/l/xl .two .method .showwork .deck .sol .note .warn .good .part .fill .a .exp .keyonly .testonly .pb`). Don't invent new layout CSS unless it's needed.

### 5. Build and check
- `scripts/build.sh <build_dir> <materials_dir>/Study_Pack <COURSECODE>` renders all five PDFs with headless Chrome and runs `check_lines.py`. **If the coverage check fails, fix the content (add the missing teaching/method, or retag) — never delete the check or tag problems with methods they don't really use.** Fix flagged code lines that are too long by splitting them (every flagged line in units/ and wb_*.html should be zero), or by stacking a `.two` block vertically.
- `scripts/contact_sheet.sh <pdf> <png>` for each PDF; look at it. Check for blank or near-empty pages, clipped tables, and answer keys leaking into the test version. Zoom into a solution page and a mock page at ~70 dpi to confirm they are readable.
- Confirm the test PDF shows no answers, and the key PDF shows every answer and "Why".
- **Verify every card's example answer** with a throwaway Python check (layouts, arithmetic, traces), like the practice solutions.
- **Student read-through:** render one whole unit (header → cards → practice → solutions) at ~55 dpi and read it in order, as the student would. Does each card actually *explain*? Does each problem follow from the cards before it?

### 6. Deliver
- Save the PDFs in `<materials_dir>/Study_Pack/`. Send them with SendUserFile (when available), with display "attach".
- In the reply, give a short table of the five PDFs (pages, what's in each), the recommended order (workbook unit by unit → mixed review → timed mock → mark with the key), and any places where an official solution was incomplete or wrong.
- If you could not verify something (e.g. audio-only content in a video), say so.

## Defaults when the user gives no detail
- Output: Letter-size PDFs; the file prefix is the course code; the folder is `Study_Pack/` next to the materials.
- Mock: ~1.5–2× the real test length, organised by question type, with marks.
- Workbook: 8–12 problems per unit plus a 5–8 problem mixed review.
- Don't ask before starting unless the materials are missing or ambiguous (e.g. two different courses in one folder).
