{ var expDoc = System.IO.File.ReadAllText(@"D:\Бекасыл КЖ КМ\3602_Порталы_КМ\_авто\_expect_doc.txt", System.Text.Encoding.UTF8).Trim(); if (document.Title != expDoc) return "WRONG DOC: «" + document.Title + "»"; }
const double MM = 304.8;
var L = new System.Text.StringBuilder(); var FAILS = new List<string>();
try {
var opt = new Options { DetailLevel = ViewDetailLevel.Fine };
Func<Element, List<Solid>> sols = e => { var r = new List<Solid>(); var g = e.get_Geometry(opt); if (g == null) return r;
    foreach (var go in g) { IEnumerable<GeometryObject> objs = go is GeometryInstance gi ? gi.GetInstanceGeometry().Cast<GeometryObject>() : new[] { go };
        foreach (var x in objs) { var s = x as Solid; if (s != null && s.Volume > 1e-9) r.Add(s); } } return r; };
Func<Solid, double[]> bb = s => { double[] r = { 1e18, 1e18, 1e18, -1e18, -1e18, -1e18 };
    foreach (Edge ed in s.Edges) foreach (var p in ed.Tessellate()) { var q = new[] { p.X * MM, p.Y * MM, p.Z * MM }; for (int i = 0; i < 3; i++) { if (q[i] < r[i]) r[i] = q[i]; if (q[i] > r[i + 3]) r[i + 3] = q[i]; } } return r; };
Func<IEnumerable<double[]>, double[]> ubb = ls => { double[] r = { 1e18, 1e18, 1e18, -1e18, -1e18, -1e18 }; foreach (var b in ls) for (int i = 0; i < 3; i++) { if (b[i] < r[i]) r[i] = b[i]; if (b[i + 3] > r[i + 3]) r[i + 3] = b[i + 3]; } return r; };
Func<double[], double[], double> dist = (p, q) => { double dx = Math.Max(0, Math.Max(p[0] - q[3], q[0] - p[3])), dy = Math.Max(0, Math.Max(p[1] - q[4], q[1] - p[4])), dz = Math.Max(0, Math.Max(p[2] - q[5], q[2] - p[5])); return Math.Sqrt(dx * dx + dy * dy + dz * dz); };
Func<double[], double[], double> distXY = (p, q) => { double dx = Math.Max(0, Math.Max(p[0] - q[3], q[0] - p[3])), dy = Math.Max(0, Math.Max(p[1] - q[4], q[1] - p[4])); return Math.Sqrt(dx * dx + dy * dy); };
Func<Solid, Solid, double> ix = (a, b) => { try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(a, b, BooleanOperationsType.Intersect); return r == null ? 0 : r.Volume * MM * MM * MM; } catch { return -1; } };
Func<double[], string> F = b => "[" + Math.Round(b[0], 1) + ".." + Math.Round(b[3], 1) + " | " + Math.Round(b[1], 1) + ".." + Math.Round(b[4], 1) + " | " + Math.Round(b[2], 1) + ".." + Math.Round(b[5], 1) + "]";
var dsAll = new FilteredElementCollector(document).OfClass(typeof(DirectShape)).Cast<DirectShape>().ToList();
Func<Element, string> mk = d => d.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)?.AsString() ?? "";
var pl2 = dsAll.Where(d => mk(d) == "ПЛ2").ToList(); var pl5 = dsAll.Where(d => mk(d) == "ПЛ5").ToList();
var wRib = dsAll.Where(d => mk(d) == "шов kf=3" && d.Name == "шов ребро").ToList(); var wPl = dsAll.Where(d => mk(d) == "шов kf=3" && d.Name == "шов пластина").ToList();
var other = dsAll.Where(d => { var m = mk(d); return m == "ПЛ1" || m == "ПЛ4" || m == "ПЛ2" || m == "ПЛ3"; }).ToList();
L.AppendLine("ПЛ2 " + pl2.Count + ", ПЛ5 " + pl5.Count + ", шов ребро " + wRib.Count + ", шов пластина " + wPl.Count + ", ПЛ1 " + dsAll.Count(d => mk(d) == "ПЛ1") + ", ПЛ4 " + dsAll.Count(d => mk(d) == "ПЛ4") + ", ПЛ3 " + dsAll.Count(d => mk(d) == "ПЛ3"));
var fr = new FilteredElementCollector(document).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().Cast<FamilyInstance>()
    .Where(f => f.Symbol.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_MARK)?.AsString() != "шов").ToList();
