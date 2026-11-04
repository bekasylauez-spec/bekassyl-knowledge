---
name: fm-dop-copy-analog-objects
description: "Фм доп./разрез листтері — аналогтың өз объектілерін (стержень, шаг размері, СПДС позиция выноскасы, разрез) көшіріп созып/қысқартып жаса; шаг размерлері бір тізбекте"
metadata:
  node_type: memory
  type: feedback
  originSessionId: e166461b-bde0-4f75-9345-660eafbd0735
  modified: 2026-11-04T13:27:44.401Z
---

04.11.2026, ЖК Галакси Фм-1 3.3–3.6. The user crossed out my zone dims: «200x12», «125», «1475», «200x3» sat at different levels, the «125» text was on the axis, the «1475» text was crossed by a line, and the position number «53» was plain text between the bars. Their correct sample: ONE chain on one line, «200x12 | 125 | 1475 | 200x3». Short values go out on a short leader shelf («125», «200x3»), and each text sits right at its own segment.

They said: «Аналогтың арматураларын осында көшіріп созып қысқартып жаса… шагтарын бергенде қате… барлық размерлі тексер, жазу не выноскалар қабаттаспасын, размердің мәні алысқа созылмасын, арматураға арналған барлық выноскаларды СПДС-пен жаса. біздің ережелерге сай». Then: «Разрезді соңғы аналогтан алып жаса».

**Why:** a hand-built style drifts from the analog. Dims on several levels and plain-text position numbers read badly and break СПДС rules.

Later the same day (screenshot ✗/✓): the position callout of a zone = СПДС note whose origin sits ON the comb line — the vertical comb runs from the first to the last bar (oblique ticks on both), extended straight past the zone up to the shelf when the shelf is outside; the shelf starts at the comb line and goes sideways. No 45° diagonal leader («выноскаларды реттеп жаса. Шагтарды да ретте»).

Third sample (✗/✓, «Шаг размерлерді осылай жаса. барлығын. Алысқа кетіп қалмасын»): a spacing value that does not fit («200», «200x5», «400») sits on the OUTER side of the chain at its own segment on a short shelf; colliding neighbours step one column further out. Never shift it along the line or put it on the inner side across bars.

Fourth correction (04.11 19:50, «Шагтарын неге қате жасадың», 3.6 screenshot): zones 51 and 2 had no spacing dim near them, and «200x2»/«200x5» hung on long shelves. Cause: I chained every zone whose bars overlapped ≥30% along their length into one chain, placed past the farthest bar end of the whole group. Zones ending elsewhere got their spacing far away (ext lines run along the bars, so they are invisible).

**How to apply:**
- Clone the analog's bars, dims and СПДС position callouts, then stretch or shorten them. Never draw your own line+text marks.
- Spacing dims of neighbouring zones go in one chain on one line — but only zones whose bar ends on that side are within ~500 of each other; the chain sits 300–500 beyond those ends. Every zone must have its spacing right at its own bar ends. Check this per zone after drawing.
- After drawing, check every dim: no text overlaps another text or line, and no text sits far from its segment.
- Draw sections (разрез) from the analog's section sheet in the same way.

Related: [[dop-zones-only-on-slab]], [[kzh-dim-text-and-shelves]], [[galaxy-kzh-scheme]], [[cad-callouts-spds]]
