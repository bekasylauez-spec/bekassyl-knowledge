---
name: project-abk-zavod-make
description: АБК завод (От Маке) КЖ — өз аналогын жаңа Задание осьтеріне келтіру; сечение/арматура аналогтан; 05.11 BEKA-2 күйі
metadata:
  node_type: memory
  type: project
  originSessionId: 92892291-7735-4e20-9a30-a83b0b257986
  modified: 2026-11-05T14:45:14.025Z
---

05.11.2026: user gave `D:\РАБОЧКА\От Маке\Завод\АБК\Аналог\КЖ Чертеж АБК Последний.dwg` (own 34-sheet КЖ, 11.5×22.5 m, +3.800/+7.600) and `Задание по АБК для КЖ.dwg` (new: 11 axes × 6000 = 60 m, А–В 12 m, 0/+3.300/+6.600).
Rule: «жаңадан сызба, тек менікін переделка» — dims from Задание, element sections and rebar exactly as analog.
**Why:** user wants their own style/solutions reused. **How to apply:** clone analog sheets and stretch/remap to new grid; never invent new sections. Obsidian: `15_Проекты\АБК Завод (Маке)\КЖ АБК — переделка по аналогу.md`. Related: [[cad-clone-analog-stretch]]

05.11 LIRA scheme `Расчет\ABK_zavod.lir` (gen_abk.py), open questions in Obsidian note. Related: [[lira-model-by-analog]]

**ВАРИАНТ 2 (05.11 evening, BEKA-2):** `КЖ Чертеж АБК ВАРИАНТ 2.dwg` — Фм Ø16, Км Ø28, Рм Ø25, bored piles Ø700 L=9500 (1 per column, new sheet 1.5 from Лестница Блок 6), strip grid on Б and 2…10. Open: slab dop ~20 % (user decision), oc TOTAL 59, no PDF. Details + tools in Obsidian note and `_Инструменты\beka2_v2`. Trap: SPDS serfix with TILEMODE=0 lands in a layout.

**New task 05.11 late (supersedes dop + Ø700 piles):** beams 350×500 8Ø25+2Ø20 side, 4-leg stirrup Ø8; slabs Ø12 ш.100 no dop (dop erased); 1 m compacted-loam cushion + раскатные сваи Ø500 concrete L=11 m (1×1 under foundations, 2×2 under slab-on-ground), Ø700 sheet 1.5 to remove; Пм-1 120 mm, 2 meshes Ø12. LIRA prompt `Расчет\ПРОМПТ_ЛИРА_вариант2.md`.

**State 05.11 15:30 (BEKA-2):** all 32 sheets rebuilt in the new row of `КЖ Чертеж АБК.dwg`, old analog row deleted, layouts retargeted, specs recalculated. User decisions: stair 150×22, march 250×12; long elements stay on A2 with a break (not A2x4). Open: oc.py TOTAL 1426 to fix, then PDF from layouts. Handoff: `_Инструменты\ПРОМПТ_BEKA-2.md`, tools `_Инструменты\beka2\`.
