---
name: agsk-code-in-spec
description: Every material row in a spec table must carry its АГСК-3 code in parentheses after the ГОСТ (rebar and concrete too)
metadata:
  type: feedback
---

12.11.2026 (Обезвоживание КЖ) user: «толықтай барлық материалда агск код болуы міндетті. Госттың жанына жақша ашып жазып шығасың толық» — in the «Обозначение» column write `ГОСТ 34028-2016 (214-210-0502)`; concrete rows `ГОСТ 7473-2010 (212-101-09xx)`.

**Why:** the user requires AGSK codes on all materials in the specification; he gave АГСК-3 PDF (`C:\Users\Admin\Downloads\agsk-3.pdf`) as the source (АГСК-1 is only the list of norms).
**How to apply:** every KЖ/КМ spec, all projects. Codes are 3-part from АГСК-3 (text dump `D:\_claude_work\obez_chk\agsk3.txt`); never invent the 4th part; if a material is not found — ask. Common codes and the check script are in Obsidian `09_Таблицы\АГСК коды спецификацияда…` and `ЕРЕЖЕЛЕР.md`. Related: [[km-spec-rules]], [[no-repeat-check-pipeline]]

12.11.2026 (Цех предобработки, BEKA-2): reusable toolset `D:\_claude_work	sekh_agsk` (accoreconsole plugin tb.cs: TDUMPALL/TAPPLY/ATTFIX + build/cmp/verify/plotall/cmp_pdf/deploy); АГСК-3 text on BEKA-2 is `D:\_claude_workbk_agskgsk3.txt`. В30: 1101 plain / 1102 F150 W6 / 1103 F150 W8; В30 F100 W6 does not exist in АГСК-3 — user decided 12.11.2026: use 1101 (без добавок), not the higher F150 W6 code. Also replace leftover 4-part analog codes and check block attributes outside tables. Pitfalls: tset+cpfmt as two ops on one table wipes a formula cell; row-height change needs RecomputeTableBlock(true); run accoreconsole from PowerShell only.
