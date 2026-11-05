---
name: reference-spds-api
description: "How to read/create the user's SPDS GraphiCS objects (frames, marks, nodes) by script: second acad.exe instance + MultiCAD .NET API plugin"
metadata:
  node_type: memory
  type: reference
  originSessionId: 1ef51441-e103-4b74-9733-3540011db41e
  modified: 2026-11-04T08:24:11.333Z
---

The user's КМ DWGs use SPDS GraphiCS objects (CSoft «СПДС Металлоконструкции 2021», `C:\Program Files\CSoft\...\mg142x64`). accoreconsole sees them only as ACAD_PROXY_ENTITY; COM exposes no custom properties. Files named «Без СПДС» are exploded copies.

Working method (04.11.2026):
- Never touch the user's running AutoCAD. Start a separate `acad.exe /nologo <dwg> /b <scr>`; the SPDS bundle loads itself. Script: SECURELOAD 0, FILEDIA 0, `_.NETLOAD <dll>`, command, `_.QUIT _Y`. Env vars set in the same PowerShell call are inherited. The script stops at the first error and the instance then hangs, so wrap LISP in vl-catch-all and always end with QUIT.
- Plugin: csc.exe v4.0.30319 `/platform:x64`, refs acmgd/acdbmgd/accoremgd + mapimgd.dll + mapibasetypes.dll. `McObjectManager.SelectObjects(new ObjectFilter{AllObjects=true}` + `SetCurrentDocument())`, `id.GetObject()`.
- Typed classes: McNotePosition (FirstLine/SecondLine/TextSize/Origin) = mark leaders, McNoteKnot (Knot/Sheet/Note) = node callouts, McFormat (Name A3, Width/Height, Multiplicity, Template −3, Origin) = frames, McSectionVS = sections, McAxisEntity = axes, McConnectionFix/Break, McLinearDimension. Level marks and welds come back as plain McEntity.
- Command-line output from vlax-dump-object goes to `%LOCALAPPDATA%\Autodesk\AutoCAD 2021\R24.0\rus\<dwg>_*.log` when LOGFILEMODE=1.

Related: [[project-zavod-b109-km]], [[user-env-cad]].
- Untyped SPDS objects (level mark mcsDbObjectLevelMark, welds): read/write via DbObject.ObjectProperties (PropertyDescriptor GetValue/SetValue: Text, Associative, Size…), clone the AutoCAD entity (WblockClone/DeepClone), move with TransformBy, reshape with McEntity.OnGetGripPoints/OnMoveGripPoints. Code: Завод_В109_КМ\_авто\BkLevel.cs.
- 05.11.2026 SPDS level mark value without BkLevel.cs: own plugin `net\lvl.cs` (session 4c62aff2 scratchpad): McObjectId.FromOldIdPtr(id.OldIdPtr).GetObject() → reflection prop "DbObject" → "ObjectProperties" (Multicad.McProperties, ICustomTypeDescriptor) → PropertyDescriptor "Text" SetValue. Command LVLCOPY clones a mark (DeepCloneObjects) so its lowest grip (= arrow tip) lands on x,y and sets the text. Compile: csc x64 refs accoremgd/acdbmgd/acmgd + mapimgd/mapibasetypes from CSoft …\mg142x64.
