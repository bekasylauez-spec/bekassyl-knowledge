---
name: project-obezvozhivanie-make
description: "Помещение обезвоживания (Станция очистки, Завод Маке) — КЖ+КМ из .lir по стилю АБК; 06.11: КЖ 1.1–7.2 (42 л.) + КМ-1…КМ-6 сызылды, oc 0"
metadata:
  node_type: memory
  type: project
  originSessionId: 709ba837-83a0-4b00-b448-39f0aa80a012
  modified: 2026-11-11T13:35:27.840Z
---

05.11.2026 user: «Мынаның кжсын и км сыз. Расходын мейілінше көбейт. Сосын подушка и раскладканы АБК сияқты ал» for `D:\РАБОЧКА\От Маке\Завод\Обезвоживание\Станция очистки - Помещение обезвоживания (1).lir`.
«Расход көбейт» = reinforce with margin (same as АБК «пусть будет с запасом»).
**Why:** user wants their АБК ВАРИАНТ 2 album style, cushion and rolled-pile layout reused. **How to apply:** working DWG `Обезвоживание\КЖ Помещение обезвоживания.dwg` (copy of АБК ВАРИАНТ 2), own acad + `acadjob_ob` (АБК session uses acadjob_ab in parallel). Full data, levels, pile rules and progress: Obsidian `15_Проекты\Помещение обезвоживания (Маке)\КЖ КМ Обезвоживание — исходные данные (05.11.2026).md`. .lir 2013 binary parse method is written there too.
Related: [[project-abk-zavod-make]], [[lira-model-by-analog]]

05.11 evening: user asked to re-check openings symbol, dims and mark leaders against Obsidian rules → 2.1–2.5 rebuilt (arrow marks to element edge facing centre, 45° short leader, shelf opposite arrow; 1000-mm outer dim rows; template broken-line opening symbol; axis→face→size→face→axis). Foundation = one monolithic Фм-1 like АБК (Фб marks dropped). Next: reinforcement sheets 3.x (АБК 3.1–3.5 as analog), 4.x, 6.x, 7.x, then КМ.

05.11 кеш → 06.11: Фм-1 қайта: ЛИРА деңгейі (балка −1.3…−0.7), АБК принципімен 3.1–3.6 (oc 0), PDF «листы 1.3-3.6». 4.1–4.6 колонналар дайын (oc 0), PDF «листы 1.3-4.6». АБК артық парақтары/layout-тары өшірілді (пайдаланушы сұрады); 0/00 обложка-титул қалпына келтірілді (тұзақ: рамкадан тыс мәтіндер). PDF «КЖ Обезвоживание (листы 1.3-3.2).pdf». Шаблондар енді АБК DWG-сынан import арқылы алынады. Келесі: колонна 4.x, балка 6.x, плита 7.x, 1.1/1.2, штамп, рамка тығыздау, КМ.

06.11: 6.1–6.17 балки, 7.1/7.2 плиты, КМ-1…6 (AutoCAD, Σ≈12.8 т), 1.1 мәтіні мен 1.2 ведомость жобаға ауыстырылды. ПБ1 детальды парағы жоқ (КМ схемалық бірінші нұсқа). Толығы Obsidian жобалық жазбада.

11.11.2026 (BEKA-1): котлован/сваи/гидроизоляция brought to ABK final: Св1 362 armed + Св2 32 unarmed L=9, 0.000 = 347.90, ABK geology column, new sheet 1.5 pile reinforcement, hydro/steel tables, geomembrane; full КЖ album 45 p. in project folder. Details in Obsidian note. Related: [[project-abk-zavod-make]], [[project-tsekh-predobrabotki]]

11.11.2026 (BEKA-2): separate `КМ Помещение обезвоживания.dwg` split out of the КЖ DWG (D:\_claude_work\obez_km\kmmake.cs, accoreconsole) + АГСК codes (notes: anchors/ГФ-021/ПФ-115 from analog «Кж-склад рулонов»; spec column: sheet 214-101-0201, □120 214-205-0103). Rest filled from the official list ks.gov.kz/download/productcodes_ru.pdf (local copy D:\_claude_work\obez_km\agsk_dl, user approved the download): [18П 214-203-0202, □80 214-205-0102, Тр.140х4.5 group code 241-102-0200 (no exact size). КМ layouts inside the КЖ DWG left unchanged.

11.11.2026: stamps/titles made like ABK (blocks Штамп_ОБЗ_КЖ/КМ from Штамп_АБК, object «Помещение обезвоживания»); КЖ 45 p. + КМ 7 p. PDFs rebuilt.
