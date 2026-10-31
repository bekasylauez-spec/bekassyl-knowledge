---
name: tsekh-fakhverk
description: "ЦЕХ (Алматинский завод гиг. изделий) КМ Блок 1/2: sandwich-panel фахверк sheets, Ст2/Ст3 naming, what was added 2026-10-21, open questions"
metadata:
  node_type: memory
  type: project
  originSessionId: 2abe8c86-5fbf-456a-968e-eb031cf7adca
  modified: 2026-10-21T14:31:34.269Z
---

Folder «D:\РАБОЧКА\От Асқар аға\КЖ и КМ Чертеж» (КМ Чертеж ЦЕХ Блок 1.dwg, «…Блок 2  вариант 2.dwg» — two spaces). AR task in «…\Задание\DWG» (листы 4–7, 17.08.2026). Analogs: «H:\От Дастанкотелный\100гкал\…\КМ Чертеж Блок 1–4.dwg» (фахверк sheets: Блок 1 л.21–23, Блок 4 л.5).

2026-10-21, done live in the user's open AutoCAD, NOT saved:
- Block 1: user's sheets 15 (оси А/Е) and 16 (ось 1). User decision: window posts = Ст2 □80×4, gate posts = Ст3 □120×4, Ст1 stays the end-wall post □140×4. Added sheet 17 (nodes 12/д-д, 13/е-е, ведомость, notes), spec column «Фахверк» (4.10 t), layouts 15–17.
- Block 2: sheets 14 (А, Е), 15 (ось 15 + ведомость), 16 (node 7/д-д); spec filled into the user's existing «Фахверк» column (2.21 t); layouts 14–16 (not plot-verified: full Wblock of Block 2 fails with eExcessiveItemCount, use op wblockwin).
- User decision 2026-10-21: Block 1 sheet 16 keeps 5 windows on the 3600 grid (AR shows 3×2400 on 6000) — do not change.
- Spec tables: the user wants Block 1 «Техническая спецификация» laid out like Block 2 (615A5A): groups Двутавры → Швеллер гнутые (Гн 160х80х5) → Уголки (3 rows) → Профили → Прокат; each group ≥2 rows; № column empty; formulas ((kg*0.001)*(length)), value text height 250. Done 2026-10-21; the plate codes (214-101-…) in Примечания were restored on request.
- Open: Ст1 at Г/В shifted 270 vs plans, Ст3 base not designed. Sheet lists (table 5F8EEB in both files) filled with real sheets 21.10; stamps of sheets 1–3 renamed, Block 2 sheet 13 number fixed, Block 2 node-7 section renamed Л-Л (Д-Д is used on its sheet 12).

**Why:** the user draws фахверк only around openings (panels hang on columns).
**How to apply:** for more blocks of this project reuse the same system and gen_c.py (session 2abe8c86 scratchpad). SPDS level marks here are static text: clone + levelval with the same-length string; table formulas can get wiped after EvaluateFields/recompute — re-write and re-dump.

Related: [[km-copy-user-nodes]], [[cad-dedicated-instance]], [[obsidian-log-work]]

2026-10-21 evening: the user moved my node sheets onto the development sheets themselves (Block 1 nodes 12/13 + ведомость → sheet 16, sheet 17 deleted; Block 2 node 7/Л-Л → sheet 15, sheet 16 deleted) and edited my opening dims to outer window sizes. Don't recreate deleted sheets/layouts — re-read the live drawing first. Albums «КМ Чертеж ЦЕХ Блок 1 (21.10).pdf» / «…Блок 2 (21.10).pdf» were plotted from layouts inside the live AutoCAD (scratchpad net\plt.cs, PublishEngine per layout with its own page setup, numeric layout order), because Wblock of Block 2 fails.
