---
name: cad-mirror-spds-views
description: "AutoCAD+СПДС: чертеж көріністерін скриптпен айнадай аудару (MIRROR) — жұмыс істейтін тәсіл, СПДС/размер тұзақтары және қабаттасуды регрессиямен тексеру (17.11, БЦ Лестница)"
metadata:
  node_type: memory
  type: reference
  originSessionId: 7f13e48d-e330-4f2a-9476-26f9df9418c6
  modified: 2026-11-17T17:31:11.314Z
---

17.11.2026, БЦ Лестница («лестницаны айнадай аудар»): a whole album (plans, sections, railing sheets with SPDS marks) was mirrored view by view by script.

**Method that works**
- Own acad.exe instance (`/b` script → NETLOAD → command), not a listener: `ed.Command("_.MIRROR", SelectionSet.FromObjectIds(ids), "", p1, p2, "_Y")` needs command context. MIRRTEXT 0, OSMODE 0 during the call.
- Select by explicit handle lists per view (entities whose extents lie inside the view window, exclusive assignment, SPDSFORMAT excluded), axis = centre of the view's bbox → the view keeps its place on the sheet. A `shift` on the axis moves a view when it sits too close to the frame.
- Handles survive MIRROR, so before/after comparisons by handle work.
- Texts, dimensions, hatches, level marks, knot callouts, axis and section marks come out readable and correct.

**What MIRROR does NOT mirror exactly (fix afterwards)**
- SPDS notes without a leader and with vertical text (Angle ≈ 90°/270°: «Л» on frame ends, «Б1», «Пр1») keep the text on the same absolute side → swap FirstLine ↔ SecondLine (op `noteflipv`).
- Dimension texts placed outside with a leader (small dims like «540», «370») get a new default side → set TextPosition to the mirrored original (measure the tp ↔ text-box relation once: it changes for rotation-180 dims).
- Vertical dimension texts stay on the readable (left) side of the dim line, i.e. ~3.8 mm away from the mirror image → can run into a neighbouring callout; check and move the callout.
- Horizontal no-leader notes shift by about one text width along their line (harmless).
- SPDS section marks with a vertical cut line (3-3, 4-4, Р4, Р5): the number drops from above to below the arrow (~3 mm lower) and touches the dim chain / tick → move the mark up 300 or sideways 100, and check on the plot that its arrow does not cross a callout leader (the independent checker caught this, not my regression).
- Table sums are computed from unrounded cells → shown parts can differ from the shown total by 0.01; write new formulas as `round(…*100)/100` (works in AutoCAD table formulas).

**Checking**
- Exploded text boxes of mirrored SPDS notes are unreliable (off by the text width) — judge notes on the plot, not on geomdump boxes. Dimension text boxes are reliable.
- Regression instead of absolute check: `ovl.py` (text box vs segment / text box / inner frame, per handle pair) for original vs variant; only NEW pairs matter, the original's own overlaps stay as they were.
- `mdiff.py`: render the original view, flip it, diff against the variant view (closing + dilation, dimension texts masked) — shows every annotation that is not at its mirror place.
- Unchanged sheets: pixel-compare PDF pages with the original (must be 0).

**Table trap (same job)**: `Table.GenerateLayout()` after setting a cell formula dropped the formula of another cell (H4). Do not call it; set formulas, then `db.EvaluateFields()` and the command `_.UPDATEFIELD _ALL` — values of dependent cells are right only after UPDATEFIELD.

Code: `D:\_claude_work\bc_lestnitsa\var\` (net\mv.cs, net\run.ps1, mkops.py + wins.json, fix1.py, ovl.py, mdiff.py, zoom.py). Related: [[cad-dedicated-instance]], [[reference-spds-api]], [[no-repeat-check-pipeline]], [[bc-stair-02-lira]].
