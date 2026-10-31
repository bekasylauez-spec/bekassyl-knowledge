---
name: check-levels-by-element
description: "КЖ тексеру ережесі: отметканы «схемада бар ма» деп емес, әр элементтің ҮСТІ/ТАБАНЫ схема разрезіндегі қай деңгейге тең болуы керек деп тексеру (колонна/қабырға үсті = ригель табаны)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 760c999f-c28c-44e9-ba81-9cb2aa467e81
  modified: 2026-10-30T09:25:31.495Z
---

2026-10-30, БЦ Байтурсынова Блок 2: I reported columns 4.1–4.4 (top −0.100, h 3900) and wall plans 5.5/5.19 (−0.100, 3900/3700) as «схемамен сәйкес», although the scheme section 2.2 shows columns and walls ending at **−0.750** (beam bottom; beam 650 deep, top −0.100). The user caught it: «колоннамен стеналарды тексер, биіктігі −0,750-ге дейін болуы керек… осы қателерді қалай көрмей қалдың».

**Why I missed it:** my check only tested whether each level VALUE on a sheet exists in the scheme's level set ({−4.000, −0.750, −0.100}). −0.100 exists (slab/beam top), so a column drawn to −0.100 passed. I never asked *which element's top* a mark belongs to, and I didn't cross-check the height dim (3900 vs 3250) against the section.

**Second miss, same day:** even after that I read the Block 2 section with Block 1 eyes — took −0.750 as the *beam bottom* (650 beam under a slab at −0.100). The section 2.2 actually dimensions 3250 = 3050 + 200 (slab) with the −0.750 mark ON the slab top and small 400 beams hanging below it: slab top = column top = wall top = beam top = −0.750; the «−0.100» in the plan title is not a structural level. The user had to correct me twice («схеманы неге қарамадың»). → Read the section's own dimension chain (what the 200/400/3250 belong to) before assigning any level to any element; never import the other block's storey model.

**How to apply (every КЖ check):**
1. From the scheme section, build an element table: for each element type the expected TOP and BOTTOM level and the resulting height (column/wall top = beam bottom = beam top − beam depth; beam top = slab top; foundation top/bottom; wall top under beams −0.750 here).
2. For each sheet take the level mark nearest the element's top edge and the vertical height dim, and compare BOTH to the table — a level that merely «exists in the scheme» is not a pass.
3. Compare plan views and sections on the same sheet with each other (5.5 plan said −0.100/3900 while its section said −0.750/3250 — an internal contradiction that a per-sheet diff would have caught).
4. For a one-storey/basement block, columns do not run through the beams: assume the Block 1 «column to slab top» pattern is wrong there until the section proves otherwise.
5. Write the expected table into the report before checking, so the pass/fail is explicit per element.

Related: [[baitursynova-4floor-new]], [[kzh-scheme-karkasa]], [[pdf-from-layouts]]
