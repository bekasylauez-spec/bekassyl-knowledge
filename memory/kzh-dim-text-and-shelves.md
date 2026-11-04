---
name: kzh-dim-text-and-shelves
description: Dim text stays at the standard gap on its line, shifted only along it. Note shelves never cross axes or elements. Фм sheet order is exactly the analog's.
metadata:
  type: feedback
---

Three corrections from 31.10.2026 on the Резервуар КЖ.

1. The user sent a sample of their own dimension next to mine (17750): «менің размерім қалай сызылған соны үйрен».
   - My text sat about 4.5 mm from the dim line. Theirs sat at the standard ~2.25 mm.
   - Cause: I put the text point 2.25 mm off the line, and then DIMTAD=1 lifted it another DIMGAP.
   - **How to apply:** when overriding a dim's TextPosition, keep the perpendicular coordinate ON the dim line and shift only along it. When an axis runs through the middle of a short dim, split the dim at the axis instead (625|625).
2. Screenshot of sheet 3.2: the «1/ш.200» shelf ran across a column and axis Б, and «Ск1» lay on axis 2.
   - **How to apply:** put note shelves in a free bay between axes, away from columns and axis lines.
   - oc.py now checks this as «ПОЛКА/ЛИНИЯ». Its exceptions: the SPDS section cut line, and a «поз →» arrow note that continues a dim chain.
3. «доп арматура ретін тағы қара».
   - **How to apply:** Фм sheet order must be exactly the analog's: 3.1 опалубка, 3.2 основная, 3.3–3.6 доп. (низ букв, верх букв, низ цифр, верх цифр). Sections go to a later sheet (3.7). Position numbers ascend in the same order.

All three are recorded in the vault: `01_Общие правила/Оформление КЖ в AutoCAD — СПДС (утверждённые правила).md` §6.

Related: [[obsidian-first]], [[reservoir-kzh]], [[sheet-orientation-by-building]]

04.11.2026 (ЖК Галакси Фм), what dimtx actually does with СПДС-style rotated dims:
- A text standing on its dim line is centred on the given point. Horizontal dim: point = (segment middle, line y + 155). Vertical dim: point = (line x, segment middle) — the text then sits 225 left of the line.
- A text moved off the line onto a leader shelf is anchored at one END of the text, and which end flips with the leader direction. Place it, re-dump the geometry and look again; never trust a computed box.
- Never let fixtext.py run after manual dimtx fixes: it moved my fixed texts back. Keep it to automatic passes only.
