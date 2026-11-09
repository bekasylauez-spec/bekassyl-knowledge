var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\x_check_out.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; string r;
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt")); r = Chk(nd); }
  catch (Exception ex) { r = "ERR " + ex; }
  System.IO.File.WriteAllText(log, r, System.Text.Encoding.UTF8); };
uiapp.Idling += hnd;
return "queued";
}

const double M = 304.8;
static List<Solid> Sol(Element el) { var r = new List<Solid>();
    foreach (var go in el.get_Geometry(new Options { DetailLevel = ViewDetailLevel.Fine }))
    { IEnumerable<GeometryObject> objs = go is GeometryInstance gi ? gi.GetInstanceGeometry().Cast<GeometryObject>() : new[] { go };
      r.AddRange(objs.OfType<Solid>().Where(x => x.Volume > 1e-9)); } return r; }
static double Ax(XYZ p, int i) { return i == 0 ? p.X : i == 1 ? p.Y : p.Z; }
static XYZ Ve(int i, double v) { return i == 0 ? new XYZ(v, 0, 0) : i == 1 ? new XYZ(0, v, 0) : new XYZ(0, 0, v); }
static List<double[]> Segs(IEnumerable<Solid> ss, XYZ a, XYZ b)
{
    var res = new List<double[]>(); var ln = Line.CreateBound(a, b); var dir = (b - a).Normalize();
    var o = new SolidCurveIntersectionOptions { ResultType = SolidCurveIntersectionMode.CurveSegmentsInside };
    foreach (var s in ss) { SolidCurveIntersection ix = null; try { ix = s.IntersectWithCurve(ln, o); } catch { continue; }
        if (ix == null) continue;
        for (int i = 0; i < ix.SegmentCount; i++) { var c = ix.GetCurveSegment(i); double t0 = (c.GetEndPoint(0) - a).DotProduct(dir) * M, t1 = (c.GetEndPoint(1) - a).DotProduct(dir) * M; res.Add(new[] { Math.Min(t0, t1), Math.Max(t0, t1) }); } }
    return res.OrderBy(x => x[0]).ToList();
}
static void Bb(Solid s, out XYZ mn, out XYZ mx) { var b = s.GetBoundingBox(); var t = b.Transform; var c = new[] { b.Min, b.Max }; double[] lo = { 1e9, 1e9, 1e9 }, hi = { -1e9, -1e9, -1e9 };
    for (int i = 0; i < 8; i++) { var p = t.OfPoint(new XYZ(c[i & 1].X, c[(i >> 1) & 1].Y, c[(i >> 2) & 1].Z)); for (int k = 0; k < 3; k++) { lo[k] = Math.Min(lo[k], Ax(p, k)); hi[k] = Math.Max(hi[k], Ax(p, k)); } }
    mn = new XYZ(lo[0], lo[1], lo[2]); mx = new XYZ(hi[0], hi[1], hi[2]); }

