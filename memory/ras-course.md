---
name: ras-course
description: "RAS GROUP Revit КЖ course (14 lessons, BI template v3.52) studied 20.10.2026 — notes in _Стандарт_КЖ\\RAS_курс; how the user's school does КЖ in Revit"
metadata:
  node_type: memory
  type: reference
  originSessionId: 1627bee1-9218-4ed4-bb58-ee22da3b578f
  modified: 2026-10-20T06:59:08.176Z
---

Source: `D:\РАБОЧКА\RAS GROUP PROJECT` (lesson videos Урок 1–15 without 11, BI_Шаблон_КЖ_v3.52*.rvt, KeyboardShortcuts.xml). Notes: `D:\Бекасыл КЖ КМ\_Стандарт_КЖ\RAS_курс\КУРС_ҚОРЫТЫНДЫ.md` (summary + proposals awaiting approval) and `урок_NN.md`; template sample sheets with mm layout in `_Стандарт_КЖ\шаблон_каталог\v3.52_парақтар\ПАРАҚ_ҮЛГІЛЕРІ.md`. Read these before starting a new КЖ project or a new kind of element (stairs, slabs, walls, pits, frames).

Key points: bent bars with template «(форма)…» shapes (RAS_префикс Х/Ш/Ск/Ф/Г); BI_марка_конструкции set before placing rebar; views carry BI_марка_конструкции/BI_назначение_вида/BI_группирование; templates #01→#02 Опалубка→#03 Армирование; products Кр/С as model groups + «…_изделия_СА»; ModPlus «Смещение размеров».

How frames were taken (no ffmpeg/audio): WinRT MediaComposition.GetThumbnailAsync in PowerShell (scratchpad video\frames.ps1 — ICollection.Add for Clips; save .ps1 with BOM). Opening another .rvt in the background then ExportImage makes it the ACTIVE doc — switch back via Вид → Смена окон, then Close(false) on Idling.

Related: [[template-catalog]], [[revit-kzh-oformlenie]]

Applied 20.10.2026 (user: «видео уроктай», «ешқандай сурет», «фундаменттен бастап», «схемаға тиіспе»): walls 5.1/5.2 and foundation 3.1–3.9 rebuilt course-style — no DWG copies; template view types/templates/filters; course titles via viewport type «загаловок_на_листе»; notes in BI_примечание_расширенное; schedules = template chains; outlets = BI_марка_конструкции «Выпуски» + Комментарии «Выпуск» + «выпуски_d=» types, Вп-1/Вп-2 products. API lessons in ЕРЕЖЕЛЕР 3в-14/15 (section box flip, set constraints, Coarse for dims, tag the set's first bar 2000000, label offset measured).
