// READ-ONLY: export every sheet to PNG (150 dpi, 100 %) into the scratchpad.
var sb = new StringBuilder(); var d = document;
string dir = @"C:\Users\Admin\AppData\Local\Temp\claude\f4c3a78720b97f45\677e944d-f832-4f85-987d-aa96db42c8c8\scratchpad\png\";
System.IO.Directory.CreateDirectory(dir);
try {
  var ids = new FilteredElementCollector(d).OfClass(typeof(ViewSheet)).Cast<ViewSheet>().Select(x => x.Id).ToList();
  var opt = new ImageExportOptions { FilePath = dir + "s", ExportRange = ExportRange.SetOfViews, ZoomType = ZoomFitType.Zoom, Zoom = 100,
      ImageResolution = ImageResolution.DPI_150, HLRandWFViewsFileType = ImageFileType.PNG, ShadowViewsFileType = ImageFileType.PNG };
  opt.SetViewsAndSheets(ids); d.ExportImage(opt); sb.Append("exported " + ids.Count);
} catch (Exception ex) { sb.Append("ERR " + ex); }
return sb.ToString();
