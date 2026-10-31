---
name: plan-wall-rethickness
description: "How a floor plan was re-laid with new wall thicknesses while keeping room areas (AKTAU, 2026-10-13) — piecewise old→new coordinate maps"
metadata:
  node_type: memory
  type: reference
  originSessionId: 52c71a7a-6791-46c3-a097-4edf9b6d817c
  modified: 2026-10-13T13:30:30.653Z
---

Task "бөлме площадтарын сақтап, перегородка 20, несущий 40" (AKTAU_Yerel Taslak Proje, 2026-10-13). The user marked load-bearing walls in red only on screen (not saved). Here that was the perimeter plus the two corridor walls (axes B, C).

Method that worked:
- Room widths and depths were solved so each label area (2 decimals) stays the same. The building grows: 22100×13350 became 22248×13605.
- Piecewise-linear old→new maps per band (bottom row, corridor, top row) and sub-zone (Revir/Banyo, WC cabins, pano, cold rooms). Elastic stretch segments are placed only where no door/window opening is.
- Walls and room polylines are mapped vertex by vertex (zone picked by nudging along the adjacent edges). Furniture, doors and windows are moved rigidly.
- Checks: opening widths unchanged; area of every m2 polygon equals its label.
- Scripts are in the session 52c71a7a scratchpad (plan40.py, gen_ops.py, plan4020.cs, run.ps1). Work files are in `D:\РАБОЧКА\AKTAU_work`.
- In accoreconsole: clone the block def to a new name (it was shared), then repoint the BlockReference.
- Associative DIMs don't update when the def points change, so replace them with clones.
- Delete the old .dxf before DXFOUT, otherwise the console hangs on the overwrite prompt.

Related: [[cad-console-net-workflow]]

Multi-floor version (AKTAU KIZ YURDU, 2026-10-13, script bld.py in the same scratchpad):
- All floors share one grid. User agreed: main rooms exact; service rooms (corridor, stair, WC hall, lobby, bath) act as absorbers and may only grow.
- The stair core and shafts stay aligned on every floor.
- The attic outer wall (40 cm) sits on the slab cantilever, ≤60 cm out. Its position is solved so attic areas stay exact.
- Take elastic placement from the gaps between wall polylines, not from door/window insert bboxes. Window blocks have oversized bboxes.
- The dims layer "olcu yatay" is frozen in the user's file. New dims go on that same layer.
- The 'antet' sheet frames sit inside the floor regions. Exclude them from moves.
- 2026-10-14 correction: the wall on axis B is NOT load-bearing → 20 cm partition (BW param). Load-bearing = perimeter + axis C only.
- User rule: door openings 102/107 → 95 cm. Door blocks are dynamic "kapi_plan_tekli_4" (props "kapi Genisligi", "Duvar Kalinligi"; attribute KAPI_POS "W/H"). Set width + wall thickness, extend the far-jamb wall by the difference.
- The user opens and saves my v2 outputs in AutoCAD. Never overwrite a file that may hold their edits; write a new version (v3) and tell them.

2026-10-17 (session e91febd6, scratchpad gen20.py + net/apply20.cs + net/probe.cs): user rejected the v2–v4 redesigns (moved to Мусор) and asked a simpler thing on their own _10.dwg: "load-bearing A,B,C,D + contour → 20 cm, keep interior area" on all 3 floors (B/C 25→20 too). Method: per-floor STRETCH-like band maps (inner/room faces fixed, outer/corridor faces move; outside items stay except fire-stair landing within +10 of facade). Windows pencere_plan_3-2: keep insert ≤20 from inner face, Distance1-3 -= outer shift. Doors kapi_plan_*: B/C → Duvar Kalinligi=20 + move with face; fire door tekli_3 moves with facade, DK -= shift. Axes: clone AKSLAR→AKSLAR_20 (roof plan keeps old), A/D/1/6 at new outer face, B/C at new wall centres. Attic 73 (48+25) walls → 20, division lines erased. Area labels are fields: db.EvaluateFields() (UPDATEFIELD is unknown in accoreconsole). Paths with Kazakh letters (қ) break accoreconsole scripts (cp1251) → work in the scratchpad. Output: "AKTAU KIZ YURDU PROJESİ_10 v5 (20 см).dwg". User then said to do the same on another file.
Same day, _12.dwg (Downloads): user had already made Z = 38/25 like K1, drawn external insulation 10 + finish 10 (layers 'yalıtım ısı', 'sıva') outside the walls, attic side walls 25 on the axes, attic top/bottom 25 + 48 outer strip, and a 12 partition instead of the C wall at K1 axes 3-4. gen20_12.py adds: attach zone 20.5 cm outside the outer face (moves with the face), rigid +18 for the Z entrance vestibule, NOBC span for that partition, the attic 48 strip outer edge kept. Output "AKTAU KIZ YURDU PROJESİ_12 v2 (20 см).dwg". Each new file needs its walls re-dumped; never reuse the old face coordinates blindly.
Final user rule for _12 (2026-10-17): "несущий 40, қалғанының барлығы 20" = contour (as drawn, 38) + B/C → 40 (room faces fixed, grow into corridor), every other wall (25 and 12 partitions) → 20 about its own centre line (flush-with-fixed-face partitions grow away from it). Script genpw.py (face-move engine: wall runs → face lines, vertex map, consistent-coordinate rule against skew, stubs extend runs, shorter run sticks to longer one on shared face). Output "_12 v4 (несущий 40, қалғаны 20).dwg". Room areas change ±0.1–0.6 m² with this rule; corridors lose ~15 cm per side.
Then (same day) "контуры 38 қалып кетіпті 40 қыл": Z/K1 contour 38 → 40 with inner faces fixed (outer +2, insulation/finish, windows D+2, fire doors DK+2, vestibule −2 rigid), axes A/D/1/6 moved with the outer face (convention in this project: perimeter axis = outer face), attic dims via axis map. gen38to40.py; apply20.cs now skips the AKSLAR clone when there are no akslar ops. Output "_12 v5 (контур 40, несущий 40, қалғаны 20).dwg". Lesson: the user calls 38 "40" in speech but wants exactly 40 when it is drawn.
Then "коридорды 180 жаса, зданиені 30 см үлкейт": gengrow.py = STRETCH +30 in y. Cut lines: corridor interior y=-6376 (Z, K1) / -6398 (CK), chosen outside door gaps of cross-corridor partitions; end walls cut inside solid pieces (left -6240, right -6290) so corridor-end windows/doors stay; fire stairs and far-outside items (entrance steps) static; the AKSLAR_20 block is stretched in block coords. Output "_12 v6 (коридор 180, +30 см).dwg": 1369 × 2214, B–C axis 220.
2026-10-19 full spec (user pasted RU instructions): axes A,B,C,D,1,6 walls 40, all others 20; rooms/corridors never narrower (grow the building); WC/shower cabins exact; symmetric bays grow equally (1-2=5-6, 2-3=4-5, A-B=C-D); windows keep relative position in their room. Solution from ORIGINAL _12: layout.py = constraint-graph compaction (wall runs → face nodes, visibility ≥ old width, exact for gaps ≤125 cm and WC/BANYO rooms <6 m², shared axis nodes, attic perimeter free (grows outward), longest path + backward pass, symmetry iteration). genlay.py maps all entities (faces, perimeter bands, façade openings proportional, door-gap anchors, rigid fire stairs/vestibule, main stair pinned to the axis-3 wall face). Result: bays 498/482/323/482/498 × 606.5/220/606.5 (2283 × 1433). Output "_12 v7 (осьтер 40, қалғаны 20, бөлмелер сақталды).dwg".
