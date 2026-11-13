// РМЦ КМ q20: ГС1/ГС2 ұштары мен заглушка арасы (вершина қашықтықтары, бет қалыңдығы). ТЕК ОҚИДЫ. Lib: rmc_misc_lib.cs
return RunCap(document);
}
const string OUT = @"C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\w\out\";
class S1 { public string Kind, Key, Loc, Name, Mark; public long Eid; public Solid S; public double[] B; public bool Bolt, Weld, Cap, Conc; public string Cls; }
static Dictionary<long, List<int>> Grid = new Dictionary<long, List<int>>(); static List<S1> It = new List<S1>(); const double CS = 250;
static long GK(int ix, int iy, int iz) { return (ix + 100) * 1000000L + (iy + 100) * 1000L + (iz + 100); }
static void GAdd(int idx) { var b = It[idx].B; for (int ix = (int)Math.Floor(b[0] / CS); ix <= (int)Math.Floor(b[3] / CS); ix++) for (int iy = (int)Math.Floor(b[1] / CS); iy <= (int)Math.Floor(b[4] / CS); iy++) for (int iz = (int)Math.Floor(b[2] / CS); iz <= (int)Math.Floor(b[5] / CS); iz++) { List<int> l; long k = GK(ix, iy, iz); if (!Grid.TryGetValue(k, out l)) { l = new List<int>(); Grid[k] = l; } l.Add(idx); } }
static HashSet<int> GQ(double x, double y, double z, double r) { var rs = new HashSet<int>(); for (int ix = (int)Math.Floor((x - r) / CS); ix <= (int)Math.Floor((x + r) / CS); ix++) for (int iy = (int)Math.Floor((y - r) / CS); iy <= (int)Math.Floor((y + r) / CS); iy++) for (int iz = (int)Math.Floor((z - r) / CS); iz <= (int)Math.Floor((z + r) / CS); iz++) { List<int> l; if (Grid.TryGetValue(GK(ix, iy, iz), out l)) foreach (int i in l) rs.Add(i); } return rs; }
// белгіленген қашықтық: нүктеден солид бетіне (мм), > 0 сырт, < 0 ішкі
static double SD(Solid s, XYZ p)
{
    double best = 1e18; double sgn = 1;
    foreach (Face f in s.Faces)
    {
        IntersectionResult ir = null; try { ir = f.Project(p); } catch { } if (ir == null) continue; double dd = ir.Distance / QMM; if (dd < best) { best = dd; var n = f.ComputeNormal(ir.UVPoint); var v = p - ir.XYZPoint; sgn = v.GetLength() < 1e-9 ? 1 : (v.DotProduct(n) >= 0 ? 1 : -1); }
    }
    return best * sgn;
}
static string RunCap(Document d)
{
    var sb = new StringBuilder(); var frames = new List<FamilyInstance>();
    foreach (var fi in new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>())
    {
        if (fi.Category == null) continue; long cid = fi.Category.Id.Value; if (cid != (long)BuiltInCategory.OST_StructuralFraming && cid != (long)BuiltInCategory.OST_StructuralColumns) continue;
        var pm = fi.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS); string mk = pm == null ? "" : (pm.AsString() ?? ""); if (mk == "") continue; frames.Add(fi);
        foreach (var s in QSolidsOf(fi)) It.Add(new S1 { Kind = "F", Key = "каркас", Mark = mk, Name = mk + " " + fi.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString(), Eid = fi.Id.Value, S = s, B = QBBox(s), Cls = "frame" });
    }
    foreach (var ds in new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>())
    {
        string nm = ds.Name ?? ""; if (nm.IndexOf("заглушка", StringComparison.OrdinalIgnoreCase) < 0 || nm.IndexOf("шов", StringComparison.OrdinalIgnoreCase) >= 0) continue;
        foreach (var s in QSolidsOf(ds)) It.Add(new S1 { Kind = "N", Key = "", Name = nm, Eid = ds.Id.Value, S = s, B = QBBox(s), Cls = "cap" });
    }
    for (int i = 0; i < It.Count; i++) GAdd(i);
    int nEnds = 0, nNoCap = 0, nGt03 = 0, nGt1 = 0; double gMax = 0; string gWhere = ""; var rows = new List<string>(); rows.Add("id\tmark\tim\tend\tdotNormals\tcapName\tcapFaceDistCenter\tvertexDistToCapPlane(mm,signed along end normal)");
    foreach (var fi in frames)
    {
        string mk = fi.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString(); if (!(mk == "ГС1" || mk == "ГС2" || mk == "Р1" || mk == "Р2" || mk == "Р3" || mk == "СВ1" || mk == "СВ2" || mk == "СВ3" || mk == "СВ4" || mk == "СВ5")) continue; string im = fi.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString();
        var c = ((LocationCurve)fi.Location).Curve; var a = c.GetEndPoint(0); var u = (c.GetEndPoint(1) - a).Normalize(); var sols = QSolidsOf(fi);
        var ef = new List<PlanarFace>[2] { new List<PlanarFace>(), new List<PlanarFace>() };
        foreach (var s in sols) foreach (Face f in s.Faces) { var pf = f as PlanarFace; if (pf == null) continue; double dp = pf.FaceNormal.DotProduct(u); if (dp < -0.7) ef[0].Add(pf); else if (dp > 0.7) ef[1].Add(pf); }
        for (int e = 0; e < 2; e++)
        {
            if (ef[e].Count == 0) continue; nEnds++; var big = ef[e].OrderByDescending(q => q.Area).First(); var n = big.FaceNormal; var vs = new List<XYZ>(); foreach (var lp in big.GetEdgesAsCurveLoops()) foreach (Curve cu in lp) vs.Add(cu.GetEndPoint(0));
            XYZ cen = XYZ.Zero; foreach (var v in vs) cen += v; cen = cen / vs.Count; var cm = cen / QMM;
            S1 bestCap = null; double bd = 1e18; foreach (int ci in GQ(cm.X, cm.Y, cm.Z, 60)) { var o = It[ci]; if (o.Cls != "cap") continue; double sd = Math.Abs(SD(o.S, cen)); if (sd < bd) { bd = sd; bestCap = o; } }
            if (bestCap == null) { rows.Add(fi.Id.Value + "\t" + mk + "\t" + im + "\t" + e + "\tNOCAP"); continue; }
            PlanarFace bf = null; double bdd = 1e18; foreach (Face f in bestCap.S.Faces) { var pf = f as PlanarFace; if (pf == null) continue; if (Math.Abs(pf.FaceNormal.DotProduct(n)) < 0.5) continue; var ir = pf.Project(cen); if (ir != null && ir.Distance < bdd) { bdd = ir.Distance; bf = pf; } }
            if (bf == null) { rows.Add(fi.Id.Value + "\t" + mk + "\t" + im + "\t" + e + "\tNOCAPFACE"); continue; }
            var dists = new List<string>(); double endMax = 0; foreach (var v in vs) { double dd = (v - bf.Origin).DotProduct(bf.FaceNormal) / QMM; dists.Add(QF(dd)); endMax = Math.Max(endMax, Math.Abs(dd)); } if (endMax > gMax) { gMax = endMax; gWhere = mk + " " + im + " end " + e; } if (endMax > 0.3) nGt03++; if (endMax > 1) nGt1++;
            rows.Add(fi.Id.Value + "\t" + mk + "\t" + im + "\t" + e + "\t" + QF(Math.Abs(bf.FaceNormal.DotProduct(n))) + "\t" + bestCap.Name + "\t" + QF(bdd / QMM) + "\t" + string.Join(" ", dists));
        }
    }
    System.IO.File.WriteAllLines(OUT + "capprobe.tsv", rows, new UTF8Encoding(false));
    return "tube ends " + nEnds + ", without cap " + nNoCap + ", ends with max |vertex dist to cap plane| > 0.3 mm: " + nGt03 + ", > 1 mm: " + nGt1 + ", largest " + QF(gMax) + " mm (" + gWhere + ")";
}