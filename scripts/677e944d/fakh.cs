// READ-ONLY: fachwerk members (+ columns, struts) with solid bbox and centroid, fachwerk node solids, PNG of sheets 27–31 and 3D node views 11/12.
var d = document; double M = 304.8; var sb = new StringBuilder(); var ss = new StringBuilder();
string dir = @"C:\Users\Admin\AppData\Local\Temp\claude\f4c3a78720b97f45\677e944d-f832-4f85-987d-aa96db42c8c8\scratchpad\f\";
System.IO.Directory.CreateDirectory(dir);
try {
  var gopt = new Options { DetailLevel = ViewDetailLevel.Fine };
  Func<XYZ, string> P = p => (p.X * M).ToString("0.0") + "\t" + (p.Y * M).ToString("0.0") + "\t" + (p.Z * M).ToString("0.0");
  sb.AppendLine("id\tmark\tax\tay\taz\tbx\tby\tbz\tx0\ty0\tz0\tx1\ty1\tz1\tcx\tcy\tcz\tvol_cm3");
  var marks = new HashSet<string> { "Рф1", "Ст2", "Ст3", "К1", "К2", "Р1", "СВ1" };
  foreach (var f in new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>()) {
    string mk = f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? ""; if (!marks.Contains(mk)) continue;
    var bb = f.get_BoundingBox(null); XYZ a, b;
    if (f.Location is LocationCurve lc) { a = lc.Curve.GetEndPoint(0); b = lc.Curve.GetEndPoint(1); } else { var lp = ((LocationPoint)f.Location).Point; a = new XYZ(lp.X, lp.Y, bb.Min.Z); b = new XYZ(lp.X, lp.Y, bb.Max.Z); }
    double vol = 0; XYZ c = XYZ.Zero;
    Action<GeometryElement> walk = null; walk = ge => { foreach (var g in ge) { if (g is Solid s && s.Volume > 1e-9) { c += s.ComputeCentroid() * s.Volume; vol += s.Volume; } else if (g is GeometryInstance gi) walk(gi.GetInstanceGeometry()); } };
    walk(f.get_Geometry(gopt)); if (vol > 0) c = c / vol;
    sb.AppendLine(f.Id.Value + "\t" + mk + "\t" + P(a) + "\t" + P(b) + "\t" + P(bb.Min) + "\t" + P(bb.Max) + "\t" + P(c) + "\t" + (vol * 28316.846592).ToString("0"));
  }
  System.IO.File.WriteAllText(dir + "fm.tsv", sb.ToString(), Encoding.UTF8);
  ss.AppendLine("data\tcat\tname\tvol_cm3\tx0\ty0\tz0\tx1\ty1\tz1\tfaces");
  foreach (var ds in new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел" && (x.ApplicationDataId == "узел 11" || x.ApplicationDataId == "узел 12" || x.ApplicationDataId == "узел 3"))) {
    foreach (var g in ds.get_Geometry(gopt)) { var s = g as Solid; if (s == null || s.Volume < 1e-9) continue; var b = s.GetBoundingBox(); var t = b.Transform;
      double x0 = 1e9, y0 = 1e9, z0 = 1e9, x1 = -1e9, y1 = -1e9, z1 = -1e9;
      foreach (var px in new[] { b.Min.X, b.Max.X }) foreach (var py in new[] { b.Min.Y, b.Max.Y }) foreach (var pz in new[] { b.Min.Z, b.Max.Z }) { var p = t.OfPoint(new XYZ(px, py, pz)) * M; x0 = Math.Min(x0, p.X); y0 = Math.Min(y0, p.Y); z0 = Math.Min(z0, p.Z); x1 = Math.Max(x1, p.X); y1 = Math.Max(y1, p.Y); z1 = Math.Max(z1, p.Z); }
      ss.AppendLine(ds.ApplicationDataId + "\t" + ds.Category.Name + "\t" + ds.Name.Substring(0, Math.Min(40, ds.Name.Length)) + "\t" + (s.Volume * 28316.846592).ToString("0.0") + "\t" + x0.ToString("0.0") + "\t" + y0.ToString("0.0") + "\t" + z0.ToString("0.0") + "\t" + x1.ToString("0.0") + "\t" + y1.ToString("0.0") + "\t" + z1.ToString("0.0") + "\t" + s.Faces.Size); } }
  System.IO.File.WriteAllText(dir + "fs.tsv", ss.ToString(), Encoding.UTF8);
  var ids = new List<ElementId>();
  foreach (var sh in new FilteredElementCollector(d).OfClass(typeof(ViewSheet)).Cast<ViewSheet>()) if (sh.Name.Contains("Развертка") || sh.Name.Contains("Узлы 11")) ids.Add(sh.Id);
  var opt = new ImageExportOptions { FilePath = dir + "s", ExportRange = ExportRange.SetOfViews, ZoomType = ZoomFitType.Zoom, Zoom = 100, ImageResolution = ImageResolution.DPI_300, HLRandWFViewsFileType = ImageFileType.PNG, ShadowViewsFileType = ImageFileType.PNG };
  opt.SetViewsAndSheets(ids); d.ExportImage(opt);
  var v3 = new FilteredElementCollector(d).OfClass(typeof(View3D)).Cast<View3D>().Where(x => !x.IsTemplate && (x.Name.Contains("Узел 11") || x.Name.Contains("Узел 12"))).Select(x => x.Id).ToList();
  if (v3.Count > 0) { var o3 = new ImageExportOptions { FilePath = dir + "v", ExportRange = ExportRange.SetOfViews, ZoomType = ZoomFitType.FitToPage, PixelSize = 1500, ImageResolution = ImageResolution.DPI_150, HLRandWFViewsFileType = ImageFileType.PNG, ShadowViewsFileType = ImageFileType.PNG, FitDirection = FitDirectionType.Horizontal }; o3.SetViewsAndSheets(v3); d.ExportImage(o3); }
  return "ok sheets " + ids.Count + " 3d " + v3.Count + " modified=" + d.IsModified;
} catch (Exception ex) { return "ERR " + ex; }
