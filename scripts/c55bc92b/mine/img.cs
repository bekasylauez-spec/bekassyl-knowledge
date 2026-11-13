var d = document; var sb = new StringBuilder(); string outDir = @"C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\mine\img\"; System.IO.Directory.CreateDirectory(outDir);
var views = new FilteredElementCollector(d).OfClass(typeof(View)).Cast<View>().Where(v => !v.IsTemplate && v.ViewType == ViewType.ThreeD).ToList();
sb.AppendLine("3D views: " + string.Join(" | ", views.Select(v => v.Name)));
var want = new[] { "КМ 3D Узел 6", "КМ 3D Узел 15", "КМ 3D Узел 5", "КМ 3D Узел 15 (г)", "КМ 3D Узел 15 (б)", "{3D}" };
int k = 0;
foreach (var nm in want)
{
    var v = views.FirstOrDefault(x => x.Name == nm); if (v == null) { sb.AppendLine("no view " + nm); continue; }
    string safe = "v" + (k++) + "_" + new string(nm.Select(c => char.IsLetterOrDigit(c) ? c : '_').ToArray());
    var opt = new ImageExportOptions(); opt.ExportRange = ExportRange.SetOfViews; opt.SetViewsAndSheets(new List<ElementId> { v.Id }); opt.FilePath = outDir + safe; opt.FitDirection = FitDirectionType.Horizontal;
    opt.HLRandWFViewsFileType = ImageFileType.PNG; opt.ShadowViewsFileType = ImageFileType.PNG; opt.ImageResolution = ImageResolution.DPI_150; opt.PixelSize = 1600; opt.ZoomType = ZoomFitType.FitToPage;
    try { d.ExportImage(opt); sb.AppendLine("exported " + nm + " -> " + safe); } catch (Exception ex) { sb.AppendLine("FAIL " + nm + ": " + ex.Message); }
}
return sb.ToString() + " modified=" + d.IsModified;
}
static void _end() {