---
name: km-tube-families
description: "Own parametric steel tube families (ГОСТ 30245) in _Стандарт_КЖ\семейства, shared params КМ_*; user asked to build and reuse them"
metadata:
  type: reference
---

User 29.10.2026: «Семействоны өзің жаса алдағы уақытта қолданасың». Built by `3602_Порталы_КМ\_авто\fam_01_tube.cs`: `(КМ)труба_ГОСТ30245_каркас.rfa` (structural framing, hollow profile, faces locked to planes h/b/t) and `(КМ)труба_ГОСТ30245_колонна.rfa`, 15 types □40x2…□120x5, □60x40x3 etc. Shared params file `_Стандарт_КЖ\КМ_общие_параметры.txt` group КМ: КМ_Масса_1м (ГОСТ mass, R=2t), КМ_Сечение, КМ_ГОСТ, КМ_Длина_1м, КМ_Масса (framing formula = КМ_Масса_1м·Длина/КМ_Длина_1м). Family API lessons: SketchEditScope only works in projects — make a 2-loop extrusion and NewAlignment its faces; family formulas cannot use "1000 mm" (use a length param). Use these for any future КМ job.

31.10.2026 plate added: `(КМ)пластина_ГОСТ19903.rfa` (face-based, Соединения несущих конструкций / Пластины, b/h/t, 8 types -150x100x8…-400x400x20, instance КМ_Масса formula), built by `_Стандарт_КЖ\скрипттер\fam_02_plate.cs` (run with `скрипттер\run_cs.ps1 -File … -Log …`). Flex ALL PASS. The template schedule «КМ Спецификация металлопроката» is Каркас несущий only, so plates got their own: «КМ Спецификация пластин» in БК_КМ.rte (user chose «Бөлек спецификация» 31.10.2026), built by `скрипттер\sch_02_plates.cs`. It is grouped by type, with columns Марка | Размеры | ГОСТ | Сталь | Кол-во | Масса 1 шт (type shared КМ_Масса_шт, added because the API cannot create calculated fields) | Масса общ. (КМ_Масса totals). The plate family is loaded into the template. The look of the schedule has not been approved yet, so there is no ЕРЕЖЕЛЕР line. More API lessons in [[revit2025-plugins-families]].
