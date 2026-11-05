---
name: project-abk-zavod-make
description: АБК завод (От Маке) КЖ — өз аналогын жаңа Задание осьтеріне келтіру; сечение/арматура аналогтан; 05.11 BEKA-2 күйі
metadata:
  node_type: memory
  type: project
  originSessionId: 92892291-7735-4e20-9a30-a83b0b257986
  modified: 2026-11-05T15:48:36.772Z
---

05.11.2026: user gave `D:\РАБОЧКА\От Маке\Завод\АБК\Аналог\КЖ Чертеж АБК Последний.dwg` (own 34-sheet КЖ, 11.5×22.5 m, +3.800/+7.600) and `Задание по АБК для КЖ.dwg` (new: 11 axes × 6000 = 60 m, А–В 12 m, 0/+3.300/+6.600).
Rule: «жаңадан сызба, тек менікін переделка» — dims from Задание, element sections and rebar exactly as analog.
**Why:** user wants their own style/solutions reused. **How to apply:** clone analog sheets and stretch/remap to new grid; never invent new sections. Obsidian: `15_Проекты\АБК Завод (Маке)\КЖ АБК — переделка по аналогу.md`. Related: [[cad-clone-analog-stretch]]

05.11 LIRA scheme `Расчет\ABK_zavod.lir` (gen_abk.py), open questions in Obsidian note. Related: [[lira-model-by-analog]]

**ВАРИАНТ 2 (05.11 evening, BEKA-2):** `КЖ Чертеж АБК ВАРИАНТ 2.dwg` — Фм Ø16, Км Ø28, Рм Ø25, bored piles Ø700 L=9500 (1 per column, new sheet 1.5 from Лестница Блок 6), strip grid on Б and 2…10. Open: slab dop ~20 % (user decision), oc TOTAL 59, no PDF. Details + tools in Obsidian note and `_Инструменты\beka2_v2`. Trap: SPDS serfix with TILEMODE=0 lands in a layout.

**New task 05.11 late (supersedes dop + Ø700 piles):** beams 350×500 8Ø25+2Ø20 side, 4-leg stirrup Ø8; slabs Ø12 ш.100 no dop (dop erased); 1 m compacted-loam cushion + раскатные сваи Ø500 concrete L=11 m (1×1 under foundations, 2×2 under slab-on-ground), Ø700 sheet 1.5 to remove; Пм-1 120 mm, 2 meshes Ø12. LIRA prompt `Расчет\ПРОМПТ_ЛИРА_вариант2.md`.

**Done 05.11 ~20:00:** new task drawn in ВАРИАНТ 2 (plates ш.100, Пм-1 2 meshes, beams 350, rolled piles 453+80, cushion, sheet 1.5 deleted); oc TOTAL 2 (old 8.2); PDF `КЖ АБК ВАРИАНТ 2.pdf`. Open items listed in Obsidian note. Tools `_Инструменты\beka2_v2` (ops mcrep, sysvar, laycopy, laydel, import wins).

**LIRA v3 (05.11 20:50, BEKA-2):** `Расчет\ABK_zavod_v3.lir` (gen_abk3.py, c1_calc.py, v3_results.py → v3_нәтиже.md + PNG). Inputs changed vs prompt after the user said «геологиясын жақсылап қара» and «раскатный свайды осыдан ал»: ag 0.54g (geology СМЗ II-В-2), piles from analog `Аналог\Кж-склад рулонов-02.11.26.dwg` (Ø300 C16/20; Ск1 L11 1×1 armed Ø22 under foundations, Ск2 L9 2×2 under slab), C1 pad 680 / strip 470 т/м³. Result: corner columns 1/А,1/В,11/А,11/В (+1/Б,11/Б basement) exceed 8Ø28 (ΣAs up to 60.7); beams OK except +2 % at gable ends; slabs Ø12/100 OK everywhere; settlement 16–21 mm. Open decisions in Obsidian «Схема v3». RSN cannot be transferred by copying .crsn1 — enter by hand.

**State 05.11 15:30 (BEKA-2):** all 32 sheets rebuilt in the new row of `КЖ Чертеж АБК.dwg`, old analog row deleted, layouts retargeted, specs recalculated. User decisions: stair 150×22, march 250×12; long elements stay on A2 with a break (not A2x4). Open: oc.py TOTAL 1426 to fix, then PDF from layouts. Handoff: `_Инструменты\ПРОМПТ_BEKA-2.md`, tools `_Инструменты\beka2\`.
