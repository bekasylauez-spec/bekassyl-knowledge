// probe: node 15 2-B-2 weld (вставка–труба) vs ГС2-701 tube: per-solid intersection + bbox of intersection
var d = document; var sb = new StringBuilder();
var tube = new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().FirstOrDefault(f => (f.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)?.AsString() ?? "") == "ГС2-701");
var ts = QSolidsOf(tube); sb.AppendLine("tube solids " + ts.Count + " bb " + string.Join(",", QBBox(ts[0]).Select(QF)));
var lc = (LocationCurve)tube.Location; sb.AppendLine("tube ends " + string.Join(" | ", new[] { 0, 1 }.Select(k => QF(lc.Curve.GetEndPoint(k).X / QMM) + "," + QF(lc.Curve.GetEndPoint(k).Y / QMM) + "," + QF(lc.Curve.GetEndPoint(k).Z / QMM))));
foreach (var ds in new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => (x.ApplicationDataId ?? "") == "узел 15 | 2-B-2" && x.Name.Contains("вставка–труба")))
{
    int i = 0;
    foreach (var s in QSolidsOf(ds))
    {
        var bb = QBBox(s); string how = "bool"; double v;
        try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(s, ts[0], BooleanOperationsType.Intersect); v = r == null ? 0 : QCu(r.Volume); if (r != null && r.Volume > 1e-9) sb.AppendLine("   inter bb " + string.Join(",", QBBox(r).Select(QF))); } catch { bool vs, fl; v = QOvlVol(s, ts[0], out vs, out fl); how = "shift"; }
        sb.AppendLine("weld#" + i + " vol " + QF(QCu(s.Volume)) + " bb " + string.Join(",", bb.Select(QF)) + " inter " + how + " " + QF(v)); i++;
    }
}
return sb.ToString();
}
