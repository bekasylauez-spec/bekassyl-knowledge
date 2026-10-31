---
name: km-paint-consumption
description: "КМ: ведомость расхода ГФ-021/ПФ-115 — площадь по м²/т профилей спецификации, таблица под спецификацией; первый раз Елмонте Блок 14 Пл.2"
metadata:
  type: project
---

2026-10-30: user asked «металл үшін грунтовка и краска расходын жаса» for «Елмонте\Лестница Блок 14\КМ Чертеж Лестница Блок 14 Площадка 2 07-09-2026 v2.dwg». The sheet-14 notes already say «ГФ-021 + 2 раза ПФ-115».
Done: an ACAD_TABLE «Ведомость расхода лакокрасочных материалов» goes under the spec table 641368 (handle 6611CC, same style and layer, all borders 0.30). The area cell holds a formula Σ(t × m²/t) = 198.3 m². ГФ-021 1×0.10 = 19.8 kg, ПФ-115 2×0.12 = 47.6 kg. I saved it to the file through accoreconsole (it was not open). Then the user asked «коэфициент қос», so I added a «Коэфф. потерь» column 1.10 → 21.8 / 52.3 kg. That went live into their open AutoCAD (table 661561, rebuilt with paint2.cs PAINTTBL2) and is NOT saved. Inserting a column into the existing table broke its formulas and borders, so rebuild the table instead. The original is in Мусор «(до ЛКМ 30-10)». The user has NOT confirmed the norms or the layout yet.
Method/rules: Obsidian `16_КМ чертежи/06_Спецификации и ведомости/Ведомость расхода лакокрасочных материалов.md`. Plugin: scratchpad 4a661048 `paint.cs` (PAINTTBL).
Note: sheet 1 note 7 also has a conflicting line «ПФ-1189 в заводских условиях», which I left unchanged.

Related: [[km-spec-rules]], [[cad-console-net-workflow]], [[obsidian-log-work]]
