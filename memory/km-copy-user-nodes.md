---
name: km-copy-user-nodes
description: "КМ node sheets: copy the user's own node drawings (e.g. ЛК-1 sheet 7) and resize them by stretching — never redraw nodes in my own style"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 31c24da5-b358-45a3-b1ee-c1d716ba778d
  modified: 2026-10-18T16:48:50.457Z
---

On 2026-10-18 the user said twice that I had drawn in my own style: «сен менің стилімде емес өз стиліңде жасағансың… менің софтыммен менің стилімнен аумасын» and «қате көп, оформлененің барлығын менің лестницама қарап жаса». My parametric re-drawings, even with the same layers, were rejected. What worked:
- Import the whole reference node sheet with WblockCloneObjects: ЛК-1 sheet 7, frame (2480944,-1756151)–(2485144,-1753181) at 1:10.
- Then adapt each node to the new sizes. Session 31c24da5 `net\rn.cs` ops:
  - `widen` moves stretch points by side of an axis line;
  - `stretchwin` is an AutoCAD-like STRETCH;
  - `movegrp`, `arcrad`, `dimpts`;
  - `mcset` sets SPDS props (Origin, Center/Rack/Knot of NOTEKNOT, Start/EndPoint of BREAK, FirstLine of notes, Scale);
  - `levelval` byte-replaces a level value; `addleader`.
- Nodes the reference doesn't have: draw them with SPDS objects cloned from it (WELD, JOINT, BREAK, LEVELMARK, SECTION). Helper library `lkstyle.py`.
- Gotcha: ЛК node 4/5 is drawn ×2 with dimlfac 0.5, so its offsets must be doubled.
- Node marks on schemes and sections use SPDSNOTEKNOT (oval plus shelf). On node sheets they use the circle block plus two texts.
- Tables (Ведомость элементов) are imported from ЛК-1 sheet 4 and extended by stretching and cloning a row. The general table and the truss table are separate.

**Why:** the user judges every line and letter against their own album, so imitation fails.
**How to apply:** for any new КМ sheet, start from the closest user sheet, copy it, and modify it. After that, plot and check for overlaps. Run 3 reviewers (style / SPDS / technical) when the user asks for a review.

Related: [[karasu-lk1-canopy]], [[km-callout-style]], [[obsidian-log-work]]
