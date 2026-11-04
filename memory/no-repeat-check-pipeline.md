---
name: no-repeat-check-pipeline
description: MANDATORY before showing any drawing sheet — the full check pipeline (AutoCAD geomdump + oc.py, no silent skips, zoomed halves of every sheet); fix the whole class of an error, not the one spot
metadata:
  type: feedback
---

On 31.10.2026 the user circled the same kinds of errors again («Мына қателер неге жасалды саған жаңа ғана ескерттім ғой»). The circled errors:
- section marks over bars and dims;
- crowded corner «625» texts;
- callouts on axes.

The user then said: «Неге қайталадың қайталамайтын шешімін тауып оны бекіт», «көрмейтін болайын».

**Why it kept happening:**
1. oc.py silently skipped every SPDS object that ezdxf cannot parse (SPDSSECTION, SPDSNOTEPOSITION — 108 objects were never checked).
2. I fixed only the spot the user pointed at, not the same class of error elsewhere.
3. Callouts were placed before the dims existed.
4. There was no check for text outside the frame, text on the stamp, text on a hatch, or section strokes and shelves crossing lines.

**How to apply (every sheet, every project):**
- Read SPDS geometry from AutoCAD itself, not from proxy graphics: rz.cs `geomdump` explodes it. Take the callout text box from its mask frame — Explode returns the text unmirrored.
- oc.py must report «НЕ ПРОЧИТАНО» and fail if any object is unread.
- Checks: text/text, line/text, shelf/line, section stroke/line, text outside the inner frame, text on the stamp, text on hatch.
- Run `chk.sh` (dxfout + geomdump + oc --geom + plot + look.py), then `tiles.py`, and look at every half of every sheet.
- Show nothing until the result is TOTAL 0.
- Generators place every label by searching for a free spot against everything already drawn:
  - mark() is queued and runs last;
  - dop notes, «200xN», section marks.
- When an error is found, search all sheets for its category, add a check to oc.py, and record the rule.

The vault note is `01_Общие правила/Проверка листа перед показом — автоматическая (oc.py).md`. Tool copies are in `15_Проекты/Резервуар/Инструменты проверки/`.

Related: [[obsidian-first]], [[kzh-dim-text-and-shelves]], [[reservoir-kzh]]

Later on 31.10, the user said «тексермедің», «қателерің неге көп» (you didn't check; why so many errors). They showed the corner «625» text touching the extension lines, then their own sample: short-dim text pulled OUT of the dim line with a leader.

What I had missed:
- I accepted defects I could see as "minor".
- My digit width was wrong: the real ISOCPEUR digit width is 0.85·h, not 0.72.
- The text/text check ignored touches under 8 %.
- I trusted ezdxf positions for moved dimension texts.

**Now:**
- Dims come from AutoCAD geomdump too.
- Any touch is an error.
- Fixed elements are placed first, then everything that searches for a free spot.
- Every sheet is reviewed in 4 quarters at 190 dpi, all 40 images, before reporting.
- Never call a visible defect minor — fix it.