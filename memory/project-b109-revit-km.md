---
name: project-b109-revit-km
description: "Завод В109 Цех Блок 1 — КМ Revit модель (08.11.2026, BEKA-2): DWG альбом «(Цех Блок 1, ЛИРА)» + В_109_v3_КМ.lir → gen.py → Revit, Алатау стилі"
metadata:
  node_type: memory
  type: project
  originSessionId: 38383950-ff15-462c-99ed-3b9b23e702df
  modified: 2026-11-08T17:05:46.632Z
---

**Request 08.11.2026:** «…КМ (Цех Блок 1, ЛИРА).dwg-ның КМ-ін Revit-те тұрғыз, алдыңғы цех (Алатау) стилінде». User confirmed the LIRA: `Том 14…\Расчет\В_109_v3_КМ.lir`.

**Files (BEKA-2):** model `D:\Бекасыл КЖ КМ\Завод_В109_КМ\227-23-П-УВПиОС-ВП-В109-КМ_Цех Блок 1.rvt`; scripts `Завод_В109_КМ\_авто\revit\`:
- `gen.py` → `members.tsv` (all members, mm, origin axis 1 × A, X along 1→28, Y A→M); `gs1.json` = ГС1 diagonals read from sheet 8 DXF.
- `b109_01_frame.cs` (project from БК_КМ.rte, grids 1–28 / A…M Latin, levels, members; type per mark, colour per mark), `b109_10_bases.cs`, `b109_90_clash.cs` (al_90 copy), `b109_91_shot.cs` + `_shots.txt` (PNG to `_тексеру\`). Run with `_Стандарт_КЖ\скрипттер\run_cs.ps1 -File … [-Lib b109_lib.cs] -Log …`.
- Library extended: `fam_03b_ibeam.cs` added 60Ш2 589×300×16×21, 60Ш3 597×300×18×25, 40Ш2, 40Ш1, 20Ш1, 30Б1, 40Б1, 45Ш1; `fam_06b_weldedI_asym.cs` → `(КМ)двутавр_сварной_несимметричный.rfa` (БМ1 250х10/640х6/200х10, top-surface line).

**Geometry decisions:** roof = one line +14.490 at A/M column faces → +15.240 ridge (slope 750/29705.5); ФФ1 Warren from section 1-1 (top nodes 3000k, bottom 1498.5+3000k, bottom chord top 12337.4 + 0.025·d); assumed НП 20Ш1, lattice □120x5 (2 per end) / □100x3 (Tekla ФФ1) — album says only «ВП 30Б1, решётка по расчёту». СВ1 Λ/V tiers 0…+5.020…+10.340, СВ2/СВ3 V above; Р1 centre +10.340 axes 3–26; БМ1 bottom +10.340 on КН 40Ш1 (950 from row); площадка from LIRA (Б7 assumed 30Б1, Б3 = К3 box). Bases: К1/К2 by узел 1 (600×950×40, 4 М42) — sheet 2 draws Б1 600×1500 / Б2 600×1790 (contradiction, ask user); СФ/СФ1/К3 anchors not in DWG (assumed).

How to apply: continue with nodes (truss gussets, brace gussets, caps, welds) in the same scripts; ask the user the open points above. Related: [[project-zavod-b109-km]], [[project-alatau-ceh-km]], [[revit-mcp-bridge]].
