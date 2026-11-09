// READ-ONLY gusset coverage check (checker). Run WITHOUT -Lib.
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\q_gus7.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; string r;
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt")); r = Q(nd); }
  catch (Exception ex) { r = "ERR " + ex; }
  System.IO.File.WriteAllText(log, r, System.Text.Encoding.UTF8); };
uiapp.Idling += hnd;
return "queued";
}
const double M = 304.8;
class Pl { public long id; public string name; public double t; public XYZ n, o, e1, e2; public List<double[]> p2 = new List<double[]>(); public double x0, x1, y0, y1, z0, z1; public Solid so; }
static Pl MkPl(DirectShape d, Solid so)
{
    PlanarFace best = null; foreach (Face f in so.Faces) if (f is PlanarFace pf && (best == null || pf.Area > best.Area)) best = pf; if (best == null) return null;
    var r = new Pl { id = d.Id.Value, name = d.Name, so = so, t = so.Volume / best.Area * M, n = best.FaceNormal };
    var loops = best.GetEdgesAsCurveLoops(); var pts = new List<XYZ>();
    foreach (var cu in loops[0]) { var tz = cu.Tessellate(); for (int i = 0; i < tz.Count - 1; i++) pts.Add(tz[i]); }
    r.o = pts[0]; var z = Math.Abs(r.n.Z) < 0.9 ? XYZ.BasisZ : XYZ.BasisX; r.e1 = r.n.CrossProduct(z).Normalize(); r.e2 = r.n.CrossProduct(r.e1).Normalize();
    foreach (var p in pts) r.p2.Add(new[] { (p - r.o).DotProduct(r.e1), (p - r.o).DotProduct(r.e2) });
    var bb = so.GetBoundingBox(); var a = bb.Transform.OfPoint(bb.Min); var b = bb.Transform.OfPoint(bb.Max);
    r.x0 = Math.Min(a.X, b.X) * M; r.x1 = Math.Max(a.X, b.X) * M; r.y0 = Math.Min(a.Y, b.Y) * M; r.y1 = Math.Max(a.Y, b.Y) * M; r.z0 = Math.Min(a.Z, b.Z) * M; r.z1 = Math.Max(a.Z, b.Z) * M; return r;
}
static bool Pip(List<double[]> P, double x, double y) { bool c = false; for (int i = 0, j = P.Count - 1; i < P.Count; j = i++) if ((P[i][1] > y) != (P[j][1] > y) && x < (P[j][0] - P[i][0]) * (y - P[i][1]) / (P[j][1] - P[i][1]) + P[i][0]) c = !c; return c; }
static Pl Gsel(List<Pl> lst, string name) { var c = (name ?? "").Contains("ГС1") ? lst : lst.Where(p => Math.Abs(p.n.Z) < 0.5).ToList(); if (c.Count == 0) c = lst; return c.OrderByDescending(p => PolyA(p)).FirstOrDefault(); }
static double PolyA(Pl p) { double s = 0; for (int i = 0, j = p.p2.Count - 1; i < p.p2.Count; j = i++) s += p.p2[j][0] * p.p2[i][1] - p.p2[i][0] * p.p2[j][1]; return Math.Abs(s) / 2; }
static double EdgeD(List<double[]> P, double x, double y) { double m = 1e9; for (int i = 0, j = P.Count - 1; i < P.Count; j = i++) { double ax = P[j][0], ay = P[j][1], bx = P[i][0], by = P[i][1]; double dx = bx - ax, dy = by - ay, l2 = dx * dx + dy * dy; double t = l2 < 1e-12 ? 0 : Math.Max(0, Math.Min(1, ((x - ax) * dx + (y - ay) * dy) / l2)); m = Math.Min(m, Math.Sqrt((x - ax - t * dx) * (x - ax - t * dx) + (y - ay - t * dy) * (y - ay - t * dy))); } return m; }
static string Q(Document nd)
{
    var sb = new System.Text.StringBuilder(); var opt = new Options { DetailLevel = ViewDetailLevel.Fine };
    Func<FamilyInstance, string> Cm = f => f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "";
    var ends = new List<KeyValuePair<XYZ, XYZ>>(); var endMk = new List<string>();
    foreach (var f in new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Location is LocationCurve && x.Symbol.Family.Name.Contains("труба")))
    { string mk = Cm(f).Split(' ')[0]; if (!(mk == "СВ1" || mk == "СВ2" || mk == "СВ3" || mk == "ГС1" || mk == "Р1" || mk == "ВС1" || mk == "ВФ1" || mk == "Р2")) continue; var c = (f.Location as LocationCurve).Curve; var a = c.GetEndPoint(0); var b = c.GetEndPoint(1); var u = (b - a).Normalize();
      ends.Add(new KeyValuePair<XYZ, XYZ>(a, -u)); endMk.Add(mk); ends.Add(new KeyValuePair<XYZ, XYZ>(b, u)); endMk.Add(mk); }
    var all = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел").ToList();
    var plates = all.Where(d => d.Category.Id.Value == (long)BuiltInCategory.OST_StructConnections).ToList();
    var gus = new List<Pl>(); var tubeNode = new List<DirectShape>();
    var perDs = new Dictionary<long, List<Pl>>();
    foreach (var d in plates)
    {
        string n = d.Name ?? ""; if (!(n.StartsWith("Узел ") && n.Contains("вкладыши"))) continue; tubeNode.Add(d); var lst = new List<Pl>();
        foreach (var go in d.get_Geometry(opt)) { var so = go as Solid; if (so == null || so.Volume < 1e-12) continue; var p = MkPl(d, so); if (p != null) lst.Add(p); }
        perDs[d.Id.Value] = lst; { var gg = Gsel(lst, d.Name); if (gg != null && gg.p2.Count >= 3) gus.Add(gg); }
    }
    sb.AppendLine("tube-node DS " + tubeNode.Count + ", gusset solids (t=10) " + gus.Count);
    { var th = new Dictionary<string, int>(); double[] RY0 = { 0, 24000, 36000, 60000 };
      foreach (var d in tubeNode) { var G = Gsel(perDs[d.Id.Value], d.Name); if (G == null) continue; string mk = d.Name.Split(' ')[1].TrimEnd(':'); string cls = mk;
        double ax = Math.Round(G.x0 / 6000) * 6000; bool colTop = (mk == "СВ2" || mk == "СВ3") && G.z0 > 13500 && Math.Abs(G.n.Y) > 0.98 && (Math.Abs(G.x0 - ax) < 20);
        bool gcol = false; if (mk == "ГС1") foreach (double ry in RY0) if (Math.Abs(G.y0 - (ry + 321)) < 8 || Math.Abs(G.y1 - (ry - 321)) < 8) { double cx = (G.x0 + G.x1) / 2; if (Math.Abs(cx - Math.Round(cx / 6000) * 6000) < 500) gcol = true; }
        if (colTop) cls = mk + " top at column"; else if (gcol) cls = "ГС1 gcol (over column)"; string key = cls + " t=" + Math.Round(G.t, 1); th[key] = th.ContainsKey(key) ? th[key] + 1 : 1; }
      sb.AppendLine("(0) gusset thickness by class: " + string.Join("; ", th.OrderBy(q => q.Key).Select(q => q.Key + " x" + q.Value))); }    // (2) insert coverage by its own node's gusset, part with a >= 22 from the nearest tube end
    var stat = new Dictionary<string, int[]>(); var bad = new List<string>(); int tested = 0; var svIns = new Dictionary<long, double>();
    foreach (var d in tubeNode)
    {
        var lst = perDs[d.Id.Value]; var G = Gsel(lst, d.Name); if (G == null) continue;
        string mk = d.Name.Split(' ')[1].TrimEnd(':'); if (!stat.ContainsKey(mk)) stat[mk] = new int[3];
        foreach (var I in lst)
        {
            if (object.ReferenceEquals(I, G) || Math.Abs(I.t - 8) > 0.6 || Math.Abs(I.n.DotProduct(G.n)) < 0.98 || I.p2.Count < 3) continue;
            var c = I.so.ComputeCentroid(); double bd = 1e18; int bi = -1; for (int i = 0; i < ends.Count; i++) { double dd = c.DistanceTo(ends[i].Key); if (dd < bd) { bd = dd; bi = i; } }
            if (bi < 0 || bd * M > 300) continue;
            var Pe = ends[bi].Key; var U = ends[bi].Value;
            // insert polygon in G basis
            var ip = new List<double[]>(); double ux0 = 1e9, ux1 = -1e9, uy0 = 1e9, uy1 = -1e9;
            // rebuild insert polygon points in 3D from its own 2D
            foreach (var q in I.p2) { var p3 = I.o + I.e1 * q[0] + I.e2 * q[1]; var g2 = new[] { (p3 - G.o).DotProduct(G.e1), (p3 - G.o).DotProduct(G.e2) }; ip.Add(g2); ux0 = Math.Min(ux0, g2[0]); ux1 = Math.Max(ux1, g2[0]); uy0 = Math.Min(uy0, g2[1]); uy1 = Math.Max(uy1, g2[1]); }
            double step = 3 / M; int tot = 0, outc = 0;
            for (double x = ux0 + step / 2; x < ux1; x += step) for (double y = uy0 + step / 2; y < uy1; y += step)
            { if (!Pip(ip, x, y)) continue; var p3 = G.o + G.e1 * x + G.e2 * y; if ((p3 - Pe).DotProduct(U) * M < 22) continue; tot++; if (!Pip(G.p2, x, y)) outc++; }
            if (tot == 0) continue; tested++; stat[mk][0]++; double outA = outc * 9.0; if (outA > 25) { stat[mk][1]++; if (bad.Count < 14) bad.Add("INS " + I.id + " " + d.Name + " tube " + endMk[bi] + " end@" + Math.Round(Pe.X * M) + "," + Math.Round(Pe.Y * M) + "," + Math.Round(Pe.Z * M) + " outside area " + Math.Round(outA) + " mm2 of " + Math.Round(tot * 9.0)); }
        }
    }
    sb.AppendLine("(2a) inserts/tabs tested " + tested + " (part a>=22 mm from the end plate); per mark [tested, with >25 mm2 outside its gusset]: " + string.Join("; ", stat.Select(kv => kv.Key + " " + kv.Value[0] + "/" + kv.Value[1])));
    foreach (var s in bad) sb.AppendLine("    " + s);
    // bolts: axis of every M16 shaft must hit a gusset inside its outline
    int nb = 0, bout = 0; double minEdge = 1e9; var bex = new List<string>(); var edgeHist = new Dictionary<int, int>(); var boltEdge = new Dictionary<long, double>();
    foreach (var d in all.Where(x => x.Category.Id.Value == (long)BuiltInCategory.OST_StructConnectionBolts && (x.Name ?? "").StartsWith("Болт М16 (")))
        foreach (var go in d.get_Geometry(opt))
        {
            var so = go as Solid; if (so == null) continue; CylindricalFace cyl = null; foreach (Face f in so.Faces) if (f is CylindricalFace cf && Math.Abs(cf.get_Radius(0).GetLength() * M - 8) < 0.3) { cyl = cf; break; } if (cyl == null) continue;
            nb++; var c = so.ComputeCentroid(); var ax = cyl.Axis.Normalize(); bool okb = false; double ed = -1; Pl hit = null;
            foreach (var G in gus)
            {
                if (c.X * M < G.x0 - 150 || c.X * M > G.x1 + 150 || c.Y * M < G.y0 - 150 || c.Y * M > G.y1 + 150 || c.Z * M < G.z0 - 150 || c.Z * M > G.z1 + 150) continue;
                double dn = ax.DotProduct(G.n); if (Math.Abs(dn) < 0.98) continue; double tp = (G.o - c).DotProduct(G.n) / dn; if (Math.Abs(tp) * M > 40) continue;
                var q = c + ax * tp; double x = (q - G.o).DotProduct(G.e1), y = (q - G.o).DotProduct(G.e2); if (Pip(G.p2, x, y)) { okb = true; ed = EdgeD(G.p2, x, y) * M; hit = G; break; }
            }
            if (!okb) { bout++; if (bex.Count < 10) bex.Add("BOLT " + d.Id.Value + " " + d.Name + " @" + Math.Round(c.X * M) + "," + Math.Round(c.Y * M) + "," + Math.Round(c.Z * M)); }
            else { minEdge = Math.Min(minEdge, ed); int k = (int)Math.Floor(ed / 5) * 5; edgeHist[k] = edgeHist.ContainsKey(k) ? edgeHist[k] + 1 : 1; boltEdge[hit.id] = boltEdge.ContainsKey(hit.id) ? Math.Min(boltEdge[hit.id], ed) : ed; }
        }
    sb.AppendLine("(2b) M16 shafts " + nb + ": axis outside every gusset outline " + bout + "; min edge distance " + Math.Round(minEdge, 1) + " mm; edge-distance histogram (5 mm bins): " + string.Join(", ", edgeHist.OrderBy(q => q.Key).Select(q => q.Key + ":" + q.Value)));
    foreach (var s in bex) sb.AppendLine("    " + s);
    // (1) СВ2 / СВ3 top nodes at the column
    var ribs = new Dictionary<string, double>(); var colDs = plates.Where(d => (d.Name ?? "").StartsWith("Оголовок К ") && !d.Name.EndsWith("связь")).ToList(); sb.AppendLine("leftover rib-under-cap DS (names ending связь): " + plates.Count(d => (d.Name ?? "").StartsWith("Оголовок К ") && d.Name.EndsWith("связь")));
    sb.AppendLine("(1) СВ2/СВ3 top nodes at columns:  [DS id, column x/row, gusset z0..z1, rib-under-cap bottom, lower stiffener top, gap up, gap down, insert outside mm2, min bolt edge mm]");
    int nTop = 0, bandBad = 0; string[] RL = { "A", "E", "H", "M" }; double[] RY = { 0, 24000, 36000, 60000 };
    foreach (var d in tubeNode.Where(x => x.Name.StartsWith("Узел СВ2") || x.Name.StartsWith("Узел СВ3")))
    {
        var lst = perDs[d.Id.Value]; var G = Gsel(lst, d.Name); if (G == null) continue;
        double ax = Math.Round(G.x0 / 6000) * 6000; double axL = Math.Round(G.x1 / 6000) * 6000; double axis = Math.Abs(G.x0 - ax) < 20 ? ax : Math.Abs(G.x1 - axL) < 20 ? axL : double.NaN;
        if (double.IsNaN(axis) || G.z0 < 13500 || Math.Abs(G.n.Y) < 0.98) continue;
        double yr = Math.Round(G.y0 / 100) * 100; int ri = -1; for (int i = 0; i < 4; i++) if (Math.Abs(G.y0 - RY[i]) < 30) ri = i; if (ri < 0) continue; nTop++;
        double ribB = 1e9; foreach (var rd in colDs.Where(x => x.Name == "Оголовок К " + (long)axis + " " + RL[ri])) foreach (var go in rd.get_Geometry(opt)) { var so = go as Solid; if (so == null || so.Volume < 1e-12) continue; var bb = so.GetBoundingBox(); ribB = Math.Min(ribB, Math.Min(bb.Transform.OfPoint(bb.Min).Z, bb.Transform.OfPoint(bb.Max).Z) * M); }
        double lowTop = -1e9;
        foreach (var pd in plates.Where(x => x.Name == "Узел 20Ш1 шарнир к колонне " + (long)axis + " " + RL[ri] + " " + 1 || x.Name == "Узел 20Ш1 шарнир к колонне " + (long)axis + " " + RL[ri] + " -1" || x.Name == "Узел 40Б1 жёсткий к колонне " + (long)axis + " " + RL[ri] + " 1" || x.Name == "Узел 40Б1 жёсткий к колонне " + (long)axis + " " + RL[ri] + " -1"))
            foreach (var go in pd.get_Geometry(opt)) { var so = go as Solid; if (so == null || so.Volume < 1e-12) continue; var p = MkPl(pd, so); if (p == null || Math.Abs(p.n.Z) < 0.9 || p.t < 6) continue; if (p.y0 < RY[ri] - 260 || p.y1 > RY[ri] + 260 || p.z1 > G.z0 + 0.6 || p.z1 < G.z0 - 80) continue; lowTop = Math.Max(lowTop, p.z1); }
        double outA = 0; foreach (var I in lst) { if (object.ReferenceEquals(I, G) || Math.Abs(I.t - 8) > 0.6 || Math.Abs(I.n.DotProduct(G.n)) < 0.98) continue; var ip = new List<double[]>(); double ux0 = 1e9, ux1 = -1e9, uy0 = 1e9, uy1 = -1e9; foreach (var q in I.p2) { var p3 = I.o + I.e1 * q[0] + I.e2 * q[1]; var g2 = new[] { (p3 - G.o).DotProduct(G.e1), (p3 - G.o).DotProduct(G.e2) }; ip.Add(g2); ux0 = Math.Min(ux0, g2[0]); ux1 = Math.Max(ux1, g2[0]); uy0 = Math.Min(uy0, g2[1]); uy1 = Math.Max(uy1, g2[1]); }
            double step = 3 / M; for (double x = ux0 + step / 2; x < ux1; x += step) for (double y = uy0 + step / 2; y < uy1; y += step) { if (!Pip(ip, x, y)) continue; var p3 = G.o + G.e1 * x + G.e2 * y; double a = 1e9; foreach (var e in ends) if (e.Key.DistanceTo(p3) * M < 400) a = Math.Min(a, 0); /* region filter below */ if (!Pip(G.p2, x, y)) { double dmin = 1e9; for (int i = 0; i < ends.Count; i++) { if (ends[i].Key.DistanceTo(p3) * M > 400) continue; dmin = Math.Min(dmin, 0); var aa = (p3 - ends[i].Key).DotProduct(ends[i].Value) * M; if (aa >= 22) { outA += 9; break; } } } } }
        double gu = ribB - G.z1, gd = G.z0 - lowTop; bool badn = Math.Abs(gu) > 1.0 || Math.Abs(gd) > 1.0 || outA > 25; if (badn) bandBad++;
        sb.AppendLine("   " + d.Id.Value + " x" + (long)axis + "/" + RL[ri] + " z " + Math.Round(G.z0, 1) + ".." + Math.Round(G.z1, 1) + " rib " + Math.Round(ribB, 1) + " low " + Math.Round(lowTop, 1) + " up " + Math.Round(gu, 1) + " down " + Math.Round(gd, 1) + " insOut " + Math.Round(outA) + " t=" + Math.Round(G.t, 1) + " boltEdge " + (boltEdge.ContainsKey(G.id) ? Math.Round(boltEdge[G.id], 1).ToString() : "?") + (badn ? "  <<<" : ""));
    }
    sb.AppendLine("(1) top nodes found " + nTop + ", out of band/outside " + bandBad);
    // tube end distance from column axis for СВ2/СВ3 top ends
    var dh = new Dictionary<int, int>();
    foreach (var f in new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Location is LocationCurve && x.Symbol.Family.Name.Contains("труба")))
    { string mk = Cm(f).Split(' ')[0]; if (mk != "СВ2" && mk != "СВ3") continue; var c = (f.Location as LocationCurve).Curve; foreach (int k in new[] { 0, 1 }) { var p = c.GetEndPoint(k); if (p.Z * M < 13500) continue; double dx = Math.Abs(p.X * M - Math.Round(p.X * M / 6000) * 6000); if (dx > 700) continue; int bk = (int)Math.Round(dx / 10) * 10; dh[bk] = dh.ContainsKey(bk) ? dh[bk] + 1 : 1; } }
    sb.AppendLine("СВ2/СВ3 top tube-end distance from the column axis, mm (10 mm bins): " + string.Join(", ", dh.OrderBy(q => q.Key).Select(q => q.Key + ":" + q.Value)));
    return sb.ToString();
}
static void _end() {