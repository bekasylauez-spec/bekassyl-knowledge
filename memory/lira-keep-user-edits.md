---
name: lira-keep-user-edits
description: "When the user has edited a LIRA model by hand, build on their saved file; add new parts with «Сборка схем», never regenerate over their edits (user rule 16.11.2026); before every calc compare the canonical R: .lir with the local copy (17.11 lesson: stale v9 calculated)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 9252f8e4-753b-43e2-aae3-c6e03c79625e
  modified: 2026-11-18T06:00:46.825Z
---

The user said on 16.11.2026 (Касымова, LIRA): «Қазір бірнеше өзгеріс жасадым. Оларға тиіспе. Енді осы моделге лестницаны қос». They had deleted 492 slab overhang elements and 38 perimeter beams at −0.100/+4.100 in the open model and saved it.

**Why:** a regenerated model would silently lose the user's manual edits. The text export does not even carry materials.

**How to apply:**
- Find out what they changed by exporting their model to text and diffing it against my last export (`D:\_claude_work\Kasymova\v9\diff_user.py`).
- Then «Сохранить как» a new version from their tab, so their file stays untouched.
- Add the new part with «Сборка схем». If existing elements must be re-meshed, delete only those elements and re-add them with the same loads, materials and E-factor.
- Prove afterwards that every user element and its loads are unchanged (`v9\verify_v9.py`).
- Say in the report what was re-meshed and why.

**Check the canonical file before every calc (lesson 17.11.2026).** The user also edits the project's canonical .lir on R: directly (Касымова: `R:\От Маке\Қасымова\Расчет\Kasymova.lir` saved 16.11 22:30 with new beams and a removed wall). I calculated my local v9 copy without checking R:. The result was stale and 3 hours of FESolver + ArmaDA were lost.
- Before starting a calc or building on a local copy, compare the R: file with the local copy: size, time and md5. Also look for LIRA's `*.~lir` / `*_Backup.~lir` beside it: they mean someone opened it in LIRA.
- If they differ, diff them semantically before anything else: the header counts first ([[lira-lir-binary-diff]]), then a text export of both and a doc-by-doc diff (`D:\_claude_work\Kasymova\v10\diff_v10.py`).
- Calculate the user's newest file under a new local name (v10), never the older copy.
- Never overwrite the R: file with an older local version.

**An odd-looking user element stays too (confirmed 18.11.2026).** The user's v10 had a 0.5 m beam stub with a free end at x=32, y 34→34.5, +4.100. I asked whether to keep it; the user answered «Қалсын». So keep an element the user added by hand even if it looks unfinished. If I ask, keeping it is the default I offer, and I pass the answer on to the Revit session as well.

Related: [[lira-model-by-analog]], [[project-kasymova-hotel]], [[lira-stiffness-order-named]]
