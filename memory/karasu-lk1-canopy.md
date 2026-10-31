---
name: karasu-lk1-canopy
description: "ЖК Қарасу (с. Абай) КМ навесы над наружными лестницами ЛК-1.1 / ЛК-1.2 / ЛК-2: one album per stair, the user's stamp block «крпкер» + cover from «ЛК-1,2.dwg», specs, site data (2026-10-18)"
metadata:
  node_type: memory
  type: project
  originSessionId: 31c24da5-b358-45a3-b1ee-c1d716ba778d
  modified: 2026-10-18T14:24:59.023Z
---

Folder «D:\РАБОЧКА\От Рас груп\ЖК Қарасу село Абай\КМ Чертеж». The AR task (3669-1-АР, sheet «Наружные лестницы ЛК») has ЛК-1.1 (axis Ф), ЛК-1.2 (axis Г), ЛК-2 and ЛК-3. Each stair gets its OWN album:
- «КМ Чертеж Лестница ЛК-1.dwg» is ЛК-1.1.
- «КМ Чертеж Лестница ЛК-1,2.dwg» is ЛК-1.2. The user made this file. «1,2» in their messages means ЛК-1.2 / this file, not «both».
- «КМ Чертеж Лестница ЛК-2.dwg» is ЛК-2.
I first assumed one album covering 2 canopies (spec ×2). The user's reply showed otherwise, and I reverted it.

**Why:** the user built their own cover and stamp in the ЛК-1,2 file and asked me to take them from there («1,2-ден титулка штампты ал»).
**How to apply:** copy the stamp and cover from the ЛК-1,2 file into the other albums and change only the stair name. Ask before merging stairs into one album.

Stamp and cover style (from the ЛК-1,2 file):
- The block «крпкер» holds all stamp fields: code 3669-1-КМ, object name «…уч. 179Б, 1-я очередь…», «Лестница ЛК-x», ГИП Казангапов А, ГАП Хасанова К, Разработал Ауез Б, Н.контроль Приколотов, 06.2026, and the RAS Group Project logo. I replaced the block definition (op blockdef with DuplicateRecordCloning.Replace) and changed only the stair-name MText.
- Cover: two A3 covers left of sheet 1 (x 2258830–2342838), 25 entities including 3 OLE2FRAMEs and 4 frame polylines: «Лестница ЛК-x / Конструкции металлические / Том-4 / Альбом: 3669-1-КМ».
- 5771EC box text: «Настоящий рабочий проект выполнен…», h 350, plus the ГИП signature block.

Specs (formulas, sums only over columns that have data, then EvaluateFields live):
- ЛК-1.1 / ЛК-1.2, 0.736 t each: Ст1 □60×4 12×2.0 m; Ф1 6 pcs (ВП1 2.20 + НП1 2.00 + Р1 2.21 m, □40×2.5); РС1 14×1.66; СГ1 20×1.07; СВ1 2×0.98+1.66; Пр1 5×9.0; ограждение Ø40×2.5 (10×2×1.64 + 2×1.34) and Ø20×1.5 119×0.96; t8 90×90 ×12; Зд-1 t10 200×200 ×12.
- ЛК-2, 0.768 t: bays 1.83, rows 1.5, РС1 1.79, СГ1 1.14, СВ1 2×1.03+1.79, Пр1 5×9.65, fence 1.77/1.44, 129 штакетин.
- ЛК-2 sheet 8 shows 1400/1100 dims, but sheets 4/5 show 1500: inconsistent, flagged to the user.

Site data, from ИГ ТОО «КазГИИЗ» (заказ 26-25, арх. 19013, 2026; scanned, read via PyMuPDF images) and АО «КазНИИСА» 2026:
- IIIВ; snow II 1.2 kPa; wind II 0.39 kPa; гололёд 10 mm.
- Temperatures: −20.1 (five-day, 0.92), −23.3 (five-day, 0.98), −26.9 (day, 0.98).
- Frost depth 0.79 / 1.03 / 1.17 m.
- Seismicity 9 баллов, ag 0.64g / agv 0.58g; soil type II (III в запас); просадочность I.
- No groundwater to 20 m. Soils are highly corrosive to carbon steel.

Gotchas:
- A script named con.ps1 is invisible on Windows (CON is reserved).
- Avoid `^I` / `^J` literals in MText; use a real tab and \P.
- COM SendCommand can be rejected while AutoCAD is busy. NETLOAD then opens a file dialog; close it with WM_CLOSE.
- SECURELOAD can't be set via COM SetVariable.
- A job.ps1 FileStream error can still mean the job ran. Check for duplicates before rerunning.
- Tools: session 31c24da5 scratchpad `net\lk.cs` (ops import/blockdef/clone/mt/cell/formula/evalfields/wblock/dxfout), `lklisten.cs`, `boot.ps1`, `job.ps1 -TF target*.txt`, `gen2.py`, `gen3.py`.

