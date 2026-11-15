---
name: lira-keep-user-edits
description: "When the user has edited a LIRA model by hand, build on their saved file; add new parts with «Сборка схем», never regenerate the model over their edits (user rule 16.11.2026)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 9252f8e4-753b-43e2-aae3-c6e03c79625e
  modified: 2026-11-15T20:17:46.253Z
---

The user said on 16.11.2026 (Касымова, LIRA): «Қазір бірнеше өзгеріс жасадым. Оларға тиіспе. Енді осы моделге лестницаны қос». They had deleted 492 slab overhang elements and 38 perimeter beams at −0.100/+4.100 in the open model and saved it.

**Why:** a regenerated model would silently lose the user's manual edits. The text export does not even carry materials.

**How to apply:**
- Find out what they changed by exporting their model to text and diffing it against my last export (`D:\_claude_work\Kasymova\v9\diff_user.py`).
- Then «Сохранить как» a new version from their tab, so their file stays untouched.
- Add the new part with «Сборка схем». If existing elements must be re-meshed, delete only those elements and re-add them with the same loads, materials and E-factor.
- Prove afterwards that every user element and its loads are unchanged (`v9\verify_v9.py`).
- Say in the report what was re-meshed and why.

Related: [[lira-model-by-analog]], [[project-kasymova-hotel]], [[lira-stiffness-order-named]]
