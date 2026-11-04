---
name: dop-zones-only-on-slab
description: Доп. арматура аймағы плита жоқ жерден (атриум, отверстие) өтпейді — плитаның әр бөлігіне жеке аймақ, жеке шаг/ұзындық; выноска аналог MLeader стилінде
metadata:
  type: feedback
---

04.11.2026 (БДМ Блок 4, Пм1 +7.000) the user crossed out my dop zone «5» that spanned from В to Е across the atrium: «плита жоқ жерге доп арматура қойып тастағансың». Their sketch: the same bars split into separate zones per slab piece (above the void, in the Д band, right of the void, below it), each with its own first/last bar, «200xN» and length. «Шагтарын ұзындығын жеке жеке жаз. Выноскалар стилі аналогтан аумасын. Аналогтан соған ұқсайтын сызбаны алып переделка жаса.»

**Why:** a zone rectangle drawn over a void reads as bars in the air; spec lengths are wrong too.

**How to apply:**
- After zoning, clip every bar to the slab (minus cover) and regroup consecutive bars with the same clipped segment into separate zones; never draw a zone envelope across a void/opening.
- Each zone: first + last bar, «200xN» across, its own length dim, its own position mark.
- Position marks = clone of the analog MLeader (text in the middle of the leader, arrows on first/last bar), bars on the analog layer ByLayer — no home-made line+tick labels.
- For any sheet: take the analog's equivalent sheet/elements and rework them, don't invent a style.
- Opalubka of every slab carries its sections (as the analog), not only the reinforcement sheet.

Related: [[obsidian-first]], [[bdm-block4-slabs]], [[km-callout-style]]

04.11.2026 (same job, 2nd correction): «2 түрлі доп арматура 1 жерге түсе алмайды» — two dop zones (different Ø/position) must never share bar positions; the stronger zone keeps the place, the weaker one is cut around it. «Арматура қалыңдығы 0,40 мм, основной/доп арматура сызылған жерлерде плита контурлары 0,05 мм». The user fixed my opening symbols by hand («қазір түзеттім, оларды өшірме») — never erase user edits; copy their style.
