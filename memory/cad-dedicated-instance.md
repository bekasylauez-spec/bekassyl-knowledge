---
name: cad-dedicated-instance
description: "Live AutoCAD+СПДС edits: run them in my own AutoCAD instance via a job-listener plugin, never by SendCommand into the user's AutoCAD"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 490b478b-b8f5-44f2-b8db-d48a50b10622
  modified: 2026-10-14T17:17:35.888Z
---

The user keeps working in AutoCAD while I edit drawings (2026-10-13: they switched tabs, opened another project, saved the original). COM `GetActiveObject`/`ActiveDocument` then hits THEIR document: my NETLOAD landed in their drawing and raised an error dialog there.

**Why:** all ROT entries "!{AutoCAD CLSID}" resolve to the same (first) instance, and `Marshal.BindToMoniker(dwgPath)` silently spawns a hidden extra acad.exe. Typing via Windows-MCP can land in the Claude chat box instead of AutoCAD.

**How to apply:**
- Work on a copy "... v2.dwg"; close it in the user's AutoCAD if open there.
- Start my own instance: `acad.exe "<v2>" /nologo /b boot.scr` where boot.scr does FILEDIA 0, SECURELOAD 0, NETLOAD listen.dll, JOBLISTEN, FILEDIA 1. listen.dll polls `%TEMP%\acadjob\job.txt` ("dll|Ns.Type|Method") on Application.Idle, runs it under LockDocument, writes done.txt. Scripts: session 490b478b scratchpad `net\listen.cs, job.ps1, relaunch.ps1, savedxf.ps1, quit.cs`.
- Save from inside (`db.SaveAs(doc.Name, true, DwgVersion.Current, …)`), then copy + accoreconsole DXFOUT + ezdxf render to check.
- At the end: SECURELOAD 1, FILEDIA/CMDDIA 1, QUIT my instance so the user can open v2.
- Write C# with the Write tool, not bash heredocs (they turned `"\t…"`/`"\f…"` into control chars).
- 2026-10-14: before setting a formula, set `cell.DataType = new DataTypeParameter(DataType.Double, UnitType.Unitless)`. Otherwise, after TextString="", formula cells hold string values: Sum/+ in other cells gives 0 or ####, and Wblock fails with eWasErased/eExcessiveItemCount. Then run db.EvaluateFields() and UPDATEFIELD _ALL.
- AutoCAD Table formulas: `cell.TextString=""; if(Contents.Count==0) Contents.Add(); Contents[0].Formula="=(…)"; Contents[0].TextHeight=…; cell.DataFormat=…` — never set Contents[0].DataFormat (it drops the formula on GenerateLayout). Loose sketch blocks over tables do not move with inserted rows.

2026-10-14: my own instance showed «Лицензия на продукт — время истекло» while the user's two AutoCADs were running; jobs never ran. I closed it via its «Выйти без сохранения» button (BM_CLICK) and did all non-SPDS work in accoreconsole; SPDS callouts/format frames left for when a seat is free. Check for that dialog (EnumWindows on my pid) before waiting on jobs.

2026-10-14 user override: «Ашық тұрған автокадқа жібер, файлды жаңадан ашпа» — when the target drawing is already open in the user's AutoCAD, apply the work there (COM: set ActiveDocument to it, SendCommand NETLOAD + my command, then restore FILEDIA/CMDDIA/SECURELOAD and switch back to the doc they were on). Don't save it; the user reviews and saves. Plot checks: COM PlotToFile came out blank here, so instead Wblock() the live db to %TEMP% and plot that copy in accoreconsole.

Same day, porch КР1 (session 8d95cd67, scratchpad `net\krlisten.cs, kr.cs, job2.ps1, gen.py`): another Claude session was editing the same open drawing at once. A listener with its own folder (`%TEMP%\acadjob_kr`, command KRLISTEN, job = "dll|Type|Method|target dwg name") avoided job collisions. It activates the target doc per job and switches back afterwards. Stop it with KRSTOP. SendCommand NETLOAD needs "\n" terminators (a space after the path doesn't submit file prompts). In the user's live AutoCAD, polylines edited via SetPointAt/RemoveVertexAt and newly created hatches stayed invisible until regen (the user thought the sections were deleted). Always finish with SendCommand "_.REGENALL\n". Editing vertices also remaps associative dims to the wrong vertices: remove ACAD_DIMASSOC from the dims first, then set their points. Before placing new sheets, list the live frames (SPDSFORMAT) because the other session may have taken sheet numbers.

2026-10-14 (КМ БЦ парапет, scratchpad 1ebaf694 `net\pp.cs` = generic JSON ops: clone/pline/hatch/mtext/spdsnote/spdsdim/erase): to read live handles, `db.DxfOut()` the LIVE db. `db.Wblock()` renumbers handles. Python `-I` ignores PYTHONIOENCODING, so use `-X utf8`. JavaScriptSerializer arrays come back as object[], so cast to IList. Hatch from a temp polyline failed with eInvalidInput; use AppendLoop(Point2dCollection, DoubleCollection). A modal "eWasErased" dialog in the user's AutoCAD (from another doc) blocks Idle jobs. Read it via UIAutomation and PostMessage BM_CLICK on «Продолжить». accoreconsole from bash: MSYS mangles `/i` `/s`, so start it from PowerShell, with the -PLOT script one answer per line. Stop the listener at the end: SendCommand "KRSTOP\n".

Related: [[cad-console-net-workflow]], [[cad-callouts-spds]]
