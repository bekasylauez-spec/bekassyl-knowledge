---
name: feedback-match-dwg-exactly
description: "When modelling from the user's DWG, every part's shape, size and length must match the drawing exactly — read each node from model space, never invent a generic detail"
metadata:
  node_type: memory
  type: feedback
  originSessionId: c4f44258-6943-4b10-8e73-e6f1e42efec6
  modified: 2026-10-31T15:15:20.903Z
---

On 31.10.2026, in the Алатау цех КМ model, I first built nodes 1/2 as generic fin/seat details. The user said: «менің двгдағы узелге жақсылап қара. қателерің бар», then «формасы ұзындығы барлығы сәкес келсін».

**Why:** the user is the author of the drawing and checks the model against it. Plausible-but-different details count as errors.

**How to apply:**
- Before modelling any node, render its model-space region (dwg_render2.ps1 on km_geo.txt) and read every section of it, zoomed in.
- Take plate sizes, bolt counts and pitches, member end positions and piece lengths from the drawing's geometry and dimensions. Do not take them from typical practice.
- Where the drawing is unclear, write down the assumption and tell the user. Do not silently simplify.

Related: [[project-alatau-ceh-km]], [[originals-are-dwg]].
