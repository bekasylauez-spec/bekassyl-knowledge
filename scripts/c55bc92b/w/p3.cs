// probe: pair of DS (ids) — solids bbox overlap + intersection volume per solid pair (direct bool / shift)
var d = document; var sb = new StringBuilder();
var A = QSolidsOf(d.GetElement(new ElementId(2857060L))); var B = QSolidsOf(d.GetElement(new ElementId(2857061L)));
int i = 0;
foreach (var sa in A) { int j = 0; foreach (var sbb in B) {
    var ba = QBBox(sa); var bb = QBBox(sbb);
    bool ov = !(ba[0] > bb[3] + 0.3 || bb[0] > ba[3] + 0.3 || ba[1] > bb[4] + 0.3 || bb[1] > ba[4] + 0.3 || ba[2] > bb[5] + 0.3 || bb[2] > ba[5] + 0.3);
    if (ov) {
        string how = "bool"; double v;
        try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(sa, sbb, BooleanOperationsType.Intersect); v = r == null ? 0 : QCu(r.Volume); } catch { bool vs, fl; v = QOvlVol(sa, sbb, out vs, out fl); how = fl ? "FAIL" : "shift"; }
        sb.AppendLine("A#" + i + " B#" + j + " " + how + " v=" + QF(v) + " A bb " + string.Join(",", ba.Select(QF)) + " B bb " + string.Join(",", bb.Select(QF)));
    }
    j++; } i++; }
return sb.ToString();
}
