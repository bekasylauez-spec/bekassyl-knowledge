---
name: column-rules-template
description: Колонна КЖ — өз шаблоны «Колонна Км-1» (Шаблон для Кж.dwg), хомут 50…50 аралығын 4-ке бөлу (100|200|100, қалдық 200 ішінде), әр қабатта накладкамен стык, барлық негізгі Ø бірдей, разрез выноскасы засечкасыз
metadata:
  type: feedback
---

05.11.2026, ЖК Галакси Км-1. I drew the column from the Онкоцентр analog with my own hoop step (one «150» at the zone change), continuous bars without splices, oblique ticks on bar sections and cramped «40» dims. The user marked it wrong and gave the rules below, then added: «БАРЛЫҚ ОСНОВНОЙ АРМАТУРА СЕЧЕНИЕСІН БІРДЕЙ ҚЫЛУҒА ТЫРЫС. КОЛОННА МЕН РИГЕЛГЕ ҚАТЫСТЫ».

**Why:** the user's own template sheet already shows how a column must look; I did not look for it.

**How to apply:**
- Analog for a column sheet = `D:\РАБОЧКА\Шаблон для Кж.dwg`, sheet «Колонна Км-1» (frame 1:50 at x 264717…294417, y 271898…292898). Import it whole, then edit. Hoops/S-pins = its dynamic blocks «Хомут_динамический2» / «Шпилька_динамическая2». Square hoop: Расстояние1 = width, Расстояние2 = height (outer = R + ~96 after scaling); the 45° hoop scales with the bar spacing.
- Hoops per storey: from lower level +50 to beam bottom −50, split in 4 → end quarters step 100, middle step 200; the leftover (100…200) goes inside the 200 zone. No hoops inside the beam height (meshes there). Script `colgeo.py`.
- Main bars break every storey, joined with накладки (С21-Рн, 10d), staggered: corners +600, mids +1200 above the slab; выпуски from Фм dashed.
- Main-bar Ø (user, 05.11, «Основнойды неге 32 жасадың»): take the column's MAX total required area over all its sections from LIRA (AU1…AU4 + AS1…AS4), divide by the number of bars, choose the Ø whose area covers that per-bar value. Not the corner AU alone. Then try to keep one Ø for all columns/beams. ЖК Галакси: Км-1 27.32/8 → 8Ø22; Км-2.1 37.40/8 → Ø25; Км-2.2 57.04/12 → Ø25; Км-2.3 93.96/20 → Ø25. Script `arm/col_tot.py`.
- Every rebar line sits on its own diameter layer (hoops Ø8 → «диам8», lw 0.30; mains «диамNN» 0.40) — never on «Размеры» (05.11: «Хамуттарды 8 дік арматурамен жаса, толщина сызық аты 8 дікке ауыстыр размерден»).
- In sections the position callout leader goes straight to the bar centre — no oblique tick. Section dims 40 | 210 | 210 | 40 + 250 | 250; short «40» outside along the line, clear of the ticks.
- Spec tables: re-import the template's tables and change only input cells (Ø, L, qty) by text — editing formula cells makes AutoCAD drop neighbouring formulas.

Related: [[column-sheet-scale50]], [[galaxy-kzh-scheme]], [[kzh-template-saveas]], [[rebars-never-overlap]]

**12.11.2026 (пайдаланушы):** колонна мен ригель парағы әрдайым шаблон бойынша (шаблон Онкологиядан алынған); колонна–ригель қиылысында әрдайым сетка, сейсмикада да — тұйық хомут қосылмайды.
