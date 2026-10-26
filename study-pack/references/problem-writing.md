# Writing problems and solutions that actually prepare someone for the test

## Mirror the instructor, never copy them
- First catalogue the **problem types** in the official practice material, revision videos, assignments and past tests (e.g. "fill in the C from assembly", "operand value table", "struct layout").
- Every type the instructor uses must appear in the workbook (several times) and in the mock.
- Write new instances: change the numbers, the code, the constants and the structure, but keep the format and difficulty. Add harder variants that combine two ideas.
- Paraphrase textbook statements when summarising official problems (master reference, section D). Never reproduce long copyrighted text.

## Write for someone who knows nothing
- The user said: "even looking at a problem for the first time, I have no clue." Write every card, glossary and solution for a complete beginner.
- **Unit 0** covers the background the course assumes. Ask: what would someone need to know *before lecture 1* to follow it? Number systems, the machine model, notation, the language basics, how a problem page is laid out.
- **Define before use.** Each unit's glossary lists every term and symbol it uses. Inside a card, define a new term the first time it appears, or name the Unit 0 card that teaches it.
- **Decode the question** ("What you're looking at"): name each part of the question (template, given code, register line, tables, labels) and each symbol (%, $, parentheses, labels, 0x …), and say in plain words what is being asked.
- Avoid "simply", "obviously", "as usual", and unexplained jargon or abbreviations.

## Problem-type cards: show, decode, answer, explain
- The **ask** is not a description of the problem type. It IS a problem, formatted exactly as the instructor formats them (the same wording style, table shapes, code layout, blanks), so the student recognises it instantly on the test.
- The **write** is the answer a full-marks student would put on paper: setup line, one line per step with the reason, a clearly marked final answer, and a numeric check where possible.
- The **explain** must teach, not list. Cover what the concept is; the mechanism that makes it work (e.g. why cmp sets both kinds of flags, why alignment needs padding); each rule with its reason; a small diagram (pre block) when spatial (stack, memory layout, register nesting); the classic traps; and where it appears in the lectures or official problems. If the student could ask "but why?" after reading it, it isn't finished.
- The **steps** checklist is short (2–4 items) and is what the student runs through on the test.

## Teach before you test (coverage rule)
- Plan each unit as a **problem-type list first**: one card M1…Mn per problem type, then write the problems, tagging each with `data-uses`.
- Every problem type needs a card, including the easy-to-forget ones:
  - the reverse direction ("now write the assembly/code", not just "read it");
  - definition and "why" questions (toolchain, ISA vs. microarchitecture, why an idiom is used);
  - edge cases and tricks (do-while runs once, a dropped loop guard, division bias, scale limits, sign extension);
  - evaluation and tracing questions ("give f(7)", "stack depth in bytes").
- Each card's explanation must contain every fact its practice problems rely on.
- After writing a unit, do an **audit pass**: for each problem, ask "could a student who has read only this unit's Learn-it and methods solve this?" If not, add the missing teaching, or move the problem.

## Every answer must be verified
- Work every problem yourself before writing the solution. For anything computable, compute it: write a throwaway Python check (arithmetic, hex, bit operations, struct offsets, loop outputs for 2–3 inputs) in the scratchpad.
- Check that each problem has exactly one intended answer, or list all the accepted answers.
- Check that the given code or data are internally consistent (labels exist, jump tables match their ranges, struct sizes add up, units are consistent).
- Where an official solution is incomplete or wrong, say so explicitly and give the full answer.

## The show-your-work format
Each subject needs its own written-solution format. Define it once in the unit's model answer, and use it in every solution. Patterns that worked:
- **Setup line first:** givens / variable-to-register map / known quantities.
- **Annotated working:** one line per step, saying what changed and why ("rax = x + 2y", "Addr = 0x10 + 0x100 = 0x110 → M[0x110] = 0x3").
- **Tables** for anything stateful: trace tables (one row per step), layout tables (field / size / align / offset / pad), mapping tables (index → case → label).
- **Condition labels** for branching logic: write both edges of each decision.
- **Numeric check:** plug in small values and confirm both sides agree.
- **Final answer** clearly separated (on its own line, or prefixed with "Answer:").
- **Trap:** one line naming the mistake that loses marks on this problem.

## Difficulty mix per unit (8–12 problems)
- 2–3 easy: direct recall or one-step application (tables, definitions, single lookups).
- 4–6 medium: the bread-and-butter test types.
- 2–3 harder: combined ideas, trick cases (wrap-around, sign/unsigned, fall-through, padding), "describe in English what this computes".

## Mock test
- Longer than the real test, covering every type; label it as such.
- Each answer has a "Why" that teaches the method, not just restating the answer.
- Scoring guide → maps weak parts back to workbook units.
