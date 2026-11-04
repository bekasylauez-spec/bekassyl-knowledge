---
name: revit-build-via-addin
description: "How to build Revit 2025 models automatically here — csc-compiled add-in, job file, dialog clicks; Рампа canopy built 2026-10-30"
metadata:
  node_type: memory
  type: reference
  originSessionId: 7e55ac1d-056c-477c-b1ef-1657f3036e17
  modified: 2026-10-30T13:12:46.065Z
---

Revit 2025 (RUS) is installed; Revit 2024 has no exe. No .NET SDK, but the add-in compiles with Framework64 `csc.exe /noconfig /nostdlib` against `dotnet\shared\Microsoft.NETCore.App\8.0.26\{System.Private.CoreLib,System.Runtime,System.Collections,System.Linq,System.Text.Encoding.Extensions,netstandard}.dll` + RevitAPI/RevitAPIUI. Only C# 5 syntax.

Method (session 7e55ac1d scratchpad `rv/`: rb.cs, gen.py, dlgwatch.ps1, wins.ps1):
- Manifest in `%APPDATA%\Autodesk\Revit\Addins\2025\RB.addin` (moved to rv\RB.addin.off after use, so the user's Revit is clean).
- Job file in `%LOCALAPPDATA%\rvjob\job.txt`. NOT %TEMP%: Revit sets its own TEMP subfolder (GUID), so Path.GetTempPath() differs.
- Idling does NOT fire with no document open, and ApplicationInitialized did not run the job either. Start Revit with a document argument (a copy of the .rte), then Idling runs the job.
- OpenAndActivateDocument fails inside the event («Switching active documents is not allowed»). Restart Revit with the .rvt as argument instead.
- Startup dialogs: «Безопасность — Надстройка без подписи» → button CommandButton_1002 «Загрузить один раз» (BM_CLICK on its hwnd); ModPlus info box → BtOk (Invoke). Closing Revit with the boot doc asks «Сохранить изменения…» → CommandButton_7 «Нет».
- Families made in code from «Метрическая система, несущий каркас - Балки и раскосы.rft» / «…несущая колонна.rft»: delete the template extrusion, NewExtrusion with outer+inner loop, NewAlignment+lock to «Элемент слева/справа» or the ref levels. Material set directly on the extrusion (associating STRUCTURAL_MATERIAL_PARAM failed with «regeneration failed»).
- ExportImage of the 3D view to PNG to check the result.

Рампа result: «ЖК Қарасу село Абай\Revit\Навес 1 Рампа.rvt» + «Семейства» + 2 PNG, from LIRA «Data\Навес 1 Рампа 02.txt». Revit X/Y = LIRA X/Y (Л Y=0, М 7300, К2 row 8800, cantilever −680), Z = LIRA z + 870.
- My first build used Y = −LIRA Y and came out mirrored. The user said «теріс түсті», «чертежды дұрыстап қара». On the КМ plans (album PDF sheets 4–6), М is at the top, Л at the bottom, the cantilever is below Л, and К2 is above М.
- **How to apply:** before building, render the album PDF sheets and compare the orientation with the plans and sections. Do not trust garbled DXF axis labels.
- Marks: type 7 at Л = СВ2, at М = СВ1; sloped type-8 bars = СВ3 (V braces between trusses). No roofing («кровля керек емес»).

**Album formatting** (2026-10-30). The user said «оформление тура К?-дағыдай, барлық элементті 3D-дан ал, цвет бер». I first used the КЖ Revit template «RAS GROUP PROJECT\BI_Шаблон_КЖ_v3.52 … Бекасыл.rvt», and the user stopped it: «КЖ аналогты қолданба, сен КМ жасап жатсың, стиль дегенім DWG-дағы жазу стильдері».
- **How to apply:** for a KM album, copy the look of the user's KM DWG itself: the stamp block «крпкер», text styles and dimension style. Do not use the КЖ template.
- What was built, «Revit\КМ Навес 1 Рампа.rvt» + «(Revit).pdf», is a clean RU structural template with:
  - my own titleblock families КМ_Штамп А3/А2: frame 20/5, stamp 185×55 drawn from the «крпкер» block geometry, ISOCPEUR / GOST Common italic text, logo and signatures cropped from the album PDF;
  - text 3.0, stamp 2.5 and «КМ_СПДС» dims 2.5 with oblique ticks;
  - level marks «+0,870» (project length unit in m with a plus sign and decimal comma; dims keep their own mm format);
  - DWG scales and sheet numbers 2–10: plans 1:75, sections 1:50, 3-3/4-4 on A2;
  - viewport titles as underlined text above each view;
  - colours per mark through filters «КМ_<марка>».
- The RU framing/column tags show the type name, so the marks are text notes. Revit API cannot create family labels, so per-sheet stamp fields (sheet name, number) are text notes on the sheet.
- Gotchas:
  - section boxes come out with screen-right = −BasisX, so pass BasisX = −right;
  - grid bubbles: use GetCurvesInView(Model) ends;
  - level model extents must be stretched in 3-3 and 1-1, or the 2-2 section can't see them;
  - Family objects go invalid after LoadFamily, so read their names first.
- Code: scratchpad 7e55ac1d `rv/km2.cs` (mode km2), `job_km2.txt`, `cycle.ps1` (close / compile / restart / watch).

Full album, 13 sheets, numbered like the DWG (2026-10-30 afternoon). The user said «ОД мен узелдерді қос; размер, разрез барлығы қалай көрініп тұр содан ал».
- Sheets:
  - 1 ОД (A2): DWG texts at their positions from `od.txt` (¶ = paragraph break), a Revit sheet-list schedule, a drawn table of reference documents, and the ГИП box with signature;
  - 2 технический спецификация (A3 portrait), drawn as a table, masses from the model by profile × group;
  - 10 truss schemes Ф1/Ф2 (coarse sections; their markers hidden with SECTION_COARSER_SCALE = 20) + «Ведомость элементов» schedule;
  - 11/12 nodes as callouts of 1-1, 3-3, 4-4, p5 and p3 (1:10, 1:20), titled with a drawn bubble «N / parent sheet»; sections а-а and б-б are plan callouts with a low view range;
  - 13 the 3D view.
- Plates as DirectShape (km3.cs AddPlates):
  - ribs -t8 on К1 bases;
  - caps -t10 on К1/К2 tops; the columns are cut down to the cap;
  - caps -t4 on free ends of the chords and П1;
  - gussets -t10 on axis 3.
- DWG look:
  - section type «Разрез» (head «Заголовок разреза» = stroke + arrow + number) with view names "1".."4";
  - dims «КМ_СПДС»: witness extension 1.25, line extension 2, gaps 0.625;
  - plans: top chain of column spacings + 23950; bottom grid chain + last column (3150) + 20800; left 7300/680; right chain of П1/РС1 rows;
  - sections: П1 panel chain on top, a level dim 3750, grid/К2 dims at the bottom.
- Gotchas:
  - callouts inherit filters (AddFilter throws) and do not clip datums, so hide grids, levels, sections and elevations in the node views;
  - node marks need the circle like the DWG («дөңгелектері жоқ»). The RU Detail type uses «Заголовок фрагмента - Без марки», whose circle is drawn with invisible lines. Set the parameter «Марка фрагмента» of the Detail/Plan/Section ViewFamilyTypes to the type «…с радиусом углового закругления 3 мм» (head «M_Заголовок фрагмента»). There is no API to move callout heads, and some of them land on top of members;
  - 2026-10-30, «жаңа семействоларды жаса, полный ретте DWG-дағыдай». The SPDS sizes come from the DWG proxies (spds_geo2.py: frames give the sheet scale; SPDSSECTION graphics don't decode, so they were measured from a 500-dpi PDF crop). New families in `Revit\Семейства` (km4.cs, km5.cs):
    - КМ_Ось: Ø7 circle, text 3.5;
    - КМ_Отметка: stem 7.5, V arrow 2, shelf 12.54, text 2.5 at 1.5 mm from the shelf end;
    - КМ_Узел: shelf 7.6, number 3.5 above it, sheet 2.5 below it; callout radius 4 → oval;
    - КМ_Марка каркаса / колонны: text 2.5 on a 9 mm shelf; the label shows the type name, so every mark gets its own type (К1, ВП1, …);
    - КМ_Знак разреза (+ mirrored): stroke 6 (thick line, because Revit rejects curves < 0.8 mm), arrow 8.4 at 1.3 mm from the outer end, filled head 3×1, the number as a text note 6.3 mm along and 2 mm off.
    The real section markers are hidden on the plans, because the line between the marks could not be removed: OST_Sections/Viewers colours, VG overrides and the tag's own GraphicsStyle all failed.
    Gotchas:
    - a type named like its family («КМ_Разрез») made Find<ElementType> return the FamilySymbol; filter `!(t is FamilySymbol)`;
    - labels can't be created by the API, so edit existing families (EditFamily → redraw → SaveAs new name → LoadFamily);
    - label text ends with "\r" (Trim before comparing);
    - rotated tag labels need RotateElement by -atan2(BaseDirection).
  - titleblock templates keep 4 sheet-edge lines that cannot be deleted; reshape them with SetGeometryCurve to W×H (the «Новый размер» template is 297×210 by default).

- Braces gone from plans (2026-10-30, «горизонталь связдар неге көрінбей тұр»): every StructuralType.Brace, horizontal ones included, draws through the framing sub-category «Вертикальные раскосы», and RU plan views hide it. Fix: `ShowBraces` (fix.cs) unhides every framing sub-category whose name contains «раскос», called from StyleView.
- Edit the user's file in place (they asked «неге файлды ашып жасамайсың»): job `mode=fix` (fix.cs FixInPlace) runs OpenDocumentFile on the album .rvt, makes the change, saves, then re-exports the PDF. This keeps the user's manual edits; prefer it over a full km2 rebuild for small fixes. Back up to `Revit\Мусор` first.

- **Live in the user's open Revit (preferred; user: «ашып қойып өзгерт, көріп отырайын»):**
  - Shim `rv\live\RBLive.dll` with manifest `RBLive.addin` (in Addins\2025) polls `%LOCALAPPDATA%\rvjob\live.txt` on Idling.
  - It loads the worker DLL named in `dll=` via Assembly.Load(bytes), so a rebuild needs no restart: compile all rv\*.cs to a new `live\w_HHmmss.dll`.
  - It calls `RB.App.LiveRun(UIApplication, J)` on the active document and writes `livedone.txt`.
  - Job keys: inline, bysection, declutter, famdir, pdf, save, noimg.
  - ActiveView cannot be set from Idling («temporarily disabled»); use RequestViewChange.
- Plan marks like the DWG (sheets 4–6): text along the member over its middle, no leader or shelf. Tag families «КМ_Марка по оси» / «…низ» use TagOrientation.AnyModelDirection. There is one mark per row/bay, and СВ3 wins over РС1. Trusses get the TextNote «Ферма Ф1/Ф2» rotated 90°; Ф1 = chord reaching Y > 8000 (inline.cs).

- 30.10 evening, sheets 7–10 brought to the DWG live. Code: rv\secdress.cs, braces.cs, sheet10.cs; run with `live\live.ps1 -Job "braces=1;secdress=1;sheet10=1;famdir={r}\Семейства"`.
  - Extra levels 4040/2920/2810/2300/2030; each section shows its own set (others hidden), short lines with heads on the L or R side, chain dims between them.
  - Shelf marks are TextNotes with leaders; the foundation is a FilledRegion «КМ_Бетон».
  - Details СВ1/СВ2/СВ3 at 1:25; the sections table is drawn on the sheet.
  - Gotchas:
    - Revit flips raw-box sections; use Sec() with origin = far plane, right = +X (the 3-3 recipe).
    - Level view curves must keep the datum's direction.
    - Detail views snap level lines back to the crop width; set them again in a last transaction.
    - Annotation crop offset defaults to 25.4 mm.
    - SheetTitle(StartsWith) caught the stamp's sheet-name text, so match exactly.
    - ';' is not allowed in sheet names.
    - A live job needs WM_MOUSEMOVE posted to Revit, or Idling never fires.
  - Node sheets 11–12 done live (rv\nodes.cs, job `nodes=1`):
    - per-node crop and scale (NodeSpec);
    - outline style (filter overrides keep only the line colour);
    - shelf TextNotes at member ends with collision avoidance;
    - width dims between two short detail lines, sized from КМ_Сечение. The tube families' Left/Right refs are the template's planes, which gave «500»;
    - concrete and +0,870 at nodes 1/2/13;
    - sheets laid out in rows with the bubbles redrawn.
  - Still open: dims on а-а/б-б, the «Закладная пластина Зд-1…» note; sheets 1–3 not compared yet.

Related: [[karasu-lk1-canopy]], [[revit-mcp-bridge]] (BEKA-2's way)
