// READ-ONLY (image export only): views of sheet 16
var d = document;
try {
  string dir = @"C:\Users\Admin\AppData\Local\Temp\claude\f4c3a78720b97f45\677e944d-f832-4f85-987d-aa96db42c8c8\scratchpad\img\"; System.IO.Directory.CreateDirectory(dir);
  var o = new ImageExportOptions { ExportRange = ExportRange.SetOfViews, FilePath = dir + "u1", HLRandWFViewsFileType = ImageFileType.PNG, ShadowViewsFileType = ImageFileType.PNG, ImageResolution = ImageResolution.DPI_300, ZoomType = ZoomFitType.FitToPage, PixelSize = 2600, FitDirection = FitDirectionType.Horizontal };
  o.SetViewsAndSheets(new List<ElementId> { new ElementId(2901370L), new ElementId(2901379L) });
  d.ExportImage(o);
  return "ok " + string.Join(" | ", System.IO.Directory.GetFiles(dir).Select(System.IO.Path.GetFileName)) + " modified=" + d.IsModified;
} catch (Exception e) { return "ERR " + e; }