var conc = new List<Element>();
foreach (var bc in new[] { BuiltInCategory.OST_Floors, BuiltInCategory.OST_Walls, BuiltInCategory.OST_StructuralFoundation })
    conc.AddRange(new FilteredElementCollector(document).OfCategory(bc).WhereElementIsNotElementType());
var concBB = conc.Select(e => new { e, b = e.get_BoundingBox(null) }).Where(x => x.b != null).Select(x => new { x.e, b = new[] { x.b.Min.X * MM, x.b.Min.Y * MM, x.b.Min.Z * MM, x.b.Max.X * MM, x.b.Max.Y * MM, x.b.Max.Z * MM } }).ToList();
foreach (var d in pl2)
{
    var ss = sols(d); if (ss.Count == 0) { FAILS.Add("ПЛ2 " + d.Id + " no solids"); continue; }
    var plate = ss.OrderByDescending(s => s.Volume).First(); var pb = bb(plate);
    var anc = ss.Where(s => s != plate).Select(s => new { s, b = bb(s) }).ToList();
    double cx = (pb[0] + pb[3]) / 2, cy = (pb[1] + pb[4]) / 2, top = pb[5], bot = pb[2];
    string tag = "ПЛ2 #" + d.Id + " (" + Math.Round(cx) + "," + Math.Round(cy) + ",z" + Math.Round(bot, 1) + ") ";
    var sb = new System.Text.StringBuilder(tag);
    sb.Append("плита " + Math.Round(pb[3] - pb[0], 1) + "x" + Math.Round(pb[4] - pb[1], 1) + "x" + Math.Round(pb[5] - pb[2], 1));
    if (Math.Abs(pb[3] - pb[0] - 200) > 0.1 || Math.Abs(pb[4] - pb[1] - 200) > 0.1 || Math.Abs(pb[5] - pb[2] - 10) > 0.1) FAILS.Add(tag + "плита не 200x200x10");
    FamilyInstance tube = null;
    foreach (var f in fr) { var c = ((LocationCurve)f.Location).Curve; var a = c.GetEndPoint(0); var b = c.GetEndPoint(1);
        if (Math.Abs(a.X - b.X) > 1e-6 || Math.Abs(a.Y - b.Y) > 1e-6) continue; if (Math.Abs(a.X * MM - cx) > 3 || Math.Abs(a.Y * MM - cy) > 3) continue;
        if (Math.Abs(Math.Min(a.Z, b.Z) * MM - bot) < 2) { tube = f; break; } }
    if (tube == null) { FAILS.Add(tag + "ТРУБА над плитой не найдена"); L.AppendLine(sb.ToString() + " NO TUBE"); continue; }
    var tsol = sols(tube); Solid ts = null; foreach (var s in tsol) { try { ts = ts == null ? s : BooleanOperationsUtils.ExecuteBooleanOperation(ts, s, BooleanOperationsType.Union); } catch { if (ts == null) ts = s; } }
    var tb = ubb(tsol.Select(bb)); double gap = tb[2] - top;
    sb.Append(" | труба #" + tube.Id + " " + tube.Symbol.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_MARK)?.AsString() + " " + tube.Symbol.Name + " " + F(tb) + " зазор до плиты " + Math.Round(gap, 2));
    if (Math.Abs(gap - 0.3) > 0.06) FAILS.Add(tag + "зазор труба-плита " + Math.Round(gap, 2) + " (ждём 0.3)");
    double tcx = (tb[0] + tb[3]) / 2, tcy = (tb[1] + tb[4]) / 2;
    if (Math.Abs(tcx - cx) > 0.5 || Math.Abs(tcy - cy) > 0.5) FAILS.Add(tag + "труба не по центру плиты (" + Math.Round(tcx - cx, 1) + "," + Math.Round(tcy - cy, 1) + ")");
    double tw = tb[3] - tb[0], th = tb[4] - tb[1]; sb.Append(" сеч " + Math.Round(tw, 1) + "x" + Math.Round(th, 1));
    var cc = concBB.Where(x => cx > x.b[0] - 1 && cx < x.b[3] + 1 && cy > x.b[1] - 1 && cy < x.b[4] + 1 && Math.Abs(x.b[5] - bot) <= 30).OrderBy(x => Math.Abs(x.b[5] - bot)).FirstOrDefault();
    if (cc == null) { var near = concBB.Where(x => cx > x.b[0] - 1 && cx < x.b[3] + 1 && cy > x.b[1] - 1 && cy < x.b[4] + 1 && x.b[5] >= bot - 600 && x.b[2] <= bot + 5).OrderBy(x => Math.Abs(x.b[5] - bot)).FirstOrDefault();
        sb.Append(" | ЖБ ЖОҚ" + (near != null ? " (ең жақыны " + near.e.Category.Name + " #" + near.e.Id + " үсті z" + Math.Round(near.b[5], 1) + ")" : ""));
        FAILS.Add(tag + "плита ж/б бетінде тұрған жоқ" + (near != null ? "; ең жақыны " + near.e.Category.Name + " #" + near.e.Id + " үсті z=" + Math.Round(near.b[5], 1) : "")); }
    else { double mg = Math.Min(Math.Min(pb[0] - cc.b[0], cc.b[3] - pb[3]), Math.Min(pb[1] - cc.b[1], cc.b[4] - pb[4]));
        sb.Append(" | ЖБ " + cc.e.Category.Name + " #" + cc.e.Id + " үсті z" + Math.Round(cc.b[5], 1) + " (саңылау " + Math.Round(bot - cc.b[5], 1) + ") жиекке дейін " + Math.Round(mg, 1));
        if (Math.Abs(bot - cc.b[5]) > 1) FAILS.Add(tag + "плита мен ж/б үсті арасы " + Math.Round(bot - cc.b[5], 1) + " мм (" + cc.e.Category.Name + " #" + cc.e.Id + ")");
        if (mg < 0) FAILS.Add(tag + "плита ж/б бетінің сыртына шығып тұр " + Math.Round(mg, 1) + " (" + cc.e.Category.Name + " #" + cc.e.Id + ")");
        var ab0 = anc.Count > 0 ? anc.Min(a2 => a2.b[2]) : bot; sb.Append(" анкер түбі " + Math.Round(ab0, 1) + " ж/б түбі " + Math.Round(cc.b[2], 1));
        if (ab0 < cc.b[2]) FAILS.Add(tag + "анкер ж/б түбінен өтіп кетті"); }
    var grp = anc.GroupBy(a2 => Math.Round((a2.b[0] + a2.b[3]) / 2, 0) + "|" + Math.Round((a2.b[1] + a2.b[4]) / 2, 0)).Select(g => new { g = g.ToList(), b = ubb(g.Select(x => x.b)) }).ToList();
    sb.Append(" | анкер " + grp.Count + " (" + anc.Count + " дене)");
    if (grp.Count != 4) FAILS.Add(tag + "анкер саны " + grp.Count + " ≠ 4");
    var gc = grp.Select(g => new[] { (g.b[0] + g.b[3]) / 2, (g.b[1] + g.b[4]) / 2 }).ToList();
    var xs = gc.Select(c0 => Math.Round(c0[0] - cx, 1)).Distinct().OrderBy(x => x).ToList(); var ys = gc.Select(c0 => Math.Round(c0[1] - cy, 1)).Distinct().OrderBy(x => x).ToList();
    sb.Append(" X-ofs " + string.Join("/", xs) + " Y-ofs " + string.Join("/", ys));
    if (grp.Count == 4 && (xs.Count != 2 || ys.Count != 2 || Math.Abs(xs[1] - xs[0] - 140) > 0.5 || Math.Abs(ys[1] - ys[0] - 140) > 0.5)) FAILS.Add(tag + "анкер аралығы 140 емес: X " + string.Join("/", xs) + " Y " + string.Join("/", ys));
    foreach (var g in grp)
    {
        double inpl = Math.Min(Math.Min(g.b[0] - pb[0], pb[3] - g.b[3]), Math.Min(g.b[1] - pb[1], pb[4] - g.b[4]));
        if (inpl < 0) FAILS.Add(tag + "анкер плитаның шетінен шықты " + Math.Round(inpl, 1));
        double dt = distXY(g.b, tb);
        if (dt < 3) FAILS.Add(tag + "анкер (" + Math.Round((g.b[0] + g.b[3]) / 2) + "," + Math.Round((g.b[1] + g.b[4]) / 2) + ") трубаға тым жақын " + Math.Round(dt, 1));
    }
    sb.Append(" мин анкер–труба " + (grp.Count > 0 ? Math.Round(grp.Min(g => distXY(g.b, tb)), 1) : 0));
    foreach (var g in grp) foreach (var a2 in g.g) { double v = ts == null ? 0 : ix(a2.s, ts); if (v > 0.5) FAILS.Add(tag + "анкер ∩ труба " + Math.Round(v, 1) + " мм³"); }
    var rds = pl5.Where(p => { var b = p.get_BoundingBox(null); if (b == null) return false; var px = (b.Min.X + b.Max.X) / 2 * MM; var py = (b.Min.Y + b.Max.Y) / 2 * MM; return Math.Abs(px - cx) < 140 && Math.Abs(py - cy) < 140 && Math.Abs(b.Min.Z * MM - top) < 2; }).ToList();
    if (rds.Count != 1) { FAILS.Add(tag + "ПЛ5 DirectShape саны " + rds.Count + " (ждём 1)"); sb.Append(" | ПЛ5 DS " + rds.Count); }
    var ribs = rds.SelectMany(p => sols(p)).Select(s => new { s, b = bb(s) }).ToList();
    sb.Append(" | қабырға " + ribs.Count);
    if (ribs.Count != 4) FAILS.Add(tag + "қабырға саны " + ribs.Count + " ≠ 4");
    var dirs = new List<string>();
    foreach (var r in ribs)
    {
        double dTube = dist(r.b, tb); double dz = r.b[2] - top; double rcx = (r.b[0] + r.b[3]) / 2, rcy = (r.b[1] + r.b[4]) / 2;
        string dr = Math.Abs(rcx - tcx) > Math.Abs(rcy - tcy) ? (rcx > tcx ? "+X" : "-X") : (rcy > tcy ? "+Y" : "-Y"); dirs.Add(dr);
        double outer = dr == "+X" ? pb[3] - r.b[3] : dr == "-X" ? r.b[0] - pb[0] : dr == "+Y" ? pb[4] - r.b[4] : r.b[1] - pb[1];
        double vT = ts == null ? 0 : ix(r.s, ts), vP = ix(r.s, plate);
        double vA = 0; foreach (var a2 in anc) vA += ix(r.s, a2.s);
        sb.Append("\n      қабырға " + dr + " " + F(r.b) + " труба-қаб. саңылау " + Math.Round(dTube, 2) + ", плитаға z-саңылау " + Math.Round(dz, 2) + ", плита шетіне дейін " + Math.Round(outer, 1) + ", ∩труба " + Math.Round(vT, 1) + " ∩плита " + Math.Round(vP, 1) + " ∩анкер " + Math.Round(vA, 1));
        if (dTube > 0.1) FAILS.Add(tag + "қабырға " + dr + " трубаға тимейді, саңылау " + Math.Round(dTube, 2) + " мм");
        if (Math.Abs(dz) > 0.1) FAILS.Add(tag + "қабырға " + dr + " плитаға тимейді (z-саңылау " + Math.Round(dz, 2) + ")");
        if (outer < 0) FAILS.Add(tag + "қабырға " + dr + " плита шетінен " + Math.Round(-outer, 1) + " мм шығып тұр");
        if (vT > 0.5) FAILS.Add(tag + "қабырға " + dr + " ∩ труба " + Math.Round(vT, 1) + " мм³");
        if (vP > 0.5) FAILS.Add(tag + "қабырға " + dr + " ∩ плита " + Math.Round(vP, 1) + " мм³");
        if (vA > 0.5) FAILS.Add(tag + "қабырға " + dr + " ∩ анкер " + Math.Round(vA, 1) + " мм³");
    }
    if (ribs.Count == 4 && dirs.Distinct().Count() != 4) FAILS.Add(tag + "қабырға бағыттары қайталанады: " + string.Join(",", dirs));
    var wr = wRib.Where(p => { var b = p.get_BoundingBox(null); if (b == null) return false; var px = (b.Min.X + b.Max.X) / 2 * MM; var py = (b.Min.Y + b.Max.Y) / 2 * MM; return Math.Abs(px - cx) < 140 && Math.Abs(py - cy) < 140 && Math.Abs(b.Min.Z * MM - top) < 2; }).ToList();
    var wsol = wr.SelectMany(p => sols(p)).Select(s => new { s, b = bb(s) }).ToList();
    int wTouchRib = wsol.Count(w => ribs.Any(r => dist(w.b, r.b) < 0.1) && (dist(w.b, pb) < 0.1 || dist(w.b, tb) < 0.1));
    sb.Append("\n      шов ребро DS " + wr.Count + ", денелер " + wsol.Count + ", қабырға+(плита/труба)-ға тиетіні " + wTouchRib);
    if (wr.Count != 1) FAILS.Add(tag + "«шов ребро» DS саны " + wr.Count + " (ждём 1)");
    if (wsol.Count != 16) FAILS.Add(tag + "қабырға шовтары " + wsol.Count + " ≠ 16");
    if (wTouchRib != wsol.Count) FAILS.Add(tag + "қабырға шовтарының " + (wsol.Count - wTouchRib) + " денесі қабырғаға/плитаға/трубаға тимей тұр");
    foreach (var r in ribs) { int k = wsol.Count(w => dist(w.b, r.b) < 0.1); if (k != 4) FAILS.Add(tag + "қабырға " + F(r.b) + " бойынша шов денелері " + k + " (ждём 4)"); }
    var wp = wPl.Where(p => { var b = p.get_BoundingBox(null); if (b == null) return false; var px = (b.Min.X + b.Max.X) / 2 * MM; var py = (b.Min.Y + b.Max.Y) / 2 * MM; return Math.Abs(px - cx) < 3 && Math.Abs(py - cy) < 3 && Math.Abs(b.Min.Z * MM - top) < 2; }).ToList();
    sb.Append("\n      шов пластина DS " + wp.Count);
    if (wp.Count != 1) FAILS.Add(tag + "«шов пластина» DS саны " + wp.Count + " (ждём 1)");
    foreach (var w in wp) { var wss = sols(w); var wb = ubb(wss.Select(bb)); double dd1 = dist(wb, pb), dd2 = dist(wb, tb);
        double vwt = 0; foreach (var s in wss) if (ts != null) vwt += ix(s, ts); double vwp = 0; foreach (var s in wss) vwp += ix(s, plate); double vwr = 0; foreach (var s in wss) foreach (var r in ribs) vwr += ix(s, r.s);
        sb.Append(" " + F(wb) + " плитаға " + Math.Round(dd1, 2) + " трубаға " + Math.Round(dd2, 2) + " ∩труба " + Math.Round(vwt, 1) + " ∩плита " + Math.Round(vwp, 1) + " ∩қабырға " + Math.Round(vwr, 1));
        if (dd1 > 0.1) FAILS.Add(tag + "шов пластина плитаға тимейді (" + Math.Round(dd1, 2) + ")"); if (dd2 > 0.1) FAILS.Add(tag + "шов пластина трубаға тимейді (" + Math.Round(dd2, 2) + ")");
        if (vwt > 0.5) FAILS.Add(tag + "шов пластина ∩ труба " + Math.Round(vwt, 1) + " мм³"); if (vwr > 0.5) L.AppendLine("  (info) " + tag + "шов пластина ∩ қабырға " + Math.Round(vwr, 1) + " мм³"); }
    L.AppendLine(sb.ToString());
}
var allp = other.Select(p => new { p, m = mk(p), b = p.get_BoundingBox(null) }).Where(x => x.b != null).Select(x => new { x.p, x.m, b = new[] { x.b.Min.X * MM, x.b.Min.Y * MM, x.b.Min.Z * MM, x.b.Max.X * MM, x.b.Max.Y * MM, x.b.Max.Z * MM } }).ToList();
var rib5 = pl5.Select(p => new { p, b = p.get_BoundingBox(null) }).Where(x => x.b != null).Select(x => new { x.p, b = new[] { x.b.Min.X * MM, x.b.Min.Y * MM, x.b.Min.Z * MM, x.b.Max.X * MM, x.b.Max.Y * MM, x.b.Max.Z * MM } }).ToList();
int clash = 0; double minGap = 1e9; string minPair = "";
for (int i = 0; i < allp.Count; i++) for (int j = i + 1; j < allp.Count; j++) { var a = allp[i]; var b = allp[j]; if (a.m == "ПЛ3" || b.m == "ПЛ3") continue; double dd = dist(a.b, b.b); if (dd < minGap) { minGap = dd; minPair = a.m + a.p.Id + "/" + b.m + b.p.Id; }
    if (dd <= 0.01) { clash++; FAILS.Add("плиталар жанасады/қабаттасады: " + a.m + " #" + a.p.Id + " ↔ " + b.m + " #" + b.p.Id + " (" + Math.Round((a.b[0] + a.b[3]) / 2) + "," + Math.Round((a.b[1] + a.b[4]) / 2) + "," + Math.Round(a.b[2]) + ")"); } }
