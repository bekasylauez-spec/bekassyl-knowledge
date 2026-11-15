---
name: revit-hatch-ansi36-join
description: "Revit КЖ plans/sections — concrete hatch like the analog (ANSI36×20 drafting pattern, walls rotate with host, columns 45°), column must cut wall, full column outline, opening mark in the clear opening (ЕРЕЖЕЛЕР №124)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 94c03bfb-48e3-4972-8913-5871021722f0
  modified: 2026-11-15T15:40:36.430Z
---

15.11.2026 (Касымова, Revit 2.x sheets) the user said: «барлық штрихты реттеу керек. масштабын кішірейт. Сосын стилін аналогтан қара қалай жасалатынын». My Revit hatch had a ≈2 mm spacing, while the analog (Онкоцентр, AutoCAD) uses ANSI36 at scale 20.

**Why:** the Revit sheets must look like the AutoCAD analog. The general rule «ANSI36, масштаб 20» applies in Revit too.

**How to apply (Revit)**

Fill patterns:
- Use Drafting fill patterns in paper mm: offset 0.635, shift 1.11125, segments 1.5875 / 0.3175 / 0.05 (dot) / 0.3175.
- Walls get «КЖ_ANSI36_20» at 135° with FillPatternHostOrientation.ToHost. It rotates with the wall: horizontal walls show «\\\», vertical walls «///».
- Columns get «КЖ_ANSI36_20_45» at 45°.
- Apply the patterns to the material cut pattern and to the view category overrides.
- Script: `D:\_claude_work\Kasymova\revit\k14_hatch.cs`.

Column and wall joins:
- Revit auto-joins walls to structural columns with the wall cutting the column. The column then splits into 4 corners and shows wall hatch inside.
- Fix it with `JoinGeometryUtils.SwitchJoinOrder` for every joined pair (`k15_join.cs`).
- ElementIntersectsElementFilter finds 0 pairs once they are joined, so iterate over bbox candidates and check AreElementsJoined.
- Switching the order invalidates dimensions that reference wall faces, so regenerate the sheets afterwards.
- Draw the column outline in plan as detail lines at the wall cut weight.

Opening mark:
- Use the analog's two-segment mark inside the clear opening. The LIRA hole is at the axes, so shrink it to the wall faces.
- Move any point that falls inside a column out of it.
- Split the opening by an internal wall and mark each part.
- Draw the mark in the fragment views too.

Check with zoomed PNGs: no crossed hatch inside columns, and no mark over walls.

Related: [[drawing-spacing-hatch-rules]], [[kzh-callout-hatch-level-rules]], [[project-kasymova-hotel]], [[compare-with-analog-sheet]]
