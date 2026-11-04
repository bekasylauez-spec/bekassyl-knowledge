---
name: feedback-km-error-checklist
description: Every КМ defect the user pointed out lives in КМ_ҚАТЕЛЕР_ПРОМПТ.md; audit with km-model-checker / q20_audit before showing; answer in Kazakh; say clearly when everything is done
metadata:
  node_type: memory
  type: feedback
  originSessionId: 72af3b3f-2397-48af-af38-773774531e1c
  modified: 2026-10-29T15:16:19.388Z
---

Before showing any КМ model/3D view, run the km-model-checker agent (C:\Users\beka\.claude\agents\km-model-checker.md), which runs q20_audit.cs (checks C1…C9) — show only on ALL PASS. The list of defects with cause → rule → check is `D:\Бекасыл КЖ КМ\_Стандарт_КЖ\КМ_ҚАТЕЛЕР_ПРОМПТ.md`.

**Why:** 29.10.2026 the user found the same kinds of defects one screenshot at a time (tube inside tube, post under belt corner, open ends, no welds, z-fighting stripes, seam lines) and asked for a checking agent and saved prompts so they never come back. They also asked: «қазақша ответ бер» and «барлық задание біткенде айт».

**How to apply:** a new defect from the user → add it to the prompt file table, ЕРЕЖЕЛЕР.md and a new check in q20_audit.cs. Don't show a model mid-chain (m05 deletes welds until m07/m11/m12 rerun). Reply in Kazakh; at the very end of a task say «Бәрі бітті» with what was done and the audit result. Related: [[project-3602-km-portals]], [[feedback-oformlenie-together]].
