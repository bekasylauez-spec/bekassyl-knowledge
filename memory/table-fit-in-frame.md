---
name: table-fit-in-frame
description: "КЖ кестесіне жол қосқаннан (insRows) кейін кестенің төменгі шегі рамка/штамп сызығынан шықпайтынын бірден тексеру; парақ сілтемелерін марка↔парақ кестесімен салыстыру"
metadata:
  type: feedback
---

2026-10-30, БЦ Байтурсынова Блок 2, схема 2.2: I added 5 rows (Км-2…4, См-4, См-5) to the spec table 5D664A and never checked its new bottom edge. The table grew 3.2 m (1:100) and ran 2.7 m below the sheet frame; the user caught it on the PDF («схеманы ретте, қате бар»). In the same table I had written «лист 6.2/6.3/6.4» in Рм-2/3/4 order, although the rigel file's sheets are 6.2 = Рм-3, 6.3 = Рм-4, 6.4 = Рм-2.

**Why:** insRows changes geometry, not just text; my verification compared only cell texts (tables.txt) and the PDF regex, neither of which sees the frame boundary. Sheet references were filled «by order» instead of from the actual mark↔sheet map.

**How to apply:**
1. After any insRows/row-height change: TDUMP `pos.y − h` must be ≥ frame `y0 + 500` (and above the stamp block); else `move{h,dy}` up (keep ≥ 5 mm paper gap to the drawing above — measure the lowest entity with ezdxf bbox) or reduce row heights.
2. Render the sheet (fitz pixmap) and look at the table bottom vs the frame, not only at text.
3. Every «лист N» reference comes from an explicit mark→sheet table built from the target file's stamps (e.g. rigel 6.1 Рм-1, 6.2 Рм-3, 6.3 Рм-4, 6.4 Рм-2), never from the row order.

Related: [[baitursynova-4floor-new]], [[check-levels-by-element]], [[cad-clone-analog-stretch]]
