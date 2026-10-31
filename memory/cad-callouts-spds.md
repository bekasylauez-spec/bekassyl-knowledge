---
name: cad-callouts-spds
description: "КЖ drawings — callouts (выноски) must be made with the user's AutoCAD 2021 СПДС module, rules live in Obsidian vault Bekassyl"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 1ba4a828-8529-416e-b794-9c0aff795b78
  modified: 2026-10-14T16:00:56.674Z
---

Выноски on КЖ drawings must be created with the user's own AutoCAD software (AutoCAD 2021 + СПДС objects), not plain LEADER/MLEADER/text. Design rules (выпуски, нахлёст, накладки, анкеровка) are in Obsidian vault `C:\Users\Admin\Documents\Bekassyl` (02_Фундамент, 06_Стены, 08_Типовые узлы, 09_Таблицы). User writes in Kazakh mixed with Russian terms.

**Why:** user stated on 2026-10-10 "выноскалар менің автокадымдағы софтпен жасалуы міндетті"; vault notes reference СПДС-выноски.
**How to apply:** before drawing rebar starters/details, read the Bekassyl notes; draw callouts via СПДС commands in the running AutoCAD.

Plan style the user approved for выпуски (analog: Онкологический центр "3. Фундамент"): few marks (one per bar form, e.g. Вп-1..3); dims/level marks from СПДС too; chains anchored on axes; one callout "поз / ш.шаг" per spacing zone; when another diameter is added, its callout + spacing go on the opposite face and the diameter change gets its own dim; dimensions must never overlap each other (merge tiny segments, single wall-thickness dim, check by zoomed screenshot).

Template rules the user wants in every job (2026-10-10):
- One callout per bar run between columns; mixed spacing written as "ш.100;200". Long run: a bracket-shaped comb, legs at the run ends, long flat top. Short run: comb lines meet at one point at the shelf start, and the shelf goes off to the side.
- Callout to a bar drawn as a line gets a tick (SPDS Arrow = Oblique). Callout to a cut bar (dot) has no tick, just a line (Arrow = None).
- Every column on the plan gets tie dims to its axes, like 400|400 / 500|500. These are SPDS dims at the sheet scale, with the line about 1.5×737 below and 1.5×496 left of the column at 1:75.
- Every SPDS object (dims, notes, marks) uses the scale of the sheet (format) it sits on. The user set plan 3.1 to a non-standard 1:75 sheet.
- The bar chain along a wall is tied to every axis: "…|450|450|…" at each column. A dim too short for its text gets the text moved out: the left one to the left, the right one to the right, a small gap centred below. Set it with McDimension.TextPosition; a 600 measured as 599.97 must not count as "short". TextPosition is where the text shelf starts, at the leader, and the shelf runs away from the dim's middle. For a neat result: left text tpos = (left end + 20, line − 280), right text tpos = (right end − 20, line − 280), so leaders stay short. The user disliked long diagonal leaders. Rule: if the text fits (dim ≥ about 125·chars + 100 at 1:75, so 500 fits and 450/400 don't), keep it inside next to the dim line. Only text that doesn't fit goes outside with the short leader.
- Wall callout combs between columns: keep the shelf low, about 900 off the wall face at 1:75, so it sits below the Вп column marks. The note must not sit on a column's vertical dim; shift it sideways in short spans.
- Bar spacing must always appear in chain dims: "200х11=2200". If that doesn't fit, use the short form "200х5". If even that doesn't fit, keep the full text but move it outside the chain with a leader. Never leave only the bare length.
- Axis bubbles sit outside all dim chains with a clear gap, in this order outward: bar chain, then axis-to-axis chain, then overall chain, then bubbles. If the chains run into the bubbles, move the axis ends (McAxisSpecificLinear.setPoints) and the axis-dim lines.
- After automating the live AutoCAD (NETLOAD needs FILEDIA 0 and SECURELOAD 0), ALWAYS restore FILEDIA 1, CMDDIA 1 and SECURELOAD 1 before handing back. On 2026-10-10 the user hit Save As prompting in the command line instead of a dialog because of this. SECURELOAD can't be set via COM SetVariable; use SendCommand "_SECURELOAD 1".
- "Use the SPDS dimension" means: let SPDS place the text itself (default text position, no manual TextPosition) wherever that already looks clean. Only pull text aside (to the left) when it would overlap something.
- Vertical column dims go on the RIGHT of the column by default (user's sample), with the line about 1200 off the face at 1:75. If the right side is busy (callout combs on a wall row, a wall running off the right face), put them on the left. Never leave two dims on the same points; check for duplicates after each run.
- The user edits the live drawing between my runs, for example moving the whole plan or moving dim lines. Before regenerating, re-read the positions (columns, chains) and adopt the moves rather than overwriting them.
- On sections and elevations, level marks and dim chains sit outside the footing outline at its edge, never inside it.
- 2026-10-14, porch/ramp (Склад Рикаус): the callout is the position only, like "4 / ш.200", "Ск1 / ш.200", "Шп1 / ш.п.400х400". Never write "4(Ф12A500C)". Wall horizontal bars sit outside the verticals. Take the position numbers from the user's own latest sheet of the same object type, and re-read it each time because they renumber. As of 2026-10-14 evening (ramp spec): 1 = slab transverse (plus wall horizontals of the same length), 2 = slab longitudinal, 3 = wall horizontals, 4 = wall verticals, 5 = front-wall verticals, then Ск1, Ф1, Шп1. Шп1 is drawn as the user's dynamic block (clone their insert, from dot to dot), not a polyline.
- Rebar drawing style («стилін айнытпай»): copy the user's own entities rather than drawing look-alikes.
  - Bar dots: block A$C76f4a3b3 at scale 0.25 on layer Размеры, at any sheet scale. No circles.
  - Bars: диам12 polylines.
  - Slab edge Ск1: green (color 3), legs 400, back 20 from the face.
  - Wall cap: a narrow U inside the verticals, legs at 64/136.
  - Ф1: their диам8 outline plus an ANSI32 hatch (deep-clone both together).
  - Offsets: wall verticals at 52/148, horizontal dots at 40/160. In the slab, the bottom line is at 52 with dots at 40, the top line at 28 with dots at 40.
- Callout text (2026-10-14, Склад Рикаус пандус): first line = position mark only («4», «Ск1», «Шп1»), second line = spacing («ш.200», «ш.п.400х400»). No diameter/class in the callout; that lives in the spec.
