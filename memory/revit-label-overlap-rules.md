---
name: revit-label-overlap-rules
description: "Revit КЖ scheme generator — how to keep marks/dims from overlapping (text×text penalty, short-segment rule, placement order, fragment region empty) and how to measure it (k97_overlaps.cs), ЕРЕЖЕЛЕР №128"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 94c03bfb-48e3-4972-8913-5871021722f0
  modified: 2026-11-15T17:11:39.067Z
---

15.11.2026, Касымова: the user said «Тығыз жерлердегі марка/размер қабаттасуын түзет» → «Иә, түзет». Before the fix, «150»×«См-1», «200»×«200» and «2500»/«250» collided in the dense cores.

**Why:** the user rejects any label touching another label. The occupancy scoring had weighted text-over-text the same as text-over-line, so dense spots were "forced" into text collisions.

**How to apply** (generator `D:\_claude_work\Kasymova\revit\k10_scheme.cs`, reuse for new Revit КЖ schemes):

Scoring:
- Keep a separate list of text boxes (`occT`). Score text×text at ×30, text over wall/column at ×6, text over a line at ×3.
- Choose column ties by score over 8 candidates instead of taking the first free one.

Placement:
- A dimension segment is "short" when its length < (number of characters × 1.8 + 1.2) mm on paper. Move its text outside the line.
- Place in this order: wall-thickness dims → wall marks. The element with fewer options goes first.
- Reserve the «Фрагмент 1» label and the opening mark (sample boxes along its line) before the dims and marks.
- In the main plan, drop chain points that lie inside the fragment region.
- Put the title above the highest visible dimension text. Ignore dims far outside the crop: on 2.9 they pushed the title up by 84 mm.

Checking:
- Measure with `k97_overlaps.cs` (reads the real elements). Text size is calibrated from the PNG: 1.55 mm per character, 2.3 mm high. Left-aligned TextNotes are measured from their left point.
- Target text×text = 0. Inspect borderline hits on a PNG before trusting them.
- Касымова result: 100 → 3 (all 3 borderline) and 51 → 15 (edges touching).

Related: [[revit-hatch-ansi36-join]], [[kzh-callout-hatch-level-rules]], [[check-callouts-honestly]], [[project-kasymova-hotel]]
