// READ-ONLY: elements visible in views 2901370 / 2901379 by category; non-solid ones with position in view coords
var d = document; double M = 304.8; var ci = System.Globalization.CultureInfo.InvariantCulture;
try {
  var sb = new StringBuilder();
  foreach (long vid in new[] { 2901370L, 2901379L }) {
    var v = d.GetElement(new ElementId(vid)) as View; var cb = v.CropBox; var inv = cb.Transform.Inverse; sb.AppendLine("=== " + v.Name + " detail=" + v.DetailLevel + " style=" + v.DisplayStyle + " discipline=" + v.Discipline);
    var cnt = new Dictionary<string, int>();
    foreach (var e in new FilteredElementCollector(d, v.Id).WhereElementIsNotElementType()) {
      string k = (e.Category == null ? "(no cat)" : e.Category.Name) + " / " + e.GetType().Name; int n; cnt.TryGetValue(k, out n); cnt[k] = n + 1;
      bool interesting = e is CurveElement || e is ReferencePlane || (e is FamilyInstance fi0 && !fi0.Symbol.Family.Name.StartsWith("(КМ)")) || e.Category == null || (e.Category != null && (e.Category.Name.Contains("Аналит") || e.Category.Name.Contains("Линии")));
      if (!interesting) continue; var bb = e.get_BoundingBox(v); if (bb == null) bb = e.get_BoundingBox(null); string pos = "";
      if (bb != null) { double u0 = 1e9, v0 = 1e9, w0 = 1e9, u1 = -1e9, v1 = -1e9, w1 = -1e9; foreach (var x in new[] { bb.Min.X, bb.Max.X }) foreach (var y in new[] { bb.Min.Y, bb.Max.Y }) foreach (var z in new[] { bb.Min.Z, bb.Max.Z }) { var p = inv.OfPoint(bb.Transform.OfPoint(new XYZ(x, y, z))); u0 = Math.Min(u0, p.X); v0 = Math.Min(v0, p.Y); w0 = Math.Min(w0, p.Z); u1 = Math.Max(u1, p.X); v1 = Math.Max(v1, p.Y); w1 = Math.Max(w1, p.Z); }
        pos = "u " + (u0 * M).ToString("0", ci) + ".." + (u1 * M).ToString("0", ci) + " v " + (v0 * M).ToString("0", ci) + ".." + (v1 * M).ToString("0", ci) + " w " + (w0 * M).ToString("0", ci) + ".." + (w1 * M).ToString("0", ci); }
      string fam = e is FamilyInstance fi ? fi.Symbol.Family.Name + " : " + fi.Symbol.Name + " | " + (fi.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "") : e.Name;
      sb.AppendLine("  " + e.Id.Value + "\t" + k + "\t" + fam + "\t" + pos + "\thidden=" + e.IsHidden(v)); }
    foreach (var kv in cnt.OrderByDescending(x => x.Value)) sb.AppendLine("  # " + kv.Value + "\t" + kv.Key); }
  return sb.ToString() + "modified=" + d.IsModified;
} catch (Exception e) { return "ERR " + e; }
