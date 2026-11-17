---
name: layout-from-model-frames
description: "Модельдегі рамкаға Layout жасау (бөтен АР файлы) — MKLAY құралы, жаңа viewport тұзақтары (VP-freeze қабаттары, PSLTSCALE), PMP-ге custom қағаз қосу (mkpmp.py)"
metadata:
  node_type: memory
  type: reference
  originSessionId: 329462b1-55b9-4578-b28b-f85b12edb13f
  modified: 2026-11-17T10:43:29.692Z
---

17.11.2026, `KZ_Aktau Kız Yurdu Projesi_2026.11.05.dwg` (Turkish AR file in Downloads). Request: «Мынаның моделдегі рамкаларын листке салып бер. Суреттегі листті». I made ONE layout, for the pictured frame only, and offered the other 12 — that scope was my reading; the user had not answered yet when this was written.

**Tools** — `D:\_claude_work\aktau_ar_layout\`: `mklay.cs` (accoreconsole commands MKLAY / LAYPLOT / MWPLOT / MEDIALIST), `mkjobs.py`, `run.ps1 -Ctb monochrome.ctb -Idx 2 3 …`, `mkpmp.py`, `check.py` (pixel diff: layout plot vs model-window plot), `cmpdxf.py`, `cmpblk.py`. Frames there are in `frames.json` (13 INSERTs on layer `antet`, dynamic block at scale 50, attributes PAFTANO / PAFTAADI; units cm, so 5 model units per paper mm at 1:50).

**Traps — a new viewport does not show what the model shows until:**
- `vp.ThawAllLayersInViewport()`: layers flagged "frozen in new viewports" (layer flag 2; here yazı-merd, agac, …) are VP-frozen automatically and their objects silently vanish.
- `db.Psltscale = false` while the new layout is current: PSLTSCALE is a per-layout flag and a new layout gets 1 (BATTING insulation came out 5× too coarse).
- The frame's outermost line lies on the paper edge: give the viewport a 0.02 mm overhang and pass the frame corners at full double precision (`%r`). Only then was the layout plot pixel-identical to the model-window plot.
- `SetPlotCentered` throws eInvalidInput for PlotType.Layout.

**PMP/PC3 container** (measured): header text + adler32 of the COMPRESSED stream + uncompressed size + compressed size (uint32 LE) + zlib level 9; payload cp1251, LF, one trailing NUL. `mkpmp.py <pmp> <bakdir> W H` appends "UserDefinedMetric (W x Hмм)" full-bleed; the user's running AutoCAD saw the new size without a restart. Supersedes the note in [[project-v113-km]] that BEKA-1 needs BEKA-2's `mkpmp.py`.

**Delivery:** the drawing open in the user's AutoCAD can be another copy of the attached file (here WhatsApp's `transfers` folder vs Downloads, same SHA1) — compare `FullName` over COM before assuming it is the same file. I wrote the result to the attached path and opened it in the user's AutoCAD with COM `Documents.Open` (no SendCommand); the first calls after Open return RPC_E_SERVERCALL_RETRYLATER, so retry.

Related: [[pdf-from-layouts]], [[spds-format-frames-standard-paper]], [[cad-console-net-workflow]], [[close-user-file-myself]]
