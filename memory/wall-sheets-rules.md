---
name: wall-sheets-rules
description: МАРКА = ОСЬ бойындағы тұтас стена (барлық қабат), бірдейі бір марка; КЖ стена парақтары — аналог «4.1 Стена См-1…» (ЖК Галакси) бойынша; шеткі аймақ ш.100; тік арматура сызу: жоғарғы қабат 20 мм оңға ығысады, шагтар подвалдағыдай; торецке/үстіне скоба; рамка міндетті
metadata:
  type: feedback
---

05.11.2026, ЖК Галакси См-1 (sheets 5.1–5.4 from the analog «Аналог\4.1.Стена См-1 ...См-5 Тип С.dwg», same building series).

User decisions/corrections:
- Edge zones of wall pieces ш.100 (≈450 mm at free ends, Ø by the LIRA peak), middle base Ø12 ш.200 (or by calc); vertical Ø never grows upwards (see [[wall-vertical-diameter-down]]) — the old «neighbouring storeys Ø differ ≤ 4 mm» rule is cancelled (06.11).
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

- 05.11 (2): спецификация — масса/жиын тек 2 таңба, саны бүтін; болат ведомості Ø бойынша спецификация жолдарының қосындысына тең (ved_check.py). Әр стенаның спецификациясы — бөлек A3 парақ (5.9 үлгісі). Ск (скоба): негізгі стерженьнің жанына бөлек қысқа сызық (горизонтальда 20 мм ішке, вертикальда 20 мм сыртқа), выноска сол сызыққа — аналогтағыдай.

- 17.11.2026, Гостиница Касымова (Revit): «Стеналарды неге бұлай жасадың. Ережелерді қарадың ба? Маркалары қалай бөлінетінін». Мен 46 «марка» жасадым — бір қабаттағы кесінділер (t, L) бойынша автоматты топталған (См-1 = 218 дана 1250 мм кесінді, әр қабатта, әр ось бойынша), әр маркаға бір парақ, бір қабат кесіндісі. Бұл ереже мен аналогқа қайшы: **марка — ось/сызық бойындағы тұтас стена (фундаменттен жоғарыға дейін, барлық қабат, ойықтар, ішіндегі колонналар), бірдей осьтер бір марка, саны көрсетіледі**; әр маркаға аналог Онкоцентр 5.2–5.6 құрамы: «Опалубочный чертеж монолитной стены по оси Хс стена См-N (тол.…)», «Основное армирование…», «Разрезы…», «Спецификация стены См-N».
  **Why:** маркалау схема кезеңінде (15.11) «келісілмеген» деп белгіленіп қалған, мен оны тексермей 46 парақтық серияны соның үстіне құрдым.
  **How to apply:** элемент парақтарын бастамас бұрын маркалауды осы ережемен және аналог парақ тізімімен салыстыр; күй.md-де «келісілмеген» деп тұрған шешімнің үстіне серия құрма — алдымен ережемен шеш, болмаса сұра.

- 17.11.2026 (Касымова, 3): пайдаланушы «қате. Кароче стенаны өшір… 1-ші осьтің бойындағы стенаны ал, ол См-1 болады, соның опалубкасын сыз. Гитхабта BI-дің стенасына байланысты ереже бар, соның ішінен стенаға қатыстысын алып жаса». Менің «үздіксіз қабырға + бірдейі бір марка» нұсқам (39 марка) қате деп табылды. **Марка = ось бойындағы стена, нөмір цифрлы осьтен басталады (1-ось = См-1), сосын әріпті осьтер.** Оформление — GitHub `BI_Group_Стена — парақтар және оформление.md` (S03 СЖм-1 КЖ-52): A1 кітаптық, развертка 1:100 үзілмейді, сол жақта отметка + екі тізбек (қабат; плита / таза биіктік), екі жақта қима белгілері «N» / «по N» (қима типі `*01_Стена_разрез`, «Метка связи = по»: қайталанатын қабатта сілтеме белгі), ойық — қара сына, астында бөліктер / осьтер / жалпы, қызыл осьтер, атау «Стена См-N. Опалубочный чертеж», ескертпе 3 тармақ. Үлгі суреті пайдаланушы берген «Стена в плоскости СВн-1».
  **How to apply:** стенаны бір-бірлеп (бір марка → пайдаланушы Revit-те тексереді → келесі); өз белгісі қасбеттің кропымен кесілмеуі үшін кроп «тарақ» пішінді (`k69_wall_opal_body.cs`).

- 17.11.2026 (Касымова, 4) — ЕРЕЖЕЛЕР №146: «Разрездері аз. Неге әр түрлі размерлерге сечение не форма өзгерсе бөлек разрез беруің керек» → мен тік разрездер қостым → «Вертикальный қажет емес, горизонтальный жетеді. Разрез 1-1 мен 2-2 опалубканың бетіне сыймай ма?». **Опалубкада тек көлденең разрез — жоспар орналасуы (кесінділер, қалыңдық, ось ығысуы, ойықтар) өзгерген әр қабат тобына біреу; тік разрез сызылмайды. Разрездер опалубка парағының өзінде, қасбеттің астында** (сыйса бөлек парақ жоқ).
  **How to apply:** `k69_wall_opal_body.cs` (VERT = false); бір парақ: қасбет + 1-1…N-N + ескертпе.

- 17.11.2026 (Касымова, 5) — ЕРЕЖЕЛЕР №148: «шахматно орналасқанын неге жасамадың? ЕРЕЖЕМЕН АНАЛОГТЫ ТЕКСЕР», «каждый арматура нахлестпен жалғанғанына көз жеткіз», «шагтары қайда». Шпилька шах. п400 (қатар 200, ығысу 200); тік позициялар төменнен мұраланады (05.11 ережесі, мен әр қабатта қайта есептеп нахлёстсыз қалдырғанмын); әр ұшы нахлёст / көршіге 71d / выпуск; шаг MRA «шаг_количество/поз.».
  **Why:** 05.11 ережесі мен BI шпилька шахматын генераторға енгізбей, тексерусіз парақ көрсеттім. **How to apply:** стена парағынан бұрын `chk_lap.py <марка>` TOTAL 0; шешілмегені — СҰРАҚ.
