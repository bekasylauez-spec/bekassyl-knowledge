// READ-ONLY: everything within a box around the column end of beam 2852689 (узел 1)
var d = document; double M = 304.8; var ci = System.Globalization.CultureInfo.InvariantCulture;
try {
  var bm = d.GetElement(new ElementId(2852689L)) as FamilyInstance; var ln = (bm.Location as LocationCurve).Curve as Line;
  XYZ a = ln.GetEndPoint(0), b = ln.GetEndPoint(1); XYZ c = a.Z < b.Z ? a : b; XYZ ax = (a.Z < b.Z ? b - a : a - b).Normalize();
  double R = 900 / M; var ol = new Outline(c - new XYZ(R, R, R), c + new XYZ(R, R, R));
  var sb = new StringBuilder(); sb.AppendLine("centre " + (c.X * M).ToString("0", ci) + "," + (c.Y * M).ToString("0", ci) + "," + (c.Z * M).ToString("0", ci) + " beamdir " + ax.X.ToString("0.000", ci) + "," + ax.Y.ToString("0.000", ci) + "," + ax.Z.ToString("0.000", ci));
  Func<BoundingBoxXYZ, string> B = bb => ((bb.Min.X - c.X) * M).ToString("0", ci) + ".." + ((bb.Max.X - c.X) * M).ToString("0", ci) + " | " + ((bb.Min.Y - c.Y) * M).ToString("0", ci) + ".." + ((bb.Max.Y - c.Y) * M).ToString("0", ci) + " | " + ((bb.Min.Z - c.Z) * M).ToString("0", ci) + ".." + ((bb.Max.Z - c.Z) * M).ToString("0", ci);
  foreach (var e in new FilteredElementCollector(d).WherePasses(new BoundingBoxIntersectsFilter(ol)).WhereElementIsNotElementType()) {
    if (e.Category == null) continue; var bb = e.get_BoundingBox(null); if (bb == null) continue;
    if (e is FamilyInstance fi) { string mk = fi.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? ""; sb.AppendLine("M\t" + e.Id.Value + "\t" + mk + "\t" + fi.Symbol.Family.Name + " : " + fi.Symbol.Name + "\t" + B(bb)); }
    else if (e is DirectShape ds) { double vol = 0; PlanarFace big = null; foreach (var g in ds.get_Geometry(new Options())) { var s = g as Solid; if (s == null) continue; vol += s.Volume; foreach (Face f in s.Faces) { var pf = f as PlanarFace; if (pf != null && (big == null || pf.Area > big.Area)) big = pf; } }
      string n = big == null ? "" : "t=" + (vol / big.Area * M).ToString("0.0", ci) + " n=" + big.FaceNormal.X.ToString("0.00", ci) + "," + big.FaceNormal.Y.ToString("0.00", ci) + "," + big.FaceNormal.Z.ToString("0.00", ci) + " A=" + (big.Area * M * M / 100).ToString("0", ci) + "cm2";
      sb.AppendLine("D\t" + e.Id.Value + "\t" + ds.ApplicationDataId + "\t" + e.Category.Name + " : " + e.Name + "\t" + B(bb) + "\t" + n); }
  }
  // views on sheets named like узел 1
  foreach (var vs in new FilteredElementCollector(d).OfClass(typeof(ViewSheet)).Cast<ViewSheet>()) { if (!(vs.Name ?? "").Contains("Узел 1") && !(vs.Name ?? "").Contains("узел 1")) continue; sb.AppendLine("SHEET " + vs.SheetNumber + " " + vs.Name);
    foreach (var vid in vs.GetAllPlacedViews()) { var v = d.GetElement(vid) as View; var cb = v.CropBox; var t = cb.Transform; sb.AppendLine("  V " + v.Id.Value + " " + v.Name + " type " + v.ViewType + " dir " + v.ViewDirection.X.ToString("0.00", ci) + "," + v.ViewDirection.Y.ToString("0.00", ci) + "," + v.ViewDirection.Z.ToString("0.00", ci) + " org-c " + ((t.Origin.X - c.X) * M).ToString("0", ci) + "," + ((t.Origin.Y - c.Y) * M).ToString("0", ci) + "," + ((t.Origin.Z - c.Z) * M).ToString("0", ci) + " crop " + (cb.Min.X * M).ToString("0", ci) + ".." + (cb.Max.X * M).ToString("0", ci) + " ; " + (cb.Min.Y * M).ToString("0", ci) + ".." + (cb.Max.Y * M).ToString("0", ci) + " ; depth " + (cb.Min.Z * M).ToString("0", ci) + ".." + (cb.Max.Z * M).ToString("0", ci) + " farclip " + v.get_Parameter(BuiltInParameter.VIEWER_BOUND_OFFSET_FAR)?.AsValueString()); } }
  return sb.ToString() + "modified=" + d.IsModified;
} catch (Exception e) { return "ERR " + e; }
