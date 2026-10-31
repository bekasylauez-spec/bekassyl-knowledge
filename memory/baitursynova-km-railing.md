---
name: baitursynova-km-railing
description: "КМ БЦ Байтурсынова Блок 1: ограждение лестницы Л2 (sheets 11-12 after sheet 10), design choices and how it was built (2026-10-17)"
metadata:
  node_type: memory
  type: project
  originSessionId: 412db224-1ed1-4b1d-b780-71b9e3570735
  modified: 2026-10-17T12:25:46.607Z
---

2026-10-17, file «КМ Чертеж БЦ для клауда.dwg» (open in the user's AutoCAD, applied live, not saved). The user sketched the railing on their own copy of Разрез 1-1 (x≈2727000–2738500, y≈-1939500…-1906000) and asked: make the railing, attach it after the main KM, add a spec.

What I built:
- Sheet 11 (A3 portrait, origin 2617013.5,-1756151): a clone of their section, plus intermediate posts (step ≤1500), SPDS marks О1–О12, «Узел крепления стойки к косоуру М1:20» and an ACAD table «Ведомость элементов ограждения» with formulas.
- Sheet 12 (A3 landscape, origin 2646713.5,-1756151): typical fragments О2 and О10 at М1:25, «Техническая спецификация металла» (a clone of the stair spec 63F6C7, rows trimmed), and Примечания.
- Sheets 11 and 12 were also added to «Ведомость рабочих чертежей» (5A3DDE).
- Profiles: стойки, поручень and нижний пояс are Тр.50х3 (4.25 kg/m); балясины are Тр.20х2 (1.07 kg/m) at a 150 step; С245. Posts are 1350 long (150 welded to the [20П stringer web). Total 0.91 t.
- No layouts were made for 11/12. The existing layouts' viewports point to old coordinates.

Gotchas:
- In this file the SPDS level marks are auto marks with a foreign base, which is why they show −934,313 and similar. Fix: clone a correct mark (+7,300 for 6 chars, +25,200 for 7 chars) and use the byte-replace «level» op.
- McNotePosition stretch point 0 = shelf/text origin and point 1 = leader target. A cloned MText title 63FAFF is MiddleCenter.
- In the cloned spec table, a tcell th/formula write could blank a neighbouring formula cell. After edits, re-set the formulas in one op and verify them with a dumptable on the live drawing.

Tools: session 412db224 scratchpad `net\rl.cs` (RLLISTEN, `%TEMP%\acadjob_rl`, ops include noteat/newtable/pl/hatchnew), `g2.py`, `snap.sh`.

Related: [[km-spec-rules]], [[cad-dedicated-instance]], [[cad-clone-analog-stretch]]

Round 2 (same day): the user asked for the railing sheets AFTER THE STAIR SET (not after main sheet 10), railing on the plan per their red sketch, and «офорление келтір».
- Stair sheets renumbered to 11 (plan) through 15 (nodes); railing sheets are now 16 (x 2742000), 17 (2771700) and 18 (2813700), all at y -1947176.73.
- The plan (1:50 notation, x≈2707136–2714136) got railing polylines w=50: both landing outer ends, the whole bottom edge, and the inner edges of both flights along the 100 mm gap.
- New marks: О13 (end railing, 13 pcs) and О14–О21 (inner flight railings). Total is now 2.44 t.
- Sheet list (5A3DDE): rows made to match the stamps (1.1 начало, 1.2 конец, no 1.3), row height 600; recompute was needed.
- The cloned spec table kept destroying its formula fields, so I rebuilt it with newtable (style 63F6C7) plus border/rot cell ops. The new table is stable.
- Still open: the stair spec sheet «2» at x 2517590 (an extra copy). The user's original section and plan remain beside the sheets.

Round 3: the user said «use my drawing, draw it on all 5 sections» and chose «add it to the stair sections».
- 1-1 (sheet 12): the user's own railing, mirrored back from their copy plus intermediate posts, with marks О1–О12.
- 2-2: inner railing of the upper flights (О19–О21).
- 3-3: О13 face-on plus inner strips; 4-4: edge-on strips. Also fixed the broken level marks on sheet 13.
- New Разрез 5-5 on sheet 16, replacing my 1-1 clone: a mirrored 3-3 with О13.
- Mirroring (clonemir op): SPDS objects survive a mirror, but plain DIMENSION and MTEXT come out reversed. Rebuild them with newtext from the source using the mirrored points, and only translate (do not mirror) the level marks.

Round 4 (user: «Лестницаның өзіне тиіспе, көшіріп жанына жаса, лестницаның барлығын 0,05 мм-ге келтір»): the user's stair sheets must stay untouched. I restored 12–13 to their original state (my railing, marks and level-mark fixes removed; the original marks unerased). The railing versions now live in copies of those sheets, at sheets 17 and 18 (x 2771700 / 2801400). Fragments moved to sheet 19 (2831100) and the spec to sheet 20 (2873100).
In the railing sheets, stair geometry is set to lineweight 0.05 mm (op «lw»); the railing keeps its own weight.
- Lesson: when moving neighbouring sheets one after another by region, the second region can catch entities the first move already shifted into it. Move the right-hand sheet first, or select by handles.

Round 5 («3 пен 4-ші разрезді дұрыстап қара»): the railing sections must follow the cuts on the user's railing plan (sheet 16), not the stair plan's numbering.
- 1-1 is a cut along the gap looking north: upper flights with the inner railing О19–О21.
- 2-2 is a cut through the lower flight looking north: lower flights with the inner railing О14–О18 (new).
- 3-3 is a cut outside the bottom edge looking north: the user's outer railing О1–О12.
- 4-4 is a cut at the right end looking west: О13 face-on at the right landings. 5-5 (left end, looking east) is on sheet 16.
- Sheet 17 now holds 1-1 and 2-2; sheet 18 holds 3-3 and 4-4.
- In stair 4-4 the +2.600 landing is drawn at about +3.100; the railing follows the drawn landing.

Round 6: the user asked to remove the intermediate posts (only end posts remain) and to delete all callouts, keeping only those on the fragments sheet 19. Spec and ведомость were recounted: 66 posts, 2.22 t.
- The user rearranged sheets 16–18 themselves WHILE I was working: 1-1 went to sheet 16 next to the plan, 2-2 and 3-3 to sheet 17, 4-4 and 5-5 to sheet 18. My region erase and redraw at the old coordinates hit the wrong blocks; I repaired it by measuring each block's axis dims.
- Lesson: before every redraw, re-locate the targets (dims, titles) in the live drawing; never trust stored coordinates.
- Rewriting formulas in an existing table corrupts its fields (cells share field ids). Rebuild the table with newtable and write the formulas once.
- Round 7: the user asked to make sheet 19 «әдемі» (neat). I redrew it with posts at both ends of О2 in the railing style and callouts on the free sides with short leaders that do not cross the drawing. Overall 1200 replaced the floating 2200 rise dim, and duplicate dims were removed. Tags: f19, f19d, f19n.
- 2026-10-19: the user asked to add the stair spec (63F6C7) together with the railing into the main spec, in the «Лестница» column of their new table 658A05 (12 cols incl. Лестница and Лифт, at 2426513.5,-1678661.5).
  - I rebuilt that table with g13.py (newtable plus fcells in one transaction). Лестница = 16.46 t, total 52.53 t. The new table handle is in the map as ms3:SPEC.
  - Logged in Obsidian: «Ограждение лестницы — правила», spec rules, project note, chat note.
- 2026-10-19, user review («қате бар, өзің тап»): I found 18 issues but forgot to print the list before asking — always show the findings text before asking for approval.
  - Fixes done:
    - main spec rebuilt onto sheet 2 (ms4, Лифт Тр.100/80 cleared on the user's request, total 49.62 t); old 61D698 and the extra stair-spec sheet «2» (2517590) deleted;
    - sheet 20 tables rebuilt inside the frame (user had moved the frame to 2855913,-1600875; sp5/tbv5);
    - node callouts (nd9);
    - railing sections renamed Р1…Р5 (SPDS McSectionVS.Word via op mcset);
    - ГОСТ list added on 1.2; typos fixed.
  - Open question: the post length. Both the user's node and the fragment show 1200 posts on top of the stringer, but the spec uses 1.35.
  - Background job race: a timed-out run.sh can still execute later. Check the table state before re-sending.
- 2026-10-19 ~11:45: the user's AutoCAD crashed (.dwl left behind, no acad.exe). The cause is unknown, possibly my plugin.
  - The saved dwg is from 10:52 and lacks all of the morning's fixes. The autosave `%TEMP%\КМ Чертеж БЦ для клауда_1_6037_4e8b6559.sv$` (11:45) has everything; I copied it to «КМ Чертеж БЦ для клауда - восстановлено 11-45.dwg» next to the original.
  - Still pending: the node mark (SPDS knot, needs GUI AutoCAD) and the post length question (1.2 vs 1.35).
- 2026-10-19 later: the user reopened the recovered file. Work continues in «КМ Чертеж БЦ для клауда - восстановлено 11-45.dwg» (job.ps1 target changed).
  - The user confirmed posts are 1350 (150 down onto the stringer web). The node post now sits on the outer face of the web and the fragment posts are extended down 150, each with a 150 dim. The spec is unchanged (1.35).
  - Node mark «А» (McNoteKnot cloned from the stair sheet 63F8F8; props Knot/Sheet/Center/Rack) placed on Р1 at the foot of the lowest flight end post. Node title: «Узел А. Крепление стойки к косоуру. М 1:20».
- The user asked for the railing as its own «Ограждение» column in the main spec, not inside «Лестница». Main spec rebuilt with g16.py (13 cols, ms6:SPEC = 65E500): Лестница 14.25, Ограждение 2.22, total 49.62.
- Notes on all sheets rewritten from analogs (g17.py, op mtset): bottom-left above the stamp; sheet 8 left of stamp; sheets 4/9/14 moved to free space. Rule note in Obsidian «Примечания на листах КМ — правила». Wblock of the whole sheet 8 fails (eExcessiveItemCount) — plot it in halves.
- Layouts 11–20 added (tabs after «10»). The user's layouts each hold one long strip viewport with target (-293546,-755233) panned so the frame sits at paper (0,0). I cloned from templates (landscape 1:100 «1.1», portrait «2», 1:10 «10») with LayoutManager.CloneLayout OUTSIDE any transaction (inside one it throws eNotInPaperspace). Then I set the model viewport: target 0, ViewCenter = frame centre, size = frame/scale, CenterPoint = paper centre. Check: db.Wblock() copy, then accoreconsole `-PLOT _N <layout> "" "" "<pdf>" _N _Y` (no Y/N file prompt for the PDF device).
