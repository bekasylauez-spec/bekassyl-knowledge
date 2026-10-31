---
name: cad-console-net-workflow
description: "How DWG edits were done when AutoCAD GUI/SPDS license failed — accoreconsole + C# .NET plugin applying JSON ops"
metadata:
  node_type: memory
  type: reference
  originSessionId: 1ba4a828-8529-416e-b794-9c0aff795b78
  modified: 2026-10-10T13:17:30.454Z
---

On 2026-10-10 the AutoCAD 2021 GUI and the СПДС GraphiCS (CSoft) network license both failed on this machine ("Сетевая лицензия недоступна", "Истекло время ожидания выдачи лицензии"). I must not troubleshoot licensing. User chose: do the work without SPDS, plain callouts, convert to SPDS later.

Working method that succeeded:
- `accoreconsole.exe` (AutoCAD 2021) + C# plugin compiled with Framework64 csc (refs accoremgd/acdbmgd/System.Web.Extensions), NETLOAD with SECURELOAD 0, command APPLYOPS reads a JSON of ops (create circle/line/pline/text/mtext/hatch/dim-clone/dimtext, table set/insrow/merge/delcol/thall/rowh/pos, erase by handle).
- Read drawings by DXFOUT + ezdxf; SPDS objects are ACAD_PROXY_ENTITY (erasable, not clonable); their text/geometry readable via ezdxf ProxyGraphic.
- Scripts live in the session scratchpad; work files in `...\КЖ Чертеж\_Claude\vypusk\_work`.

PDF of an album (later, 2026-10-10):
- Plot each SPDS format frame as a window with a 1:sc custom scale onto the smallest full-bleed A/B sheet (DWG To PDF has no 891x420 etc.). Then crop the page centred to the frame size and merge with PyMuPDF (show_pdf_page plus TOC).
- Window coordinates are in DCS, so subtract the TARGET sysvar, otherwise the plot comes out blank.
- The GUI COM PlotToFile works, and so does accoreconsole with PublishEngine (Core), which avoids the GUI license timeout. In console, force Model (LayoutManager.CurrentLayout = "Model"), otherwise you get eLayoutNotCurrent.
- Stamp sheet name: MText MiddleCenter in the 70x15 mm cell (x1-5-120..-50, y0+5..+20, times sc), width 68 mm; tighten LineSpacingFactor down to ~0.65 if it doesn't fit (user wants it like that).

Related: [[cad-callouts-spds]]

Notes job (2026-10-13, Байтурсынова 7.1/7.2 from Онкоцентр 7.Плита):
- Before overwriting a source DWG: check for `.dwl` lock and that it is byte-equal to my working copy (cmp). The user opened and edited 7.2 mid-job, so I could not write it.
- Quick visual check without GUI: in accoreconsole, `_-PLOT _Y Model "DWG To PDF.pc3" "ISO без полей A3 (420.00 x 297.00 мм)" _M _L/_P _N _W x,y x,y _F _C _Y monochrome.ctb _Y _A "out.pdf" _N _Y`. The paper name must be the Russian localized one, then rasterize with PyMuPDF. ezdxf rendering drops text here.
- Sheet notes on these frames: MText on layer О_Формат above the Штамп№1 stamp (stamp 18.8x5.5 m at 1:100). MText GeometricExtents include the defined-height box, so anchor BottomLeft at stamp top +250 rather than using extents. On spec (A3) sheets, find free space separately.
