// probe: узел 8 1-A: гусет ↔ шов (вставка–труба)
var d = document; var sb = new StringBuilder();
var dss = new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => (x.ApplicationDataId ?? "") == "узел 8 | 1-A").ToList();
sb.AppendLine("DS count " + dss.Count);
DirectShape gus = dss.First(x => x.Name.Contains("гусет"));
DirectShape w = dss.First(x => x.Name.Contains("вставка–труба"));
var gs = QSolidsOf(gus);
foreach (var g in gs) sb.AppendLine("gusset bb " + string.Join(",", QBBox(g).Select(QF)) + " vol " + QF(QCu(g.Volume)));
int i = 0;
foreach (var s in QSolidsOf(w)) {
  sb.AppendLine("weld solid " + i + " vol " + QF(QCu(s.Volume)) + " bb " + string.Join(",", QBBox(s).Select(QF)));
  foreach (Edge e in s.Edges) { var c = e.AsCurve(); sb.AppendLine("    edge " + QF(c.GetEndPoint(0).X / QMM) + "," + QF(c.GetEndPoint(0).Y / QMM) + "," + QF(c.GetEndPoint(0).Z / QMM) + " -> " + QF(c.GetEndPoint(1).X / QMM) + "," + QF(c.GetEndPoint(1).Y / QMM) + "," + QF(c.GetEndPoint(1).Z / QMM)); }
  foreach (var g in gs) { try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(s, g, BooleanOperationsType.Intersect); sb.AppendLine("  inter " + QF(r == null ? 0 : QCu(r.Volume))); } catch (Exception ex) { sb.AppendLine("  inter FAIL"); } }
  i++; }
return sb.ToString();
}
