---
name: baitursynova-album-stamps
description: "Байтурсынова Блок 1 КЖ — штамп эталоны (Штамп№1 из 3.2), крпкер, мусорные листы 2.x в чужих файлах, сборка PDF-альбома"
metadata:
  node_type: memory
  type: project
  originSessionId: f254f70b-9327-4406-8090-0914f166a8f6
  modified: 2026-10-16T17:32:48.465Z
---

2026-10-16: all 12 КЖ drawings (Байтурсынова Блок 1) got identical stamps and a 157-page PDF album (`_Claude\pdf\Финал 16.10`).

- Stamp = block `Штамп№1` (188x55 mm, origin = bottom-right inner corner of the frame, insert scale 1 at 1:100, 0.5 at 1:50). Some files used block `крпкер`, an old variant with a different header row, 515 mm rows and geometry offset ~(-982118,-811553). Fix: redefine the block contents from the reference `Штамп№1` (3.2 Выпуск), offset taken from the "RWD 24.02.01-КЖ" text, which sits at (-12000,5000).
- Sheet number (TEXT/MTEXT 2.5 mm, centre (-2750,2000)) and sheet name (centre (-8500,750)) live outside the block.
- 1.2 Котлован, 3.2 Выпуск and 9. Рампа also contain leftover copies of the Схема каркаса sheets (all numbered 2.x, plus an old 3.1 in Выпуск). Exclude them from the album.
- Found and fixed: sheet 7.57 had a stamp from another project (17/03-26-1-АР, ТОО "ПРОЕКТ ПЛЮС"). Sheet 9.1 is an A3 frame at 1:100 but its stamp and notes were at 1:50 size; scaled them x2 and moved the plan clear of the stamp.
- SPDS objects (SPDSSECTION, axes) can't be transformed in accoreconsole (eNotAllowedForThisProxy). That move was done in the user's AutoCAD 2021 (open doc, NETLOAD, save, close, restore sysvars).
- Frame for a sheet = the SPDS proxy whose bottom-right corner is 5 mm (sometimes 10 mm) off the stamp origin. Check the plot scale against the "Формат Ax" label height.
- Scripts: session f254f70b scratchpad `net\stampuni.cs, uni.ps1, plotall.ps1, fix757.cs, fix91.cs, move91.cs, find91.cs`; analysis/merge in `_Claude\stamps\*.py` (jobs.json = plot jobs).

2026-10-17 later: the user had added an empty 3.9 row to the Ведомость in 1.1 and renumbered Выпуск to 3.10–3.12 there. I filled the 3.9 name, renumbered the Выпуск stamps (3.9/3.10/3.11 → 3.10/3.11/3.12) and reflowed the 6 sheet-list tables. The tables are ACAD_TABLE 7D8DB…7D8E0, and each table's last row moves to the top of the next because the first table overflowed the 1.2 frame. After InsertRows/DeleteRows the last row lost its grid lines until `RecomputeTableBlock(true)`. Album: 158 pages in `_Claude\pdf\Финал 17.10`, jobs in `_Claude\ved1017\jobs.json`, scripts in session 4f5ceea1 scratchpad `net\ed.cs` (EDOPS: text/cell/shift/gridcopy/recompute), `run.ps1`, `plotall.ps1`.

Related: [[cad-console-net-workflow]], [[cad-dedicated-instance]]

2026-10-17: 3.1 Фундамент got sheet 3.9 «Фундамент Фм-2 на отм. -0.900» (A3 1:100, frame x 1404089–1446089, y −1012532…−982832; stamp Штамп№1 at 1445589,−1012032). Strip 600×200 ring 4180×3200, 4 pedestals 400×400 h900; levels assumed −0.900 top / −1.800 / −2.000; user then asked: pedestal mesh С1 → closed stirrup Х2 (Ø8 A240, 330×330 по в.г., L=1520, 36 pcs), strip gets TWO overlapping X1 stirrups as the user drew them: bars 1–4 and 2–5 (375 c/c each); after the user's 'recalculate' then user: 335→320, 385→320, so X1 = 420/130/320/230 L=1100 ×124, Х2 420/320/320/420 L=1480, pos1 1020/320/1020 L=2360, Ск1 L=1130; Сетка С1 detail removed; spec 214.03 kg. The analog copy (КР9–12) still sits above it at x 1417948–1438948, y −979604…−964754 for the user to delete. Sheet list in 1.1 not updated (done later the same day, see below).

2026-10-17 (Лестница 8.6/8.7): these sheets' SPDS Формат proxies (5AA43, 5CE1D) carry their own built-in title block from another project (65П-АИП-2024-1-КЖ). The console can't edit SPDS, so I covered each with a Wipeout (185×55 mm, 0.8 mm inside the frame lines, WIPEOUTFRAME 0). On top of it went a copy of the 8.5 Штамп№1 insert (scale 0.5), and the existing О_Формат number/name MTexts were moved to the top of the draw order. Plugin: session 4f5ceea1 `net\stamp8.cs`. The SPDS stamp is still inside the format object; switching it off in SPDS would be the cleaner fix.

2026-10-17 cleanup, after the user saw a doubled Разрез 1-1 on 5.19 and said "delete in the original DWG, then PDF":
- 5.19: an offset copy of the section (8 objects, 17CA94…17CA9F) was erased, and the notes 1885A5 were moved −7 mm.
- 1.1: MText 7B55A width 7912→7312.
- 11 exact-duplicate polylines erased (d02, d03, d06, d11).
- Kept 3 "duplicates" whose colour or lineweight differs: 7.56, 7.58, 8.6.
- Scanner: `_Claude\ved1017\scan.py` (only texts/dims count as shifted copies; ezdxf MText bbox gives false "out of frame" hits, so verify by rendering).
- Backups: `_Claude\ved1017\fix\backup` and `s519\orig.dwg`.
