// READ-ONLY: which visible elements have edges inside given regions of the view (view coords, mm)
var d = document; double M = 304.8; var ci = System.Globalization.CultureInfo.InvariantCulture;
try {
  var sb = new StringBuilder();
  var jobs = new[] { new { vid = 2901370L, n = "main mid-lines", u0 = 160.0, u1 = 840.0, v0 = 365.0, v1 = 480.0 }, new { vid = 2901370L, n = "main top items", u0 = 380.0, u1 = 980.0, v0 = 600.0, v1 = 720.0 }, new { vid = 2901379L, n = "1-1 top left", u0 = -20.0, u1 = 160.0, v0 = 1060.0, v1 = 1300.0 }, new { vid = 2901379L, n = "1-1 top right", u0 = 330.0, u1 = 540.0, v0 = 1060.0, v1 = 1300.0 } };
  foreach (var j in jobs) { var v = d.GetElement(new ElementId(j.vid)) as View; var cb = v.CropBox; var inv = cb.Transform.Inverse; var opt = new Options { View = v }; sb.AppendLine("=== " + v.Name + " : " + j.n + " u " + j.u0 + ".." + j.u1 + " v " + j.v0 + ".." + j.v1);
    foreach (var e in new FilteredElementCollector(d, v.Id).WhereElementIsNotElementType()) { if (!(e is FamilyInstance) && !(e is DirectShape)) continue; if (!(e is DirectShape) || e.Category.Name == "Соединения несущих конструкций") continue; if (e is AnnotationSymbol) continue; GeometryElement ge = null; try { ge = e.get_Geometry(opt); } catch { } if (ge == null) continue;
      int n = 0; double w0 = 1e9, w1 = -1e9, a0 = 1e9, a1 = -1e9, b0 = 1e9, b1 = -1e9; int nsol = 0;
      Action<GeometryElement> walk = null; walk = g0 => { foreach (var g in g0) { if (g is GeometryInstance gi) { walk(gi.GetInstanceGeometry()); continue; } IEnumerable<XYZ> pts = null; if (g is Solid s) { if (s.Edges.Size == 0) continue; var l = new List<XYZ>(); foreach (Edge ed in s.Edges) { var tt = ed.Tessellate(); for (int q = 0; q + 1 < tt.Count; q++) for (int r = 0; r <= 40; r++) l.Add(tt[q] + (tt[q + 1] - tt[q]) * (r / 40.0)); } pts = l; nsol++; } else if (g is Curve c) { var tt = c.Tessellate(); var l2 = new List<XYZ>(); for (int q = 0; q + 1 < tt.Count; q++) for (int r = 0; r <= 40; r++) l2.Add(tt[q] + (tt[q + 1] - tt[q]) * (r / 40.0)); pts = l2; } if (pts == null) continue;
          foreach (var p0 in pts) { var p = inv.OfPoint(p0); double u = p.X * M, vv = p.Y * M, w = p.Z * M; if (u < j.u0 || u > j.u1 || vv < j.v0 || vv > j.v1) continue; if (w > 1 || w < cb.Min.Z * M - 1) continue; n++; w0 = Math.Min(w0, w); w1 = Math.Max(w1, w); a0 = Math.Min(a0, u); a1 = Math.Max(a1, u); b0 = Math.Min(b0, vv); b1 = Math.Max(b1, vv); } } };
      walk(ge); if (n == 0) continue;
      string nm = e is FamilyInstance fi ? fi.Symbol.Family.Name + " | " + (fi.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "") : ((DirectShape)e).ApplicationDataId + " / " + e.Category.Name;
      sb.AppendLine("  " + e.Id.Value + "\t" + nm + "\tname=" + e.Name + "\tpts " + n + " sol " + nsol + "\tu " + a0.ToString("0", ci) + ".." + a1.ToString("0", ci) + "\tv " + b0.ToString("0", ci) + ".." + b1.ToString("0", ci) + "\tw " + w0.ToString("0", ci) + ".." + w1.ToString("0", ci)); } }
  return sb.ToString() + "modified=" + d.IsModified;
} catch (Exception e) { return "ERR " + e; }

