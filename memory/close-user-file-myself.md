---
name: close-user-file-myself
description: Керекті DWG пайдаланушының AutoCAD-ында ашық тұрса — сұрамай өзім сақтап жабамын да, өз AutoCAD данамда жұмыс істеймін
metadata:
  type: feedback
---

04.11.2026 (ЖК Галакси): I asked the user to close the open DWG so I could edit it. Their answer: «Өзің жауып жаса алдағы уақытта».

**Why:** the user does not want to be interrupted for this step.

**How to apply:**
- When the drawing I need is open in the user's AutoCAD (a .dwl exists or the COM document list shows it), close it myself without asking.
- First **Save** it (their edits are kept; never close without saving), then Close. Do this via COM on that document.
- Then open it in my own dedicated AutoCAD instance with the listener and work there ([[cad-dedicated-instance]]).
- Tell the user in one line that I saved and closed it.

Related: [[cad-dedicated-instance]], [[galaxy-kzh-scheme]]
