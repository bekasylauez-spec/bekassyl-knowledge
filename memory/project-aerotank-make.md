---
name: project-aerotank-make
description: Аэротенк (Маке) КЖ из .lir — 34 листа 1.1…7.3, Фм/плиты на A2 как 3.1 пользователя, ОД из АБК; oc 112
metadata:
  type: project
---

05.11.2026: КЖ по `D:\РАБОЧКА\От Маке\Завод\Аэротенк\Станция очистки -Аэротенк.lir` → `КЖ Аэротенк.dwg` + `КЖ Аэротенк.pdf` (30 листов из Layout «КЖ-N»). Ход работ и решения: Obsidian `15_Проекты/Аэротенк (Маке)/КЖ — ход работ.md`.
User decisions: «арматуру максимально»; ригели 350×500 между колоннами павильона, на оси 1 в проёме ригеля нет; Фм-1 основная Ø16, внутри каркасов КР-1 нет; колонны и ригели — только из шаблона «Колонна Км-1» / «Ригель Рм-1» (Шаблон для Кж.dwg), каждая марка на своём листе.
**Why:** user rejected my own-style column/ригель sheets («Қателер өте көп», «обсидианнан қалай жасалуын жаттап оқып шық»).
**How to apply:** continue from the Obsidian note; open items there (oc TOTAL 580, лист 1.1, gaps in model). Related: [[obsidian-first]], [[column-rules-template]], [[reservoir-kzh]]

05.11 вечер: user shrank 3.1 to A2 → all Фм/плита plans A2 (Пм-1 spec moved to 7.3); order 1 ОД, 2 схема, 3 фундамент+выпуски (Фм-2 = 3.8), 4 колонна, 5 стена, 6 ригель, 7 плита; model row gapless in that order; 1.1 content from АБК 1.1 (same zavod), 1.2 ведомость. Live DWG is master now — generator scripts (s3x/s7x slots) are stale, do not rerun them blindly. Geology/climate text in 1.1 (from АБК) confirmed correct by user 05.11 — same site data for all Маке zavod buildings.
06.11: added 3.9/3.10 (выпуски, user: «выпусктар қайда») and walls per axis 5.1–5.24 (См-1…См-8, opalubka + arm + A3 spec each, user approved structure); album 59 sheets. Rule saved in Obsidian: every КЖ needs 3.9/3.10 выпуски and per-axis wall sets.
