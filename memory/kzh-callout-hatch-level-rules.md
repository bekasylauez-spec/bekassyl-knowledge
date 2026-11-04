---
name: kzh-callout-hatch-level-rules
description: "Bekassyl 31.10 «барлығы ереже» — выноска полкасы стрелкаға қарсы, стрелка элемент қырына, 300–600 мм ортаға қарай; бетон штрихы ANSI36 20; отметкалар қабаттаспайды"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 22eb71ac-88c3-4c99-9c61-2c7547468f19
  modified: 2026-10-31T13:45:05.939Z
---

2026-10-31 (Резервуар КЖ) the user corrected my sheets and said «барлығы ереже» (all of these are rules):
- Callout text/shelf on the side OPPOSITE the arrow. SPDS McNotePosition: `Angle = π` puts the shelf to the left, `0` to the right; `Align` only moves text on the shelf.
- The arrow touches the element's EDGE (the face toward the drawing centre), never the middle of the element or its hatch.
- Shelf start is 300–600 mm from the element (standard ~300–400; never closer than 300 or further than 600), with a 45° leader, and callouts are gathered toward the centre of the scheme.
- Main element outlines 0.30 mm; hatches, dims, thin and hidden lines 0.05 mm. Set the hatch lineweight explicitly.
- Concrete hatch as in the template («пож резервуар» sample): ANSI36, scale 20 on both 1:100 and 1:50 sheets, layer «Размеры», 0.05 mm.
- Level marks must not overlap: turn the lower of two close marks downward (sp_set [1] below the level), or move it to the other side of the section (sp_set [2]/[1] to the right).

- Short dims (text does not fit): put the text BESIDE the dim line on its outer side (away from the element), near the segment end, tied by the dim leader. Never continue the text along the line past the extension line. If the next chain sits there, drop the short end segment (bind to a farther axis).

- Sheets in model space sit edge to edge (frame touching frame, same bottom line). A scheme sheet carries its element spec (template table 11BF4 style: group rows + Поз. | лист | Наименование | Кол.) and numbered notes (template MText 11E6D style; use a real tab, not "^I", via the API) at the right, above the stamp.

- Text clearance (user sample «См-1», 31.10): element edge to top of text 400 mm (4 mm at 1:100); a callout BELOW the element has its shelf 400 + 400 (text band) = 800 below the edge.
- Always draw the foundation contour on the scheme («Фундамент контуры қайда»); chains and overall size from the slab edge.

- Sheet notes sit right on top of the stamp (bottom-left anchor at stamp top + 250, stamp width), not up under the spec table.
- Show the concrete preparation (подбетонка): thin contour 100 outside the slab on the foundation scheme, AR-CONC plus a callout «Бетонная подготовка / C8/10 t=100» in sections.

- Slab scheme: elements under the slab (walls, columns, beams/rigels) are ONE hidden outline (union of their rectangles, e.g. shapely unary_union). Beams stop at column faces, no line runs through a column or is drawn twice, and segments on the slab edge are skipped.

- The outer (overall) dimension runs between the extreme AXES, not over the element. The element size comes from the binding chain.
- A dimension between every pair of neighbouring level marks: the section's vertical chain passes through every mark. Local features (pit) get their own marks plus dims.

**Why:** the user checks every callout and mark visually; crossed leaders, far shelves and overlapping marks get rejected.

**How to apply:** in generators, compute the callout from the element rect: target on the face toward the centre, origin = target ± (400, 400) toward the centre, angle chosen by target side (see gen1.py `mark()` in session 22eb71ac). Render a PDF and zoom in to check before reporting. Vault: `01_Общие правила/Оформление КЖ … СПДС (утверждённые правила).md`, last section.

Related: [[km-callout-style]], [[check-callouts-honestly]], [[reservoir-kzh]], [[drawing-spacing-hatch-rules]]
