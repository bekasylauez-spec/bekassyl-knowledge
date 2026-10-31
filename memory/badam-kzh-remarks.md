---
name: badam-kzh-remarks
description: Бадам подводящий канал ГР.КЖ — ответы на замечания 23.10; field AcObjProp gotcha in spec tables
metadata:
  node_type: memory
  type: project
  originSessionId: a65433f5-4f1e-46f2-a510-b9400a39c21d
  modified: 2026-10-23T05:27:48.148Z
---

2026-10-23: expert remarks (Шалковский) on `D:\РАБОЧКА\От Мадениет\Канал бадам\КЖ Чертеж Бадам 27-07-2026.dwg` were fixed into a new file `КЖ Чертеж Бадам 23-10-2026 (по замечаниям).dwg`, answers in `Ответы на замечания ГР.КЖ Бадам.docx` (format copied from БЦ Навес «Ответы на замечания КМ.docx»: title + table № | Замечание | Ответ).

Facts: 205 m = 10 m каменная наброска + 195 m канал; Тип-6 is 8.0 m; prep 100 mm ledge → width 9.0 m; trap 155.48 m; new sheets 3.1 (котлован) and 29.1 (балки потерны, двутавр 20 assumed). Expert numbers sheets by stamp numbers; trap plan+sections+spec are one sheet 29 (layout «30»: 1:200 + 1:10 viewports).

**Why:** follow-up rounds of remarks will build on this file, not the 27-07 one.

**How to apply:** spec tables there have «L=» cells as AcObjProp fields pointing at СПДС objects — editing a table in accoreconsole blanks them and dependent formulas (####). Freeze those cells to text and staticize formula cells before editing; never call db.EvaluateFields. Related: [[cad-console-net-workflow]], [[obsidian-log-work]].

2026-10-27: new stamp «ТОО ПКФ Таза Су» (from `Downloads\МАлматинка штамп.dwg`, block A$C2bb4aa4d, 185×55 mm, top-right base) put into all sheets → `КЖ Чертеж Бадам 27-10-2026.dwg` (now the latest). Done by redefining the shared block «крпкер» (one block for all 31 stamps, 1:100 units, frame top-right at (-982117.93,-806053.23)) = new stamp exploded ×100; nested def kept as «Штамп Таза Су». People now Чертил Есимов М. / Проверил Есперов М. / Н.контроль Мукамбек Ж. (no ГИП row); шифр kept 537-23.08.2024-ГР.КЖ. Expert's album PDF = `Downloads\Альбом_1.1._ГР-КЖ_Бадам_27.10.2026.pdf` (32 pages, old «-КЖ» stamps). Plot check: `-PLOT _N <layout> <enter><enter> "file.pdf" _N _Y` (no "write to file" prompt for DWG To PDF).
Later 27.10: sheet 3.1 had no layout (31 stamps, 30 layouts) — created layout «3.1» by CloneLayout("4") + model viewport ViewCenter.X −252000 (3.1 frame is 252000 left of sheet 3, both 1:400 A4x3). Layout names are shifted vs sheet numbers: layout 4→л.3, 5→л.4 … 29→л.28, 30→л.29. Album PDF `КЖ Чертеж Бадам 27-10-2026.pdf` (31 pages, no covers) plotted from layouts with their own page setups — that works here. Console QSAVE grows the file each time; finish with ISAVEPERCENT 0 + QSAVE.
27.10: sheet 29 name typo fixed «План траба под плотины» → «План трапа под плотиной» (MTEXT 13E01E heading, 13E189 stamp, Ведомость table 1285AD row 31) — DWG+PDF re-saved.
27.10 (remark 1.4 follow-up, user: «осындай жерлерге қойып шық барлық типте»): prep C8/10 100 mm drawn on every Стенка elevation (band under the slab polygon's bottom chain: vertical −100 for slopes <0.5, normal offset on tooth sides; follows the зуб of types 9/10), on every Подошва plan (100 strips outside the 8800 edges + 100 dims cloned from the 8800 dim, text ±500) and on the long Разрез 1-1 (л.4 начало/продолжение, л.5 конец). Style = closed pline layer 0 lw30 + assoc AR-CONC hatch on «Бетон штриховка» (0.5 at 1:100, 2.0 on 1:200 sheets); end «100» dims cloned from the 300 dims (types 2-4 elevations have none, so none added). Type 6 left: the 2500 drop dim 123368 moved down to the prep bottom. Applied LIVE in the user's open AutoCAD (doc unsaved — user saves) via PREPOPS with handle/extents pre-checks (aborts if geometry differs / already applied); scripts scratchpad 0bad4b28 `badam\gen.py, prep.cs`. PDF album rebuilt from an identical copy.
