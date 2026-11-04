---
name: bdm-block4-slabs
description: БДМ Блок 4 (Шерхан) плиты Пм1 +7.000 / Пм2 +4.500 — армирование по аналогу Б2.плита1, ЛИРА As CSV, файл Б4.плита1.dwg (04.11)
metadata:
  type: project
---

04.11.2026: user asked to copy the analog `Б2.плита1.dwg` and reinforce two Block 4 slabs from the open LIRA «бдм блок 4» («қайта ашып іздемей-ақ қой» — use the LIRA already open). Result `D:\РАБОЧКА\От Шерхан\БДМ Блок 4\Б4.плита1.dwg`, 12 sheets (Пм1 +7.000 = 1–7, Пм2 +4.500 = 8–12).

**How:** LIRA GUI «Документация → Стандартные таблицы → Арматура в элементах → в пластинах» writes CSV to `Work\<task>.docs\.INV\tbl01.32_2.csv` (AS1..AS4 cm²/m). Drawing built in accoreconsole with my plugin `p4.cs` (scratchpad 7dee2eb7 `net\`): copywin/erasewin/movewin/repl/clone/dim/table ops; freeze FIELDS first.

**Open:** P70 opalubka has no sections; dense callouts at the atrium corner (axis 38); not run through oc.py. Vault: `15_Проекты/БДМ Блок 4 (Шерхан)/`.

Related: [[obsidian-first]], [[cad-console-net-workflow]], [[no-repeat-check-pipeline]]

Block 3 (04.11, requested «4 плитасындағыдай»): folder `D:\РАБОЧКА\От Шерхан\БДМ Блок 3` = scheme `БДМ Блок 3 Без СПДС.dwg` (same layout as Block 4; axes 22=0, 23=650, 24=5950, 25=11300, 26..32 step 6000, 33=53950) + zip with only `БДМ Блок 3-кор.lir` (no results). Slabs by the user's blue contours: +4.500 (415,-250)-(23650,14200); +7.000 south (415,-250)-(53535,16900); +7.000 north L (415..53535 × 25500..36250/39300 from x 16950). User said «Күт онда» — waiting for them to calculate it in LIRA; geometry already in scratchpad 7dee2eb7 `b3\g2.txt, g3.txt`.
