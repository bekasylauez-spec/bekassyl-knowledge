---
name: km-callout-style
description: "КМ fragment drawings: the user's callout (SPDS выноска) style and how to lay them out — from their own edit of sheet 19, Байтурсынова railing (2026-10-17)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 412db224-1ed1-4b1d-b780-71b9e3570735
  modified: 2026-10-17T16:09:55.062Z
---

The user edited my railing fragments sheet by hand and said «ВЫНОСКА СТИЛЬДЕРІН ОСЫЛАЙ ЖАСА» ("make the callout styles like this"). Their version:

- Each SPDS note: first line = profile ("Тр.50х3", "Тр.20х2", "Л"), second line = element name ("поручень", "стойка", "балясина", "нижний пояс", "косоур", "обвязка площадки").
- The shelf sits just outside the drawing, right next to the element it names. The leader is short and diagonal, from the shelf end nearest the element. Leaders never cross the drawing or other callouts.
- Each callout goes on the side where its element is:
  - стойка: beside the post, at mid-height.
  - поручень: above the handrail.
  - балясина: near the top end of the balusters.
  - нижний пояс and Л: below the drawing, close to their element.
- Even spacing between callouts; no long stacked column on one side.
- Fragment posts stop at the floor line (no 150 drawn below the floor), so only one 150 dim remains at the bottom.
- Dim chains stay on the side free of callouts.

**Why:** my automatic layout put all callouts in a stack on one side with long leaders. The user re-placed every one by hand.
**How to apply:** for КМ fragments and nodes, place each callout next to its element on the nearest free side, with a short diagonal leader from the near end of the shelf. Check the plot for crossings before handing back.

Related: [[baitursynova-km-railing]], [[cad-callouts-spds]]

2026-10-23 (Рампа v2, plan of СГ1 braces): the user's green circles marked the GOOD labels. The SPDS mark's shelf lies ON the brace line, the text is parallel to it, at the brace middle. Offset labels with their own shelf and an old angle (left over after a stretch) are wrong. After any stretch, re-place marks by rotating them about the shelf middle and moving them onto the member (sc2.cs op `xform`, session a2999bcf).
29.10 (БЦ Лестница 02, plans): «выноскаларды аналогымдағыдай» — in plan views copy the analog's SPDS notes (bait.dwg plan: Ст1 63F870 = shelf + leader, Arrow None; Л 63F881/63F884 and vertical 63F88F/63F880, Б1 63F87F = no leader, label sits on the element line, FirstLine = above / SecondLine = below, WipeOut). Clone them and change only the text and position — never create notes with my own note op in plans.
29.10 (any work, user: «алдағы уақытта бұлай жасаушы болма, кез келген жұмыста»): SPDS node callout (SPDSNOTEKNOT, «узел» circle + leader + number on a shelf) — the shelf must run AWAY from the circle, continuing the leader's direction, with the number on that shelf. Leader to the lower-left → Align = Left; to the right → Align = Right. Default Align Center puts a short shelf back under the circle — wrong. rn.cs op `knotalign` sets this for every knot from Rack vs Center; run it after placing any knot callouts.
29.10 correction: setting Align on an existing SPDS knot does NOT always rebuild its shelf — knots 1, 3, 7 and 6 kept the shelf pointing back under the circle although Align showed Left/Right (the user caught it: «3 пен 1 дұрыс па»). Always VERIFY by geometry, not by the property: rn.cs `notelist` gives extents — Align Left must have Emin.x < Rack.x, Align Right must have Emax.x > Rack.x — and look at a plot. Reliable fix: clone a knot whose shelf is already correct (same side), move it by Center, change only Knot; changing Rack afterwards keeps the side.
