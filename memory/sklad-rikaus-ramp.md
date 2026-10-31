---
name: sklad-rikaus-ramp
description: "Склад Рикаус пандус (2026-10-14): where the ramp sheets are, the spec-sheet analog inside the project, and the console method used"
metadata:
  type: project
---

КЖ Склад Рикаус (D:\РАБОЧКА\От Маке\Склад Рикаус). Ramp sheets sit at the end of model space: sheet 39 plan (x≈3473000), 40 formwork (x≈3496000), copy of 40 → armirovanie sheet 41 (x 3516655–3537655, 1:50 A3), new spec sheet 42 at x 3537655–3554455 (1:40, cloned from sheet 26 «Спецификация фундамент Флм-1» at x 2170020).
User rule for this ramp: all bars Ø12 A500C ш.200, шпилька Ø8 (400х400 шахмат), фиксатор Ø12; strip footing + wall with шпильки, no хомуты.
In-project spec style = sheet 26: tables 4B03B1 (spec, formula cells), 4B03B2 (header), 4B042E (steel summary, cross-table formulas `Table(%<\_ObjId N>%).M15` work when N = OldIdPtr set from code), «Ведомость деталей» = dynamic block *U1491 (Видимость1 = 1/2/3 столбика), stamp = block «крпкер», frame = SPDS format (not clonable in console).
Generator: session 0b5010ae scratchpad w\gen.py + gen_tail.py → ops.json; plugin net
amp.cs (RAMPOPS, accoreconsole). Output file «КЖ Склад Рикаус - пандус армирование 14-10-2026.dwg».
The user keeps editing the original in parallel (and another job writes «крыльцо армирование»); diff the region before re-applying.

Decisions the user made during review (2026-10-14), reuse them for similar ramps / strip footings:
- Footing bars: use the user's dynamic blocks «Хомут_динамический2» (2 overlapping stirrups per section, Расстояние1 = bar span, Ø8) and «Шпилька_динамическая2» (Расстояние1 = 120, every 400). Mirror copies lose the dynamic link — resize the originals first, then mirror.
- Slab bars top and bottom with the same length are ONE position. The slab edge at the walls gets a П-скоба (Ск1 400/120/400), drawn green by the user.
- Side and end strip footings both 700 (250|200|250); bars at 50 + 200·j; dims «50 | 200х3=600 | 50».
- Final layout: sheet 41 = 1-1 (1:50), sheet 42 = 2-2 at 1:40 + spec + ведомость деталей + steel summary (sheet 26 style).
- The user moves sheets around while I work: re-probe positions (frames, tables, block refs) right before every edit, never trust old coordinates or Wblock-copy handles.
- A full Database.Wblock() of this drawing fails with eWasErased since the 2-2 A2 frame was erased; a partial Wblock(ids) of the ramp region works for plot checks.

Porches КР2–КР12 (2026-10-16): A3 1:50 sheets 46–51 in a row at y 1844961, x from 3613254.7 every 21000 (46 КР2, 47 КР3, 48 КР4, 49 КР5, 50 КР6;7;8, 51 КР9–12). All share one foundation: strip 400×200 ring 4350×1900, 6 pedestals 250×250 h400 (user changed 200→250), levels −1.200/−1.600/−1.800 (my assumption). Style follows Блок 7 Фм-1 ([[cad-clone-analog-stretch]]). Spec per porch 118.27 kg, no Зд-1. The user lays out their own sheet copies, so before editing, find which copy they are looking at.

Related: [[cad-console-net-workflow]], [[cad-dedicated-instance]], [[cad-callouts-spds]]

Рандбалки sheet 32 (2026-10-30): format 51F3B5 at x 2827380–2851140, y 1828161–1844961; sections drawn ×2 (dims lfac 0.5). Рб-1 is now a 600×600 beam only (the user removed the wall), top −0.400, aligned with Рб-2 at y 1843123. Spec 539DBF (Рб-1): the real length is 263.3 m (formulas write 526.6/2; Ø16 = 8 bars). The wall rows Шп2/Ск1/2/3 are gone, concrete = 0.36×263.3 = 94.79 m³, Рб-1 = 7106.65 kg. Рб-1 cells and the Рб-1 row of steel table 51F428 now hold plain numbers, and so does 51F428 [7,6]. «Ведомость деталей» = *U1491 51F3BD set to «1 столбик» (Х1, Х2, Шп1). Open question: Рб-3 concrete is 130.75×0.5 = 65.38 m³, but the 400×600 section suggests far less. Scripts: session 0ae38f71 scratchpad `netr.cs` (RRLISTEN, `%TEMP%cadjob_rr`; ops list/tform/tformula/tnum/tfmtcopy/dyn/viewset/viewrestore).
LESSON: after Table.DeleteRows, do NOT call db.EvaluateFields. It wiped constant formulas (526.6/2/0.2) and plain cells. Later GenerateLayout/DataFormat jobs kept dropping formulas in other cells, including an untouched Рб-2 cross-table cell. Write computed values with tnum (plain Double) and re-dump in a separate job to confirm they stick.
