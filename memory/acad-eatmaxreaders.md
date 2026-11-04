---
name: acad-eatmaxreaders
description: rz.cs плагинінде eAtMaxReaders — McObject орамдарын dispose ет, динамикалық блоктың allowed values тізімін шақырма; сақтау/DXFOUT құлайды
metadata:
  type: feedback
---

04.11.2026, ЖК Галакси. After thousands of ops in one AutoCAD session my plugin (rz.cs) broke the drawing: DXFOUT and Save failed with eAtMaxReaders. A later attempt failed with eFileAccessErr, and SaveAs wrote only a partial file. Unsaved work was lost twice.

**Why:**
- `McObjectManager.GetObject` wrappers were never disposed.
- The `dyn` op enumerated `GetAllowedValues()` on dynamic block properties.
- Both leave DB objects open for read, until one object hits 256 readers.

**How to apply:**
- In rz.cs, get every СПДС object through `MGet()` (it registers the wrapper; `McRelease()` disposes them after each op).
- Set dynamic block properties without listing their allowed values.
- Save right after each logical batch of changes, never only at the end.
- Once eAtMaxReaders appears, nothing in that session can be saved. Kill the instance, reopen the last saved DWG in a fresh instance, re-DXFOUT, rebuild the ops from that fresh dump, apply them, save.
- Killing the Python wrapper does not stop the AutoCAD job already taken by the listener.

Related: [[cad-dedicated-instance]], [[cad-console-net-workflow]], [[galaxy-kzh-scheme]]
