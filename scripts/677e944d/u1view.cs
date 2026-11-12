// READ-ONLY: what lies inside the view volume of "Узел 1" main view (2901370) and "Разрез 1-1" (2901379)
var d = document; double M = 304.8; var ci = System.Globalization.CultureInfo.InvariantCulture;
try {
  var sb = new StringBuilder(); var opt = new Options { DetailLevel = ViewDetailLevel.Fine };
  var all = new List<Tuple<string, Solid>>();
  foreach (var f in new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>()) {
    string mk = f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? ""; var ge = f.get_Geometry(opt); if (ge == null) continue;
    Action<GeometryElement> walk = null; walk = g0 => { foreach (var g in g0) { if (g is Solid s && s.Volume > 1e-9) all.Add(Tuple.Create("M " + f.Id.Value + " " + mk + " [" + f.Symbol.Family.Name + "]", s)); else if (g is GeometryInstance gi) walk(gi.GetInstanceGeometry()); } }; walk(ge); }
  foreach (var ds in new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>()) { foreach (var g in ds.get_Geometry(opt)) { var s = g as Solid; if (s != null && s.Volume > 1e-9) all.Add(Tuple.Create("D " + ds.ApplicationDataId + " / " + ds.Category.Name, s)); } }
  foreach (long vid in new[] { 2901370L, 2901379L }) {
    var v = d.GetElement(new ElementId(vid)) as View; var cb = v.CropBox; var inv = cb.Transform.Inverse; sb.AppendLine("=== " + v.Name + "  (u=right, v=up, w=depth toward viewer; visible w " + (cb.Min.Z * M).ToString("0", ci) + "..0)");
    var rows = new List<Tuple<double, string>>();
    foreach (var t in all) { double u0 = 1e9, v0 = 1e9, w0 = 1e9, u1 = -1e9, v1 = -1e9, w1 = -1e9;
      foreach (Edge e in t.Item2.Edges) foreach (var p0 in e.Tessellate()) { var p = inv.OfPoint(p0); u0 = Math.Min(u0, p.X); v0 = Math.Min(v0, p.Y); w0 = Math.Min(w0, p.Z); u1 = Math.Max(u1, p.X); v1 = Math.Max(v1, p.Y); w1 = Math.Max(w1, p.Z); }
      if (u1 < cb.Min.X || u0 > cb.Max.X || v1 < cb.Min.Y || v0 > cb.Max.Y || w1 < cb.Min.Z || w0 > 0) continue;
      if (t.Item1.Contains("Болты") || t.Item1.Contains("швы")) continue;
      rows.Add(Tuple.Create(-v1, t.Item1 + "\tu " + (u0 * M).ToString("0", ci) + ".." + (u1 * M).ToString("0", ci) + "\tv " + (v0 * M).ToString("0", ci) + ".." + (v1 * M).ToString("0", ci) + "\tw " + (w0 * M).ToString("0", ci) + ".." + (w1 * M).ToString("0", ci) + "\tvol " + (t.Item2.Volume * M * M * M / 1000).ToString("0", ci) + "cm3")); }
    foreach (var r in rows.OrderBy(x => x.Item1)) sb.AppendLine(r.Item2); }
  return sb.ToString() + "modified=" + d.IsModified;
} catch (Exception e) { return "ERR " + e; }
