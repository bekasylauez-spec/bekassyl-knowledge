---
name: km-spec-rules
description: "КМ спецификация (навесы): what the user expects in the steel spec table, and how to read LIRA .lir geometry without LIRA GUI"
metadata:
  node_type: memory
  type: feedback
  originSessionId: abf9821f-4a68-421d-a487-ba9dedaf39cc
  modified: 2026-10-13T05:43:35.396Z
---

User's rules for КМ steel specs (Навес 3, 2026-10-13):
- Lengths come from the DWG sections/plans, not from the LIRA model (LIRA levels may differ). LIRA is only used to confirm which members exist (e.g. purlin rows, cantilever).
- The spec must also list plates wherever a column touches concrete (base plates, wall plates of brackets), with anchors counted, plus the glass/roof area (m²).
- The user's table style: quantity in п.м. for tubes, formula cells (Кол = length formula, Масса = D*E, total = Sum). Keep the formulas, not typed numbers.
- When a detail is missing (e.g. wall plate size), drawing an extra node in their style (1:10, dimstyle "СПДС М10" cloned dims, title like "Вид А") is welcome.

**Why:** the user rejected v1 for counting a bracket as column length, taking cross-beam length to axes instead of between beam faces, and leaving out plates and glass area.
**How to apply:** count brackets separately from columns, take cross-beam length as the clear span between beam faces, and check every support for a plate. If the target DWG is open in AutoCAD (it has a .dwl), save the result as "... v2.dwg" next to it.

LIRA-SAPR 2013 .lir: the node array is plain little-endian doubles, 48-byte records (x, y, z + 3 doubles), in metres. Find it by searching for runs of 6-double records. Section names appear as ASCII strings like "100 x 4".

Related: [[cad-console-net-workflow]], [[cad-callouts-spds]]

КМ БЦ (Офис Байтурсынова Блок 1), 2026-10-16: the sheet-2 «Техническая спецификация металла» is an ACAD table (handle 5E967D, style Спецификация_АС): rows grouped by ГОСТ (швеллер / профили квадратные / прокат листовой), columns = masses in t per element group (Балка, Связи, Прогоны, Парапет, Фахверк), Общая = Sum. Cells hold formulas that show the derivation, e.g. `=(12*7.85*0.001*area_m2)` for plates and `=(kg_per_m*count*length*0.001)` for profiles. The user's own draft numbers there (t16 0.62, t14 0.05, t12 9.80) matched my recount, but the purlin, tube and C345 rows were left over from an analog. I rebuilt it with scratchpad 5f3c8931 `w\speckm.cs` (command SPECKM) and applied it in the user's open AutoCAD without saving.

КЖ bending schedules / specs (user correction 2026-10-17, Байтурсынова Фм-2): "дұрыстап есепте" — I had copied the analog's rule for stirrup sides (giving a side shorter than the bar spacing) and a Х2 sketch whose labels did not sum to L. Rules now: the user wants the side = bar c/c with NO +Ø (pedestal 320, not 335; they also set X1 bottom to 320). The overlapping ends add the hook (100) to the top and right sides. L = sum of the labelled sides. Масса ед. rounded to 0.01, and the row total = displayed unit × quantity (the user checks by multiplying). Ring stirrup count = centerline / spacing. Never trust the analog's numbers, recompute from the drawn geometry.

Table line weights (user, 2026-10-19, from their spec 5E967D): header rows and every column divider are 0.30 mm. Inside a group, horizontal lines between rows are 0.05 mm; a group's first top and last bottom are 0.30. «Всего профиля / Итог» rows and the last row are 0.30 all round. My newtable op takes bord [r,k,T,B,L,R] lineweights.
