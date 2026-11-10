---
name: project-abk-zavod-make
description: АБК завод (От Маке) КЖ — өз аналогын жаңа Задание осьтеріне келтіру; сечение/арматура аналогтан; 05.11 BEKA-2 күйі
metadata:
  node_type: memory
  type: project
  originSessionId: 92892291-7735-4e20-9a30-a83b0b257986
  modified: 2026-11-05T16:12:33.700Z
---

05.11.2026: user gave `D:\РАБОЧКА\От Маке\Завод\АБК\Аналог\КЖ Чертеж АБК Последний.dwg` (own 34-sheet КЖ, 11.5×22.5 m, +3.800/+7.600) and `Задание по АБК для КЖ.dwg` (new: 11 axes × 6000 = 60 m, А–В 12 m, 0/+3.300/+6.600).
Rule: «жаңадан сызба, тек менікін переделка» — dims from Задание, element sections and rebar exactly as analog.
**Why:** user wants their own style/solutions reused. **How to apply:** clone analog sheets and stretch/remap to new grid; never invent new sections. Obsidian: `15_Проекты\АБК Завод (Маке)\КЖ АБК — переделка по аналогу.md`. Related: [[cad-clone-analog-stretch]]

05.11 LIRA scheme `Расчет\ABK_zavod.lir` (gen_abk.py), open questions in Obsidian note. Related: [[lira-model-by-analog]]

**ВАРИАНТ 2 (05.11 evening, BEKA-2):** `КЖ Чертеж АБК ВАРИАНТ 2.dwg` — Фм Ø16, Км Ø28, Рм Ø25, bored piles Ø700 L=9500 (1 per column, new sheet 1.5 from Лестница Блок 6), strip grid on Б and 2…10. Open: slab dop ~20 % (user decision), oc TOTAL 59, no PDF. Details + tools in Obsidian note and `_Инструменты\beka2_v2`. Trap: SPDS serfix with TILEMODE=0 lands in a layout.

**New task 05.11 late (supersedes dop + Ø700 piles):** beams 350×500 8Ø25+2Ø20 side, 4-leg stirrup Ø8; slabs Ø12 ш.100 no dop (dop erased); 1 m compacted-loam cushion + раскатные сваи Ø500 concrete L=11 m (1×1 under foundations, 2×2 under slab-on-ground), Ø700 sheet 1.5 to remove; Пм-1 120 mm, 2 meshes Ø12. LIRA prompt `Расчет\ПРОМПТ_ЛИРА_вариант2.md`.

**Done 05.11 ~20:00:** new task drawn in ВАРИАНТ 2 (plates ш.100, Пм-1 2 meshes, beams 350, rolled piles 453+80, cushion, sheet 1.5 deleted); oc TOTAL 2 (old 8.2); PDF `КЖ АБК ВАРИАНТ 2.pdf`. Open items listed in Obsidian note. Tools `_Инструменты\beka2_v2` (ops mcrep, sysvar, laycopy, laydel, import wins).

**Stamp/title 05.11 late:** naming + stamp taken from `Аналог\Кж-склад рулонов-02.11.26.dwg` (ТОО «КазНПИ СтройПроект», code СР-2026/1-КЖ, dates 05.09.26); new block «Штамп_АБК» on all 32 sheets, Разраб. = Ауез Б. (user) with own signature from template «крпкер»; title pages 0/00 from analog. Drawing keeps piles Ø500 per user's instruction (LIRA v3 used Ø300 from this analog). oc TOTAL 2, PDF rebuilt.

