---
name: pdf-from-layouts
description: "КЖ PDF альбомын модель терезесінен емес, әр файлдың Layout (лист) қойындыларынан шығару керек"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 4f5ceea1-c4c7-4b1b-9cf3-f4f8b4eff153
  modified: 2026-10-30T06:12:48.048Z
---

On 2026-10-17 the user rejected an album I had plotted from model-space frame windows: «ПДФ жасағанда қате жасағансың. Осыларға кіріп ПДФ жасауың керек» (they showed the layout tabs). Every PDF sheet must come from the drawing's Layout tabs.

**Why:** the layouts are the sheets the user actually prints. The model-window method also silently dropped sheets: 8.6 and 8.7 (Лестница) were never in the album because their stamps weren't detected in model space.

**How to apply:**
- Enumerate the layouts with a console dump that lists viewports (ViewTarget + ViewCenter, scale). Map each layout to its sheet by projecting the model frame through the viewport. Layout names are unreliable: 4. Колонна has layouts named 3.x, 2.Схема has 1..12, Стена has «19», 1.1 has an empty «1.5».
- Don't trust each layout's own page setup in accoreconsole. Some custom media (UserDefinedMetric 420x891 on DWG To PDF.pc3, «User-4», «User-5») fail or resolve to the wrong size, and rotations vary.
- What worked: in each layout, plot a paper-space Window around the frame at 1:1, with DWG To PDF.pc3, the smallest full-bleed sheet, centered, rotation 0. Then crop the page to the format in PyMuPDF.
- 1.1 «Общие данные» has no layout, so it still comes from the model window.
- Scripts: session 4f5ceea1 scratchpad `net\plotl.cs`, `laydump.cs`, `laysall.ps1`; `_Claude\ved1017\laymap.py, genwin.py, mergeL.py`.

2026-10-30 — the user restated it as a RULE («пдф моделде емес листте жасалсын бұл ереже»). Now the working pipeline (session 760c999f scratchpad): `w\mkjobs.py` reads the frame's own format text («Формат|A2», «A3x3»…) from the SPDS frame proxy and derives paper size + scale (don't guess from height: an A2-1:50 frame looks like A4-1:100); `net\layfix.cs` LAYFIX (console) renames/creates one layout per sheet number, sets page setup (DWG To PDF_all_formats.pc3 custom W×H or full-bleed fallback, mm, rot 0, Layout 1:1, origin 0) and replaces all model viewports by ONE locked viewport = whole page showing the frame at 1:sc (needs `LayoutManager.CurrentLayout = name` first, else eNotInPaperspace); `net\plotl.cs` PLOTL with `win:[0,0,w,h]` jobs plots each layout 1:1; `w\merge.py` crops; `w\chk\album_full.py` builds the album with TOC from the 1.1 register. Driver: `w\chk\layrun.ps1 -Keys ...`.

**2026-10-30 hard lesson — NEVER replace the user's viewports.** Sheets like 5.3 «Разрезы 1-1; 2-2 (См-1)», 5.8/5.11–5.13/5.16–5.18 and all ригель 6.x are COMPOSED in the layout: the main viewport shows the model frame, extra viewports bring sections/узлы (1:50, 1:20) from other model areas, so the model frame alone is nearly empty («разрездер жоқ ішінде»). The model-frame album had been wrong on those sheets since 26.10. Correct pipeline now: keep layouts as they are (only rename to sheet numbers / create missing ones with a frame viewport), compute the plot window = frame rectangle projected into paper space through the main viewport (CenterPoint + (frame − (ViewCenter+ViewTarget))·CustomScale), PLOTL `win` 1:1 on full-bleed media, crop. Scripts: `w\chk\genlay2.py`, `layrun2.ps1`, `layfix.cs` (jobs only for missing layouts), `album_full.py pL2_`. Verify by text-count: layout page ≥ model page.

Related: [[baitursynova-album-stamps]], [[cad-console-net-workflow]]

**06.11.2026 (АБК, the user):** «Рамканың сыртында ақ бос жер көп… PDF рамканың ең шеткі сызығынан тұру керек, артық ақ жер болмасын». Every album page is cropped to the frame.
- PyMuPDF: crop to the largest drawing rect (the frame), extended by the union of the drawings for the 1.1 side stamp (Инв. № подл.), plus «Формат А2» text under the frame, ±1.5 pt.
- `set_mediabox` takes PDF coordinates: y = H − y. Without this, A3x3 pages on A0 came out blank.
- Script: scratchpad `dw\crop.py`. Check every corner at 150 dpi: the frame line must be intact.

**12.11.2026 (АБК, the user):** rejected the frame-cropped album: «ПДФТІ дұрыстап жаса. Өзінің стандарттары болуы керек. Реттеп жаса». He confirmed the result the same day («Иә, дұрыс»): every PDF page must be an exact GOST 2.301 format (A4 210x297, A3 420x297, A2 594x420, A3x3 891x420 …) with the frame at 20 mm left / 5 mm other sides — not a page cut to the frame line; pages in sheet-number order, bookmarks «номер + название» from the 1.2 register. This supersedes the 06.11 «crop to frame» note. Script: `D:\_claude_work\abk_agsk\merge2.py` (frame = largest drawing rect → snap (w+25, h+10) to a standard format, flag anything outside). Also: spec rows drawn as attribute blocks (vcBlockST…, e.g. сетка ГОСТ 23279-2012 → 214-403-0101) are not table cells — scan INSERT attributes for ГОСТ too ([[agsk-code-in-spec]]).
