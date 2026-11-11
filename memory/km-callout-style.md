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

- (ескі, 09.11 ауыстырылды) Маркасы бар элементке тек марка; маркасыз бөлшекке (поручень, стойка т.б. маркасыз болса) профиль + атауы.
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
29.10 (any work, user: «алдағы уақытта бұлай жасаушы болма, кез келген жұмыста»): SPDS node callout (SPDSNOTEKNOT, «узел» circle + leader + number on a shelf) — the shelf must run AWAY from the circle, continuing the leader's direction, with the number on that shelf. A short shelf bent back under the circle is wrong. (10.11.2026: the old instruction «set Align = Left / Right, rn.cs `knotalign`» was removed as contradicting the later finding — Align does not move the shelf; see the next paragraph and [[leader-shelf-opposite-side]].)
29.10 correction: setting Align on an existing SPDS knot does NOT always rebuild its shelf — knots 1, 3, 7 and 6 kept the shelf pointing back under the circle although Align showed Left/Right (the user caught it: «3 пен 1 дұрыс па»). Always VERIFY by geometry, not by the property: rn.cs `notelist` gives extents — Align Left must have Emin.x < Rack.x, Align Right must have Emax.x > Rack.x — and look at a plot. Reliable fix: clone a knot whose shelf is already correct (same side), move it by Center, change only Knot; changing Rack afterwards keeps the side.

09.11 (В109 Узел 7, пайдаланушы скриншотпен көрсетті): выноска сызығы полканың ЖАҚЫН ұшына келеді, полка (мәтін) стрелкадан АРЫ қарай созылады. Менің қатем: SPDS note клонының Angle-ын (π) өзгертпей, сызық полканың алыс ұшына барып мәтінді кесіп өтті. Ереже: shelf.x ≥ arrow.x → Angle 0, shelf.x < arrow.x → Angle π (mcset Angle). Бір выноска — бір стрелка (екі стрелкалы -t8 жоқ). Көрсетпес бұрын әр выносканы жақындатып тексер: сызық мәтінді кеспейді.

## Марка выноскасы (КМ узелдері) — 09.11.2026, пайдаланушы үлгісі (В109 Узел 7)
1. Стрелка элементтің қырына тиеді (ортасына/штрихына емес); бір выноскада бір стрелка.
2. Бағыттаушы — стрелкадан полкаға бір қысқа қиғаш сызық, полканың элементке ЖАҚЫН ұшына келеді.
3. Полка көлденең, стрелкадан АРЫ созылады (элемент солда → полка оңға, оңда → солға). SPDS note: shelf.x ≥ arrow.x → Angle 0, әйтпесе π.
4. Сызық мәтінді, элементті, трубаны, осьті, басқа выносканы кеспейді; выноска өз элементінің қасында, полка элементтен 300–600.
5. Марка жазылса сечение жазылмайды: маркалы элементке (Пр1, ФФ1, ГС1, БП2, К1, СВ1…) тек марка, бір жол. Сечение/қалыңдық тек маркасыз бөлшекке («-t8 / С245», «L100x7 / С245»).
6. Көрсетпес бұрын әр выносканы жақындатып тексер: сызық полканың жақын ұшында ма, мәтінді кеспей ме.


11.11.2026: узел парағының выноска ережесі толық түзілді (үлгі 40К2-30Б1) — `D:\РАБОЧКА\Узлы_КМ\ЕРЕЖЕ_Выноска_узел.md` (+ Obsidian `16_КМ чертежи_Марки и позиции`): полка ені max(8; таңба×1,6+3), сынық полка ұшынан 1 мм, стрелка ұшы → полка ортасы 10–35 мм қағазда, «Болты» стрелкасыз, бір мәтін бір выноска, саңылаулар 2–3 мм, есеппен қабаттасу 0. Узел выноскасын қоймас бұрын оқы. Байланысты: [[km-node-one-by-one-3d]].
