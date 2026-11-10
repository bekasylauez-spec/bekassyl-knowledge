var uiapp = new UIApplication(document.Application);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\pdf.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder(); var d = uiapp.ActiveUIDocument.Document;
  try {
    var sheets = new FilteredElementCollector(d).OfClass(typeof(ViewSheet)).Cast<ViewSheet>().Where(x => !x.IsPlaceholder).OrderBy(x => x.SheetNumber).ToList();
    foreach (var sh in sheets) sb.AppendLine("SHEET " + sh.SheetNumber + " " + sh.Name + " viewports " + sh.GetAllViewports().Count);
    var o = new PDFExportOptions { FileName = "В109_КМ_листы", Combine = true, ExportQuality = PDFExportQualityType.DPI600, ColorDepth = ColorDepthType.Color, ZoomType = ZoomType.Zoom, ZoomPercentage = 100, PaperFormat = ExportPaperFormat.Default, HideCropBoundaries = true, HideScopeBoxes = true, HideReferencePlane = true, HideUnreferencedViewTags = false };
    d.Export(@"D:\Бекасыл КЖ КМ\Завод_В109_КМ\_тексеру", sheets.Select(x => x.Id).ToList(), o); sb.AppendLine("pdf ok");
  } catch (Exception ex) { sb.AppendLine("ERR " + ex.Message); }
  System.IO.File.WriteAllText(log, sb.ToString()); };
uiapp.Idling += hnd; return "queued";
