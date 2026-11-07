---
name: project-tsekh-predobrabotki
description: Цех предобработки (Станция очистки, Маке) КЖ — аналог Онкоцентр (бөлім-бөлім DWG), конструктивно: Фм/плита ш.100 доп жоқ, Км/Рм Ø28, Шп; 07.11 бөлім 2 дайын
metadata:
  type: project
---

07.11.2026 user: «Цех пере оброботки КЖ-сын сыз, арматура мейлінше көп, конструктивно; расчеттан тек сечение; фундамент и плитада шаг 100 доп жоқ; колонна и ригелге Ø28; ригель боковой арматурасы болса шпилька, шагы хомуттыкындей». Сосын: «АНАЛОГ ОНКОЛОГИЯНЫ АЛ».
**Why:** user wants Онкоцентр album style (separate DWG per section like `D:\РАБОЧКА\ЖК Альбион\Онкологический центр блок 1 секция 1\*.dwg`), not Аэротенк/Обезвоживание.
**How to apply:** work dir `D:\_claude_work\tsekh` (tools = Обезвоживание toolset retargeted: acadjob_ts, ts_ops/ts_log/ts_map, guard = files under D:\_claude_work\tsekh\). Element model `tsdata.py` (ЛИРА `lir\ceh.lir`: stiffness array @5481130; ФП t600 top −4.000/−3.000, walls t400 См-1…11, slabs t200 Пм-1…5 at 0/+2/+3.2/+5.65/+11.2, Км-1…6, 68 beams → Рм-1…49). Each section DWG = copy of the Онкоцентр section DWG in `out\`, objects imported from the Онкоцентр file and cloned; stamp «крпкер» replaced by Аэротенк «Штамп_АБК» (`stamp.py`). Section 2: `sch.py` (2.1–2.6, auto mark/binding placer), `sec27.py` (разрез 1-1 y=7500; level marks need levelval same length, 7-char from imported mark). Final copy always AUDIT (accoreconsole via PowerShell — git-bash mangles /i). Proxy dialog on open: PostMessage IDOK.
Sheet refs: Фм-1 3.1, Км-k 4.k, См-k 5.(3k-2), Рм-k 6.k, Пм-k 7.(3k-2), Л-1 9.1.
Status 07.11: section 2 (7 sheets) and section 3 (3.1 опалубка, 3.2 арматура Ø28 ш.100, 3.3 спец ≈195.8 т, 3.4 выпуски Вп-1…3 + стены Ø16, 3.5 спец выпусков) in project folder. Scripts gen31…gen35, fmdata.py, coldata.py, secbase.py, finalize.py (save→AUDIT→PDF→copy). Analog sheets 3.3–3.7 deleted, layouts renamed. Section 4 (4.1–4.6 Км-1…6, gen4.py, coldata.STOREYS) done 07.11. Next: 5 Стены, 6 Ригели, 7 Плиты, 9 Лестница, 1 ОД.
Related: [[project-obezvozhivanie-make]], [[project-aerotank-make]], [[rigel-pins-hoop-steps]], [[rebar-sizes-28-12-16]]
