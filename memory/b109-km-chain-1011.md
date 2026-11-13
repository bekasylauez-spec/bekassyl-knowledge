---
name: b109-km-chain-1011
description: "В109 Цех Блок 1 КМ Revit — chain with the new slot step 13, state on 10.11.2026 evening, open items"
metadata:
  node_type: memory
  type: project
  originSessionId: b9d48af9-f7a2-4623-89d1-541fa9dfc459
  modified: 2026-11-10T11:50:49.224Z
---

В109 КМ model (D:\Бекасыл КЖ КМ\Завод_В109_КМ, scripts _авто\revit): chain is now gen.py → b109_01 → b109_10 → b109_11 → nodes.py (run without -I, it imports gen) → b109_12 → **b109_13_slots.cs** (void «БК_паз_541x12_v3» cuts 16 Р1 slots for the узел 6 through gusset; must run after every 01/11) → b109_90 → q20. Last push a82d0c8 (10.11 ~17:40), clash 0, q20 PASS.

**Why:** user's DWG revision 10.11 10:44 + user decisions: bracing Λ/V by LIRA (rule 52), узел 6 one gusset through Р1, Р1 end 180 off the column axis, узел 7 −t8 ribs, узел 1 разрез 2-2 gusset kept wider (M24 does not fit the 150 band).

**How to apply:** R:\ (\\BEKA-1\рабочка) and D:\РАБОЧКА (shared memory, Obsidian) went offline at ~17:30 — the model copy to R:\…\КМ Чертеж\227-23-П-УВПиОС-ВП-В109-КМ (Цех Блок 1, Revit).rvt and the Obsidian/shared-memory notes for rules 53–55 are still to do when BEKA-1 is back. km-model-checker's bolt sweep counts bolt shanks through plates as "nut in solid" — check the part volume (shank Ø16×L) before trusting it. Next: drawings (sheets) after the user confirms. Related: [[km-user-node-dwg-plot-read]].
