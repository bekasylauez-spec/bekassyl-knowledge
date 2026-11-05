---
name: project-abk-zavod-make
description: АБК завод (От Маке) КЖ — өз аналогын жаңа Задание осьтеріне келтіру; сечение/арматура аналогтан
metadata:
  type: project
---
05.11.2026: user gave `D:\РАБОЧКА\От Маке\Завод\АБК\Аналог\КЖ Чертеж АБК Последний.dwg` (own 34-sheet КЖ, 11.5×22.5 m, +3.800/+7.600) and `Задание по АБК для КЖ.dwg` (new: 11 axes × 6000 = 60 m, А–В 12 m, 0/+3.300/+6.600).
Rule: «жаңадан сызба, тек менікін переделка» — dims from Задание, element sections and rebar exactly as analog.
**Why:** user wants their own style/solutions reused. **How to apply:** clone analog sheets and stretch/remap to new grid; never invent new sections. Obsidian: `15_Проекты\АБК Завод (Маке)\КЖ АБК — переделка по аналогу.md`. Related: [[cad-clone-analog-stretch]]

05.11.2026 LIRA: new scheme `D:\РАБОЧКА\От Маке\Завод\АБК\Расчет\ABK_zavod.lir` from `gen_abk.py` (same folder): geometry from Задание, loads/seismic (module 61, ag 5.3, soil II, q 3.9) and mass coefficients from the analog `Аналог\Станция очистки - Цех пред обработки.lir`. Partitions of floor 2 placed at their real plan positions (floor-1 partitions are on slab-on-grade). Open: RSN, torsion cases, wall material and footing level (−0.800) to be confirmed by the user. Details in the Obsidian note above. Related: [[lira-model-by-analog]]
