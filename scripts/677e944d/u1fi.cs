// READ-ONLY: visible family instances in the two views + their view-geometry pieces clipped to crop (view coords)
var d = document; double M = 304.8; var ci = System.Globalization.CultureInfo.InvariantCulture;
try {
  var sb = new StringBuilder();
  foreach (long vid in new[] { 2901370L, 2901379L }) { var v = d.GetElement(new ElementId(vid)) as View; var cb = v.CropBox; var inv = cb.Transform.Inverse; var opt = new Options { View = v }; sb.AppendLine("=== " + v.Name + " crop u 0.." + (cb.Max.X * M).ToString("0", ci) + " v 0.." + (cb.Max.Y * M).ToString("0", ci) + " w " + (cb.Min.Z * M).ToString("0", ci) + "..0");
    foreach (var e in new FilteredElementCollector(d, v.Id).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>()) { if (e is AnnotationSymbol) continue; if (e.Category.CategoryType != CategoryType.Model) continue;
      sb.AppendLine(e.Id.Value + "\t" + e.Category.Name + "\t" + e.Symbol.Family.Name + " : " + e.Symbol.Name + "\t" + (e.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "") + "\tsuper=" + (e.SuperComponent == null ? "-" : e.SuperComponent.Id.Value.ToString()) + " subs=" + e.GetSubComponentIds().Count);
      var ge = e.get_Geometry(opt); if (ge == null) continue; int k = 0;
      Action<GeometryElement, string> walk = null; walk = (g0, pre) => { foreach (var g in g0) { if (g is GeometryInstance gi) { walk(gi.GetInstanceGeometry(), pre + ">"); continue; } var l = new List<XYZ>(); string kind = g.GetType().Name; if (g is Solid s) { if (s.Edges.Size == 0) continue; foreach (Edge ed in s.Edges) l.AddRange(ed.Tessellate()); kind += " f" + s.Faces.Size + " vol" + (s.Volume * M * M * M / 1000).ToString("0", ci); } else if (g is Curve c) l.AddRange(c.Tessellate()); else continue;
          double u0 = 1e9, v0 = 1e9, w0 = 1e9, u1 = -1e9, v1 = -1e9, w1 = -1e9; foreach (var p0 in l) { var p = inv.OfPoint(p0); u0 = Math.Min(u0, p.X); v0 = Math.Min(v0, p.Y); w0 = Math.Min(w0, p.Z); u1 = Math.Max(u1, p.X); v1 = Math.Max(v1, p.Y); w1 = Math.Max(w1, p.Z); }
          if (u1 * M < -50 || u0 > cb.Max.X + 50 / M || v1 * M < -50 || v0 > cb.Max.Y + 50 / M || w0 > 0.01 || w1 < cb.Min.Z - 0.01) continue; if (k++ > 40) continue;
          sb.AppendLine("   " + pre + kind + "\tu " + (u0 * M).ToString("0", ci) + ".." + (u1 * M).ToString("0", ci) + "\tv " + (v0 * M).ToString("0", ci) + ".." + (v1 * M).ToString("0", ci) + "\tw " + (w0 * M).ToString("0", ci) + ".." + (w1 * M).ToString("0", ci)); } };
      walk(ge, ""); } }
  return sb.ToString() + "modified=" + d.IsModified;
} catch (Exception e) { return "ERR " + e; }
