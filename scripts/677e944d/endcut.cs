// READ-ONLY: end-face orientation of every sloped (КМ) framing member vs vertical
var d = document; double M = 304.8; var ci = System.Globalization.CultureInfo.InvariantCulture;
try {
  var opt = new Options { DetailLevel = ViewDetailLevel.Fine };
  var cnt = new Dictionary<string, int>(); var ex = new Dictionary<string, string>();
  foreach (var f in new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Symbol.Family.Name.StartsWith("(КМ)"))) {
    var lc = f.Location as LocationCurve; if (lc == null) continue; var ln = lc.Curve as Line; if (ln == null) continue;
    XYZ ax = ln.Direction; double slope = Math.Asin(Math.Abs(ax.Z)) * 180 / Math.PI; if (slope < 0.5 || slope > 60) continue;
    string mk = f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "";
    var sols = new List<Solid>(); Action<GeometryElement> walk = null; walk = ge => { foreach (var g in ge) { if (g is Solid s && s.Volume > 1e-9) sols.Add(s); else if (g is GeometryInstance gi) walk(gi.GetInstanceGeometry()); } };
    walk(f.get_Geometry(opt));
    foreach (int end in new[] { 0, 1 }) {
      PlanarFace best = null; double bq = end == 0 ? 1e9 : -1e9;
      foreach (var s in sols) foreach (Face fc in s.Faces) { var pf = fc as PlanarFace; if (pf == null) continue; if (Math.Abs(pf.FaceNormal.DotProduct(ax)) < 0.7) continue; if (pf.Area * M * M < 300) continue;
        double q = (pf.Origin - ln.GetEndPoint(0)).DotProduct(ax); if (end == 0 ? q < bq : q > bq) { bq = q; best = pf; } }
      if (best == null) continue;
      double tilt = Math.Asin(Math.Abs(best.FaceNormal.Z)) * 180 / Math.PI; // 0 = vertical cut
      string kind = tilt < 0.2 ? "тік (колоннаға параллель)" : (Math.Abs(tilt - slope) < 0.2 ? "осіне 90° (ҚИҒАШ)" : "басқа " + tilt.ToString("0.0", ci));
      string k = mk + "\t" + f.Symbol.Name + "\tеңіс " + slope.ToString("0.00", ci) + "°\t" + kind;
      int v; cnt.TryGetValue(k, out v); cnt[k] = v + 1; if (!ex.ContainsKey(k)) ex[k] = f.Id.Value + " end" + end;
    }
  }
  var sb = new StringBuilder(); foreach (var kv in cnt.OrderBy(x => x.Key)) sb.AppendLine(kv.Value + "\t" + kv.Key + "\t" + ex[kv.Key]);
  return sb.ToString() + "modified=" + d.IsModified;
} catch (Exception e) { return "ERR " + e; }
