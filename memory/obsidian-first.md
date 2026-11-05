---
name: obsidian-first
description: МІНДЕТТІ — кез келген жұмысты бастамас бұрын Obsidian (D:\РАБОЧКА\Bekassyl) ережелері мен аналогтарын оқу; барлық чаттарда
metadata:
  node_type: memory
  type: feedback
  originSessionId: 22eb71ac-88c3-4c99-9c61-2c7547468f19
  modified: 2026-10-31T14:54:32.813Z
---

On 2026-10-31 (Резервуар КЖ) I designed the Фм-1 reinforcement without opening the vault. The user asked «обсидианға неге қарамадың» and then said: «Ереже кез келген жұмыста обсидианнан қарауға міндеттісің алдағы чаттарда да».

**Why:** the vault already held the rules I broke:
- `02_Фундамент/Фундаментная плита.md`: base Ø by thickness (300–400 → Ø14), dop bars between base bars at one level, a zone needs ≥4 cells, As_avg of two cells, ≥70% → raise base Ø, Ф-1 with 300 legs, П-скоба H−80 with legs Ø12 700 / Ø14 800 / Ø16 1000.
- The Онкоцентр analog `15_Проекты/Онкологический центр Блок 1 Секция 1/03 Фундамент и выпуски.md` plus its source PDFs, with this sheet order:
  - 3.1 опалубка;
  - 3.2 основная арматура;
  - 3.3–3.6 доп. by face × axis family, each zone drawn as its first and last bar with «200xN»;
  - 3.7 поперечная;
  - 3.8 спецификация.

**How to apply:** before ANY task (КЖ, КМ, LIRA, РПЗ, Revit, anything), grep the vault (`D:\РАБОЧКА\Bekassyl`) for the element/topic and the project. Read:
- `01_Общие правила`;
- the topic folder (02_Фундамент … 09_Таблицы, 16_КМ чертежи);
- `14_Мои правила`;
- `15_Проекты/<object>`;
- the analog listed there, including its PDFs/images.

Do this before designing or drawing. State briefly which notes you used. Vault rules override my defaults, and the latest user decision wins.

Same day, user: «листтердің санында аналогтан қара не сызар болсаң аналогты оқы сосын жаса кез келген жұмыста». So sheet numbering, composition and graphics come from the analog: read the analog's sheets (PDF) BEFORE drawing anything. Онкоцентр numbering is section.sheet:
- 1.x общие;
- 2.x схема каркаса;
- 3.x фундамент (3.1 опалубка, 3.2 основная, 3.3–3.6 доп., 3.7 поперечная, 3.8 спецификация, 3.9–3.10 выпуски);
- 4.x колонны, 5.x стены, 6.x ригели, 7.x плиты, 8.x парапеты/лестница.

On 2026-10-31 the user also said «мен саған айтқанның барлығы ереже» (everything I tell you is a rule), and repeated «отметкалардың барлығында размер болуы керек ереже». So every correction and preference the user gives is a GENERAL rule for all future work, not a one-off fix. Record each one immediately in the vault (`01_Общие правила/Оформление КЖ в AutoCAD — СПДС (утверждённые правила).md`, or the topic note) and in memory. Then apply it to everything already drawn in the current job.

One more rule from the same day: **one scale per sheet**. Every annotation on a sheet (texts, notes, level marks, dims, titles) uses the sheet scale (100 → 100, 75 → 75). Never put an enlarged detail on a sheet of another scale; give it its own sheet at its scale, and don't write «М 1:xx» in the titles.

Repeated mistakes on 31.10 came from never opening `01_Общие правила/Чек-лист проверки КЖ — Схема каркаса.md` (41 numbered checks: №21 scale, №28/30 dim rows 1000/1000, №31 extension lines touch, №32 no overlaps, №35 small dim text…). Before showing ANY sheet, go through the project checklist section «0. ПЕРЕД ПОКАЗОМ» (`15_Проекты/<obj>/Чек-лист проверки КЖ.md`) and run oc.py (overlaps = 0).

