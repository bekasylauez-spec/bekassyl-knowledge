---
name: project-zavod-b109-km
description: "Завод УВПиОС В109 (Шерхан) КМ: 03.11 Tekla бір DWG + ТХ крандар (BEKA-1), 04.11 Цех Алатау альбомы рамкасында жаңадан сызу (BEKA-2) — ережелер, pipeline, күйі"
metadata:
  node_type: memory
  type: project
  originSessionId: 1ef51441-e103-4b74-9733-3540011db41e
  modified: 2026-11-04T14:53:20.959Z
---

**Ерте кезең (03–04.11.2026, BEKA-1: КМ бір DWG-ға, ТХ, крандар, замечания).**

2026-11-03: «От Шерхан\Завод\Том 14 Водоподготовка ВП-В109\КМ Чертеж\227-23-П-УВПиОС-ВП-В109 КМ (все листы).dwg» — 11 Tekla парағы + титул бір файлда (модель Y −100000·N, лист 01…11). Жоқтар ғана қосылды: 1-парақ жалпы мәтіндері (модельде видовой экрансыз еді), 4/7-парақта видовой экран кескен мәтіндер, логотип (Company_logo.png сол папкада).

03.11 кешке: КМ ТХ бойынша түзетілді (ортаңғы H–E аралыққа ПБ+КН, 8/4/2-парақтар) және бәрі моделге шығарылды: «КМ Чертеж/227-23-П-УВПиОС-ВП-В109 КМ (все листы, модель).dwg». Сосын «ТХ бойынша өзгерт»: рельс осьтен 500, ПБ үсті +11.893 (рельс басы +12.000), спец. подкрановые 78,5 т. АШЫҚ: 24 м аралықта ферма асты +12.37, кран үсті +12.85 → соқтығыс; ТХ таза биіктік ≥+14.00 орындалмайды (ЛИРА-мен көтеру керек). Крандар ТХ-дан 3-3 қимасына көшірілді → «… (все листы, модель) v2.dwg» (негізгісі пайдаланушыда ашық еді). Пайдаланушы шешімі: ТХ-ға хабарлау — сұрау хаты «КМ Чертеж\В109 - запрос в ТХ по мостовым кранам.txt» (RU+CN), ТХ жауабын күтеміз.

Бастапқы айырма: ТХ (папка ТХ, 30.10–03.11) үш кран 2 т (L120001 двухбалочный, L140002/L140003 однобалочные), пролёт 23000/11000/23000 (рельс осьтен 500), рельс Р24, давление колеса 23,9 кН, чистая высота ≥+14.00. КМ лист 8: ПБ тек 24 м аралықтарда, рельс 750, консоль +11.000.

2026-11-03: замечания экспертизы по В109 собраны в «В109 — замечания и что делать.xlsx» (папка тома 14): 141 строка, наши КЖ/КМ — 24; сводный лист исходника «Замечания», остальные листы — дубли.

**Why:** пайдаланушы «жаңадан сызба, копировать ет, тек жоқ сызықты сыз» деді және сұрақтарды соңында жинап беруді сұрады.
**How to apply:** бұл жобаны жалғастырғанда Obsidian «15_Проекты/Завод УВПиОС В109 (Шерхан)» және [[cad-console-net-workflow]] әдісін қара; Tekla DWG біріктіруде жалпы видовой экранды да клондау керек (әйтпесе экрандар бос).

04.11: пайдаланушы — кран жолының отметкасы +11,000 (ПБ үсті), мен +11,893 қойғанмын (ТХ +12.00-ді рельс басы деп түсіндім) → қайтарылды. Ереже: КМ-дегі бар отметкаларды ТХ-ға өз түсінігіммен өзгертпе, алдымен сұра. Двутавр белгісі «I» әрпі емес, сызылған таңба (IBEAM op).

**Кейінгі кезең (04.11.2026, BEKA-2: Цех альбомы негізінде қайта сызу).**


**Request.** Source DWG: `D:\РАБОЧКА\От Шерхан\Завод\Том 14 Водоподготовка ВП-В109\КМ Чертеж\227-23-П-УВПиОС-ВП-В109 КМ (все листы, модель) v2.dwg`. The user keeps editing it in their own AutoCAD (last save 04.11 14:19), so take a fresh copy before each run.

