---
name: wall-sheets-rules
description: КЖ стена парақтары — аналог «4.1 Стена См-1…» (ЖК Галакси) бойынша; шеткі аймақ ш.100; тік арматура сызу: жоғарғы қабат 20 мм оңға ығысады, шагтар подвалдағыдай; торецке/үстіне скоба; рамка міндетті
metadata:
  type: feedback
---

05.11.2026, ЖК Галакси См-1 (sheets 5.1–5.4 from the analog «Аналог\4.1.Стена См-1 ...См-5 Тип С.dwg», same building series).

User decisions/corrections:
- Edge zones of wall pieces ш.100 (≈450 mm at free ends, Ø by the LIRA peak), middle base Ø12 ш.200 (or by calc); neighbouring storeys Ø differ ≤ 4 mm.
- «Рамкаларын қой» — every sheet needs its format frame (the analog's SPDSFORMAT proxy was left out by my import filter of >50 m objects; import it explicitly).
- Vertical bars on the elevation: the bar coming from below stays, the upper storey's bar is drawn 20 mm to the right so the lap reads; next storey back; bar positions (шаг) stay as they start at the bottom storey.
- «Біткен жеріне скоба қой» — П-скобы: at the wall top over the vertical bars (Ск, ш.200, legs = lap 61d of that Ø, width 170) and on free ends for the horizontal bars (U / П, Ø = horizontal Ø); edge zones get closed hoops X ш.200 + Шп, as in the analog's plan 1-1 and Ведомость деталей.
- «Мынаны жақсылап қарап шық — саған арналған аналог, сенікіне қатты ұқсас»: read the analog sheets fully before drawing (positions with two numbers «6;7» = staggered laps, lap dims «730 | 220 / 730 | 140»).

Scripts: Obsidian `15_Проекты/ЖК Галакси/Инструменты/` gen_wall_geom.py, gen_wall_opal.py, gen_wall_vert.py, arm/wall_zones.py.

Related: [[galaxy-kzh-scheme]], [[column-rules-template]], [[obsidian-first]]