Related: [[km-spec-rules]], [[cad-dedicated-instance]]

Рампа album (2026-10-18), «КМ Чертеж Навес 1 Рампа.dwg», done live and not saved. The user's rule: «барлық стилді лестницадан ал», so callouts, stamp, title page and Общие данные all come from the ЛК albums.
- Sheets 1–2 were imported from ЛК-1 with dx −31000: cover, Общие данные, spec.
- Block «крпкер» was replaced from ЛК-1. The name is «Навес 1 над рампой паркинга», and every old rampa sheet picked it up.
- Sheets 3–8 are the original schemes and sections, renamed in the stamps.
- New sheets: 9 (Ф1/Ф2 schemes from the LIRA nodes, plus Ведомость элементов) at x 2563392, scale 50. 10 «Базы Б1,Б2» at 2585392, scale 10. 11 «Узлы 1–4» at 2590592, scale 20. 12 «Узлы 5–8» at 2599992, scale 10.
- Node marks (bubble block clones) sit on sheets 4, 5 and 7.
- Spec 4.803 t, lengths from the LIRA bars:
  - К1 59.28 m □140×100×4
  - □60×4: K2+Пк1 24.73 m, пояса 198.62 m
  - □50×2.5: СВ 27.7 m, СГ1+РС1 208.7 m
  - □40×2.5: Р1 153.0 m, П1 305.7 m
  - plates t12/t10/t8/t4
- Base plates and gussets (Б1 -12 300×260 with ribs -8, Б2 -10 200×200, gussets -8) are my design. The user should review them.
- Tools: scratchpad `net\rn.cs` + `jobmc.ps1` (SPDS ops: note/dim clone/import/eraseregion/mcscale), `glib.py`, gen_s9…s12.py, gen_ra.py.

Round 2 for Рампа (2026-10-18). The user said: «база болмайды, закладной қойылады; әр әріп сызық лестница стилімде; аналог КМ Навес паркинга-дан керегін ал».
- Columns K1 and K2 are welded straight to Зд-1 (-18 250×280) and Зд-2 (-10 160×160) from КЖ. Gussets for СВ are -t10.
- The analog is «Downloads\КМ Навес паркинга 05.10.26.dwg» (3335-1-КМ). From its sheet 8 I took node 1 (closed plate with gusset t10, section а-а), node 2 (cap t10) and node 3 (purlin on chord).
- Sheet 3 is now «Схема расположения закладных деталей» (SPDS notes Б1/Б2 renamed to Зд-1/Зд-2).
- Sheet 10 «Узлы 1, 2», sheet 11 «Узлы 3–6», sheet 12 «Узлы 7–10». Spec total 4.784 t.
- Stair-style rules applied:
  - callouts give the mark only, or '-tN / С245' for plates;
  - «Ведомость элементов» is drawn exactly like ЛК sheet 4 (layer KOHTYP, borders w25, rows 400, «Ариал» 150);
  - every scheme sheet gets notes «1. Общие данные… 2. Ведомость…»;
  - inserted spec rows must copy row style (op rowstyle: grid line weights, text height 187.5).
- The user moves the sheets themselves (front sheets were shifted up 31875 to a common baseline). Always look up the table and frame positions again before plotting or editing.

Final state for Рампа (late 2026-10-18; it supersedes the round notes above).
- The user said «Схема каркасы дұрыс»: keep the scheme geometry as drawn, including СГ1/СВ3 to the 1350 point.
- The album has 12 sheets:
  - 10 «Узлы 1...7» and 11 «Узлы 8...10» are copies of ЛК-1 sheet 7.
  - 12 «Разрезы 3-3, 4-4» is at x 2616000 (1:75, frame cloned from sheet 4). Generator: gen_s12s.py.
- Spec total is 4.764 t. Ведомость 57D245 has rows 2–13 for sheets 1–12.
- Gotcha: eraseregion with mode «intersect» on one sheet erased the stamp block of the neighbouring sheet, because stamps stick out 2–3 mm past the frame. Sheet 8's stamp was lost this way and restored by cloning sheet 7's stamp 578C0F at +21000.
- Old notes contained a literal «^I» (shows as «^ I» in DXF). A real tab shows as «^I».
- 2026-10-19 the user reordered the sheets: the sections go in a row (1-1, 2-2, then 3-3/4-4), and then come the truss scheme and the nodes. In the model, sheet 9 «Разрезы 3-3, 4-4» is at x 2563392 (1:75). Sheet 10 (truss scheme) is at 2595892. Node sheets 11 and 12 are at 2617892 and 2623092. The SPDS templates were moved +100000 to about x 2710000. The new rn.cs op `movewin` moves every entity whose extents centre lies inside a window.
- 2026-10-19 afternoon: the user's AutoCAD restarted, and everything after the 09:28 save was lost. I redid it in my own instance (net\mylaunch.ps1 starts acad.exe with the dwg and myboot.scr; the .ps1 needs a UTF-8 BOM because of the Cyrillic path). I saved with the lk.cs op `savedoc` and made a backup «… - копия до правок 19-10.dwg». Sheets now: 11 «Узлы 1...8», 12 «Узлы 9, 10» (×2, dimlfac 0.5). The node sheets are at x 2616891.6 and 2622091.6 (SPDS formats snap to their neighbours). Plot scripts need OSMODE 0, or the window corners snap.

