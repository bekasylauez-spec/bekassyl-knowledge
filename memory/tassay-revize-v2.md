---
name: tassay-revize-v2
description: "Tassay Revize_2026.10.21 (Downloads): m2 to wall faces, walls 12/25, doors 210, WC 80/210, floor sync — decisions made and open items"
metadata:
  node_type: memory
  type: project
  originSessionId: 9cbc3bd2-55fc-4953-93d0-a7f462e3f5f9
  modified: 2026-10-21T11:01:16.648Z
---

2026-10-21: the user pasted a Turkish spec for `C:\Users\Admin\Downloads\Tassay Revize_2026.10.21.dwg`. The output is `... v2.dwg` next to it, and the source was not touched. Layout: 5 plans spaced 5000 apart in X (local origin x=53841.4766+5000i, y=15359.8485). Plans: ZEMİN, 1.KAT, 2.KAT, 3.KAT, attic. Walls are 1 rectangle each on `duvar`. Columns are in the shared block `КУПУФКП` (scale 0.1, mm).

Decisions I made, which the user has not confirmed:
- Perimeter column inner faces 35 → 37, flush with the 37 outer wall.
- Doors x/217 → x/210, except fire doors 194/217, which stay.
- WC doors = 80/210, W=71.8, DK=12, following the user's own sample door 9B0 on 1.KAT.
- Where a WC opening was 81 or 79, a stub was shifted 1 cm. The top WC cabin door now runs to the outer wall.
- Where there is no wall between rooms, the m2 boundary follows the old m2 line.

Open items reported to the user:
- The 3.KAT BANYO rooms have no walls or doors.
- The kitchen hatch block accepts only 10/15, so it was set to 10, centred in the 12 wall.

Method:
- Scripts are in the session 9cbc3bd2 scratchpad: fixwalls.py, doorfit.py, rooms.py, mkops.py and net/apply.cs (TAPPLY).
- Door opening = the jamb segments of length DK in the anonymous block. P sits at a corner of that opening, so P can be moved straight onto the target corner.
- Room outlines come from free-space components. Door bands, windows and the outer band are closed first. Spaces shared by several rooms are split on a 1 cm grid by the nearest old outline, using cv2.distanceTransformWithLabels.

Related: [[tassay-ar-walls-from-scheme]], [[cad-console-net-workflow]], [[plan-wall-rethickness]]