On 31.10 the user also asked me to re-read the analog PDFs "every line, every dimension, every point", sheet by sheet, and write it all to the vault. The full measured breakdown is in `11_Аналоги и фото/Онкоцентр КЖ — графика и размеры (полный разбор).md` (fragments in the `Онкоцентр КЖ — фрагменты/` folder) and in the rewritten `02_Фундамент/Оформление листов Фм по аналогу (Онкоцентр 3.x).md`.

Key measured facts:
- axis bubble Ø7 mm;
- text 2.5 mm, titles 3.0–3.5 mm;
- rebar 0.4 mm; scheme outlines 0.5 mm; slab contour on the formwork sheet 0.7 mm;
- short-dim text on a shelf;
- every column bound to the axes with its own chain;
- armirovanie sections are not hatched.

For a new analog, do the same depth of reading: render each sheet, view zoomed tiles, and measure from the PDF vectors.

**Path on both PCs:** `D:\РАБОЧКА\Bekassyl` (on BEKA-2 `D:\РАБОЧКА` is a link to `\\BEKA-1\РАБОЧКА`), see [[shared-memory-two-pcs]]. BEKA-2 also repeated this rule on 04.11.2026 («обсидианнан қара»).

**Key notes:**
- `16_КМ чертежи\02_Оформление\Стиль альбома КМ — по лестнице ЛК (Қарасу).md` — КМ album style: SPDS objects (SPDSNOTEPOSITION marks, SPDSNOTEKNOT nodes, SPDSSECTION, SPDSLEVELMARK, SPDSWELD, SPDSBREAK), «СПДС» dim style, ISOCPEUR, axes ACAD_ISO03W100.
- `01_Общие правила\Оформление КЖ в AutoCAD — СПДС (утверждённые правила).md`, `14_Мои правила\Работа и оформление.md`.
- Project notes in `15_Проекты\<object>\`; В109 = `Завод УВПиОС В109 (Шерхан)\КМ В109 — сборка в один DWG и сверка с ТХ.md` (another agent's live-AutoCAD history: cranes, ТХ, expert remarks).
- Also GitHub `bekasylauez-spec/bekassyl-knowledge` (public fork) and `idea-statica-notes`.

Related: [[obsidian-log-work]], [[kzh-scheme-karkasa]], [[reservoir-kzh]]


**05.11.2026 (Аэротенк) — негізгі ереже, қатаңдатылды.** Мен колонна мен ригельді шаблонды (`Шаблон для Кж.dwg` «Колонна Км-1», «Ригель Рм-1» парақтары) және Obsidian ережелерін (03_Колонны, 04_Ригели, позиция ережелері) қарамай өзімше сыздым, Фм-ге КР-1 каркас қостым. Пайдаланушы: «СЕН ОБСИДИАННАН ҚАЛАЙ ЖАСАЛУЫН ЖАТТАП ОҚЫП ШЫҚ. Қателер өте көп», «Позициялардың ережесін обсидианнан қара. Негізгі ереже ет. соларды көрмеден ешқандай жұмыс жасамасын».
**How to apply (MANDATORY):** before drawing ANY element: (1) open its Obsidian topic note + `01_Общие правила/Оформление КЖ…` §2 позиции + `02_Фундамент/Оформление листов Фм…` «Правила позиций»; (2) find the user's own template sheet for that element in `Шаблон для Кж.dwg` (also present in every КЖ copy, template row y≈271898) and BUILD FROM IT (copywin → edit); (3) only then draw. Positions: main slab rebar = one pos «1»; доп. numbered by unique Ø+L, sequential across Фм in sheet order 3.3 низ букв. → 3.4 верх букв. → 3.5 низ цифр. → 3.6 верх цифр.; same Ø+L top/bottom = same pos; скобы/фиксаторы/каркасы = letter marks; callout = mark + step only (no Ø). Аэротенк: Фм-1 main Ø16, no КР-1 inside (user 05.11).

**05.11 (ригель):** Ригель sheet = the template «Ригель Рм-1» copied and stretched/shortened; never redraw elevation/section in own style (user: «Ригель осы стилде айнымасын. Сызғандарыңды өшір де осыны пайдалан»). Section: template combs «1(ФN)», «Х1(Ф8) ш.100;200», dims 30/420/50, 200/300, 50|100|100|50, 150|150, hoop = template dynamic block.