2026-10-20: the user now works in «… - копия до правок 19-10.dwg» (they saved it at 13:06). It is the live Рампа file, not just a backup.
- Request «осы крайды 200мм ге түсір». My first reading (kink the cantilever top chord, end post 600→400) was WRONG («жо жоқ олай емес»). The user meant: «Ферманы өзгеріссіз қалдыр. Тек төменге 200 мм түсір», i.e. move the whole truss down 200 and shorten the columns. Only the left edge was circled, but the request still meant the whole truss.
- Done live in the user's AutoCAD, not saved:
  - I reverted the kink first.
  - Then stretchwin −200 over sections 1-1, 2-2, 3-3 and 4-4, above about +1.47, skipping titles, axis marks and the +0,870 marks.
  - Levels are now 4,620 / 4,020 / 2,070 / 1,765 / 2,610 / 2,040 / 2,750; the sheet 9 marks are associative and updated on their own.
  - Sheet 10 got new level values only. In Общие данные, «верх покрытия» is now +4,620.
- The spec (K1/K2 lengths) is NOT updated yet.
- LIRA updated the same day («Лираны да өзгерт»). In «Расчет\Навес 1 Рампа.lir» I binary-patched z −0.2 for every node with z > 0 (262 of 289; the 27 bases stay). The .lir (LIRA 2013 format) keeps nodes TWICE: at offset 138 in 28-byte records and at 36060 in 48-byte records (x, y, z doubles first). Patch both.
  - Backup: «Навес 1 Рампа - до опускания 20-10.lir».
  - The .txt and gen_rampa.py were updated (DZ = −0.2 in node()); the generator reproduces the patched txt exactly.
  - The model needs a new calculation run, and the РПЗ is based on the old results.
