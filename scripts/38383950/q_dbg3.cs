// READ-ONLY gusset coverage check (checker). Run WITHOUT -Lib.
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\q_dbg3.txt";
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
class Tb2 { public XYZ a, b, u, e1, e2; public double len, hb, hb2; public string mk; public long id; }
static List<double[]> Hull2(List<double[]> pts) {
    var p = pts.OrderBy(q => q[0]).ThenBy(q => q[1]).ToList(); if (p.Count < 3) return p;
    Func<double[], double[], double[], double> cr = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
    var lo = new List<double[]>(); foreach (var q in p) { while (lo.Count >= 2 && cr(lo[lo.Count - 2], lo[lo.Count - 1], q) <= 0) lo.RemoveAt(lo.Count - 1); lo.Add(q); }
    var up = new List<double[]>(); foreach (var q in Enumerable.Reverse(p)) { while (up.Count >= 2 && cr(up[up.Count - 2], up[up.Count - 1], q) <= 0) up.RemoveAt(up.Count - 1); up.Add(q); }
    lo.RemoveAt(lo.Count - 1); up.RemoveAt(up.Count - 1); return lo.Concat(up).ToList(); }
static List<XYZ> Verts(Solid so) { var v = new List<XYZ>(); foreach (Edge ed in so.Edges) { var c = ed.AsCurve(); v.Add(c.GetEndPoint(0)); v.Add(c.GetEndPoint(1)); } return v; }
static string Q(Document nd)
{
    var sb = new System.Text.StringBuilder(); var opt = new Options { DetailLevel = ViewDetailLevel.Fine };
    foreach (long id in new long[] { 3441096, 3441688 })
    {
        var d = (DirectShape)nd.GetElement(new ElementId(id)); var lst = new List<Pl>(); foreach (var go in d.get_Geometry(opt)) { var so = go as Solid; if (so == null || so.Volume < 1e-12) continue; var p = MkPl(d, so); if (p != null) lst.Add(p); }
        var G = Gsel(lst, d.Name); sb.AppendLine("DS " + id + " " + d.Name + " gusset t=" + Math.Round(G.t, 1));
        Func<Pl, string> poly = p => string.Join(" ", p.p2.Select(q => { var w = p.o + p.e1 * q[0] + p.e2 * q[1]; return "(" + Math.Round((w - G.o).DotProduct(G.e1) * M) + "," + Math.Round((w - G.o).DotProduct(G.e2) * M) + ")"; }));
        sb.AppendLine("  GUSSET poly (G basis): " + poly(G));
        foreach (var p in lst) if (!object.ReferenceEquals(p, G)) sb.AppendLine("  plate t=" + Math.Round(p.t, 1) + " dotG " + Math.Round(p.n.DotProduct(G.n), 2) + " poly " + poly(p));
        var bd = nd.GetElement(new ElementId(id + 2)); sb.AppendLine("  bolt DS " + bd.Id.Value + " " + bd.Name);
        foreach (var go in bd.get_Geometry(opt)) { var so = go as Solid; if (so == null || so.Volume < 1e-12) continue; double best = 0, rr = 0; foreach (Face f in so.Faces) if (f is CylindricalFace cf && cf.Area > best) { best = cf.Area; rr = cf.get_Radius(0).GetLength(); } if (best * M * M < 800) continue; var c = so.ComputeCentroid(); double x = (c - G.o).DotProduct(G.e1), y = (c - G.o).DotProduct(G.e2);
            sb.AppendLine("   shaft M" + Math.Round(rr * M * 2) + " at G(" + Math.Round(x * M) + "," + Math.Round(y * M) + ") inside " + Pip(G.p2, x, y) + " edge " + Math.Round(EdgeD(G.p2, x, y) * M, 1)); }
        // end plate / tube end
    }
    return sb.ToString();
}
static void _end() {