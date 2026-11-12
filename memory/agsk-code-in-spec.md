---
name: agsk-code-in-spec
description: Every material row in a spec table must carry its АГСК-3 code in parentheses after the ГОСТ (rebar and concrete too)
metadata:
  type: feedback
---

12.11.2026 (Обезвоживание КЖ) user: «толықтай барлық материалда агск код болуы міндетті. Госттың жанына жақша ашып жазып шығасың толық» — in the «Обозначение» column write `ГОСТ 34028-2016 (214-210-0502)`; concrete rows `ГОСТ 7473-2010 (212-101-09xx)`.

**Why:** the user requires AGSK codes on all materials in the specification; he gave АГСК-3 PDF (`C:\Users\Admin\Downloads\agsk-3.pdf`) as the source (АГСК-1 is only the list of norms).
**How to apply:** every KЖ/КМ spec, all projects. Codes are 3-part from АГСК-3 (text dump `D:\_claude_work\obez_chk\agsk3.txt`); never invent the 4th part; if a material is not found — ask. Common codes and the check script are in Obsidian `09_Таблицы\АГСК коды спецификацияда…` and `ЕРЕЖЕЛЕР.md`. Related: [[km-spec-rules]], [[no-repeat-check-pipeline]]
