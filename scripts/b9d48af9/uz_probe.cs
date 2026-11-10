// Probe the local sample node rvt: families, sheets, viewports, types; export the sheet PNG; extract annotation families.
var app = document.Application; var uiapp = new UIApplication(app);
string src = @"D:\Бекасыл КЖ КМ\Узлы_КМ\БК-КМ_Узел_20К1-25Б1.rvt";
string outd = @"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\uz_probe\";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder();
  Document d = null;
  try {
    System.IO.Directory.CreateDirectory(outd); System.IO.Directory.CreateDirectory(outd + "fam");
    var mp = ModelPathUtils.ConvertUserVisiblePathToModelPath(src);
    var oo = new OpenOptions(); d = app.OpenDocumentFile(mp, oo);
    sb.AppendLine("opened " + d.Title);
    foreach (Family f in new FilteredElementCollector(d).OfClass(typeof(Family)).Cast<Family>().OrderBy(x => x.FamilyCategory?.Name).ThenBy(x => x.Name))
    {
      sb.AppendLine("FAM\t" + f.FamilyCategory?.Name + "\t" + f.Name + "\t" + (f.IsEditable ? "ed" : ""));
      if (f.IsEditable && f.FamilyCategory != null && (f.Name.StartsWith("БК") || f.FamilyCategory.CategoryType == CategoryType.Annotation))
      {
        try { var fd = d.EditFamily(f); var p = outd + @"fam\" + f.Name + ".rfa"; fd.SaveAs(p, new SaveAsOptions { OverwriteExistingFile = true }); fd.Close(false); sb.AppendLine("  saved " + p); }
        catch (Exception ex) { sb.AppendLine("  noextract " + ex.Message); }
      }
    }
    foreach (ViewSheet sh in new FilteredElementCollector(d).OfClass(typeof(ViewSheet)).Cast<ViewSheet>())
    {
      sb.AppendLine("SHEET\t" + sh.SheetNumber + "\t" + sh.Name);
      foreach (var vpId in sh.GetAllViewports()) { var vp = (Viewport)d.GetElement(vpId); var v = (View)d.GetElement(vp.ViewId);
        var bo = vp.GetBoxOutline(); sb.AppendLine("  VP\t" + v.ViewType + "\t" + v.Name + "\t1:" + v.Scale + "\tdetail " + v.DetailLevel + "\tdisp " + v.DisplayStyle + "\ttmpl " + (v.ViewTemplateId == ElementId.InvalidElementId ? "-" : d.GetElement(v.ViewTemplateId).Name) + "\tvptype " + d.GetElement(vp.GetTypeId())?.Name + "\tbox " + Math.Round(bo.MinimumPoint.X*304.8) + "," + Math.Round(bo.MinimumPoint.Y*304.8) + " " + Math.Round(bo.MaximumPoint.X*304.8) + "," + Math.Round(bo.MaximumPoint.Y*304.8));
        var cnt = new FilteredElementCollector(d, v.Id).WhereElementIsNotElementType().ToElements().Where(x => x.Category != null && x.Category.CategoryType == CategoryType.Annotation).GroupBy(x => x.Category.Name + "|" + d.GetElement(x.GetTypeId())?.Name).Select(g => g.Key + " x" + g.Count());
        sb.AppendLine("    ANN " + string.Join("; ", cnt)); }
      var opt = new ImageExportOptions { FilePath = outd + "sheet_" + sh.SheetNumber, ExportRange = ExportRange.SetOfViews, ZoomType = ZoomFitType.FitToPage, PixelSize = 3000, ImageResolution = ImageResolution.DPI_300, HLRandWFViewsFileType = ImageFileType.PNG, ShadowViewsFileType = ImageFileType.PNG, FitDirection = FitDirectionType.Horizontal };
      opt.SetViewsAndSheets(new List<ElementId> { sh.Id }); d.ExportImage(opt);
    }
    foreach (var tt in new FilteredElementCollector(d).OfClass(typeof(TextNoteType)).Cast<TextNoteType>()) sb.AppendLine("TEXT\t" + tt.Name + "\t" + Math.Round(tt.get_Parameter(BuiltInParameter.TEXT_SIZE).AsDouble()*304.8,2) + "\t" + tt.get_Parameter(BuiltInParameter.TEXT_FONT).AsString());
    foreach (var dt in new FilteredElementCollector(d).OfClass(typeof(DimensionType)).Cast<DimensionType>()) { var ts = dt.get_Parameter(BuiltInParameter.TEXT_SIZE); if (ts != null && ts.AsDouble() > 0) sb.AppendLine("DIM\t" + dt.StyleType + "\t" + dt.Name + "\t" + Math.Round(ts.AsDouble()*304.8,2)); }
    foreach (var v in new FilteredElementCollector(d).OfClass(typeof(View)).Cast<View>().Where(x => x.IsTemplate)) sb.AppendLine("TMPL\t" + v.ViewType + "\t" + v.Name);
  } catch (Exception ex) { sb.AppendLine("ERR " + ex); }
  try { if (d != null) d.Close(false); } catch (Exception ex) { sb.AppendLine("close " + ex.Message); }
  System.IO.File.WriteAllText(outd + "probe.txt", sb.ToString()); };
uiapp.Idling += hnd;
return "queued";
