---
name: revit-tag-shelf-addin
description: КЖ mark tags keep leader on shelf via own add-in KZhTagShelf (updater sets elbow at shelf end); Revit leader attach rule; extents vs annotation crop
metadata:
  node_type: memory
  type: project
  originSessionId: 1627bee1-9218-4ed4-bb58-ee22da3b578f
  modified: 2026-10-30T06:22:43.388Z
---

User requires the leader to stay joined to the mark text/shelf («ажырауы тыйым салынады»), text+shelf+leader move together, leader end on the element fixed. Installed 2026-10-16.

- Revit attaches a tag leader to the NEAREST of 4 points of the tag extents: left/right end at vertical centre, top/bottom centre (measured via DXF export of test tags). Family «(марка)несколько_категорий» has two invisible extent lines (back to ±6.5 mm paper on 2026-10-17, Visible=No) so the vertical centre is the shelf (y=0). Larger extents hide tags that cross the annotation crop — ±40 mm hid a tag in a 1:50 section, ±200 hid every tag. The add-in's elbow makes the attach point independent of the extents, so keep them small.
- Steep leaders still jump to top/bottom, so the add-in `addin\KZhTagShelf.cs` (DLL in `addin\bin`, compiled inside Revit with Roslyn — no .NET SDK on this PC; manifest %APPDATA%\Autodesk\Revit\Addins\2025\KZhTagShelf.addin) registers an IUpdater on IndependentTag add/modify: sets LeaderEndCondition=Free and puts the leader elbow at head ± «Длина полки»/2 × view scale on the side facing the leader end. Elbows are absolute (don't follow the head) — the updater re-snaps them.
- Dragging the elbow grip (at the text base) moves the whole mark: updater caches last head per tag (key = doc.PathName + id; Document wrappers have unstable hash codes) — head unchanged + elbow moved ⇒ head follows the grip. Priority ChangePriority.Views so it runs before older copies.
- Updaters can only be unregistered/disabled by their own add-in (AddInId check). Revit loaded the manifest mid-session, so a stale v1 stays registered until restart. The DLL is locked while loaded, so each rebuild needs a new file and assembly name (currently `KZhTagShelf_v5.dll`; the manifest points to it).
- Rebuild: `_addin_build.cs` (emits DLL, registers updater with MCP's ActiveAddInId for the current session, FixAll). DLL is locked while Revit runs. `_noelbow.cs` is obsolete (would fight the updater).

- v11 (18.10.2026; manifest → `KZhTagShelf_v11.dll`, built by `_addin_build11.cs`):
  - Fix handles any number of tagged references: an elbow per leader on the shelf end facing it.
  - When a rebar tag moves up/down, straight leaders on bars that run along the view's up direction slide with it, so they stay horizontal and stay on the bar.
  - The ribbon tab «КЖ» → panel «Выноска» holds the «Выноска +» (`AddLeaderCmd`: pick bars, adds a straight leader) and «Выноска −» (`RemoveLeaderCmd`) buttons. The tab is created at startup or at runtime via `UIApplication.CreateRibbonPanel`, which works mid-session.
  - Updater changes are applied at transaction commit, not at Regenerate. Check them in a second call.

- v15 (19.10.2026; manifest + package _Стандарт_КЖ\қосымша_Revit → KZhTagShelf_v15.dll, _addin_build15.cs): KZhSpec column mode — live spec + steel statement for column marks (per ONE column, mesh С1 product counted by BI_главный_элемент, gross concrete volume, А240/А500С steel form). Several builds stay loaded in one session; scripts must pick the newest assembly (StartsWith("KZhTagShelf_v") ordered by name), never a hard-coded _v14. The spec updater is replaced by registering the same GUID under MCP's ActiveAddInId (old one unregistered automatically).

- v16 (20.10.2026, _addin_build16.cs): SpecBuilder.StackSchedules — restacks the template's per-mark schedules (1СА/2СА/3ВМ chain, 4ВД/5ВРС pushed below) on every sheet after rebar changes; manifest + package → v16.

**Why:** user rejected any detached leader after dragging marks in Revit.
**How to apply:** don't remove tag elbows; new tag scripts can just create Free-end tags — the updater adds elbows. Related: [[revit-mcp-bridge]], [[revit-kzh-oformlenie]]
- v18–v20 (30.10.2026, _addin_build20.cs; manifest + package → v20): new file `addin\KmJoints.cs` — «КЖ» tab panel «КМ түйін», button «Ус» (KmMitreCmd: pick two framing tubes → mitre). KmJoint.Mitre is also called by m05 via reflection (newest KZhTagShelf_v*). Mitre = both ends +40 mm, two face-based void instances «БК_срез» hosted on reference planes through the node (normal checked via instance BasisZ, re-made flipped if wrong; work-plane-based voids did NOT orient), InstanceVoidCutUtils on each piece, weld band DirectShape «шов ус». Revit's own framing end join on braces gives a butt cut, not a mitre. A runtime ribbon button keeps the DLL path it was created with — repoint with PushButton.AssemblyName after a rebuild.
- v17 (20.10.2026, _addin_build17.cs): KZhSketch L = REBAR_ELEM_LENGTH rounded to 10 (same as template 2СА/4ВД Р_Длина), not Σ outer segments + hooks; manifest + package → v17. The v16 spec updater could not be unregistered in-session (AddInId mismatch) — restart Revit so only v17 runs.
