---
name: project-abk-zavod-make
description: АБК завод (От Маке) КЖ — өз аналогын жаңа Задание осьтеріне келтіру; сечение/арматура аналогтан
metadata:
  type: project
---
05.11.2026: user gave `D:\РАБОЧКА\От Маке\Завод\АБК\Аналог\КЖ Чертеж АБК Последний.dwg` (own 34-sheet КЖ, 11.5×22.5 m, +3.800/+7.600) and `Задание по АБК для КЖ.dwg` (new: 11 axes × 6000 = 60 m, А–В 12 m, 0/+3.300/+6.600).
Rule: «жаңадан сызба, тек менікін переделка» — dims from Задание, element sections and rebar exactly as analog.
**Why:** user wants their own style/solutions reused. **How to apply:** clone analog sheets and stretch/remap to new grid; never invent new sections. Obsidian: `15_Проекты\АБК Завод (Маке)\КЖ АБК — переделка по аналогу.md`. Related: [[cad-clone-analog-stretch]]

05.11.2026 LIRA: new scheme `D:\РАБОЧКА\От Маке\Завод\АБК\Расчет\ABK_zavod.lir` from `gen_abk.py` (same folder): geometry from Задание, loads/seismic (module 61, ag 5.3, soil II, q 3.9) and mass coefficients from the analog `Аналог\Станция очистки - Цех пред обработки.lir`. Partitions of floor 2 placed at their real plan positions (floor-1 partitions are on slab-on-grade). Wall material confirmed by the user (gas block 250 / 100). RSN done 05.11 (EN 1990, normative loads, 22 columns). Still open: torsion cases, footing level −0.800, calculation not run. Details in the Obsidian note above. Related: [[lira-model-by-analog]]

**State 05.11 14:04 (BEKA-1 stopped, BEKA-2 continues):** working file `D:\РАБОЧКА\От Маке\Завод\АБК\КЖ Чертеж АБК.dwg`; new sheets row at y −1749172.3. Done 2.1–2.4, 3.1–3.4, 7.1–7.4, 7.6 (A3x3); 7.7 needs finish; 1.3 redo; rest not started. User remark: «Разрезде выноска қате түзет». Full handoff + tools: `D:\РАБОЧКА\От Маке\Завод\АБК\_Инструменты\ПРОМПТ_BEKA-2.md`.
