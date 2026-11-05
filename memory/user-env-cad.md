---
name: user-env-cad
description: "CAD tooling on this PC — AutoCAD 2021 accoreconsole tricks, Revit 2025/Dynamo 3.0.3, no system Python"
metadata:
  node_type: memory
  type: reference
  originSessionId: 1627bee1-9218-4ed4-bb58-ee22da3b578f
  modified: 2026-10-10T09:14:55.007Z
---

**BEKA-2** (user `beka`). Python 3.13 is installed there since 04.11.2026 (`%LOCALAPPDATA%\Programs\Python\Python313`); the «no system Python» line below is from 10.10.
- AutoCAD 2021 (Russian): C:\Program Files\Autodesk\AutoCAD 2021\accoreconsole.exe. No ActiveX (vla-*) and no `layoutlist` there; need SECURELOAD 0; LSP files must be cp1251; never name a LISP variable `t`.
- In accoreconsole, entities freshly created by EXPLODE are mis-selected by ssget W/C — test them by their DXF points. SPDS proxies block WBLOCK → use erase-rest + SAVEAS + UNDO Back.
- Revit 2025, Dynamo 3.0.3 (CPython3). No system Python; embedded Python 3.9 can be extracted from DynamoForRevit\Python.Included.dll resources for syntax checks.
Related: [[revit-kzh-oformlenie]]

- 05.11.2026 (BEKA-1): accoreconsole started from Bash (`timeout ... accoreconsole.exe /s x.scr`) hung on «Команда:» and did nothing. Working: PowerShell `Start-Process ... -NoNewWindow -PassThru -RedirectStandardOutput`, script written with CRLF (`[IO.File]::WriteAllText(..., [Text.Encoding]::Default)`). `_-PLOT _N <layout> "" "DWG To PDF.pc3" file _N _Y` plots every layout of an album in one script.
