// READ-ONLY: individual node solids near the column end of beam 2852689
var d = document; double M = 304.8; var ci = System.Globalization.CultureInfo.InvariantCulture;
try {
  var bm = d.GetElement(new ElementId(2852689L)) as FamilyInstance; var ln = (bm.Location as LocationCurve).Curve as Line;
  XYZ a = ln.GetEndPoint(0), b = ln.GetEndPoint(1); XYZ c = a.Z < b.Z ? a : b;
  var sb = new StringBuilder(); var opt = new Options { DetailLevel = ViewDetailLevel.Fine };
  foreach (var ds in new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел")) {
    if (ds.Category.Id.Value == (long)BuiltInCategory.OST_StructConnectionWelds) continue;
    foreach (var g in ds.get_Geometry(opt)) { var s = g as Solid; if (s == null || s.Volume < 1e-9) continue;
      double x0 = 1e9, y0 = 1e9, z0 = 1e9, x1 = -1e9, y1 = -1e9, z1 = -1e9;
      foreach (Edge e in s.Edges) foreach (var p in e.Tessellate()) { x0 = Math.Min(x0, p.X); y0 = Math.Min(y0, p.Y); z0 = Math.Min(z0, p.Z); x1 = Math.Max(x1, p.X); y1 = Math.Max(y1, p.Y); z1 = Math.Max(z1, p.Z); }
      double cx = ((x0 + x1) / 2 - c.X) * M, cy = ((y0 + y1) / 2 - c.Y) * M, cz = ((z0 + z1) / 2 - c.Z) * M;
      if (Math.Abs(cx) > 750 || cy < -500 || cy > 800 || cz < -750 || cz > 650) continue;
      PlanarFace big = null; foreach (Face f in s.Faces) { var pf = f as PlanarFace; if (pf != null && (big == null || pf.Area > big.Area)) big = pf; }
      bool bolt = ds.Category.Id.Value == (long)BuiltInCategory.OST_StructConnectionBolts;
      sb.AppendLine(ds.ApplicationDataId + (bolt ? " болт" : "") + "\t" + (bolt || big == null ? "" : "t=" + (s.Volume / big.Area * M).ToString("0.0", ci) + " A=" + (big.Area * M * M / 100).ToString("0", ci) + " n=" + big.FaceNormal.X.ToString("0.00", ci) + "," + big.FaceNormal.Y.ToString("0.00", ci) + "," + big.FaceNormal.Z.ToString("0.00", ci)) + "\tx " + ((x0 - c.X) * M).ToString("0", ci) + ".." + ((x1 - c.X) * M).ToString("0", ci) + "\ty " + ((y0 - c.Y) * M).ToString("0", ci) + ".." + ((y1 - c.Y) * M).ToString("0", ci) + "\tz " + ((z0 - c.Z) * M).ToString("0", ci) + ".." + ((z1 - c.Z) * M).ToString("0", ci)); } }
  return sb.ToString() + "modified=" + d.IsModified;
} catch (Exception e) { return "ERR " + e; }