**What the user asked (04.11.2026).**
- «новыйдан сызамыз, жұмыс тәртібі цех»: the Цех Алатау КМ album is the frame ([[project-alatau-ceh-km]]). Each Завод drawing goes onto a Цех-style sheet, in the Цех order and numbering.
- Data that is missing is left blank («жоқ данныйларды тастап кет, кейін тауып беремін»).
- Earlier: «отметка/размер орнын өзгертпе»; use their SPDS and their frames.
- Stamp: «Штамп№1» block with Infratech data.
- Base for the frame: the SPDS version of the Цех file, `ЦЕХ Алатау\КМ Чертеж\Мусор\КМ Чертеж Блок 1.dwg` (30 sheets: 1.1–1.4, 2.1, 2.2, 3–8 schemes, 9–14 sections, 15–17 bases, 18–21 nodes, 22–25 фахверк).

**Pipeline** (`D:\Бекасыл КЖ КМ\Завод_В109_КМ\_авто`):
1. `album_all.ps1` runs `album_sheet.ps1` once per Tekla sheet:
   - pass 1: geo.lsp → Restyle.cs → apply.lsp;
   - pass 2: Spds.cs (W, H and k per sheet) → BKSHEET in a separate acad.exe, saved with SAVEAS.
2. `album_finish.ps1`: BKLAYOUTS (one layout per frame, DWG To PDF, ISO full bleed media) followed by `-EXPORT PDF All`.

**Fixes that matter.**
- The format is WblockCloned from al2 for every sheet (template −3, no built-in title block). A new McFormat draws an empty default Form 3.
- Never clone the «ГОСТ 2.303 5» linetype.
- In layouts, keep the first (overall) paper-space viewport and set LAYOUTCREATEVIEWPORT 0.
- Title pages get no stamp.

**State 04.11.2026 ~16:00.**
- `Завод_В109_КМ\227-23-П-УВПиОС-ВП-В109-КМ (Цех тәртібі).dwg` and `.pdf`: 13 sheets (Т1, Т2, 1.1 ОД, 1.4 спец, 3–6 schemes 1:220, 7 перекрытие, 8 разрезы, 9 ФФ1, 10 базы, 11 узлы).
- Every sheet carries the user's SPDS frame and stamp, SPDS axes/marks/nodes/sections and СПДС dims. The file opens without SPDS.

**2.1 / 2.2 (04.11.2026 evening), built by `sheets_21_22.ps1`.**
- **2.1** sits at model x 1 400 000:
  - axes and dims are copied from sheet 3;
  - blocks База_Б1 / База_Б2 are made from the node plans (Узел 1 plate 700×1500, centre 150 inside axis A; Узел 2 plate 700×1790, on the axis);
  - Б1 goes on rows A and M (M mirrored, assumption), Б2 on rows E and H;
  - К2, СФ, СФ1 and К3 bases have no data and are left out (note 4 on the sheet).
- **2.2** sits at model x 1 700 000: the Цех table imported, with values and Цех items dropped (A3 portrait).
- Run BKSHEET with TILEMODE 1. Otherwise SPDS objects land in the current layout's paper space.
- Album: 15 layouts (Т1, Т2, 1.1, 1.4, 2.1, 2.2, 3–11).

**ОД split (04.11 evening, `od_split.ps1`).**
- 1.1, 1.2 and 1.3 are A3 frames at x 1 800 000 / 1 850 000 / 1 900 000:
  - the ОД rows of the Tekla text columns flow into 2 + 1 columns, and headings never sit alone at a column bottom;
  - «Ведомость ссылочных» goes to 1.2 right; «Принятые технические решения» with ГИП goes to 1.1 bottom-left;
  - 1.3 is a new ГОСТ ведомость (15 | 140 | 30), its names identical to the stamps.
