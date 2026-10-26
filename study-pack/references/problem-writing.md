# Writing problems and solutions that actually prepare someone for the test

## Mirror the instructor, never copy them
- First catalogue the **problem types** in the official practice material, revision videos, assignments and past tests (e.g. "fill in the C from assembly", "operand value table", "struct layout").
- Every type the instructor uses must appear in the workbook (several times) and in the mock.
- Write new instances: change the numbers, the code, the constants and the structure, but keep the format and difficulty. Add harder variants that combine two ideas.
- Paraphrase textbook statements when summarising official problems (master reference, section D). Never reproduce long copyrighted text.

## Teach before you test (coverage rule)
- Plan each unit as a **problem-type list first**: write the methods M1…Mn (one per problem type), then write the problems, tagging each with `data-uses`.
- Every problem type needs a method step, including the easy-to-forget ones:
  - the reverse direction ("now write the assembly/code", not just "read it");
  - definition and "why" questions (toolchain, ISA vs. microarchitecture, why an idiom is used);
  - edge cases and tricks (do-while runs once, a dropped loop guard, division bias, scale limits, sign extension);
  - evaluation and tracing questions ("give f(7)", "stack depth in bytes").
- The unit's "Learn it" notes must contain the facts each method relies on.
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
