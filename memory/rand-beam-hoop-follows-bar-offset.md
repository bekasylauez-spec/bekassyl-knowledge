---
name: rand-beam-hoop-follows-bar-offset
description: When one direction of crossing beams has its longitudinal bars shifted by d (to pass the other direction's bars), shrink that direction's hoops by the same d — bars must sit in the hoop corners (gap 0)
metadata:
  type: feedback
---

17.11.2026 (РМЦ КЖ, found by the full-album check, ЕРЕЖЕЛЕР №139):
- The generator (`kzh_gen.py` `rb_levels`) shifted the Y-direction rand-beam bars 22 mm inward, so that they pass over and under the X-beam bars in the pile caps.
- It kept the hoops at the X-beam height (730 mm).
- Result: on Рб-4…9 the bars sat 17 mm away from the hoop corners, so they could not be tied.

**Why:** a longitudinal bar must bear on the hoop corner. An expert reviewer rejects bars that float inside the hoop.

**How to apply:**
- Whenever bars are offset for clash avoidance, size the hoop of that direction to the shifted bars: hoop centreline = bar face ± Ø/2.
- State the covers separately in the note (longitudinal bars / hoops).
- Check: the hoop-to-bar gap must be 0 for every beam (`kz99_probe_hoop.cs`).
- In Revit, a shape-driven hoop can be resized with `GetShapeDrivenAccessor().ScaleToBox`. Its box is the OUTER faces (centreline + Ø/2).
- After resizing, recompute КЖ_длина / масса / эскиз / BI_B and rerun the spec, ВД and 7.1.

Related: [[rebars-never-overlap]], [[rigel-pins-hoop-steps]], [[project-rmc-make]]
- **ScaleToBox тұзағы (17.11):** қорап нормалі −Y болғанда жиынның таралу бағыты кері ауысты — 37 жиынның 26-сы балкадан тыс шықты. ScaleToBox-тан кейін әр жиын стерженьдері элемент ішінде ме тексер (`kz99_probe_hoop2.cs` → sets outside 0); болмаса `RebarShapeDrivenAccessor.BarsOnNormalSide` кері ауыстыр (`kz99_hoopflip.cs`).
