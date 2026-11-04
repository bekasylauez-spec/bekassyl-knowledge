---
name: feedback-acad-swap-myself
description: "User wants me to close/replace/reopen their open DWG in their AutoCAD myself, not ask them to close it"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 1739d5c1-e711-4734-a198-42e10d4e5047
  modified: 2026-11-04T13:55:34.019Z
---

When a rebuilt DWG must replace a file the user has open in AutoCAD, do the close → replace → reopen myself instead of asking them to close it (user, 04.11.2026: «жауып ашар затты өзің жаса»).

**Why:** asking «жабасыз ба?» after every sheet stalls the work; they want the new file shown in their AutoCAD without manual steps.

**How to apply:**
- Use `Завод_В109_КМ\_авто\acad_swap.ps1 -New <built dwg> -Target <album dwg>`.
- It works over COM («AutoCAD.Application.24») and closes only that drawing; other open drawings are not touched.
- Unsaved changes in that drawing are first saved as a copy to `_авто\_user_edits`.
- The «Информация о прокси-объектах» dialog of the reopen is OK'd automatically.
- Never kill the user's AutoCAD process.

Related: [[project-zavod-b109-km]], [[feedback-full-autonomy]].
