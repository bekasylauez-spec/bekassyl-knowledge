// РМЦ КМ q20: болт жиектері мен қадамы; фасонка шығысы (t бойынша); шов аяқтарының тірегі/асып кетуі. ТЕК ОҚИДЫ. Lib: rmc_misc_lib.cs
return RunParts(document);
}
const string OUT = @"C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\w\out\";
class PF { public double nx, ny, nz, d, area; public double[] bb; public PlanarFace Fc; public XYZ N { get { return new XYZ(nx, ny, nz); } } }
class S1 { public string Kind, Key, Loc, Name, Mark, Cls; public long Eid; public Solid S; public double[] B; public List<PF> F; public bool Stem; }
static Dictionary<long, List<int>> Grid = new Dictionary<long, List<int>>(); static List<S1> It = new List<S1>(); const double CS = 250;
static long GK(int ix, int iy, int iz) { return (ix + 100) * 1000000L + (iy + 100) * 1000L + (iz + 100); }
static void GAdd(int idx) { var b = It[idx].B; for (int ix = (int)Math.Floor(b[0] / CS); ix <= (int)Math.Floor(b[3] / CS); ix++) for (int iy = (int)Math.Floor(b[1] / CS); iy <= (int)Math.Floor(b[4] / CS); iy++) for (int iz = (int)Math.Floor(b[2] / CS); iz <= (int)Math.Floor(b[5] / CS); iz++) { List<int> l; long k = GK(ix, iy, iz); if (!Grid.TryGetValue(k, out l)) { l = new List<int>(); Grid[k] = l; } l.Add(idx); } }
static HashSet<int> GQB(double[] b, double r) { var rs = new HashSet<int>(); for (int ix = (int)Math.Floor((b[0] - r) / CS); ix <= (int)Math.Floor((b[3] + r) / CS); ix++) for (int iy = (int)Math.Floor((b[1] - r) / CS); iy <= (int)Math.Floor((b[4] + r) / CS); iy++) for (int iz = (int)Math.Floor((b[2] - r) / CS); iz <= (int)Math.Floor((b[5] + r) / CS); iz++) { List<int> l; if (Grid.TryGetValue(GK(ix, iy, iz), out l)) foreach (int i in l) rs.Add(i); } return rs; }
static List<PF> FacesOf(S1 s)
{
    if (s.F != null) return s.F; var r = new List<PF>();
    foreach (Face f in s.S.Faces)
    {
        var pf = f as PlanarFace; if (pf == null) continue; var n = pf.FaceNormal; var o = pf.Origin / QMM; double dd = n.X * o.X + n.Y * o.Y + n.Z * o.Z;
        double[] bb = { 1e18, 1e18, 1e18, -1e18, -1e18, -1e18 };
        foreach (var loop in pf.GetEdgesAsCurveLoops()) foreach (Curve c in loop) { foreach (var q in new[] { c.GetEndPoint(0) / QMM, c.GetEndPoint(1) / QMM }) { bb[0] = Math.Min(bb[0], q.X); bb[1] = Math.Min(bb[1], q.Y); bb[2] = Math.Min(bb[2], q.Z); bb[3] = Math.Max(bb[3], q.X); bb[4] = Math.Max(bb[4], q.Y); bb[5] = Math.Max(bb[5], q.Z); } }
        r.Add(new PF { nx = n.X, ny = n.Y, nz = n.Z, d = dd, bb = bb, area = pf.Area / (QMM * QMM), Fc = pf });
    }
    s.F = r; return r;
}
static bool IsStem(Solid s, out double rad)
{
    rad = 0; int pl = 0; var rs = new HashSet<string>(); foreach (Face f in s.Faces) { if (f is PlanarFace) pl++; else if (f is CylindricalFace) { double rr = ((CylindricalFace)f).get_Radius(0).GetLength() / QMM; rs.Add(QF(rr)); rad = rr; } else return false; }
    return pl == 2 && rs.Count == 1;
}
static bool PIP(List<double[]> poly, double x, double y)
{
    bool inside = false; for (int i = 0, j = poly.Count - 1; i < poly.Count; j = i++) { if (((poly[i][1] > y) != (poly[j][1] > y)) && (x < (poly[j][0] - poly[i][0]) * (y - poly[i][1]) / (poly[j][1] - poly[i][1]) + poly[i][0])) inside = !inside; }
    return inside;
}
static string RunParts(Document d)
{
    var sb = new StringBuilder();
    foreach (var fi in new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>())
    {
        if (fi.Category == null) continue; long cid = fi.Category.Id.Value; if (cid != (long)BuiltInCategory.OST_StructuralFraming && cid != (long)BuiltInCategory.OST_StructuralColumns) continue;
        var pm = fi.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS); string mk = pm == null ? "" : (pm.AsString() ?? ""); if (mk == "") continue;
        foreach (var s in QSolidsOf(fi)) It.Add(new S1 { Kind = "F", Key = "каркас", Mark = mk, Name = mk + " " + fi.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString(), Eid = fi.Id.Value, S = s, B = QBBox(s), Cls = "frame" });
    }
    foreach (var ds in new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>())
    {
        string adi = ds.ApplicationDataId ?? ""; string key = adi.Contains("|") ? adi.Split('|')[0].Trim() : adi; string loc = adi.Contains("|") ? adi.Split('|')[1].Trim() : "";
        long cid = ds.Category == null ? 0 : ds.Category.Id.Value; string nm = ds.Name ?? ""; string cls = ds.ApplicationId == "БК_ЖБ" ? "conc" : cid == (long)BuiltInCategory.OST_StructConnectionBolts ? "bolt" : cid == (long)BuiltInCategory.OST_StructConnectionWelds ? "weld" : nm.IndexOf("заглушка", StringComparison.OrdinalIgnoreCase) >= 0 ? "cap" : "plate";
        foreach (var s in QSolidsOf(ds)) It.Add(new S1 { Kind = "N", Key = key, Loc = loc, Name = nm, Eid = ds.Id.Value, S = s, B = QBBox(s), Cls = cls });
    }
    for (int i = 0; i < It.Count; i++) GAdd(i);
    sb.AppendLine("solids " + It.Count);
    // ---------- БОЛТ ----------
    var brow = new List<string>(); brow.Add("id\tkey\tloc\tname\tdiaMM\tlenMM\tpierced\tedgeMin\tedgeItem\tnPierced\tpitchMin\tpitchTo");
    var stems = new List<S1>(); var rads = new Dictionary<S1, double>(); var axes = new Dictionary<S1, XYZ>(); var cents = new Dictionary<S1, XYZ>();
    foreach (var s in It.Where(x => x.Cls == "bolt"))
    {
        double r; if (!IsStem(s.S, out r)) continue; XYZ ax = null; foreach (Face f in s.S.Faces) { var cf = f as CylindricalFace; if (cf != null) { ax = cf.Axis; break; } }
        if (ax == null) continue; s.Stem = true; stems.Add(s); rads[s] = r; axes[s] = ax.Normalize(); cents[s] = s.S.ComputeCentroid();
    }
    sb.AppendLine("bolt stems " + stems.Count);
    var byGrp = stems.GroupBy(s => s.Key + "|" + s.Loc).ToDictionary(g => g.Key, g => g.ToList());
    foreach (var s in stems)
    {
        var u = axes[s]; var c0 = cents[s]; double dia = rads[s] * 2; var pierced = new List<string>(); double edgeMin = 1e18; string edgeItem = ""; var seenEl = new HashSet<long>();
        double len = 0; { var bb = s.B; len = Math.Max(bb[3] - bb[0], Math.Max(bb[4] - bb[1], bb[5] - bb[2])); }
        var qb = new double[] { s.B[0] - 2, s.B[1] - 2, s.B[2] - 2, s.B[3] + 2, s.B[4] + 2, s.B[5] + 2 };
        foreach (int ci in GQB(qb, 0))
        {
            var o = It[ci]; if (o.Cls != "frame" && o.Cls != "plate") continue; if (seenEl.Contains(o.Eid * 100000 + ci)) continue;
            double bestE = 1e18; bool hit = false;
            foreach (var pf in FacesOf(o))
            {
                var n = pf.N; double dn = n.DotProduct(u); if (Math.Abs(dn) < 0.9995) continue; if (pf.area < 100) continue;
                double t = (pf.d - n.DotProduct(c0 / QMM)) / dn; if (Math.Abs(t) > len / 2 + 2) continue; var p = c0 / QMM + u * t; // mm
                if (p.X < pf.bb[0] - 0.5 || p.X > pf.bb[3] + 0.5 || p.Y < pf.bb[1] - 0.5 || p.Y > pf.bb[4] + 0.5 || p.Z < pf.bb[2] - 0.5 || p.Z > pf.bb[5] + 0.5) continue;
                // outer loop
                var e1 = Math.Abs(n.Z) < 0.9 ? XYZ.BasisZ.CrossProduct(n).Normalize() : XYZ.BasisX.CrossProduct(n).Normalize(); var e2 = n.CrossProduct(e1);
                List<double[]> bestPoly = null; double bestExt = -1; CurveLoop bestLoop = null;
                foreach (var loop in pf.Fc.GetEdgesAsCurveLoops()) { var poly = new List<double[]>(); double mnx = 1e18, mxx = -1e18; foreach (Curve c in loop) { var tp = c.Tessellate(); for (int k = 0; k < tp.Count - 1; k++) { var q = tp[k] / QMM; double xx = q.DotProduct(e1), yy = q.DotProduct(e2); poly.Add(new[] { xx, yy }); mnx = Math.Min(mnx, xx); mxx = Math.Max(mxx, xx); } } if (mxx - mnx > bestExt) { bestExt = mxx - mnx; bestPoly = poly; bestLoop = loop; } }
                if (bestPoly == null) continue; if (!PIP(bestPoly, p.DotProduct(e1), p.DotProduct(e2))) continue;
                double ed = 1e18; foreach (Curve c in bestLoop) { double dd = c.Distance(p * QMM) / QMM; if (dd < ed) ed = dd; }
                hit = true; if (ed < bestE) bestE = ed;
            }
            if (hit) { seenEl.Add(o.Eid * 100000 + ci); pierced.Add(o.Name + "[" + o.Eid + "]=" + QF(bestE)); if (bestE < edgeMin) { edgeMin = bestE; edgeItem = o.Name + " [" + o.Eid + "]"; } }
        }
        // қадам
        double pitch = 1e18; string pitchTo = ""; List<S1> grp; if (byGrp.TryGetValue(s.Key + "|" + s.Loc, out grp)) foreach (var o in grp) { if (o == s) continue; if (Math.Abs(rads[o] - rads[s]) > 0.01) continue; if (axes[o].CrossProduct(u).GetLength() > 0.01) continue; var dv = (cents[o] - c0) / QMM; var perp = dv - u * dv.DotProduct(u); double pd = perp.GetLength(); if (pd < 0.5) continue; if (pd < pitch) { pitch = pd; pitchTo = o.Name; } }
        brow.Add(s.Eid + "\t" + s.Key + "\t" + s.Loc + "\t" + s.Name.Replace("\t", " ") + "\t" + QF(dia) + "\t" + QF(len) + "\t" + string.Join(" ; ", pierced) + "\t" + (edgeMin > 1e17 ? "" : QF(edgeMin)) + "\t" + edgeItem + "\t" + pierced.Count + "\t" + (pitch > 1e17 ? "" : QF(pitch)) + "\t" + pitchTo);
    }
    System.IO.File.WriteAllLines(OUT + "bolts.tsv", brow, new UTF8Encoding(false));
    // ---------- ПЛАСТИНА ШЫҒЫСЫ ----------
    var prow = new List<string>(); prow.Add("id\tkey\tloc\tname\tt\tcontactMark\tcontactElem\toutstand\tratio\tcontactArea");
    foreach (var p in It.Where(x => x.Cls == "plate"))
    {
        var fl = FacesOf(p); if (fl.Count < 6) continue; var big = fl.OrderByDescending(q => q.area).Take(2).ToList(); if (big.Count < 2) continue; if (big[0].N.DotProduct(big[1].N) > -0.9999) continue;
        var npl = big[0].N; double tt = Math.Abs(big[0].d + big[1].d * (-1)); tt = Math.Abs(big[0].d - (npl.DotProduct(new XYZ(big[1].nx, big[1].ny, big[1].nz)) < 0 ? -big[1].d : big[1].d)); tt = Math.Abs(big[0].d + big[1].d); // normals opposite: n·x=d0 and (-n)·x=d1 → thickness = |d0 + d1|
        if (tt < 0.5 || tt > 60) continue;
        var verts = new List<XYZ>(); foreach (Edge ed in p.S.Edges) { var cc = ed.AsCurve(); verts.Add(cc.GetEndPoint(0) / QMM); verts.Add(cc.GetEndPoint(1) / QMM); }
        foreach (int ci in GQB(p.B, 2))
        {
            var o = It[ci]; if (o.Cls != "frame") continue; if (o.B[0] > p.B[3] + 1 || o.B[3] < p.B[0] - 1 || o.B[1] > p.B[4] + 1 || o.B[4] < p.B[1] - 1 || o.B[2] > p.B[5] + 1 || o.B[5] < p.B[2] - 1) continue;
            foreach (var fp in fl)
            {
                if (Math.Abs(fp.N.DotProduct(npl)) > 0.01) continue; if (fp.area < tt * 20) continue; // side face
                foreach (var fo in FacesOf(o))
                {
                    if (fp.N.DotProduct(fo.N) > -0.9999) continue; if (Math.Abs(fp.d + fo.d) > 0.3) continue;
                    double ex = Math.Min(fp.bb[3], fo.bb[3]) - Math.Max(fp.bb[0], fo.bb[0]), ey = Math.Min(fp.bb[4], fo.bb[4]) - Math.Max(fp.bb[1], fo.bb[1]), ez = Math.Min(fp.bb[5], fo.bb[5]) - Math.Max(fp.bb[2], fo.bb[2]);
                    if ((ex > 1 ? 1 : 0) + (ey > 1 ? 1 : 0) + (ez > 1 ? 1 : 0) < 2) continue; if (ex < -0.1 || ey < -0.1 || ez < -0.1) continue;
                    double mn = 1e18, mx = -1e18; foreach (var v in verts) { double pr = v.DotProduct(fp.N); mn = Math.Min(mn, pr); mx = Math.Max(mx, pr); }
                    double outst = mx - mn; prow.Add(p.Eid + "\t" + p.Key + "\t" + p.Loc + "\t" + p.Name.Replace("\t", " ") + "\t" + QF(tt) + "\t" + o.Mark + "\t" + o.Name + " [" + o.Eid + "]" + "\t" + QF(outst) + "\t" + QF(outst / tt) + "\t" + QF(fp.area));
                }
            }
        }
    }
    System.IO.File.WriteAllLines(OUT + "plates.tsv", prow, new UTF8Encoding(false));
    // ---------- ШОВ АЯҚТАРЫ ----------
    var wrow = new List<string>(); wrow.Add("id\tkey\tloc\tname\tvol\tlegsSupported\tlegsTotal\tmaxOverhang\tsupports");
    foreach (var w in It.Where(x => x.Cls == "weld"))
    {
        var fl = FacesOf(w).Where(q => q.area > 4).OrderByDescending(q => q.area).Take(3).ToList(); int sup = 0; double maxOv = 0; var sn = new List<string>();
        var cands = GQB(w.B, 1.0).Where(ci => It[ci].Eid != w.Eid && It[ci].Cls != "weld" && It[ci].Cls != "bolt").ToList();
        foreach (var fw in fl)
        {
            double bestOv = 1e18; string bestName = ""; bool any = false;
            foreach (int ci in cands)
            {
                var o = It[ci]; if (o.B[0] > w.B[3] + 0.5 || o.B[3] < w.B[0] - 0.5 || o.B[1] > w.B[4] + 0.5 || o.B[4] < w.B[1] - 0.5 || o.B[2] > w.B[5] + 0.5 || o.B[5] < w.B[2] - 0.5) continue;
                foreach (var fo in FacesOf(o))
                {
                    if (fw.N.DotProduct(fo.N) > -0.9999) continue; if (Math.Abs(fw.d + fo.d) > 0.1) continue;
                    double ex = Math.Min(fw.bb[3], fo.bb[3]) - Math.Max(fw.bb[0], fo.bb[0]), ey = Math.Min(fw.bb[4], fo.bb[4]) - Math.Max(fw.bb[1], fo.bb[1]), ez = Math.Min(fw.bb[5], fo.bb[5]) - Math.Max(fw.bb[2], fo.bb[2]);
                    if ((ex > 0.5 ? 1 : 0) + (ey > 0.5 ? 1 : 0) + (ez > 0.5 ? 1 : 0) < 2) continue; if (ex < -0.1 || ey < -0.1 || ez < -0.1) continue;
                    // шов бет бұрыштарының бөлшек бетінен тыс қашықтығы
                    double ov = 0; foreach (var lp in fw.Fc.GetEdgesAsCurveLoops()) foreach (Curve c in lp) { var q = c.GetEndPoint(0); var ir = fo.Fc.Project(q); if (ir != null) ov = Math.Max(ov, ir.Distance / QMM); }
                    any = true; if (ov < bestOv) { bestOv = ov; bestName = o.Name + " [" + o.Eid + "]"; }
                }
            }
            if (any) { sup++; maxOv = Math.Max(maxOv, bestOv); sn.Add(bestName + "~" + QF(bestOv)); }
        }
        wrow.Add(w.Eid + "\t" + w.Key + "\t" + w.Loc + "\t" + w.Name.Replace("\t", " ") + "\t" + QF(QCu(w.S.Volume)) + "\t" + sup + "\t" + fl.Count + "\t" + QF(maxOv) + "\t" + string.Join(" ; ", sn));
    }
    System.IO.File.WriteAllLines(OUT + "welds.tsv", wrow, new UTF8Encoding(false));
    sb.AppendLine("bolts rows " + (brow.Count - 1) + ", plates rows " + (prow.Count - 1) + ", welds rows " + (wrow.Count - 1));
    return sb.ToString();
}