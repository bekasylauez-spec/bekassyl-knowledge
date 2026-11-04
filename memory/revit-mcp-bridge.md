---
name: revit-mcp-bridge
description: "How I drive Revit 2025 on this PC — mcp-servers-for-revit socket (port 8080) + send_code_to_revit C#, UI automation for dialogs"
metadata:
  node_type: memory
  type: reference
  originSessionId: 1627bee1-9218-4ed4-bb58-ee22da3b578f
  modified: 2026-10-30T08:48:05.978Z
---

**BEKA-2** method (`D:\Бекасыл КЖ КМ` is BEKA-2's local disk). BEKA-1 builds Revit models with a csc add-in instead: [[revit-build-via-addin]].
- Add-in `mcp-servers-for-revit` (%APPDATA%\Autodesk\Revit\Addins\2025\revit_mcp_plugin) listens on 127.0.0.1:8080 after ribbon Надстройки → "Revit MCP Switch" is clicked (needs an open document). It is unsigned: at Revit start answer the security dialog "Загрузить один раз" (don't pick "always" without asking).
- Client: D:\Бекасыл КЖ КМ\Revit_оформление\_авто\revit.ps1 (`Invoke-RevitCode -File x.cs`). JSON-RPC method `send_code_to_revit`, params {code, parameters}. Code is the body of `static object Execute(Document document, object[] parameters)` and runs INSIDE a transaction (use SubTransaction; no SaveAs/EditFamily/Export there).
- Documentation from model (doc_lib.cs + doc_0X_*.cs in Revit_оформление\_авто): section boxes — Revit reports Right = -BasisX, ViewDirection = -BasisZ; use BasisX=-right, BasisZ=lookDir, Min.Z=0..Max.Z=depth. Rebar tags must reference a subelement (rebar.GetSubelements()[i].GetReference()), not the rebar. Template tag "(марка)арматурный_стержень" prints "Ск" itself for U shapes → BI_позиция = number only. Title block "Форма 3": never copy Ширина/Высота/Нестандартный… params (they lock Формат А); Regenerate after ViewSheet.Create before collecting the TB. Duplicate viewport detail numbers raise an un-swallowable error dialog (only Cancel → rollback) — avoid. MCP call times out after a few minutes but Revit keeps working; poll Revit CPU until idle, then check for dialog windows (EnumWindows on Revit pid) before the next call.
- For work that needs no open transaction (EditFamily, LoadFamily, SaveAs, Export, own Transactions) register `new UIApplication(document.Application).Idling` one-shot handler from the code; bring the Revit window to front so Idling fires. Classes (e.g. IFamilyLoadOptions) can be injected by closing the method/class braces in the code string (see family_fix*.cs).
- Revit journal playback (Revit.exe journal.txt) failed here ("Ошибка при работе с журналом") — don't rely on it.
- UI: PowerShell + user32 (scratchpad Win.cs): enumerate windows/buttons, real mouse clicks, screenshots via CopyFromScreen. Revit TaskDialog buttons ignore BM_CLICK; use real mouse click.
- Revit re-uses cached geometry of an imported DWG with the same file name: delete the ImportInstance AND its CADLinkType before re-importing.
- Revit renders imported DWG text badly (re-wraps, shifts). Reliable fix: plot to PDF with All_As_Geometry (custom PDF_geometry.pc3) and PDFIMPORT back in accoreconsole (make_geom.lsp).
- Restart (21.10.2026, Revit hung on a blank «Главная» after a text-less warning): with permission kill Revit, start Revit.exe with the LOCAL file C:\Users\beka\Documents\12-2025-КЖ_КМ_Гостевой дом_beka.rvt; approve KZhTagShelf «Загрузить один раз»; the «Открытие рабочих наборов» dialog must open ALL worksets — clicking OK left КЖ / axes / stairs closed and every view showed only cameras (fixed via Совместная работа → Рабочие наборы → select all → Открыть → OK); then Надстройки → «Revit MCP Switch» (first click on a tab after load may be ignored).
- Dimensions in a SECTION/elevation view (30.10.2026, 3602 s04_brackets.cs): `new Reference(grid)` and a framing family's CenterLeftRight plane both get dropped at commit → un-swallowable «Ошибка – необходимо исправить / Удаление опорных объектов» dialog (only Отмена → rollback). Works: grid = the Line.Reference from grid.get_Geometry(Options{ComputeReferences, View}); element = a PlanarFace reference from its view geometry (symbol geometry → `fi.UniqueId + ":0:INSTANCE:" + stable`).
- Error-dialog trap: after clicking «&Развернуть >>» the buttons lose their «&» (OK / Отмена) and Click-Text "&Отмена" no longer closes it — the dialog stays and every later run "sees a dialog" falsely. Click both "&Отмена" and "Отмена".
- Dimension to an element's centre where no face exists (plate centre): NewReferencePlane 2 mm long through it (Regenerate before GetReference(), else "not geometric references"); do NOT hide it in the dimension's view — dims to hidden refs vanish; hide it in all other views.
- Datum lines editable by the user: SetDatumExtentType(ViewSpecific) + SetCurveInView inside the crop (s10_datums2d.cs); ends outside the crop have no grip.
Related: [[user-env-cad]], [[revit-kzh-oformlenie]]
