---
name: close-user-file-myself
description: "Керекті DWG пайдаланушының AutoCAD-ында ашық тұрса — сұрамай өзім сақтап жабамын/ауыстырамын да қайта ашамын (COM, acad_swap.ps1); өз данамда жұмыс"
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

**Same rule on BEKA-2 (04.11.2026, В109: «жауып ашар затты өзің жаса»)** — when a rebuilt DWG replaces the open one:
When a rebuilt DWG must replace a file the user has open in AutoCAD, do the close → replace → reopen myself instead of asking them to close it (user, 04.11.2026: «жауып ашар затты өзің жаса»).

**Why:** asking «жабасыз ба?» after every sheet stalls the work; they want the new file shown in their AutoCAD without manual steps.

**How to apply:**
- Use `Завод_В109_КМ\_авто\acad_swap.ps1 -New <built dwg> -Target <album dwg>`.
- It works over COM («AutoCAD.Application.24») and closes only that drawing; other open drawings are not touched.
- Unsaved changes in that drawing are first saved as a copy to `_авто\_user_edits`.
- The «Информация о прокси-объектах» dialog of the reopen is OK'd automatically.
- Never kill the user's AutoCAD process.

Related: [[cad-dedicated-instance]], [[galaxy-kzh-scheme]], [[project-zavod-b109-km]], [[feedback-full-autonomy]]

05.11.2026 (Ақтау «для клауда»): user again: «өзің жапса сұрамай өзің жасай бер» — never ask them to close; do it.
When COM can't reach the doc (second acad.exe instance: GetActiveObject/ROT give only the other instance, the file moniker flickers in ROT), close it at window level: EnumChildWindows of that acad's main window → MDI child whose title is the dwg name (class Afx:…:b:…) → PostMessage WM_CLOSE → dialog «AutoCAD» «Сохранить изменения в …?» → PostMessage BM_CLICK on «&Да». The file is saved with the user's edits and only that drawing closes. Then rebuild my sheets on the saved file, keep .bak, replace.
