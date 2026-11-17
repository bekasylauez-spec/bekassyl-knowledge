---
name: rvjob-shared-channel
description: "BEKA-1 RBLive job channel %LOCALAPPDATA%\\rvjob\\live.txt/livedone.txt is shared by every session's Revit — use the tag/claim rv.ps1; a stuck job usually means an open Revit warning dialog"
metadata:
  node_type: memory
  type: reference
  originSessionId: 94c03bfb-48e3-4972-8913-5871021722f0
  modified: 2026-11-15T16:16:28.213Z
---

On BEKA-1 several Claude sessions run their own Revit instances, and every instance loads the same RBLive shim. They all read `%LOCALAPPDATA%\rvjob\live.txt` and write `livedone.txt` (15.11.2026: the РМЦ session copied the Kasymova `rv.ps1`).

**Failure modes with the old rv.ps1**
- Each waiter takes any livedone.txt as its own result.
- Each waiter deletes livedone.txt at start.
- Each waiter overwrites live.txt unconditionally.
- Result: one session got another's result ("Cannot modify the document…"), and queued jobs were lost.

**Fix: tag/claim protocol** (`D:\_claude_work\Kasymova\revit\rv.ps1`, copy it for new projects)
- Write live.txt only with CreateNew (only when it does not exist), and re-queue if another writer replaced it.
- Use my own runner `runner_kas.dll`, built from `runner_kas.cs` with the v113r csc line. It:
  - claims `_live\claim_<tag>` with CreateNew, so a duplicate run returns SKIP;
  - writes EVERY outcome to `_live\done_<tag>.txt`, including COMPILE ERROR;
  - returns "SKIP", so livedone.txt never carries my result;
  - on a pid mismatch, puts the job back into live.txt only if live.txt is empty.
- Give each job its own file, `_live\job_<tag>.cs`.
- Never read or delete livedone.txt. The first version peeked at it for COMPILE ERROR and took another session's error as its own, so the 2.5 fragment was silently lost.
- Check dialogs with Win32 EnumWindows (class #32770 of my pid). UI Automation blocks for minutes while Revit is busy.
- Double-clicking an .rvt (or ShellExecute on it) is sent by DDE to an already running Revit, often mine. 15.11: the user's Omar S03 R2023 model opened in my instance, spent 7 min upgrading and stopped on an error dialog. That file is the user's, so I did not press anything in its dialog.

**If a job hangs or returns "Cannot modify the document…/changes temporarily disabled"**
- Check my Revit for a `#32770 "Autodesk Revit 2025"` window. It is often a modeless DocWarnDialog left by the user's own edit.
- 15.11 example: the user was viewing sheets in my instance and accidentally dragged a wall end. Revit showed «опорные элементы размеров некорректны», and every script was blocked.
- Read the button ids with EnumChildWindows, then `PostMessage(dialog, WM_COMMAND, 3, btn)`. Here 3 is Отмена/IDABORT, which undoes that edit. BM_CLICK did not work.
- Tell the user what was undone.
- Diagnose with the journal `%LOCALAPPDATA%\Autodesk\Revit\Autodesk Revit 2025\Journals\journal.NNNN.txt`. Open it with FileShare.ReadWrite; `Jrn.` lines show the user's clicks and commands.

Related: [[beka1-run-beka2-revit-scripts]], [[revit-own-instance-mcp-autostart]], [[project-kasymova-hotel]]

**17.11.2026 (Касымова):** live.txt-ті менің Revit-ім (pid дұрыс) алмай тұрды. Диалог жоқ, процессор бос, тінтуірді жылжыту да көмектеспеді. Себебі — RBLive `OnIdling` ішіндегі `busy` жалауы: алдыңғы бір жұмыс біткен жоқ немесе ілініп қалды, сондықтан жаңа жұмыс оқылмайды. Шешім: соңғы сақтаудан кейін өзгеріс жоқ екенін тексеремін, сосын тек өз данамды тоқтатамын (`_pid.txt`) және `start.ps1 -Rvt "D:\_claude_work\Kasymova\revit\Гостиница Касымова КЖ.rvt"` арқылы қайта ашамын. Кезектегі өз live.txt-ім (tag бойынша) мен job файлдарын алдын ала өшіремін.
