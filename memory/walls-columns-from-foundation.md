---
name: walls-columns-from-foundation
description: МІНДЕТТІ (15.11.2026) — every load-bearing wall and column starts from the foundation; no beam on top of a wall (pylon ≤2.5 m excepted); check frame with struct_check.py before drawing (ЕРЕЖЕЛЕР №129–130)
metadata:
  node_type: memory
  type: feedback
  originSessionId: 94c03bfb-48e3-4972-8913-5871021722f0
  modified: 2026-11-15T17:27:15.886Z
---

The user said on 15.11.2026 (Касымова): «Конструктивті тұрғыда тексеріс жасау керек. Кей стеналар 1 қабаттан басталған. Стена фундаменттен басталуы міндетті ереже. тағыда схемадағы қателерді іздеп тап».

The same day, in ЛИРА v5: «стенаның үстіне ригель қоймайсың, подвалдағы қате. Ал пилондар үстінен ригель өтеді». The classification was confirmed: 300 mm ≤ 2.5 m is a pylon, so the beam passes over it; longer 300 mm walls and every 200 mm wall are walls, so there is no beam on top.

**Why:** a LIRA model taken as is had 18 wall pieces and 1 column starting above the foundation (on slabs or beams) and 362 beam pieces lying on walls. The user treats a wall that does not reach the foundation as a structural error.

**How to apply:** before drawing any КЖ scheme, and after every LIRA re-import, check the frame.

What to check (`D:\_claude_work\Kasymova\revit\struct_check.py` on frame.json):
- W1: walls not supported by the wall below.
- W0: wall over an opening in the wall below. The gap is ≤ 3 m with a wall or column at both ends. This acts as a lintel, so it is allowed and the opening is not filled.
- C1: columns not supported below.
- W2: wall thicker than the one below.
- B2: beam on top of a wall.
- B1 / S1: cantilever beams and walls with no slab above. These are information only and are looked at on the per-level plots from `struct_plot.py`.

How to fix:
- Do it in `extract.py` before the perimeter shift (№122):
  - extend each unsupported wall or column down to the foundation (basement columns use the basement size);
  - thicken a wall that is thinner than the wall above it;
  - trim beams lying over walls.
- Rebuild the model with k01 → k15_join → rebar_gen/audit/k02 → sheets.
- List the walls that existed on only one floor so the user can say whether any are non-structural.
- Tell the user that the LIRA model needs the same change and must be recalculated.

Also №131 (same night, user sent a 3D screenshot of a column broken at a slab level: «колонна бір тұтас болып кетсін»): columns/walls must be continuous — model their tops AT the next level (offset 0) and join the floor so the floor cuts them; never end them at slab bottom (−200), which leaves 200 mm gaps where there is no slab (double-height space, shafts outside the slab). Check concrete continuity along every column axis (k17_axis.cs = 0), not the column solid itself.

Related: [[perimeter-wall-flush-foundation-overhang]], [[project-kasymova-hotel]], [[kzh-scheme-karkasa]], [[check-levels-by-element]]
