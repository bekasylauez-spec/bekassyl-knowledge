---
name: kzh-scheme-karkasa
description: "КЖ Схема каркаса: user's required order (study Онкоцентр analog first, AR vs LIRA overlay, sheet per slab level + sections), checklist file per object"
metadata:
  type: feedback
---

2026-10-20 (ЖК Альбион) user: «артық заттың барлығын өшір. схема каркасты архитектурамен лираны салыстыра сызасың. Поный оформление. Онкология қалай жасалған соны бірінші қара, сол ретпен кел. Схема каркаста плитасына байланысты өзгеретін жерлері бар, типовой бар, олардың разрездері бар». Then: finish Схема каркаса fully before фундамент; keep a separate checklist of check conditions that the user edits.

**Why:** my first 2.1/2.2 (walls only, Байтурсынова style) were too thin; the user's reference is Онкоцентр «2. Схема каркаса» (copy in `D:\РАБОЧКА\ЖК Альбион\Онкологический центр блок 1 секция 1\`).

**How to apply:**
- Order: study the analog → delete template leftovers → overlay AR vs LIRA per level, ask which governs (Albion: basement = LIRA, typical = AR dims) → sheets: top of foundation, every distinct slab level (identical levels grouped «+…...+…»), roof; then Разрез with SPDS level marks.
- Each sheet: SPDS axes, chains, binding of every element (125|125, free ends, openings, slab holes, cantilevers), SPDS marks with arrow leader, per-sheet spec table, section marks.
- SPDS sources from Онкоцентр: axes 377C29/377EB8, section 37FBB9 (2 stretch points), level marks 37F9D3 (6-char value) / 37FB82 (7-char) changed by same-length byte replace.
- Nothing overlaps (user 2026-10-20 «выноска размерлермен, разрездер қабаттасып жатыр … тексер толық чертежды жеке-жеке»): notes placed after all dims; section marks outside the contour and outside chains; every sheet checked separately by geometry from the DWG (proxy graphics + dim virtual entities: text/text, line through text, note/section lines vs dims) and visually by PDF crops. Model AutoCAD moved-text: centre = tpos + (0, 0.225) rot0 / (−0.225, 0) rot90, drift ≤0.22 along the dim; dims ≤700 move their text.
- Openings as Онкоцентр (user: «отверстияда белгісі болсын, штрихтар болмайды»): wall hatch interrupted; symbol = rectangle across the wall + break line (0,0)→(0.27t, L−0.3t)→(t,L); extension lines of opening chains reach the wall, not the slab outline.
- Slab contour from AR, not LIRA (user 2026-10-20 «плитаның контурына қатты мән бер. Архитектурадан ал»): outer face of loggia masonry / walls / parapet per level (AR blocks «Кладка_…», «Фасад_…», roof «Кровля» inner line + parapet); LIRA mesh edges sit on axes.
- Small dim text on the same side as the chain's texts (user sketch «325»), in the text row or one row out on a shelf.
- Walls are divided into ELEMENTS and marked by TYPE, a note on every element (user 2026-10-21 «Стеналардың бөлінуін неге жасамадың»; analog «D:\РАБОЧКА\ЖК Альбион\ЖК Альбион ТИП 1.pdf» = same complex, same company — the primary analog for Albion КЖ). Pieces of a line join only across openings; identical pylons share one mark.
- Albion sheets per Тип 1 (2026-10-22): 2.1–2.3 on A3 (template frame 1A0B3, stamp −17400, notes bottom-left), rows 0.75, plan auto-placed above the stamp (two generator passes, a3_oy.json); 2.4/2.5 A2. When the user has closed the DWG, work in my own AutoCAD instance (acad.exe file /b boot.scr) and save via job Save after a backup copy; temp files (onk2.dwg) can vanish — re-copy from the Онкоцентр folder.
- Before styling anything, read ALL sheets of the analog (plot each to PDF) — the user asked twice.
- Checklist: `15_Проекты/<obj>/Чек-лист проверки КЖ.md` (A done checks, B assumptions/questions, C next section).

Related: [[kzh-template-saveas]], [[cad-callouts-spds]], [[cad-dedicated-instance]]
