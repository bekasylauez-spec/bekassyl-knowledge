---
name: cad-clone-analog-stretch
description: "\"Аналогтың стилін айнытпай\" КЖ job: clone analog drawing entities into the live DWG, scale to sheet, then stretch to new sizes (2026-10-16, КР2 porch from Блок 7 Фм-1)"
metadata:
  node_type: memory
  type: reference
  originSessionId: e16ed79d-0153-4f70-9262-3fab4f78f8e6
  modified: 2026-10-16T17:03:21.970Z
---

When the user says take an analog's style entirely and change only the lengths, the method that worked (2026-10-16, Склад Рикаус КР2 from «КМ Чертеж Лестница 7», sheets Фм-1 3/4 and Фм-2 1-1):
- Live AutoCAD 2021 (Rikaus open): my own listener K2LISTEN (`%TEMP%\acadjob_k2`), plugin k2.cs in session e16ed79d scratchpad `net\` (ops: select/import from side DB via ReadDwgFile + WblockCloneObjects, stretch via GetStretchPoints/MoveStretchPointsAt, dyn, level, hatchloop, tcell, wblock, cmd). Handle map in `%TEMP%\k2_map.json` ("tag:oldHandle").
- Analog sheets at 1:25 go onto Rikaus 1:50 frames with scale ×2. After TransformBy: dims Dimscale×2, Dimlfac/2; SPDS ImpCurve objects need DbEntity.Scale = 50 (only ImpCurve; never set it on hatches/blocks/weld marks, those keep their own scale ×2).
- Dynamic block «Хомут_динамический2» params are in world units after scaling (Расстояние1/2 must be doubled too).
- SPDS level marks: no API. Serialize, replace the ASCII value with a SAME-LENGTH string (pad with spaces), DeserializeNewFromBytes, erase old. Different length makes deserialize return null.
- Hatches don't stretch: recreate (AppendEntity, SetHatchPattern, then PatternScale/Angle, SetHatchPattern again, AppendLoop External|Polyline). Setting PatternSpace or scale before the pattern gives eInvalidInput.
- Cloned spec tables: db.EvaluateFields wipes formulas whose inputs are strings or whose fields were edited in place. I ended up writing computed numbers as plain Double values (Contents.Clear, Add, DataType Double, Value, DataFormat, then restore Contents[0].TextHeight, which Clear drops).
- Plot check: Wblock the region and plot it in accoreconsole. Cross-table field formulas show #### in the copy, so read live values with a table dump instead.
- COM to the user's AutoCAD is flaky while they work (ActiveDocument null). Run commands from inside the plugin with SendStringToExecute.

- DANGER (2026-10-16): every McObjectManager.GetObject (Mc) call without Dispose leaks one read-open on AcDbRegAppTable. After ~255 calls, Wblock/save fail with eAtMaxReaders, and a following REGEN crashed the user's AutoCAD (they had to restart; _recover.dwg). Never dump/scan SPDS objects through Mc in bulk. Use GetStretchPoints/GeometricExtents, `using` every McObject, and run a readtest (open the RegAppTable for read) after SPDS-heavy jobs.

- Layouts across files (2026-10-17): WblockCloneObjects of a Layout whose block is the source's CURRENT *Paper_Space maps it onto the target's *Paper_Space. The new layout then shares another layout's block. Erasing that stray Layout also erased the shared block. Unerase gives eDuplicateKey, so I had to rebuild the victim layout ('37') by CloneLayout from a twin. Import only non-current layouts, or recreate them with LayoutManager.CloneLayout + Viewport.ViewCenter in the target. Check btr.LayoutId == layout id after cloning.

- What worked for layouts (2026-10-17): a real CommandMethod K2LAYOUTS (net\lay.cs, session e16ed79d) that CloneLayout()s a same-file template ('35'), then sets the model viewport. ViewTarget=0 and ViewDirection=(0,0,1) are required because the template had target (46491.9, 532293.8). Then size, CustomScale, plot type Layout at 1:1, activate the layout once, vp.On=true, back to Model. For portrait use media ISO_full_bleed_A3_(297.00_x_420.00_MM) with rotation 0. Test on a copy in accoreconsole and plot with `-PLOT _N <layout>` first. Before SendCommand, check which document is active: the user had 4 drawings open. Activate the target, then switch back.

Related: [[cad-dedicated-instance]], [[sklad-rikaus-ramp]], [[cad-callouts-spds]]

- 2026-10-17 (Байтурсынова 3.1, Фм-2 sheet 3.9 from the КР9–12 analog the user pasted into the same file): faster than many stretch ops = op `pwmap` (piecewise-linear remap of every vertex/dim point/insert position, SPDS via stretch-point groups) after `clonexf` ×2 (1:50 sheet → 1:100 sheet). Sections went from ×4 (1:12.5) to ×5 = М 1:20, dims lfac 0.2, Арм.сеч4 scale 5, Хомут scale 2.578 + dyn 2500/600, SPDS clones need DbEntity.Scale 100. Scripts: session 7c42d0f8 scratchpad `net\f2.cs` (F2LISTEN, `%TEMP%\acadjob_f2`), `w\gen1-3.py`, `w\snap.py` (wblock+plot). Write JSON with `python -X utf8` / encoding='utf-8', else Cyrillic arrives garbled.