**LIRA v3 (05.11 20:50, BEKA-2):** `Расчет\ABK_zavod_v3.lir` (gen_abk3.py, c1_calc.py, v3_results.py → v3_нәтиже.md + PNG). Inputs changed vs prompt after the user said «геологиясын жақсылап қара» and «раскатный свайды осыдан ал»: ag 0.54g (geology СМЗ II-В-2), piles from analog `Аналог\Кж-склад рулонов-02.11.26.dwg` (Ø300 C16/20; Ск1 L11 1×1 armed Ø22 under foundations, Ск2 L9 2×2 under slab), C1 pad 680 / strip 470 т/м³. Recalculated 21:15 with Фм h=500 (strip 500×500, pad 2000×2000×500, base −2.500), C1 pad 700 / strip 560: 8Ø28 short only in the gable-end columns 1/А,1/Б,1/В,11/А,11/Б,11/В (−2.000…+3.300, ΣAs 52.5–62.2); beams 4+4Ø25 OK (max 18.8); slabs Ø12/100 OK (max 8.2); settlement 17–19 mm, pressure 145/115 kPa. Then the user chose 500×500 end columns (21:27 run; 400 variant kept as ABK_zavod_v3_кол400.lir): end columns ΣAs up to 68.0 → need 12Ø28; middle 400 columns OK with 8Ø28; +3.300 end beams 20.3–21.9 > 19.63 (add 1Ø16 top). User chose 500×500 + 12Ø28 (21:40), but col_check.py (fiber + Bresler) shows 12Ø28 fails (η 1.20) → 12Ø32 needed (η 0.96); middle 400 columns on А/В axes 4…9 need 4Ø32 corners + 4Ø28; end beams +1Ø18 (not Ø16). Then (22:00) user gave plan screenshot: pink 400×800 (А,В: 1,4…8,11; Б: 4…8), green 400×1500 (1/Б,11/Б), rest 400×400, remove stair → LIRA v4 `ABK_zavod_v4.lir` (gen_abk4.py, col_check4.py): 400×400 8Ø28, 400×800 12Ø28, 400×1500 14Ø25; beams/slabs OK; settlement ≤19.5 mm. Drawing (4.1 Км) not changed yet — AutoCAD listener session died on a save error, nothing saved (DWG 21:07). Open decisions in Obsidian «Схема v3». RSN cannot be transferred by copying .crsn1 — enter by hand.

**State 05.11 15:30 (BEKA-2):** all 32 sheets rebuilt in the new row of `КЖ Чертеж АБК.dwg`, old analog row deleted, layouts retargeted, specs recalculated. User decisions: stair 150×22, march 250×12; long elements stay on A2 with a break (not A2x4). Open: oc.py TOTAL 1426 to fix, then PDF from layouts. Handoff: `_Инструменты\ПРОМПТ_BEKA-2.md`, tools `_Инструменты\beka2\`.

**State 06.11 (BEKA-2) — drawing under v4: beams, slabs, выпуски done**
- New sheets added at the end of the row:
  - 6.3 Рм-3 (axes 4–8), 6.4 Рм-4 (axes 1/11) — copies of 6.2 stretched to the clear spans;
  - 3.8 Вп-2/Вп-3 (sections cloned from 4.2/4.3).
  - Coordinates of all sheets are in scratchpad `dw\w\sheets2.json`.
- Updated:
  - 2.3/2.4 spec (Рм-2 4 / Рм-3 5 / Рм-4 2) and 2.5 marks;
  - column outlines on 7.1–7.7, together with the Пм openings;
  - 3.6 edge columns and marks; 3.7 Вп-1 count 33 → 12.
- oc.py: no new hits.
- Still open:
  - 1.2 sheet list;
  - stair removal (8.x, 2.5);
  - LIRA eccentricity of the edge columns;
  - 5.2 node;
  - Фм under 1500;
  - PDF album.
- Trap: `clonexf` with `pre:''` maps old handle → clone, so a second clone of the same handles takes the first clone. Call `maprst` before each clone and omit `pre`.

**10.11.2026 (BEKA-1) — estimator remark (Дарья): pile spec, waterproofing volumes, geotextile.** Done in ВАРИАНТ 2: new sheet 1.5 «Армирование раскатных свай Св1» cloned from analog sheet 5 (1Ø22 A500С + Ø8 A240 fixators every 3 m); Св1 armed under Фм-1 (453), Св2 unarmed under Пм-1 (80), both Ø500 L=11; 1.4 got steel consumption (16883.3 kg), pile concrete 1151.3 m³, waterproofing table by elements (1162.7 m², mastic ГОСТ 30693-2000 per analog) and geomembrane HDPE 1.5 mm 1120 m² over the cushion (analog has membrane, no geotextile — awaiting user/ГИП confirmation). 1.2 list completed, PDF album 40 pages. Work dir `D:\_claude_workbk_gi`, details in the Obsidian note. Related: [[cad-dedicated-instance]]

**10.11.2026 later:** user chose «Ø500 қалсын, қалғаны аналогтай» — sheet 1.5 rebuilt as a full A2 copy of analog sheet 5 (Св1 armed L=11, Св2 unarmed L=9, concrete C16/20 W10 с.ф.ц., quality-control text); pile concrete now 1120.1 m³, steel 16883.3 kg. DWG + 40-page PDF replaced in the project folder.
