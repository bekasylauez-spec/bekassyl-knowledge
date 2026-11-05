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
