---
name: drawing-spacing-hatch-rules
description: User drafting rules 2026-10-20 — labels/dims spaced off elements, one hatch per wall contour, openings not X (template diagonal), section line outside dims
metadata:
  type: feedback
---

2026-10-20 (said mid-task while I did the Схема каркаса explication): «жазулар размерлер элементке қатты тақалмасын, алшақтау болсын», «стеналардың контурларын жеке жеке жаса», «отверстиялар Х болып белгіленбейді шаблонды қара», «Разрез зданиеге қатты тақалмасын размердің сыртында тұрсын».

**Why:** the user checks plots visually; crowded text and merged multi-loop hatches are rejected.

**How to apply:** place texts with clear margin (I used polylabel in the room minus door swings/stairs, eroded by text box + 250); one associative hatch per wall polyline; openings/shafts = single diagonal lower-left→upper-right, never X; section marks outside dimension chains. Recorded in Obsidian `01_Общие правила/Оформление КЖ в AutoCAD — СПДС (утверждённые правила).md` §9. Some of these messages may have been meant for a parallel КЖ session ("КЖ Чертеж в AutoCAD") — they still apply generally.

Related: [[cad-callouts-spds]], [[km-callout-style]], [[obsidian-log-work]]
