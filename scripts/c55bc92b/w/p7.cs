var d = document; var sb = new StringBuilder();
var F = QSolidsOf(d.GetElement(new ElementId(2842762L)));
foreach (var w in QSolidsOf(d.GetElement(new ElementId(2946893L)))) { foreach (var f in F) { double v = 0; try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(w, f, BooleanOperationsType.Intersect); if (r != null && r.Volume > 1e-9) { v = QCu(r.Volume); sb.AppendLine("weld bb " + string.Join(",", QBBox(w).Select(QF)) + " vol " + QF(QCu(w.Volume)) + " inter " + QF(v) + " interbb " + string.Join(",", QBBox(r).Select(QF))); } } catch { sb.AppendLine("fail"); } } }
return sb.ToString();
}