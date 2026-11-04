---
name: project-alatau-ceh-km
description: "Цех Блок 1 Алатау (4П-18.02.2025-КМ, user is the author «Ауез Б»): full КМ model in Revit from the DWG — data, tools, state"
metadata:
  node_type: memory
  type: project
  originSessionId: c4f44258-6943-4b10-8e73-e6f1e42efec6
  modified: 2026-10-31T17:25:31.087Z
---

**Request.** On 31.10.2026 the user asked to build in Revit the full model from `D:\РАБОЧКА\От Шерхан\ЦЕХ Алатау\КМ Чертеж\КМ Чертеж Блок 1 Без СПДС 14-03-2026.dwg`. Their words: «полный, лист, болт, барлығын жаса, майда шүйде узелдер барлығы» — everything, including plates, bolts and all small nodes. The title block lists «Разраб. Ауез Б», the user.

**Project folder.** `D:\Бекасыл КЖ КМ\Алатау_ЦЕХ_КМ`:
- `исходник\` holds the DWG and the PDF;
- `исходник\pdf_png\p01…p34` are the PDF pages, where page = sheet number + 6;
- `исходник\dwg_pdf\` holds the 20 layouts that plotted. The large A3×3 / A4×4 sheets fail with «Нет подходящего носителя».
- `_авто\00_исходные_данные.md` holds all extracted data (grid, levels, marks, profiles, nodes, open questions). Read it first.

**Building.**
- Plan 72×24 m: axes 1–13 @6000, rows А/Б/В @12000 (А/1, Б/1 are фахверк lines).
- Columns К1 60Ш4 605×300 s20 t28.5 r28 (39). Б2 welded tapered rafters (eave +11.000, ridge +12.140).
- Б1 50Б2 and БМ1 70Б1 in span В–Б. Purlins Пр1 18Б1. Bracing Вс1–5 / ГС1 / Р1 (tubes). Base plates −30 640×945 with 4 M42.

**Tools.**
- Scratchpad LISP `km_inv.lsp` (layouts, viewports) and `km_geo.lsp` (blocks exploded, full precision with rtos — `prin1` gives only 6 digits).
- `_авто\layouts_windows.csv` maps each layout to its model window.
- `_авто\dwg_render.ps1` renders a model window to PNG. Never name a PowerShell variable `$inv` next to a `-Inv` parameter: PowerShell is case-insensitive and one clobbers the other.
- accoreconsole scripts: use `_-PLOT` / `_N` / `_Y`, and output paths with no spaces (a space acts as Enter).

**State 31.10.2026 (evening).**
- Revit model `4П-18.02.2025-КМ_Блок1.rvt` built by `_авто\al_01` (frame), `al_13` (nodes 1/2, Б2 plumb ends, column-top voids), `al_10` (bases), `al_11` (tube nodes), `al_12` (nodes 3/9/10/4, purlin bolts). All run with `-Lib alatau_lib.cs`.
- Per-sheet DWG specs (Russian) in `_авто\spec\`: sheet18 (node 1, node 9/11, УП1), sheet19 (node 2, БМ1 splice 12/14), sheet20 (nodes 3, 10, 4), sheet21 (nodes 5–8), bases, frame_members. Use these, not memory, for every part.
- All nodes rebuilt to the DWG specs on 31.10.2026:
  - 1, 2 (al_13);
  - ГС1 / node 5 (al_14);
  - 9/11, УП1, БМ1 splice (al_15);
  - 3, 10, purlin welds (al_12);
  - 6, 7, 8, Б2 brace gusset (al_11);
  - bases (al_10).
- Run order after a frame change: al_13 → al_14 → al_15 → al_12 → al_11 → al_10 → al_90 (per-solid audit, writes `_al90.txt`).
- Not done yet:
  - node 4 (Сф1 top: post position vs Б2 contradicts the DWG);
  - facade elements (sheets 22–25);
  - stair (26–28).
- Open questions for the user are in `_авто\СҰРАҚТАР_DWG.md`: Б2 flange 220 vs 300, bolt diameters, node 4, splice plate width, and others.
- Sheet 18 is cropped in the DWG layout itself, so nodes must be read from model space; geometry sits on layer «Размеры».

Related: [[project-node-20k1-25b1]], [[km-tube-families]], [[feedback-km-error-checklist]].
