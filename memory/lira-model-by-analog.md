---
name: lira-model-by-analog
description: "How LIRA models are rebuilt \"по аналогу\" — generator scripts, RSN/materials steps, notes in КМ Чертеж Claude docs"
metadata:
  node_type: memory
  type: reference
  originSessionId: 62d8a218-7d3b-4f20-a503-ee957c18a98a
  modified: 2026-11-05T08:53:54.433Z
---

Task pattern "аналог етіп ал, тек каркасты өзгерт": geometry from the DWG, everything else (stiffness, loads, seismic, RSN, design variant, materials) identical to the analog .lir.

- Analog text export already sits in `C:\Users\Public\Documents\LIRA SAPR\LIRA SAPR 2024\Data\<task>.txt` (Файл → Создать текстовый файл).
- Generators per object, e.g. `D:\РАБОЧКА\От Рас груп\ЖК Қарасу село Абай\Расчет\gen_rampa.py` / `gen_naves1.py`; materials by `mat_rampa.py` / `mat_naves1.py`.
- Full procedure and GUI gotchas: `D:\РАБОЧКА\КМ Чертеж Claude\docs\lira\rabota-v-programme.md` §9, binary format: `docs\lira\format-lir.md`.
- User rule (2026-10-12): horizontal braces AND struts go on the truss BOTTOM chord; struts at column rows attach to column nodes, middle ones to chord nodes.
- Computer-use app name is " ЛИРА-САПР 2024" (leading space). The user may stop GUI actions; ask before driving LIRA.

Related: [[cad-console-net-workflow]]

Editing an existing .lir without losing РСН/materials/variant (2026-10-21, Рампа):
- Topology changes go through the GUI: PolyFilter (elements tab, «По номерам КЭ», then ✓; first set Выбор → Отметка элементов). Then «Добавить элемент → Разделить на N равных частей» (the ✓ is hidden under the PolyFilter panel until you close it), or Delete. Then Схема → Упаковка схемы, with «неиспользуемые жесткости/материалы» unchecked. Packing renumbers the elements; split bars keep stiffness, loads, materials and condensation.
- Node moves and end reconnections are a binary patch with the file closed. Both node tables: 28 B at 138 and 48 B. Both element tables (0-based node pairs): 38 B right after the nodes, plus a second copy with VARIABLE stride; find it record by record, the uint32 at +10 is the next index (0 on the last record). Verify with Файл → Создать текстовый файл compared to the generator.
- Calc sections must be 5 (Ctrl+A → Схема → Расчетные сечения), otherwise purlin midspan strength and deflection are not checked.

User rule (2026-10-22): «Сен расчет жасағанда Настройкасында нормативная нагрузка деп қой». Before every LIRA calculation I run, set the loads to normative values in the settings («нормативная нагрузка»). The user did not say which menu; find it in LIRA (Настройки / load editor) and confirm it before calculating.

LIRA text gotchas (2026-11-05, АБК):
- No round brackets in load case names (section 39). `(`/`)` break document 0 and section 35 is lost, so the seismic cases get no dynamic parameters.
- Import a .txt via File → Импортировать задачу → Текстовые файлы. The «Открыть» dialog does not list .txt.
- Start LIRA from a script only with `Bin\x64\LiraSapr.exe`. `Bin\LiraSapr.exe` crashes with 0xc0000005.
- No computer-use tools on BEKA-2: drive LIRA with PowerShell (SetCursorPos/mouse_event + SendKeys + CopyFromScreen), script `D:\РАБОЧКА\От Маке\Завод\АБК\Расчет\ui.ps1` (click/keys/screenshot).
- Mass conversion in text = doc 6 rows with kind 4: element field = static case, row value = coefficient, case = seismic case.
- Line load on a plate edge = kind 19, doc-7 row `i j q1 q2` (local node pair). Rect КЭ 41 nodes are in Z order (1-2, 3-4 opposite; 1-3, 2-4).
- «Нормативная нагрузка» rule = Описание схемы (Ctrl+Shift+P) → «Значения нагрузок: нормативные». It is not in the text export. Send the hotkey with keybd_event; SendKeys does not reach it. The РСН dialog only shows this flag (greyed).
- РСН dropdown cells: a mouse click on a list item does not register. Open ▼, press Down (index+1) times, then Enter. For the EN «Вид» order see the АБК Obsidian note.
- User rule (2026-11-05): do NOT model the slab on grade (плита по грунту) in LIRA. Its floor, partition and live loads go to the ground; the ground-floor exterior wall load goes on top of the basement wall.
- ЖБ materials (types/concrete/rebar) transfer between tasks through a *.lmcr file (Ж/Б → Редактировать → save/load icons). Assigning them needs element marking + ✓; plate and bar types are rejected for the wrong element type, so assign per group.
- Before importing a .txt under an existing task name, move the old Work\<task>.ald away, otherwise its РСУ and other leftovers are offered for import.

LIRA traps (2026-11-05 evening, АБК v3):
- RSN does not travel with files: copying `Work\<old>.crsn1` to the new task name does nothing (import deletes it, open ignores it). Enter RSN by hand (EN 1990: Вид by keyboard ▼ + Down×(index+1) + Enter; «Доминирующее» * by mouse; «Добавить» for I…VI).
- The import dialog toggles all «ald - …» items with one checkbox.
- A selection window that starts on the edge of the «Жесткости и материалы» panel resizes the panel. Close the panel before selecting. Vertical bars: the «||» button in the bottom toolbar («Отметка вертикальных стержней»), then a window.
- Results to CSV: Железобетон → Документация → Стандартные таблицы, format CSV → `Work\<task>.DOCS\.INV\tblNN.*.csv`. In «Перемещения» the X;Y;Z columns are displacements in mm and UX;UY;UZ are rotations. Bars: AU1..AU4 corner bars, AS1..AS4 intermediate. Plates: AS1/AS2 X bottom/top, AS3/AS4 Y bottom/top.
- The table window replaces LiraSapr's MainWindowHandle. Close it with WM_CLOSE on that handle.

Column check rule (2026-11-05, АБК v3): never judge column rebar by total ΣAs from LIRA (AU1..4 + AS1..4). LIRA lumps steel into the corners. Check per face (2 corners + middle) or run a fiber N–My–Mz check (`АБК\Расчет\col_check.py`: EC2 5.8.9(4) Bresler, MRd by fiber, RSN forces from «Усилия от РСН» CSV tbl04.22_1, columns N;MX;MY;QZ;MZ;QY in t, t·m). Under one-axis seismic, 12Ø28 in 500×500 failed (η 1.20) although 73.9 > ΣAs 68.
