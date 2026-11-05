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

- 05.11 «Вертикальный арматура 2 шт тұр неге… Скобаны да қате қойдың»: (1) a zone on the elevation = its TWO extreme bars only, never duplicates — before redrawing erase every LINE/LWPOLYLINE on диам* layers (old analog bars + earlier runs stacked up to 7×); (2) staggered laps as in the analog: positions «pA;pB», A lap from the slab top, B after a 0.3·L gap, chain «L | 0.3L | L»; same numbers → one number; note only where positions change; (3) П-скоба wraps the wall thickness → on the elevation it is a VERTICAL leg (L = lap) at the extreme bars at the top, not a horizontal line.
  **Why:** I copied the analog without reading its bar convention; duplicates were invisible until zoomed. **How to apply:** for every wall elevation, zoom the analog at 400 dpi first and count lines per bar on my plot.

- 05.11 «Размерлерді таптамай сыртқа шығар, аналогтағыдай»: lap dim chains go OUTSIDE the wall (dim line ~350 beyond the piece face / cross-wall face, ext. lines from the bar), never on the wall hatch; the short 0.3L text beside the chain, clear of neighbour notes.

- 05.11 (later) «Стенаны қайта жасаймыз… мыналарды переделка жасап размерлерін созу керек болса созып есептеп шық»: walls are made by REWORKING the analog sheets (import whole sheet into the main DWG so the stamp is ours, explode, drop missing pieces, stretch with op pmap/stretch, then recompute reinforcement in the analog's zones), not generated from scratch. Mapping of our marks to analog sheets: Obsidian «КЖ — ход работ» 05.11 (9).
  **Why:** the user wants the analog's look kept exactly; my generated sheets drifted from it. **How to apply:** every wall/sheet type: import analog sheet → stretch → recalc; new separate DWG gets the analog's stamp style, so work in the main DWG.

- 05.11 «Спецификацияны менің жасағанымдай етіп А3-ке сыйдыр»: every wall's specification sheet copies the user's A3 layout (См-1 sheet at x 1071200): «Ведомость деталей» one column on the left, spec table right, steel summary at the bottom, A3 stamp — not the analog's A2 sheet.

- 05.11 «Стена сызғанда арматура шагын жасағанда ең шеткі 2 жағынан 50 мм тастап сосын ішін бөлесің»: bars 50 from both faces, inner span divided by the step, leftover one space in the middle (rows over the height the same: 50 above slab, 50 below the next slab). «Выноскаларды размерден басқа жағында болсын, аналогтыкын қолдан»: keep the analog's notes in place (change text/leader points, clone for extra zones), lap dims on the other side of the piece (or same side, other storey when the other side is a cross wall).
  **Why:** my generated layout left odd gaps and my own notes clashed with the dims. **How to apply:** every wall; wl/wall_vert.py ANALOG_NOTES=True, wl/rowsplit.py.

Scripts: Obsidian `15_Проекты/ЖК Галакси/Инструменты/` gen_wall_geom.py, gen_wall_opal.py, gen_wall_vert.py, arm/wall_zones.py.

Related: [[galaxy-kzh-scheme]], [[column-rules-template]], [[obsidian-first]]

- 05.11: Bekassyl См-1 өшіріп «тек аналогтан алып жылжытып келтір» деді → парақтар аналогтан қайта импорт + pmap (sm1_redo), содан кейін ғана ЛИРА есебі сол аналог объектілерінде. Шаг тізбегінің мәтіндері бір-біріне түспейді (3 қатар), выноска мәтіні простенка үстіне түспейді (notes_clear).
