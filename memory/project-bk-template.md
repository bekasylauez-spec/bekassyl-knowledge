---
name: project-bk-template
description: "Own КМ template БК_КМ.rte (prefix БК_), how template traces were removed, marks = tube types, БК_штамп from scratch; what is still pending"
metadata:
  node_type: memory
  type: project
  originSessionId: 72af3b3f-2397-48af-af38-773774531e1c
  modified: 2026-10-30T05:22:47.387Z
---

30.10.2026 the user required that nobody can tell a third-party template was used («шаблон екенін ешкім білмеуі керек»), prefix «БК_» (their firm), clean-and-rename approach. Done on `Каркастар\3602-КМ_Портал Блок 1.rvt`, then `_Стандарт_КЖ\шаблоны\БК_КМ.rte` (1,5 MB) made from it (t16_template.cs).

Key facts learned:
- Revit API cannot create or relabel family labels; renaming a shared param with the same GUID breaks labels (they match by name too). Label *sample text* set via API does not persist. Labels CAN be copied between families (ElementTransformUtils.CopyElements) — БК_штамп (t08_stamp.cs) was built from Autodesk's «Новый размер» template with labels copied from Autodesk precast title blocks (Libraries\Russian\Сборные элементы\Основные надписи) showing built-in params only.
- Marks = tube family type per mark, «Маркировка типоразмера» = mark; tag = Autodesk «M_Марка несущего каркаса» renamed БК_марка_каркаса (ISOCPEUR 2.5 italic, 7 mm shelf, no rotation — t13_tagfam.cs). All scripts read marks via `Symbol.get_Parameter(ALL_MODEL_TYPE_MARK)`; filters КМ_<марка> by type mark (c01).
- Template cleanup chain for a file still on the old template: t02 → t09 → t11 → t12 → t14 → t14b → t14c → t15; verify with q26_origin.cs. Some names are Revit system defaults (MEP params, duct/pipe/stair types) and cannot be removed.

Pending: other block files (Блок 2, Портики Блок 3, Карниз) and the main model still carry the old template → run the cleanup chain + model chain (with m14 / top-belt rule) when their оформление starts. KZhTagShelf add-in compatibility with БК_марка_каркаса not yet checked. Related: [[project-3602-km-portals]], [[feedback-km-error-checklist]].