static string Chk(Document nd)
{
    var sb = new System.Text.StringBuilder(); double[] fr3 = { 0.1, 0.5, 0.9 };
    var fr = new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Symbol.Family.Name.StartsWith("(КМ)")).ToList();
    var cols = fr.Where(x => x.Category.Id.Value == (long)BuiltInCategory.OST_StructuralColumns).ToList();
    var cy = new SortedDictionary<long, int>(); var colPts = new List<Tuple<FamilyInstance, XYZ, string>>();
    foreach (var c in cols) { var p = ((LocationPoint)c.Location).Point; var mk = (c.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "").Split(' ')[0];
        colPts.Add(Tuple.Create(c, p, mk)); long k = (long)Math.Round(p.Y * M); if (!cy.ContainsKey(k)) cy[k] = 0; cy[k]++; }
    sb.AppendLine("E0 columns " + cols.Count + "; distinct Y(mm):count -> " + string.Join(", ", cy.Select(kv => kv.Key + ":" + kv.Value)));
    var grids = new FilteredElementCollector(nd).OfClass(typeof(Grid)).Cast<Grid>().ToList();
    sb.AppendLine("E0 horizontal grids: " + string.Join("; ", grids.Where(g => g.Curve is Line).Select(g => { var l = (Line)g.Curve; var a = l.GetEndPoint(0); var b = l.GetEndPoint(1); return g.Name + (Math.Abs(a.Y - b.Y) < 1e-6 ? " y=" + Math.Round(a.Y * M) : ""); }).Where(s => s.Contains("y="))));
    var colSol = new Dictionary<ElementId, List<Solid>>(); foreach (var t in colPts) colSol[t.Item1.Id] = Sol(t.Item1);
    var DSs = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел").ToList();
    var plDS = DSs.Where(x => x.Category != null && x.Category.Id.Value == (long)BuiltInCategory.OST_StructConnections).ToList();
    var boltDS = DSs.Where(x => x.Category != null && x.Category.Id.Value == (long)BuiltInCategory.OST_StructConnectionBolts).GroupBy(x => x.Name).ToDictionary(g => g.Key, g => g.First());
    int nPl = 0, nNoCol = 0, nGap = 0, nBoltBad = 0, nBolts = 0, nEdge = 0; double maxGap = -1e9, minGap = 1e9;
    var typeStat = new Dictionary<string, List<int>>(); var bad = new List<string>();
    foreach (var ds in plDS.Where(x => x.Name.Contains("к колонне") && (x.Name.Contains("шарнир") || x.Name.Contains("жёсткий"))))
    {
        var ss = Sol(ds); Solid ep = null; int ax = -1; double best = 0;
        foreach (var s in ss) { XYZ mn, mx; Bb(s, out mn, out mx); double[] e = { (mx.X - mn.X) * M, (mx.Y - mn.Y) * M, (mx.Z - mn.Z) * M }; int th = Array.IndexOf(e, e.Min());
            if (th == 2 || e[th] > 30) continue; double area = e[(th + 1) % 3] * e[(th + 2) % 3]; if (area > best) { best = area; ep = s; ax = th; } }
        nPl++; if (ep == null) { bad.Add("NOPLATE " + ds.Name); continue; }
        XYZ pmn, pmx; Bb(ep, out pmn, out pmx); var pc = (pmn + pmx) / 2; int o1 = ax == 0 ? 1 : 0;
        var cand = colPts.Where(t => Math.Abs(Ax(t.Item2, o1) - Ax(pc, o1)) * M < 5 && Math.Abs(Ax(t.Item2, ax) - Ax(pc, ax)) * M < 450).OrderBy(t => Math.Abs(Ax(t.Item2, ax) - Ax(pc, ax))).FirstOrDefault();
        if (cand == null) { nNoCol++; bad.Add("NOCOL " + ds.Name); continue; }
        double dir = Ax(cand.Item2, ax) < Ax(pc, ax) ? -1 : 1;
        double nearFace = dir < 0 ? Ax(pmn, ax) : Ax(pmx, ax);
        var cs = colSol[cand.Item1.Id]; double thick = (Ax(pmx, ax) - Ax(pmn, ax)) * M;
        double g0 = 1e9, g1 = -1e9; int hits = 0, miss = 0;
        foreach (var f1 in fr3) foreach (var f2 in fr3)
        {
            var p = new double[3]; p[ax] = nearFace; p[o1] = Ax(pmn, o1) + (Ax(pmx, o1) - Ax(pmn, o1)) * f1; p[2] = Ax(pmn, 2) + (Ax(pmx, 2) - Ax(pmn, 2)) * f2;
            var P0 = new XYZ(p[0], p[1], p[2]); var a = P0 - Ve(ax, dir * 30 / M); var b = P0 + Ve(ax, dir * 80 / M);
            var sg = Segs(cs, a, b); if (sg.Count == 0) { miss++; continue; }
            double gap = sg[0][0] - 30; hits++; g0 = Math.Min(g0, gap); g1 = Math.Max(g1, gap);
        }
        string typ = (ds.Name.Contains("шарнир") ? "шарнир " : "жёсткий ") + ds.Name.Split(' ')[1];
        if (hits == 0) { bad.Add("NOHIT " + ds.Name); nGap++; } else { minGap = Math.Min(minGap, g0); maxGap = Math.Max(maxGap, g1); if (g1 > 2 || g0 < -0.5) { nGap++; bad.Add("GAP " + ds.Name + " gap " + Math.Round(g0, 2) + ".." + Math.Round(g1, 2) + " hits " + hits + " miss " + miss + " col " + cand.Item3 + " y " + Math.Round(cand.Item2.Y * M)); } }
        int nbt = 0;
        if (boltDS.ContainsKey("Болт " + ds.Name))
        {
            foreach (var s in Sol(boltDS["Болт " + ds.Name]))
            {
                XYZ mn, mx; Bb(s, out mn, out mx); double[] e = { (mx.X - mn.X) * M, (mx.Y - mn.Y) * M, (mx.Z - mn.Z) * M }; int la = Array.IndexOf(e, e.Max()); if (la != ax) continue;
                if (e[la] < 25 || Math.Abs(s.Volume * 28316846.6 / e[la] - 314.16) > 8) continue;
                nbt++; nBolts++; var ctr = (mn + mx) / 2; double s0 = Ax(mn, ax), s1 = Ax(mx, ax);
                var A0 = ctr - Ve(ax, Ax(ctr, ax)) + Ve(ax, Ax(pc, ax) - dir * 200 / M); var B0 = ctr - Ve(ax, Ax(ctr, ax)) + Ve(ax, Ax(pc, ax) + dir * 200 / M);
                var sp = Segs(new[] { ep }, A0, B0); var sc = Segs(cs, A0, B0);
                double inPl = sp.Sum(q => q[1] - q[0]);
                double t0 = dir > 0 ? (s0 - Ax(A0, ax)) * M : (Ax(A0, ax) - s1) * M, t1 = dir > 0 ? (s1 - Ax(A0, ax)) * M : (Ax(A0, ax) - s0) * M;
                double pa = sp.Count > 0 ? sp[0][0] : 0, pb = sp.Count > 0 ? sp[sp.Count - 1][1] : 0;
                double flLo = sc.Count > 0 ? sc[0][0] : 0, flHi = sc.Count > 0 ? sc[0][1] : 0;
                bool ok = sp.Count > 0 && sc.Count > 0 && Math.Abs(inPl - thick) < 1.0 && (flHi - flLo) > 10 && Math.Abs(pb - flLo) < 3;
                bool cover = ok && t0 <= Math.Min(pa, flLo) + 0.5 && t1 >= Math.Max(pb, flHi) - 0.5;
                double ed = 1e9; foreach (var k in new[] { o1, 2 }) ed = Math.Min(ed, Math.Min((Ax(ctr, k) - Ax(pmn, k)) * M, (Ax(pmx, k) - Ax(ctr, k)) * M));
                if (!(ok && cover)) { nBoltBad++; if (bad.Count < 60) bad.Add("BOLT " + ds.Name + " at " + Math.Round(ctr.X * M, 1) + "," + Math.Round(ctr.Y * M, 1) + "," + Math.Round(ctr.Z * M, 1) + " inPlate " + Math.Round(inPl, 1) + " plate t " + Math.Round(thick, 1) + " flange " + Math.Round(flLo, 1) + ".." + Math.Round(flHi, 1) + " shank " + Math.Round(t0, 1) + ".." + Math.Round(t1, 1) + " plate " + Math.Round(pa, 1) + ".." + Math.Round(pb, 1)); }
                if (ed < 29.5) { nEdge++; if (bad.Count < 60) bad.Add("EDGE<30 " + ds.Name + " ed " + Math.Round(ed, 1)); }
            }
        }
        if (!typeStat.ContainsKey(typ)) typeStat[typ] = new List<int>(); typeStat[typ].Add(nbt);
    }
    sb.AppendLine("E1 end plates " + nPl + ", no column " + nNoCol + ", gap/overlap fail " + nGap + ", gap range " + Math.Round(minGap, 2) + ".." + Math.Round(maxGap, 2) + " mm; bolts checked " + nBolts + ", bad " + nBoltBad + ", edge<30 " + nEdge);
    foreach (var kv in typeStat) sb.AppendLine("   " + kv.Key + ": plates " + kv.Value.Count + ", bolts per plate " + string.Join("/", kv.Value.GroupBy(x => x).Select(g => g.Key + "x" + g.Count())));
    foreach (var s in bad.Take(25)) sb.AppendLine("   " + s);
    var bm = fr.Where(x => x.Category.Id.Value == (long)BuiltInCategory.OST_StructuralFraming && (x.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "").StartsWith("БМ1")).ToList();
    var bmSol = new List<Solid>(); foreach (var b in bm) bmSol.AddRange(Sol(b));
    int nt = 0, ntBad = 0; double tgMin = 1e9, tgMax = -1e9; var tbad = new List<string>(); int tbolt = 0, tboltBad = 0;
    foreach (var ds in plDS.Where(x => x.Name.Contains("КН")))
    {
        foreach (var s in Sol(ds))
        {
            XYZ mn, mx; Bb(s, out mn, out mx); double[] e = { (mx.X - mn.X) * M, (mx.Y - mn.Y) * M, (mx.Z - mn.Z) * M };
            if (Math.Abs(e[2] - 12) > 0.6 || Math.Abs(e[0] - 200) > 1) continue;
            nt++; double zb = mn.Z * M; double gmin = 1e9, gmax = -1e9; int hit = 0, ms = 0;
            foreach (var f1 in fr3) foreach (var f2 in fr3)
            { var P0 = new XYZ(mn.X + (mx.X - mn.X) * f1, mn.Y + (mx.Y - mn.Y) * f2, mn.Z);
              var sg = Segs(bmSol, P0 + new XYZ(0, 0, 40 / M), P0 - new XYZ(0, 0, 120 / M)); if (sg.Count == 0) { ms++; continue; }
              double topZ = P0.Z * M + 40 - sg[0][0]; double gap = zb - topZ; hit++; gmin = Math.Min(gmin, gap); gmax = Math.Max(gmax, gap); }
            if (hit == 0 || gmax > 1.0 || gmin < -0.5) { ntBad++; tbad.Add(ds.Name + " z " + Math.Round(zb, 2) + " hits " + hit + " miss " + ms + (hit > 0 ? " gap " + Math.Round(gmin, 2) + ".." + Math.Round(gmax, 2) : "")); }
            else { tgMin = Math.Min(tgMin, gmin); tgMax = Math.Max(tgMax, gmax); }
            if (boltDS.ContainsKey("Болт " + ds.Name))
                foreach (var bs in Sol(boltDS["Болт " + ds.Name]))
                { XYZ bmn, bmx; Bb(bs, out bmn, out bmx); double[] be = { (bmx.X - bmn.X) * M, (bmx.Y - bmn.Y) * M, (bmx.Z - bmn.Z) * M };
                  if (be[2] < 25 || be[2] < be[0] || be[2] < be[1] || Math.Abs(bs.Volume * 28316846.6 / be[2] - 314.16) > 8) continue;
                  double bx = (bmn.X + bmx.X) / 2, by = (bmn.Y + bmx.Y) / 2; if (bx < mn.X || bx > mx.X || by < mn.Y || by > mx.Y) continue;
                  tbolt++; var sgb = Segs(bmSol, new XYZ(bx, by, mn.Z + 40 / M), new XYZ(bx, by, mn.Z - 120 / M));
                  bool cov = bmn.Z * M <= zb - 15 && bmx.Z * M >= zb + 11.5;
                  if (sgb.Count == 0 || !cov) { tboltBad++; tbad.Add("TIEBOLT " + ds.Name + " at " + Math.Round(bx * M, 1) + "," + Math.Round(by * M, 1) + " beamhit " + sgb.Count + " shank z " + Math.Round(bmn.Z * M, 1) + ".." + Math.Round(bmx.Z * M, 1)); } }
        }
    }
    sb.AppendLine("E2 tie plates " + nt + ", bad " + ntBad + ", gap to БМ1 top flange (good ones) " + Math.Round(tgMin, 2) + ".." + Math.Round(tgMax, 2) + " mm; tie bolts " + tbolt + ", bad " + tboltBad);
    foreach (var s in tbad.Take(15)) sb.AppendLine("   " + s);
    return sb.ToString();
}
static void _e() {