foreach (var r in rib5) foreach (var p in allp.Where(x => x.m != "ПЛ3")) { var rc = new[] { (r.b[0] + r.b[3]) / 2, (r.b[1] + r.b[4]) / 2 };
    bool own = p.m == "ПЛ2" && Math.Abs((p.b[0] + p.b[3]) / 2 - rc[0]) < 140 && Math.Abs((p.b[1] + p.b[4]) / 2 - rc[1]) < 140 && Math.Abs(p.b[5] - r.b[2]) < 2; if (own) continue;
    if (dist(r.b, p.b) < 0.01) FAILS.Add("ПЛ5 #" + r.p.Id + " бөтен плитаға " + p.m + " #" + p.p.Id + " тиіп/кіріп тұр"); }
L.AppendLine("плита/плита мин саңылау " + Math.Round(minGap, 1) + " (" + minPair + "), қабаттасу " + clash);
int freeNoPlate = 0;
foreach (var f in fr) { var c = ((LocationCurve)f.Location).Curve; var a = c.GetEndPoint(0); var b = c.GetEndPoint(1); if (Math.Abs(a.X - b.X) > 1e-6 || Math.Abs(a.Y - b.Y) > 1e-6) continue;
    var lo = a.Z < b.Z ? a : b; if (!pl2.Any(d => { var bx = d.get_BoundingBox(null); return bx != null && Math.Abs((bx.Min.X + bx.Max.X) / 2 * MM - lo.X * MM) < 3 && Math.Abs((bx.Min.Y + bx.Max.Y) / 2 * MM - lo.Y * MM) < 3 && Math.Abs(bx.Min.Z * MM - lo.Z * MM) < 2; }))
    { var pt = lo; bool touched = fr.Any(o => { if (o.Id == f.Id) return false; var cc2 = ((LocationCurve)o.Location).Curve; var pr = cc2.Project(pt); return pr != null && pr.Distance < 2 / MM; });
        if (!touched) { freeNoPlate++; L.AppendLine("  свободный нижний конец вертикали без ПЛ2: #" + f.Id + " " + f.Symbol.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_MARK)?.AsString() + " (" + Math.Round(lo.X * MM) + "," + Math.Round(lo.Y * MM) + "," + Math.Round(lo.Z * MM) + ")"); } } }
L.AppendLine("вертикаль, нижний конец свободен и без ПЛ2: " + freeNoPlate);
L.AppendLine("=== FAILS " + FAILS.Count);
foreach (var s in FAILS) L.AppendLine("FAIL " + s);
} catch (Exception ex) { L.AppendLine("ERR " + ex); }
System.IO.File.WriteAllText(@"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\42cdf6e2-99f0-49e0-887d-f2503b7aa50f\scratchpad\_bases.txt", L.ToString(), System.Text.Encoding.UTF8);
return "bases done; FAILS=" + FAILS.Count;