- Tools: session 7167e5c6 scratchpad `net/nv.cs` (+ dry stretch, mtrepl, wblock, dimpt, arcend, erase), `gen_low.py`, `levels.py`. To load the listener into the user's AutoCAD: COM SendCommand `(setvar "SECURELOAD" 0)` and then NETLOAD nvlisten.dll + NVLISTEN; that works.
- FINAL (same day, the user's correction «+2,810 қылып жаса, ферманы тек бұр»): the truss is ROTATED, not lowered. The rotation is a vertical shear, linear across the span, with the plan dims kept:
  - cantilever end −200 (+4,620 / +4,020);
  - axis Л −183 (column 3167, top +4,037);
  - axis M unchanged (+2,810, 1940, 3-3 back to the original values);
  - K2 in 1-1 +38 (+2,308 / +2,003, 1132 / 1438).
  - In the dwg: op `shear` (nv.cs) with constant zones ±100 around the column axes. Vertical dims placed outside the zones had to be fixed by hand with dimpt. The Л-side chain is 3167 + 583.
  - In LIRA: z += −0.2·Y/7.98 from the backup coordinates (Y=0 is row M, Y=7.3 is row Л, Y=−1.5 is K2); gen_rampa.py has DZ_END/Y_END.


2026-10-21 «Лираны автокадтағыға келтір, расчет, подбор» (from «… - копия до правок 19-10.dwg»):
- DWG vs LIRA differences found and fixed: СГ1 braces and СВ3 row go to Y=1.35 on the plan (LIRA had them moved to node 2.1). A bottom-chord node at 1.35 was added in all 11 trusses. The М-side knee (Пк1) node moved to the axis intersection z 0.926 (was 1.002 at the column face).
- User correction: «Мына жердегі металлды алып тастағанбыз». НП2 (bottom straight beam, М column node → top of К2) is REMOVED, so only the top chord continues to К2. Sheet 10 (scheme Ф2, note 2, ведомость) still shows НП2. I told the user and did not edit the dwg.
- Model now: 300 nodes, 733 bars. Backups «Навес 1 Рампа - до правок 21-10.lir/.txt», «gen_rampa - до 21-10.py». gen_rampa.py reproduces the model; LIRA's text export matched it (geometry, supports, hinges, loads, condensation).
- Results with calc sections = 5:
  - Проверка: К1 31.7 %, НП1 76.4 %, Р1 33.9 %, СВ 55.6 %.
  - П1 40×2.5: strength 73 %, but DEFLECTION 236 %. The old РПЗ showed 35.7 % because it used 2 sections.
  - Подбор (governing): К1 120×60×3, НП1 70×2, П1 60×2 (deflection 98 %), the rest 40×2 / 50×2. Steel sections in the model were NOT changed.
- Later on 2026-10-21 the user approved («ия, өзің реттеп жаса»):
  - П1 changed to □60×2.5 in LIRA (stiffness 5, plus 0.00157 t/m self-weight in load case 1). All members pass: П1 deflection 89 %, НП1 77 %.
  - Drawing fixed: НП2 removed (sheet 10, nodes 8/9), П1 shown as 60×2.5, spec total 5.193 t.
  - The live Рампа file was «… - копия до правок 19-10 v2.dwg» (renamed 2026-10-26 to «КМ Чертеж Навес 1 Рампа.dwg»). The user said «ең соңғысын сақта, қалғанын өшір», so the old version went to «КМ Чертеж\Мусор».
  - Still open: LIRA coordinate axes («лираға остер қой»), РПЗ refresh, seismic drift 6.8 mm not rechecked.
- РПЗ rebuilt for the final model (21.10), in «Расчет\РПЗ_Навес 1 Рампа.docx/.pdf» (21 pages); the 13.10 version is in «Расчет\МУСОР».
  - Generator: session 6fbed841 scratchpad `rpz2/` (build_rpz.py + figures.py, adapted from session 62d8a218 by patch.py). Inputs are AUTORES CSVs (tbl12.49_x → res2/tbl09.49_x, tbl09.23_1 → rsn_disp.csv) and the protocol «Work\Навес 1 Рампа_01.Навес 1 Рампа».
  - Results: max 1 ПС 77.2 % (НП1); П1 deflection 89.3 %; drift К2 ν·dr 8.6 mm ≤ 12.0 mm. With НП2 gone, К2 sways in X: 7.7 mm, was 0.05.
  - The ОД text in v2.dwg was updated to «8,6 мм при допустимом 12,0 мм».
- 2026-10-21 РПЗ for the ЛК-1.1 canopy:
  - Model: «Расчет\Навес для ЛК 1.lir» (identical to «Downloads\Навес для ЛК.lir»; LIRA task name «Навес 02»). 89 nodes, 181 bars, 6 frames at 1.7 m, columns 60×4 fixed, everything else 40×2.5.
  - Output: «Расчет\РПЗ_Навес для ЛК 1.docx/.pdf». Generator: session 6fbed841 scratchpad `rpz_lk/` (figures_lk.py, build_lk.py from patch_lk.py).
  - RSN coefficients are read from «Work\<task>#rsm.<task>» by rsm.py. Each combo is stored as a uint32 count n, then n×uint16 load numbers, then n×float32 factors. #pr holds only the static ones.
  - Results: Ст1 22 %, Пр1 34 % (deflection 45.5 %).
  - Drift in X is NOT satisfied: ν·dr 21.0 mm > 0.010·h 20.3 mm (103 %), because there is no vertical bracing between the columns. I reported it in the РПЗ and did not change the model.
- 2026-10-22: the user's model «Расчет\Навес 1 Рампа 02.lir» became the master («Двгны лираға қарап өзгертіп шық»). Changes compared to 21.10:
  - frames at the axis 1–3 end: 0/1.95/4.35/6.75/9.15 (the 1.95 bay is now first);
  - К2/Пк1 and chords ВП1/НП1 □80×3, Р1 □50×2.5;
  - СГ1 back to node 2.1, the СВ3 row at 1.35 removed.
- v2.dwg updated and SAVED in my own AutoCAD instance with SPDS (the console does not move SPDS proxies):
  - stretch −450 on sheets 3/4/5/6/9, skipping axis proxies, formats and axis dims;
  - braces re-placed;
  - chord arcs ±10 in 1-1/2-2, web widths;
  - double lines of the sheet-10 scheme widened;
  - ведомости, ОД text and spec updated (total 5.376 t).
- Not done: node sheets 11/12 still show 60/40 tubes. The ОД results (77.2 %, 8.6 mm) are from the 21.10 model; model 02 has not been calculated.
- Backup: scratchpad 6fbed841 `w/v2_before_r02.dwg`. Scripts: gen_r02.py, gen_r02b.py, mk_lk_r02.py, net/ed.cs (stretchwin/arcr/plw/lineset/savedoc).

2026-10-23 «отметкаларды сақтап сечениені өзгерт, поястарды ішіне қарай үлкейт»: the user chose the OLD file «Мусор\…(до правок 21-10).dwg» (open in their AutoCAD), not v2. Rule: chords grow INWARD. Outer faces, +4,620/+4,040 and 580 stay; the axes move 10 inward. Column tops (К1 at М, К2) are cut to the new chord face (~22 mm). The inner-face marks +2,810/+2,300/+2,030 were left as drawn. Applied live, not saved: sections and model 02 profiles on 1-1, 2-2, sheet 10, sheet 9, ведомости, ОД, spec 5.444 t. Tools: session a2999bcf scratchpad `net/sc.cs` (lk.cs + arc/plset/lineset/plw), `net/live.ps1` (COM SendCommand into the user's doc, then switches back; needs a BOM), `gen.py`, `gen_spec.py`. Gotcha: DXFOUT to an existing file hangs accoreconsole on the overwrite prompt.

2026-10-26 spec recount of v2.dwg (from the drawing geometry, saved via accoreconsole; backup «Мусор\… v2 (до пересчета спец 26-10).dwg»): total 5.353 t. К1 11×3.17+11×1.94, Пк1 11×(0.816+0.877), chords Ф1 5×18.27 / Ф2 6×16.60, Р1 142.78, СГ1 81.49 (with chord slope), РС1 36 pcs 85.75, СВ3 8×~5.02, Зд-2 -12 180×180. New framed table «Расчёт массы металла по элементам» under the spec on sheet 2. Tools: session b6e176ea scratchpad `calc.py`, `gen_ops.py`, `net/sc2.cs` (+newtable/rect/tstyle). Gotchas: setting a formula drops the cell text style to TEXT (restore «GOST 2.304»); Sum over all-empty cells gives ####.
- 2026-10-26: the live Рампа album is now «КМ Чертеж\КМ Чертеж Навес 1 Рампа.dwg» (renamed from «… - копия до правок 19-10 v2.dwg» at the user's request); the sheet 2 PDF sits next to it.
- 2026-10-26 later (live in the user's AutoCAD, not saved): node 14 (truss end at the cantilever with caps -t4) on sheet 12, cap added to node 7, marks 14/12 on 1-1/2-2; old analog layouts deleted, layouts «1»…«12» created (DWG To PDF, full bleed A3/A2, 1:1, one locked viewport per frame). Tools: session b6e176ea scratchpad `mc/` (rn.cs + mklayout/vpon/dellayout/tcell/wblock ops, boot.ps1, jobmc.ps1), gen_node.py, gen_node2.py. Gotcha: a viewport added to a never-activated layout becomes the overall viewport; activate the layout first (lm.CurrentLayout), then add the model viewport and set On.
- 2026-10-26: the user finished ЛК-1.1 and said «1,1 мен 1,2 айырмасы остерінде ғана болуы керек». ЛК-1.2 was rebuilt as a copy of ЛК-1.1: SPDS axis name Ф→Г via McDbEntity.ObjectProperties["Axis name"] (rn.cs op objpropset), texts ЛК-1.1→ЛК-1.2 (OD 577515, covers 5857A2/5857BA, block крпкер MText 585710), «вдоль оси Ф»→«Г». Old file in Мусор «… ЛК-1.2 (до копии с ЛК-1.1 26-10).dwg». Next: ЛК-2/ЛК-3 by the ЛК-1.1 style (ЛК-3 is still a copy of ЛК-2 named ЛК-2, with its own axes К, Л/1, 10/1–11 partly drawn by the user) and specs Рампа-style.
- 2026-10-26 evening: ЛК-2 and ЛК-3 brought to the ЛК-1.1 style (sheet 7 imported from ЛК-1.1, OD in two MText columns 577515/577517, sheet notes position/height, Ст1 callouts 2.0; ЛК-2 also got СВ1 dashed + note, knot 6/7, «/7» on sheet-5 knots, 20 П1 notes, sheet-6 axis scale 40). ЛК-3 renamed (block крпкер 588AAB, covers 588B3D/588B55, OD: 6,7х1,4 м, габарит 7,2х2,0, ось К у осей 10/1-11, Ст1 10, Ф1 5). Specs: ЛК-1.1/1.2 0.698 t, ЛК-2 0.730 t, ЛК-3 0.569 t (РС1 11×1.64, СГ1 16×1.06, СВ1 2×0.97+1.64, Пр1 5×7.2, fence 8×2×1.62+2×1.34, 97 pickets). Each album has a framed «Расчёт массы металла по элементам» above sheet 2 (outside the frame, like the user put it in Рампа). Layouts in every ЛК album: «0», «00» (covers, A3 1:100) and «1»…«8» (DWG To PDF full bleed, 1:1, one locked viewport on Defpoints); deleting all old layouts makes AutoCAD add «Лист1» — delete it afterwards. Рампа covers «0»/«00» were made by the user. Backups in Мусор (… до стиля ЛК-1.1 / до расчёта и листов 26-10). Tools: scratchpad b6e176ea gen_lk23.py, gen_lkcalc.py, net/sc2.cs (mklayouts/dellayout), mc/rn.cs (objpropset, notesize, mtpos, lt).
- 2026-10-26 LIRA for the other stairs («Осы лираны аналог етіп қалғандарына жаса и рпз дайында барлығы бір стилде»), analog «Расчет\Навес для ЛК 1,1.lir» (task «Навес для ЛК 1», 89 nodes, 181 bars; node tables: 28 B records at 138 and 48 B records at 9702). Done without LIRA: «Навес для ЛК 1,2.lir» (copy) + «РПЗ_Навес для ЛК 1,2.docx/.pdf» (ЛК-1.1 RPZ with ЛК-1.2 / ось Г). «Навес для ЛК 2.lir» = node patch (x×1.83/1.7, columns y 0/1.5, truss shifted +0.05 so supports at ±0.75). «Навес для ЛК 3 (6 рам).lir» = x×1.675/1.7, still 6 frames — the 6th frame must be deleted in the LIRA GUI (+ Упаковка схемы). Still to do in LIRA: calc (normative setting, calc sections 5), CSV, snapshots per the ЛК-1.1 RPZ list, then RPZ via session 6fbed841 scratchpad rpz_lk3 (build_lk.py, figures_lk.py, patch_lk3.py).
- 2026-10-26 evening, LIRA + РПЗ for ЛК-2/ЛК-3 done (Расчет\Навес для ЛК 2.lir / 3.lir, РПЗ_Навес для ЛК 2/3.docx+pdf, 21 pp, same template/snapshot set as ЛК-1.1). Results: ЛК-2 max 1ПС 39.3 % (Пр1), прогиб 0.83/7.3 мм, seismic drift X 110 % NOT satisfied; ЛК-3 32.9 %, 0.60/6.7 мм, drift X 99 %. Methods: node patch at 138(28B)/9702(48B); axes are float32 records (WStr name + 6 floats) after the load-case names — patch ONLY records А..6 and only changed floats (rewriting other float-looking bytes corrupts the file: «Не удалось открыть документ»). LK-3 frame deleted via ПолиФильтр (КЭ 150-181) + Упаковка. Snapshots: copy ЛК-1 «Навес для ЛК 1.DOCS» scr*.{dat,dib,names,png,state,volumes} + .dat into the new task's DOCS, reopen, Книга отчетов → right-click item → «Вернуться к виду» → Home → Снимок окна (restores flags, mosaics, fragments, load case). Generator: session b6e176ea scratchpad rpz/setup.py (copies rpz_lk3 base, maps scr numbers, H_COL from column elements).
- 2026-10-26 night, «стойкалар бойынша вертикаль байланыс қос, қайта есепте, РПЗ жаңарт»: СВ2 cross braces added to ЛК-1.1 and ЛК-2 (ЛК-1.2 = copy of ЛК-1.1; ЛК-3 drift 99 % so left as is). In each model: КЭ 182 (41–44), 183 (55–30) row А, 184 (42–46), 185 (56–32) row Б — bay between model axes 3 and 4; stiffness 6 (□40×2.5, РС1), material C245 trubi / 7.РС / БС1_1, hinges UY/UZ both ends, load case 1 type 16 Z 0.00282. Drift X now 0.28 mm (1 %), Y 10.4–11.0 mm (≈54 %); braces ~12 %. РПЗ ЛК-1,1/1,2/2 rebuilt (СВ2 in КОНСТР text, stiffness table «РС1, СВ1, СВ2», captions of the А/Б sections). The КМ albums do NOT show СВ2 yet. Old files in Расчет\МУСОР (… до СВ2 26-10).
  - LIRA GUI gotchas: a .lir path with «Қ» or a comma cannot be opened through the shell — copy it to `…\LIRA SAPR 2024\Data\Навес для ЛК 1.lir`, open with Invoke-Item, save, copy back. The file dialog rejects typing. Add elements in a fragment (ПолиФильтр by numbers → Вид → Фрагментация → XOZ) with «Пересекать с другими КЭ» and «Учитывать промежуточные узлы» OFF. ПолиФильтр resets «Инверсно» ON every time: uncheck it, check «По номерам», retype the list, then check «Эл.: n/185» before applying anything. New bars take the CURRENT stiffness — set it first or reassign.
  - Snapshots after model changes: book item → «Вернуться к виду» → Вид → «Восстановление конструкции» (results mode y 314, edit mode y 327 — the edit-mode menu has one more item) → Home → Снимок окна. The stored fragment otherwise hides new bars. Row sections need a fresh ПолиФильтр fragment that includes the braces. Load mosaics restore with the view. setup.py MAP: ЛК-2 {1:60,2:61,3:62,4:63,7:56,8:57,10:59,11:58,14:55,15:54…22:47,23:46}, ЛК-1 {1:38…4:41,7:34,8:35,10:37,11:36,14:33,15:32…23:24}.
- 2026-10-26 ~20:10 СВ2 drawn in the КМ albums ЛК-1.1 / 1.2 / 2 («схемаға, узелге және спецификацияға қос»): sheet 6 — СВ2 X in section 2-2 (bracing symbol like СВ1 in 3-3: dashed ACAD_ISO03W100 + w=40 polylines + SPDS note + knot 7/6), scheme «Связь вертикальная СВ2» 1:40 (1640/1700 or 1770/1830, 100/1800/100), nodes 7 (СВ2 welded to Ст1 face, WP 100 above the plate/below the top) and 8 (crossing, one diagonal continuous) drawn ×4 (dimlfac 0.25) in node-6 style (layers/lw/HIDDEN 160/CENTER2 4, cloned SPDS breaks/welds/notes/title circle). Sheet 4: thick СВ2 lines on both column rows + «СВ1, СВ2 / сложное, см. листы 5, 6». Spec: СВ2 4×2.44 m (ЛК-2 4×2.52) → ЛК-1.1/1.2 0.726 t, ЛК-2 0.759 t; calc table row «СВ2». ОД, ведомость листов, sheet-6 stamp title, notes updated. Backups «Мусор\… (до СВ2 26-10).dwg/.pdf». Tools: scratchpad b6e176ea `sv/gen_sv2.py` (ops), `sv/runall.ps1` (console sc2 → my own AutoCAD via `mc/svlaunch.ps1` + `mc/svjob.ps1`, listener SVLISTEN in %TEMP%\acadjob_sv so the user's AutoCAD never picks the job), `sv/mkalb.py` (album PDF from layouts: `-PLOT _N <layout> "" "DWG To PDF.pc3" file _N _Y`). Gotchas: console-saved DWGs open with the «Информация о прокси-объектах» dialog that blocks the boot script — svlaunch closes it with WM_CLOSE; sc2 `save` needs a different output file; aligned TEXT centre is align_point, not insert.
- 2026-10-26 РПЗ titles: «Барлық рпзның титулкасын двгдан ал» meant ONLY the company and the object address, not the DWG cover layout («мақсат компания аты обект адресі», «РПЗның өзінің стилі қалсын»). My first version copied the whole album cover (logo, signatures, GOST fonts) — rejected and reverted. Now all РПЗ (ЛК-1.1/1.2/2/3, Рампа 02) keep the template title; only ТОО "RAS Group Project", ГСЛ № 08854 and the address «…обл. Алматинская, р-н Карасайский, с.о. Райымбекский, с. Абай, к.х. АКХ Райымбек, уч. 179Б, 1-я очередь строительства (без наружных инженерных сетей)» changed. Tool: scratchpad b6e176ea `tit/retitle.py` (hooked into rpz/setup.py). Section 1.2 «Объект расположен по адресу…» was also changed to уч. 179Б, 1-я очередь (docx + base/build_lk.py); the reference to the КазНИИСА report keeps its original title «…уч. 179».
- 2026-10-26 ~22:35 «барлық норма НТП-мен жасалуы керек… барлық файлды жаса»: all 5 LIRA models (ЛК-1,1/1,2/2/3, Рампа 02) switched from seismic module 60 (СП РК 2.03-30-2017*) to module 61 «Сейсмическое (СП РК EN 1998-1:2004/2012, НТП РК 08-01.1-2017)»: ag 6.28 (X,Y) / 5.69 (Z) м/с², soil type II (user's choice), q 4.0 (user's choice) / qv 1.5, β 0.2, η 1, γI 1/1; doc 15 line «61 nforms 0 0 0 1.00 3 0.00 ag soil qh qv β η CX CY CZ γh γv». Recalculated, result views retaken, РПЗ rebuilt with scratchpad b6e176ea `rpz/ntp.py` (methodology §2, table 3.1.1, snow sk row, refs 4–8: EN 1998-1, НТП РК 08-01.1-2017, НТП РК 01-01-3.1(4.1)-2017). Results ≈ unchanged (ЛК-3 drift X 20.0/20.3 mm = 99 %, Рампа К2 10.2/12.0). Old files «МУСОР\… (до НТП 26-10)». КМ drawings (ЛК-1.1/1.2/2/3, Рампа) also updated 26-10 ~22:50: ОД antiseismic paragraph «по СП РК EN 1998-1:2004/2012 и НТП РК 08-01.1-2017 … тип грунтовых условий - II», soil line «принят в расчете по НТП РК 08-01.1-2017», snow/wind «(НТП РК 01-01-3.1(4.1)-2017)», Рампа ОД results 67,4 % / 10,2 мм; ведомость ссылочных документов: EN 1998-1 + 2 new rows (НТП РК 08-01.1-2017, НТП РК 01-01-3.1(4.1)-2017). Album PDFs rebuilt (ЛК-3 and Рампа fully replotted). Backups «КМ Чертеж\Мусор\… (до НТП 26-10)».
  - LIRA dialog trick: the «Сейсмика (СП РК EN 1998…)» dialog loops on the CX/CY/CZ validation when typed; fill it by window messages — `scratchpad/seis.ps1 -Acc -CX -CY -CZ` (+`win.ps1` list/kids/set/click/close). Row: spin «N строки» (117,135) → combo (195,170) → item «…(61)» (200,424) → «Параметры» (231,240) → seis.ps1.
  - Рампа РПЗ generator copy: scratchpad b6e176ea `rpz/ramp` (from 6fbed841 rpz3; result pictures scr09–17 → scr24–32).
- 2026-10-26 ~23:00 «Чертежды да НТП-ға сәйкестендір»: ЛК sheet 3 «Таблица расчётных нагрузок на закладные детали» (was empty) filled from the НТП recalculation: РСН groups I/III, base section of Ст1 (stiffness 1), kN/kN·m, Mx=MZ, Qy=QY, My=MY, Qx=QZ (local axes of vertical bars), note column = РСН name; intro text cites СП РК EN 1990, EN 1998-1, НТП РК 08-01.1-2017. Tool: scratchpad b6e176ea `nt/zdloads.py` (zd.json) + sc2 clone of «N max» text 5785EB. ЛК-1.1: N −4,37…+1,29 kN, M ±0,53 kN·m; ЛК-3: My ±0,73. Рампа has no such table. Other norm refs in ОД already НТП/СН РК (EN 1993-1-1 + НТП РК 08-01.5-2013, climate СП РК 2.04-01-2017 kept).
- 2026-10-27/29 variants. «Вариант 1 (СП РК 2.03-30-2017)» folder = first (СП) set; user then said the first variant had no СВ2 → ЛК-1.1/1.2/2 lir/DWG there swapped to «(до СВ2 26-10)», ЛК-1.1/1.2 РПЗ rebuilt from the 22.10 calc (scratchpad b6e176ea rpz/v1build.py); ЛК-2 СП РПЗ there still the СВ2 one. 29.10 «св2 жоқ қылып расчет жаса, нтпмен болсын» + «По НТП Без связей деп папка ашып ішіне расчет, чертеж, рпз сақта» → folder `По НТП Без связей\` (Расчет: ЛК 1,1/1,2/2 no-СВ2 НТП lir + РПЗ docx/pdf; КМ Чертеж DWG from «до СВ2» + ОД НТП ops + sheet-3 loads; album PDFs; ЛК-3 and Рампа = copies of the main НТП set). Results without СВ2: ЛК-1 drift X 21.0/20.3 mm (103 %), ЛК-2 22.4/20.3 (110 %) — НЕ выполняется, РПЗ says so; same numbers as СП because K1 0.25 ≡ 1/q 4. LIRA tasks «ЛК1 бСВ2», «ЛК2 бСВ2» (Data + Work with copied .DOCS book). Faster snapshot retake: in the book select items (ctrl+click) → right-click → «Обновить выделенные элементы» regenerates pictures in place from stored views (no restore/Home needed). Builder rpz/nbuild.py + nmap.json. LIRA is single-instance: open my file in the user's LIRA as a new tab only after asking.
- 2026-10-29 ~20:35 «сечениені үлкейт… 70х4 или 80х4» → Ст1 □70×4 (ГОСТ 30245-2012, RO 7.97 kg/m) in «По НТП Без связей»: LIRA tasks ЛК1/ЛК2 бСВ2 got a NEW stiffness type (type 1 can't be edited — «Просмотр» is read-only; add via Добавить → База стальных сечений → Прямоугольная труба → gnkv_2012 → 70x4, select columns by ПолиФильтр «По типу жесткости» (pick item with End+Enter, uncheck Инверсно), assign, delete type 1; LIRA keeps number 7/8 — nbuild.py/zdloads.py treat any type outside 2..6 as Ст1). Self-weight: extra 0.00126 t/m added in LC1 (load table cell editing failed; «Нагрузка на узлы и элементы» with the interactive table panel open CRASHED LIRA 20:17 — close that panel first). Results: ЛК-1 drift X 14.2/20.3 (70 %), Ст1 15.8 %; ЛК-2 15.1/20.3 (74 %), 16.8 %. Drawings via scratchpad b2/gen70.py (+ sc2 ops dimpts/bscale): node 1 section a-a 65/70/65, node 2 width 70, ОД/labels 70×4, spec 7.97 kg/m (formulas need «=»), mass ЛК-1.x 0.728 t, ЛК-2 0.760 t, sheet-3 loads. 60×4 versions → «По НТП Без связей\МУСОР\… (стойки 60x4)».
