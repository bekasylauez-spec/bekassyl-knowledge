// READ-ONLY gusset coverage check (checker). Run WITHOUT -Lib.
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\q_col3_v.txt";
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
static double BoxGap(Pl a, Pl b) { double dx = Math.Max(0, Math.Max(a.x0 - b.x1, b.x0 - a.x1)), dy = Math.Max(0, Math.Max(a.y0 - b.y1, b.y0 - a.y1)), dz = Math.Max(0, Math.Max(a.z0 - b.z1, b.z0 - a.z1)); return Math.Sqrt(dx * dx + dy * dy + dz * dz); }
static double ZAt(Pl p, double x, double y, out double zlo, out double zhi)
{   // z of the selected face plane at world (x,y), and the slab extent
    double zf = p.o.Z - (p.n.X * (x - p.o.X) + p.n.Y * (y - p.o.Y)) / p.n.Z; double dz = p.t / Math.Abs(p.n.Z);
    if (p.n.Z > 0) { zhi = zf; zlo = zf - dz; } else { zlo = zf; zhi = zf + dz; } return zf; }
static string Q(Document nd)
{
    var sb = new System.Text.StringBuilder(); var opt = new Options { DetailLevel = ViewDetailLevel.Fine };
    double[] RY = { 0, 24000, 36000, 60000 }; string[] RL = { "A", "E", "H", "M" };
    var plates = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел" && x.Category.Id.Value == (long)BuiltInCategory.OST_StructConnections).ToList();
    var g8 = new List<Pl>(); var colPl = new Dictionary<string, List<Pl>>();
    foreach (var d in plates)
    {
        string n = d.Name ?? ""; bool gs = n.StartsWith("Узел ГС1") && n.Contains("вкладыши"); bool colNode = n.Contains(" к колонне ") || n.StartsWith("Оголовок К ") || n.StartsWith("Узел 9 КН");
        if (!gs && !colNode) continue; var lst = new List<Pl>(); foreach (var go in d.get_Geometry(opt)) { var so = go as Solid; if (so == null || so.Volume < 1e-12) continue; var p = MkPl(d, so); if (p != null) lst.Add(p); }
        if (gs) { var G = Gsel(lst, d.Name); if (G != null && Math.Abs(G.t - 8) < 0.7) g8.Add(G); }
        else { string[] tk = n.Split(' '); string key = n.StartsWith("Оголовок") ? tk[2] + " " + tk[3] : n.StartsWith("Узел 9 КН") ? tk[3] + " " + tk[4] : tk[tk.Length - 3] + " " + tk[tk.Length - 2]; if (!colPl.ContainsKey(key)) colPl[key] = new List<Pl>(); colPl[key].AddRange(lst.Where(p => Math.Abs(p.n.Z) > 0.9 && p.t > 7 && p.p2.Count >= 3)); }
    }
    int nOver = 0; double maxOver = 0, minGap = 1e9; var ex = new List<string>(); var byKind = new Dictionary<string, int>(); var perG = new Dictionary<long, string>();
    foreach (var G in g8)
    {
        double cx = (G.x0 + G.x1) / 2, cy = (G.y0 + G.y1) / 2; double ax = Math.Round(cx / 6000) * 6000; int ri = 0; double bdr = 1e9; for (int i2 = 0; i2 < 4; i2++) if (Math.Abs(cy - RY[i2]) < bdr) { bdr = Math.Abs(cy - RY[i2]); ri = i2; }
        string key = (long)ax + " " + RL[ri]; List<Pl> neigh; if (!colPl.TryGetValue(key, out neigh)) continue;
        // gusset polygon in world XY
        var gp = new List<double[]>(); foreach (var q in G.p2) { var w = G.o + G.e1 * q[0] + G.e2 * q[1]; gp.Add(new[] { w.X * M, w.Y * M }); }
        foreach (var P in neigh)
        {
            if (P.name.StartsWith("Узел 9")) continue; var pp = new List<double[]>(); foreach (var q in P.p2) { var w = P.o + P.e1 * q[0] + P.e2 * q[1]; pp.Add(new[] { w.X * M, w.Y * M }); }
            double ox0 = Math.Max(gp.Min(q => q[0]), pp.Min(q => q[0])), ox1 = Math.Min(gp.Max(q => q[0]), pp.Max(q => q[0])), oy0 = Math.Max(gp.Min(q => q[1]), pp.Min(q => q[1])), oy1 = Math.Min(gp.Max(q => q[1]), pp.Max(q => q[1])); if (ox1 <= ox0 || oy1 <= oy0) continue;
            double area = 0, gapMin = 1e9;
            for (double x = ox0 + 1.5; x < ox1; x += 3) for (double y = oy0 + 1.5; y < oy1; y += 3)
            { if (!Pip(gp, x, y) || !Pip(pp, x, y)) continue; area += 9; double glo, ghi, plo, phi; ZAt(G, x / M, y / M, out glo, out ghi); ZAt(P, x / M, y / M, out plo, out phi); double gap = plo >= ghi - 0.01 ? plo - ghi : (glo >= phi - 0.01 ? glo - phi : -1); gapMin = Math.Min(gapMin, gap); }
            if (area > 0) { nOver++; maxOver = Math.Max(maxOver, area); minGap = Math.Min(minGap, gapMin); string kind = P.name.Contains("Оголовок") ? "cap" : P.name.Contains("шарнир") ? "ФФ1 node" : "БП node"; byKind[kind] = byKind.ContainsKey(kind) ? byKind[kind] + 1 : 1; if (ex.Count < 8) ex.Add("PLAN OVERLAP gusset " + G.id + " with " + P.id + " " + P.name + " t=" + Math.Round(P.t, 1) + " area " + Math.Round(area) + " mm2, min vertical gap " + Math.Round(gapMin, 2) + " mm"); }
        }
    }
    sb.AppendLine("ГС1 t=8 gussets " + g8.Count + "; (gusset, column plate) pairs with plan overlap " + nOver + " by kind " + string.Join(", ", byKind.Select(q => q.Key + " " + q.Value)) + "; max overlap area " + Math.Round(maxOver) + " mm2; min vertical gap " + Math.Round(minGap, 2) + " mm");
    foreach (var s in ex) sb.AppendLine("  " + s);
    return sb.ToString();
}
static void _end() {