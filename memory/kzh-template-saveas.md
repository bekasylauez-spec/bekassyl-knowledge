---
name: kzh-template-saveas
description: Every КЖ drawing starts as a Save As copy of D:\РАБОЧКА\Шаблон для Кж.dwg and is drawn inside it; the template itself is never edited
metadata:
  node_type: memory
  type: feedback
  originSessionId: c08a0728-aa0c-4dc8-822f-e73b83212ec1
  modified: 2026-10-20T04:42:15.818Z
---

2026-10-20 user: «Мынау шаблон пересохранит етіп осының ішінде сызасың барлық чертежда» (about `D:\РАБОЧКА\Шаблон для Кж.dwg`).

**Why:** the template carries the user's whole КЖ album setup: 2 title pages (TUNAY STROY sample, «_/_-2026-КЖ»), Общие указания, Ведомость чертежей (начало/продолжение/конец), spec tables (vcBlockST1-6-1), sample sheets (схема элементов, разрезы, узлы стыковки, выпуски, плита Пм-2, лестница Л-1), stamp block «крпкер» (scale 1 at 1:100, 0.5 at 1:50), SPDS dimstyles, layers диам8…диам32 / ф8_арм…ф32_арм / Размеры / О_Формат, DIMSCALE 75.

**How to apply:**
- For every new КЖ job: copy the template to the project folder under the job's name (never write into the template; check it is unchanged after), then draw every sheet inside that copy.
- Reuse its title pages, общие указания, ведомость, stamp, frames, layers and styles: edit the texts (object, шифр, sheet names), delete sample sheets that don't apply, copy sample sheets as the base for new ones.
- Rules from [[cad-callouts-spds]] still apply inside it; Obsidian note: `01_Общие правила/Оформление КЖ в AutoCAD — СПДС (утверждённые правила).md`.

First use 2026-10-20: ЖК Альбион → `D:\РАБОЧКА\ЖК Альбион\КЖ ЖК Альбион.dwg` (inputs in `Задание\` АР/ГП/Геология, LIRA `Тип 3 12-04.lir`, analog Онкоцентр folder). Obsidian: `15_Проекты/ЖК Альбион/КЖ — ход работ.md`.
