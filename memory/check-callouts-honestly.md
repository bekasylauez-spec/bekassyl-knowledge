---
name: check-callouts-honestly
description: "How to check drawing callouts so errors aren't missed: per-item zoomed view vs the user's reference picture, geometry check, never trust property values or my own earlier claim"
metadata:
  type: feedback
---

2026-10-29 (КМ лестница БЦ): the user showed a wrong vs correct node-callout picture; I set Align and twice reported «all correct» — knots 1, 3, 7, 6 were still wrong. User: «оларды неге сен бірінші айтқанда көрмедің, соны ретте».

**Why I missed it:** (1) I checked the property (Align = Left/Right), not the actual shape; (2) I looked at whole-sheet plots at low resolution where a 3 mm shelf is unreadable; (3) when the user sent a screenshot I read it expecting my fix to have worked (confirmation), not comparing each item to his correct picture.

**How to apply (every check of callouts / marks / any annotation, any project):**
- Compare each item with the user's reference picture by the concrete feature he pointed at (here: leader enters the shelf's end nearest the circle, shelf and number lie on the far side).
- Look at a zoomed crop where the item is ≥ 30 px, one area at a time; never judge from a full-sheet thumbnail.
- Check geometry, not properties: rn.cs `notelist` + scratchpad `km/knotcheck.py` (knot side by extents vs Rack, leader length ≤ 1500).
- If the user asks «дұрыс па?» about specific items, re-verify those items from scratch before answering; say «тексерейін» rather than defending the earlier answer.
- Report only what was actually seen; if a property was set but not visually confirmed, say so.

Related: [[km-callout-style]], [[cad-callouts-spds]]
