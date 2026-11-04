---
name: originals-are-dwg
description: "The user's original sheets are the network AutoCAD DWGs (rendered in png\\sheets), NOT Revit_оформление\\Лист N-N.png"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 1627bee1-9218-4ed4-bb58-ee22da3b578f
  modified: 2026-10-17T14:23:39.931Z
---

"Original" = the user's AutoCAD DWGs on `D:\РАБОЧКА\От Мадениет\Ресторан\КЖ\09-11-2025\2.Офис\<N>.<раздел>.dwg` (one Layout per sheet, drawing in Model at 1:100). Their faithful renders are `_авто\png\sheets\s - Лист - N-N - ….png`. The coloured `Revit_оформление\Лист N-N.png` files come from some other Revit model — not the original.

**Why:** 17.10.2026 I rebuilt 3.9 from `Лист 3-9.png` (wrong drawing). The user: «саған жіберген чертежды қара… айнымасын». Their real 3.9 was completely different.

**How to apply:** before building any sheet, open the DWG Layout (or `png\sheets\s - …`) and compare against it. When the user's details contradict the model, ask whether they want an exact copy. They chose «Дәл көшірме» for 3.9 (pipeline: split.lsp → xdump.lsp → dwg_to_json.ps1 → doc_26_dwg_copy.cs, see ЕРЕЖЕЛЕР §3в-4). Related: [[kzh-standard-folder]], [[revit-kzh-oformlenie]].