- The old A2 sheet was erased (ERASEWIN).
- Notes on the other sheets were renumbered (REPL op).
- Stamp signatures and revision rows were cloned from sheet 1.4 (CLONEWIN). The Изм.1 row therefore says кол.уч 3 (sheet 1.4's value); check it.
- Album: 17 layouts.

**NEW DIRECTION (user, 04.11 ~16:20): «Неге жаңадан сызбадың».**
- Take the Цех DWG itself (`Завод_В109_КМ\исходник\Цех_Блок1_SPDS.dwg`).
- Erase everything inside every sheet; keep only the frames, stamps and sheet names/numbers.
- On each sheet, draw the Завод metal anew to match that sheet's name. Tekla data only, no copying of Tekla lines.
- A sheet may be enlarged when the drawing does not fit.

The album above («Цех тәртібі», 17 sheets) is NOT what they want; it is only a data source.

Prepared so far:
- BkSheet.cs has the BKCEHCLEAN command (erases format contents except McFormat, Штамп* inserts and texts in the stamp box) and the ops PLINE, LINE with linetype, and DIM (makes «СПДС 1-<k>» from «СПДС»).
- BKCEHCLEAN on the Цех file has not run yet. Opening it in a separate acad.exe hung with no log, most likely a dialog on open. Check this first: screenshot the acad window itself, or run once by hand.

Measured section data (Tekla sheet 3, real size, all centred on the axis intersections):
- К / К2: I 597×300, tf 25, tw 18.
- К1: I 589×300, tf 21, tw 16.
- СФ: I 390×300 rotated (web along x), tf 16, tw 10.
- СФ1: □200×200×6.
- К3: box 374×362 of −350×12.

Where the columns stand:
- К: row A, all axes; row M, axes 1–12 and 17–28.
- К2: row M, axes 13–16.
- К1: rows E and H, all axes.
- СФ: axes 1 and 28, rows B, C, D, F, G, I, K, L.
- СФ1: x = axis 1 − 7000, rows M, L, K, I, H.
- К3: y = 108 999 (between L and K), axes 13–19.

Grid and braces:
- Axis y values: A 58999, B 64999, C 70999, D 76999, E 82999, F 85999, G 91999, H 94999, I 100999, K 106999, L 112999, M 118999. Axis 1 x = 251857 + 6000·(n−1).
- Vertical braces: row A, bays 2-3, 9-10, 19-20, 26-27 (ВС cross, ВС1 V on top; section 1-1). Other rows unknown.

The plan for Цех sheet 3 «Схема расположения колонн и вертикальных связей» was A0 at 1:200; 1:100 does not fit the 162 m length.

**Not done yet:**
- ОД not split into 1.1–1.3, and the ведомость still lists the old Tekla numbers.
- Scales not yet standard (1:220).
- Bases and sections not one per sheet.
- Element tables still Tekla's.

**«Цех негізінде» pipeline (04.11.2026 ~17:20, sheet 3 done, waiting for the user's review):**
- `_авто\ceh_build.ps1 -Work <dir>`: BKCEHCLEAN on Цех_Блок1 (33 formats; keeps format, Штамп* inserts, texts in the stamp box; everything else in model goes) → `sheet03.ps1` ops → BKSHEET → BKLAYOUTS (BK_LAYKEEP=1 keeps the other Цех layouts) → PDF from a copy → `pdfcrop.ps1`.
- Outputs: `Завод_В109_КМ\227-23-П-УВПиОС-ВП-В109-КМ (Цех негізінде).dwg`, `03 Схема расположения колонн и вертикальных связей (Цех негізінде).pdf`.
- Sheet 3 is A3x4 at 1:200, frame origin (1007465.4, −700000); the old A3x3 frame was erased with ERASEWIN. Every К/К1/К2 has Цех-style binding dims. СФ binding only on row B, К3 only on axis 13.
- Braces: rows A, E, H, M, bays 2-3, 9-10, 19-20, 26-27. Only row A is marked «ВС, ВС1»; E/H/M marks are unknown (note 5 on the sheet). Nodes 1 and 2 → Цех sheets 15/16 (Б1/Б2); nodes 3–5 have no sheet number.
- Blockers solved: (1) the Цех file opens with the «Информация о прокси-объектах» dialog — acadrun.ps1 (bkdlg.ps1) posts IDOK to #32770 dialogs of its own acad; (2) NETLOAD of a path with spaces must be quoted in the .scr.
- DWG To PDF has no A3x4 size. BKLAYOUTS picks the smallest bigger sheet (B0) and pdfcrop.ps1 rewrites the MediaBox (same byte length).
- PowerShell trap: `@($B/2, $D/2)` parses as division by an array (comma binds tighter). Compute halves first.
- Sheet 4 done (04.11 ~17:35), waiting for review:
  - origin (1250000, −700000), A3x4 1:200;
  - name changed to «…на отм. +5.020, +10.340» (Завод levels from section 1-1);
  - row A: «рс» struts on «ВЛ» (0.50) in all bays; brace bays dashed, labelled «ВС, ВС1» above and «рс» below;
  - rows E/H/M: brace lines only.
- Refactor:
  - `zavod_grid.ps1` holds the grid, sections, Axes/Columns/Chains/Title/Notes; sheetNN.ps1 dot-source it.
  - `ceh_build.ps1` has a $sheets list, one BKSHEET run, and outputs `(Цех негізінде).dwg` plus `(Цех негізінде, сызылған парақтар).pdf`.
- Linetypes: BKLAYOUTS sets PSLTSCALE 0, as in the Цех layouts. DASHED2, «ГОСТ 2.303 5» and BK_AXLTS all use ltscale = sheet scale (200). With PSLTSCALE 1 the braces print solid.
- User (04.11 ~17:40): «Общий данный листі қайда, база колонн қайда, аналогтың ретімен жаса, спецификация барлығын». Go in the Цех order from 1.1; do not jump.
- Done 04.11 ~18:10 (8 sheets): 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 3, 4.
  - 1.1/1.2 (sheet11_12.ps1): ОД from `od_b109.txt` (Tekla sheet 1 text) in two columns; ГИП box; ссылочные table.
  - 1.3 (sheet13.ps1): lists `album_b109.txt`. Add each new sheet there.
  - 1.4 (sheet14.ps1): Цех table form with `spec_b109.txt` (Tekla sheet 2; 45 rows, row sums checked).
  - 2.1 (sheet21.ps1): A3x4 at (1495000, −700000), layout «2»; Б1/Б2 plates from Tekla sheet 10; Б1 mirrored on row M (noted).
  - 2.2 (sheet22.ps1): Цех table forms; only snow 0.8, wind 0.77 and crane values from the ОД; the rest blank.
- Helpers: `bk_draw.ps1` (Ln/Tx/Table with merged $null cells and «^» upright cells; Paragraphs). TXT op takes a rotation as the 7th field. pdfcrop only crops pages bigger than the sheet.
- 04.11 ~18:20, user: «артық рамка, листтерді өшір полный», «артық ескі чертеждарды мусорға сал».
  - `sheet00_extra.ps1` (run last in ceh_build) erases the 4 non-album Цех frames.
  - BKLAYOUTS without BK_LAYKEEP keeps only the drawn sheets' layouts and deletes «Лист1».
  - Old outputs (Цех тәртібі, БК стиль, 03 pdfs, v2/v3, .bak) went to the Recycle Bin.
  - `Завод_В109_КМ` now holds only `(Цех негізінде).dwg` + `(Цех негізінде, сызылған парақтар).pdf` + `_авто` + `исходник`.
  - Frames of sheets 5–25 (Цех) still stand empty in the model, waiting to be drawn.
- 04.11 ~18:45, user: «листтердің ретін түзе, шеті тиіп тұрсын, горизонтальды созылсын».
  - `sheet99_arrange.ps1` + `album_frames.txt`: all 29 frames go into one row from (0, −1200000), edge to edge, bottoms aligned, Цех order.
  - New BKSHEET ops: MOVEWIN (moves objects by their centre) and ERASEOUT (everything outside the row).
  - Layout TabOrder set; generators still draw at their own origins and the arrange step moves them.
- Sheet 5 done (sheet05.ps1):
  - name «…на отм. +11.000»;
  - ПБ lines 500 off the axes (A +, M −, E/H ±), 200 short of the columns, on «ВЛ» 0.50;
  - КН (I40Ш1) at every column with marks;
  - 500 dims right of axis 28;
  - ПБ section sketch at 1:10.
- When the user has the album open in AutoCAD the DWG is locked: ask them to close it, then copy and reopen it with Start-Process (shell open).
- Sheet 6 done (sheet06.ps1), in the Цех A3x3 frame at 1:100:
  - Tekla «Схема перекрытия» +4.000 (axes 13-19) and +7.600 (axes 13-16), between M and the К3 line;
  - beams а/а1/Р/Р1/Р2/Т and a ведомость элементов;
  - stamp name replaced by REPL to «…на отм. +4.000, +7.600».
- Plugin changes:
  - SCALE op sets k for SPDS objects on sheets drawn in a kept Цех frame;
  - AXIS takes a ltscale as its 6th field;
  - pdfcrop now crops each page to its sheet from sheets.txt.
  - ceh_build stops if BkSpds.dll does not compile. A comment swallowed code once and the old dll ran silently.
- The album swap in the user's AutoCAD is done by `acad_swap.ps1` ([[close-user-file-myself]]).
- 04.11 ~19:10, user, verbatim:
  > «Листті кішірейттім. Ведомость элементтің масштабын ретте. Штамппен бірдей ұзындықта болуы керек. Сосын барлығын жалғастыр. Полный чертежды бітір сосын тексерем ок. узелдерді де реттеп жаса қосымша керек болса жаса. Аналогтан алып выноска бюарлығын спдстен алып жаса»
  - In the album the user made sheet 6 A2 594x420 and deleted the empty Цех frames 7–25.
  - Every ведомость элементов is 185 wide (stamp width), placed above the stamp.
- Album plan:
  - 7 нижние пояса (рф, св);
  - 8 верхние пояса (п, с, ФФ1, Б1, ББ + annex roof);
  - 9/10/11 Разрез 1-1/2-2/3-3;
  - 12 Ферма ФФ1;
  - 13 База Б1; 14 База Б2;
  - 15 Базы колонн, узлы 3, 4, 5 (К3, СФ, СФ1 bases exist on Tekla sheet 11, earlier «no data» was wrong);
  - 16 Узлы 6, 7, 8.
- Tools:
  - `tekla_members.ps1` finds plan members by their mark text (`tekla_data\m07/m08/m08b.txt`).
  - `Transfer.cs` (+ Restyle.cs + Spds.cs) moves one real-size Tekla view onto an album sheet:
    - СПДС dims;
    - SPDS MARK for every leader note: texts merged per baseline; lines above or under the shelf become the second line;
    - SPDS KNOT, SECT, AXIS.
  - `tekla_view.ps1` View() is the driver; detail generators are `sheetDNN.ps1` (do not name them sheet13/14: those are 1.3/1.4!).
  - Tekla dumps live in `_авто\tekla_data\a_geoNN.txt`. Tag map: 04 разрезы, 05 нижние, 06 верхние, 07 ФФ1, 08 подкрановые, 09 перекрытие, 10 базы, 11 узлы.
- PowerShell traps:
  - function names ignore case (TX overrode Tx);
  - `SP` is an alias (Set-ItemProperty).
- 04.11 ~19:55: FULL ALBUM built, 20 pages (1.1-1.4, 2.1, 2.2, 3-16), swapped into the user's AutoCAD; waiting for the user's check.
  - Transfer takes a line only when both ends are in the view window (keeps out the Tekla frame) and drops «Изм.» texts.
  - The user's unsaved edits at each swap are kept in `_авто\_user_edits` (2 copies so far, not merged).
  - Rules added to ЕРЕЖЕЛЕР.md «КМ альбом аналог ретімен».
  - Open items:
    - brace marks rows E/H/M;
    - К2 base;
    - load values;
    - фахверк (Цех 22-25): no Tekla data;
    - Tekla 1-1 bays drawn compressed, as in Tekla.

- 04.11 ~21:00, user: dims = real AutoCAD dims in СПДС style, no Tekla leftovers; отметки = full SPDS; all lines thin; truss + frame ведомости from the analog.
  - SPDS level mark = class a9b900a6… (mcsDbObjectLevelMark), no typed API. BkLevel.cs Level.Make: WblockClone of Цех mark handle 581562 (ceh.dwg), set props via PropertyDescriptor (Associative false, Text), Scale, TransformBy to the tip (tip = vertical of the exploded mark), grips 0 = base-line end, 1 = shelf end (OnMoveGripPoints). Op LEVEL tipX tipY baseX shelfY | text.
  - Transfer.Levels finds Tekla marks (value over shelf + vertical + triangle + base line). Restyle pass 1: compressed views → any length with ticks, overall dims re-joined over gaps without ticks, value as DIM text override (BkSheet DIM f[5]).
  - Truss analog: D:\РАБОЧКА\От Дастан\КМ Аналогтар\East Motors_КМ_10 01 24.dwg («Ведомость элементов СФ2», x≈844000 y≈-33000). ed_elem.ps1 draws that form; ФФ1 table on sheet 12, new sheet 17 «Ведомость элементов каркаса» (sections/steels partly inferred from spec masses: К 60Ш3 С255, К1 60Ш2 С345, К2 60Ш3 С345 — ask user).

Related: [[reference-spds-api]], [[obsidian-first]].

**05.11.2026 (BEKA-2): ЛИРА сверка + геология + ведомости по листам + узлы 9-12.** Толығы: Obsidian «15_Проекты/Завод УВПиОС В109 (Шерхан)/КМ В109 — сверка с ЛИРА, ведомости по листам, узлы 9-12 (05.11.2026)».
- `.lir` жесткость-элемент массиві: uint16 0-based @1517340 (В_109_v3_КМ); узлы @166 (28 Б), элементы @76434 (38 Б, флаг+8 узел+тип). Скрипттер session scratchpad `lir\`.
- Маркалар: Б1→БП1, ББ→БП2, Р/Р1→Бм1/Бм2, Р2→а1; К = I60Ш2 С345; п = [27П; рс □100x5 барлық 4 рядта; ВС □160x5, ВС1 □100x5; К2 базасы Б1.
- Лист 17 енді «Узлы 9-12» (sheetD17n.ps1); ведомость — ved_rows.ps1 + VedSheet әр схема парағында; spec_b109.txt ЛИРА ұзындығынан (806,3 т).
- Ашық: усилия (ЛИРА нәтижесі экспорты керек), ЛИРА-да ПБ 750→500, A/1 колонна +5.020-дан, ГОСТ 26020 vs СТО АСЧМ.
- Build: `ceh_build.ps1 -Work C:\Temp\bkw\w` (~4 мин). Рикаус DWG AutoCAD 2021 GUI-ды құлатады — accoreconsole DXFOUT.
- 05.11 кеш: 7-8 парақта марка элемент үстінде (zavod_grid.ps1 MarkOn, MARK op leader нүктесі = origin → выноскасыз; SPDS бұрышы дәл 90° болса мәтінді төмен аударады — 1.5698 рад). Альбом ортақ папкада да, жергілікті де ауыстырылды.
- 05.11: «I» әрпі қайта шығып кетті (пайдаланушы ескертті). Енді bk_draw.ps1: Table ұяшығы «I xx» → IBeamSign (сызылған) + өлшем; Tx/Notes ішінде → «двутавр». Тексеріс: PDF мәтінінде `I \d` = 0.
- 05.11: примечание әр парақта штамп үстінде (bk_draw NoteAt xR yBot; zavod_grid Notes NoteX/NoteBot, VedSheet NoteBot=yTop+10). 2.1 «I60Ш3» → «двутавр 60Ш3» (regex I ?\d).

**07.11.2026 (BEKA-1): жаңа бағыт — Цех Блок 1 көшірмесінде схемалар ЛИРА бойынша.** Нәтиже `КМ Чертеж-23-П-УВПиОС-ВП-В109-КМ (Цех Блок 1, ЛИРА).dwg` + `… листы 2, 3.pdf`; 2, 3 парақ A3x4 1:200 дайын, 4–8 пайдаланушы тексерісін күтуде. Скрипттер `D:\_claude_work\zavod_km` (gen23.py, net
z.cs ZKLISTEN). Obsidian: `15_Проекты/Завод…/КМ В109 — схемы 2, 3 по ЛИРА в Цех Блок 1 (07.11.2026).md`. Ереже [[km-binding-dims-1500]].

- 07.11 замечания листа 3: размеры без дробей (294.5→295); марки вертикальных связей «СВ1 / СВ2» (не ВС/ВС1) — пайдаланушы талабы.
