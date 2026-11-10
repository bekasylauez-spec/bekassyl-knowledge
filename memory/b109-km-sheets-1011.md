---
name: b109-km-sheets-1011
description: "В109 КМ album sheets in Revit (10.11.2026 evening): which sheets exist, the scripts that build them, Revit API pitfalls found"
metadata:
  node_type: memory
  type: project
  originSessionId: b9d48af9-f7a2-4623-89d1-541fa9dfc459
  modified: 2026-11-10T16:38:40.219Z
---

В109 Цех Блок 1 КМ album is being drawn in the Revit model itself (DWG «КМ Чертеж узелдер.dwg» order). Done 10.11 ~21:40: sheets 1–13, 15–25 (24 sheets), PDF `Завод_В109_КМ\_тексеру\В109_КМ_листы.pdf`. Not done: 14 (ФФ1), 26–27 (подкрановые балки), 29–37 (развертки — elements not in the model), 38 (узлы 15–16 — not in the model). User has not given remarks yet.

Scripts (all re-runnable, `_авто\revit`): b109_s01_04 (texts/lines from DWG via scratchpad TSV), b109_s05…s11 (plans 1:200, sheet А3х4), b109_s08 (А2, 1:100), b109_s12/s13 + b109_sec_lib.cs (-Lib; sections, levels, schedule «Ведомость элементов»), b109_bases.cs (15–20), b109_s21_views/ann (sheet 21, hand-tuned), b109_nodes.cs (22–25, generated). Title block БК_штамп got formats А3х4 (b109_tb_a3x4.cs) and А3х3 (b109_tb_a3x3.cs). Own families in `_Стандарт_КЖ\семейства`: БК_узел_круг, БК_обрыв, БК_шов_заводской/монтажный (BEKA-1 has the user's originals in `D:\РАБОЧКА\Узлы_КМ\Семейства` — not swapped in yet).

**Why:** user 10.11: «барлық листерді … КМ чертеж узелдер стилімен, потом узелдерге өтесін, промпт бойынша».

**How to apply (Revit API pitfalls):** ViewSection.CreateSection mirrors the given frame — pass right/dir negated and origin on the far plane; plan Viewport.GetProjectionToSheetTransform origin = world (0,0) /scale, sections = crop min corner; grids have 3D extents ±4.6 m (SetVerticalExtents −2…+17 m needed for higher plans); levels need Model extents widened in a transverse section to show in other sections; hiding category «Стены» hid plan dimensions; view-filtered collectors need Regenerate after creating notes. Related: [[b109-km-chain-1011]].
