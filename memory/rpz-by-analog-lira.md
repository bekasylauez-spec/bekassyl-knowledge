---
name: rpz-by-analog-lira
description: "РПЗ по аналогу из .lir: модель как есть, без лишних разделов, сечения не трогать; как получить мозаики и CSV из своей копии ЛИРА"
metadata:
  node_type: memory
  type: feedback
  originSessionId: ea178d5e-07d7-4142-8ad3-70e9f550abc0
  modified: 2026-11-05T13:01:39.660Z
---

User rules for an РПЗ written from an analog PDF plus a .lir (Ангар 04, 2026-10-19):
- «Қалай тұр солай жаса, артық сейсмика қоспа»: write the РПЗ from the model **as it is**. Leave out the analog's sections the model does not have (seismic, foundations, reinforcement). Do not add new load cases.
- «Металл сечениесіне тиіспе»: never change steel sections. Run only «Проверка заданных сечений», with no подбор. Report any failures (in that job: 146.8 % on СГ1) in the text and to the user. Do not fix them silently.

**Why:** the user wants the report to reflect their model, not my redesign.

**How to apply:**
- Work on a copy (`D:\РАБОЧКА\<obj> РПЗ\Расчет\`), opened in my own ЛИРА instance on monitor 2 (X = −2560). Close it with «Нет» (do not save).
- Get the numbers from the CSV (Shift + Выполнить расчет → CSV «Все» + the РСН stage), not from screenshots. Generate the docx with python-docx and export to PDF through Word COM (python win32com; a .ps1 with a Cyrillic path breaks).
- Generator example: `D:\РАБОЧКА\Ангар 04 РПЗ\gen_rpz.py`.

Related: [[lira-model-by-analog]], [[obsidian-log-work]]

User rule (2026-10-22, «Алдын сен жасағанның барлығы қате»): **every figure in an РПЗ must be a LIRA snapshot**, never my own matplotlib drawing.
- Take each snapshot with «Книга отчетов → Снимок окна» (the book's first toolbar button). The files land in `Work\<task>.DOCS\scrNN.png`; insert those into the docx.
- Copy the analog's set and style:
  - load mosaics (the «Мозаика нагрузок» dialog, by length, Z(G));
  - 3D view, stiffness mosaic in 3D and in plan;
  - row and frame sections: window-select a band in plan, «Вид → Фрагментация», then XOZ/YOZ projection;
  - steel materials mosaic;
  - Металл tab 1ПС/2ПС/МУ/Defl;
  - Анализ: «Исходная схема», then RSN mode with the governing IV combo, X/Y/Z mosaics;
  - seismic X/Y on the dominant mode component.
- To get the same angle back, right-click a book item → «Вернуться к виду».
- Switch load cases or РСН by scrolling the mouse wheel over the bottom combobox; clicks on its list do not register.
- Generators: scratchpad `rpz3/` (Рампа 02) and `rpz_lk3/` (ЛК 1). These are patched copies of `rpz2` and `rpz_lk` with SNAP paths.
- «Признак схемы» → «нормативные» was already set in both models.

ЖБ РПЗ (АБК, 2026-11-05; generator `\\192.168.0.107\рабочка\От Маке\Завод\АБК\Расчет\РПЗ_генератор\gen_rpz.py`):
- The analog .docx is the template. Keep its generic norm inserts by element index (Ж.1–Ж.3, 7.29–7.31, п. 8.4, the ArmaDA module description). Delete everything else. Drop image rels that are no longer referenced, so no analog pictures stay in the package.
- Where the CSV files land: `Work\<task>.DOCS\AUTORES\tbl*.csv`.
  - 07.11 holds inertia forces; 08.17 holds mass weights; 05.9_1 holds periods.
  - The protocol is `Work\<task>_01.<task>` (UTF-8).
- Проверка xlsx: build it with the analog's formulas. Evaluate the formulas with the `formulas` package. BEKA-2 has no Word or Excel, so the docx cannot be exported to PDF there.
- Bottom-toolbar gotchas:
  - «Предыдущий фрагмент» is not the same as «Восстановление конструкции». After an empty fragment the view stays blank until you press «Восстановление».
  - Beam reinforcement mosaics show only in «Несимметрия» mode; column mosaics only in «Симметрия». In the wrong mode the mosaic is empty.
  - Mosaics for bars hidden under plates are invisible. Isolate the bars first: Жесткости dialog → select the type → eye button.
- Report failed checks honestly: in АБК, drift Y and θ failed and were stated in the conclusion, with no silent model change.
