---
name: column-sheet-scale50
description: Колонна парағы — фасад М1:50 (геометрия ×2, dimlfac 0.5), разрез белгілері колоннаның жанында, тізбекті кеспейді; модель өлшемдері өзгермейді
metadata:
  type: feedback
---

05.11.2026, ЖК Галакси Км-1 (лист 4.1). I first drew the column elevation at 1:100 like the Онкоцентр analog. The user: «Колоннаны сызғанда масштабы 50 мен сыз. Сосын модел өзгермесін. разрездің белгілерін дұрыстап қой».

**Why:** at 1:100 a 500 column is 5 mm wide — hoop zones, bars and callouts are unreadable; the section marks I moved stood far apart across the dim chains.

**How to apply:**
- Column elevation at М1:50 on the 1:100 sheet: geometry ×2 about the column base point, dims dimlfac 0.5 so they show real sizes; texts, СПДС callouts, level marks stay at sheet size. Sections 1:25 (×4, lfac 0.25).
- «Модел өзгермесін»: real sizes never change (only drawing scale); the LIRA model is not edited/saved — I only export tables.
- Section marks: strokes right next to the column on both sides, between the column and the dim chains, at a y with no extension lines; the top section mark above the column top.
- Rebuild generator: `15_Проекты/ЖК Галакси/Инструменты/gen_col50.py`.

Related: [[galaxy-kzh-scheme]], [[kzh-dim-text-and-shelves]], [[no-repeat-check-pipeline]]
