// READ-ONLY gusset coverage check (checker). Run WITHOUT -Lib.
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\q_vs.txt";
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
static Pl Gsel(List<Pl> lst, string name) { var c = ((name ?? "").Contains("ГС1") || (name ?? "").Contains("Р2")) ? lst : lst.Where(p => Math.Abs(p.n.Z) < 0.5).ToList(); if (c.Count == 0) c = lst; return c.OrderByDescending(p => PolyA(p)).FirstOrDefault(); }
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
    Func<FamilyInstance, string> Cm = f => f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "";
    var p2 = new List<FamilyInstance>(); var vs = new List<FamilyInstance>();
    foreach (var f in new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>()) { string c = Cm(f); if (c == "Р2") p2.Add(f); else if (c == "ВС1") vs.Add(f); }
    var gaps = new Dictionary<int, int>(); int n = 0, nop = 0; var ex = new List<string>();
    foreach (var f in vs)
    {
        var c = (f.Location as LocationCurve).Curve; var a = c.GetEndPoint(0) * M; var b = c.GetEndPoint(1) * M; var low = a.Z < b.Z ? a : b; var other = a.Z < b.Z ? b : a;
        // gusset of the lower end: DS «Узел ВС1» plate whose bbox contains low (xy) and z near
        var P = p2.Where(q => { var bb = q.get_BoundingBox(null); return bb != null && low.X > bb.Min.X * M - 20 && low.X < bb.Max.X * M + 20 && Math.Abs(low.Y - (bb.Min.Y + bb.Max.Y) / 2 * M) < 60; }).OrderBy(q => q.get_BoundingBox(null).Max.Z).FirstOrDefault();
        n++; if (P == null) { nop++; if (ex.Count < 5) ex.Add("no Р2 under ВС1 " + f.Id.Value + " low end (" + Math.Round(low.X) + "," + Math.Round(low.Y) + "," + Math.Round(low.Z) + ")"); continue; }
        double top = P.get_BoundingBox(null).Max.Z * M; var cc = (P.Location as LocationCurve).Curve; double pzc = (cc.GetEndPoint(0).Z + cc.GetEndPoint(1).Z) / 2 * M;
        int k = (int)Math.Round(low.Z - top); gaps[k] = gaps.ContainsKey(k) ? gaps[k] + 1 : 1; if (ex.Count < 3) ex.Add("ВС1 " + f.Id.Value + " low end z " + Math.Round(low.Z) + " Р2 id " + P.Id.Value + " top z " + Math.Round(top) + " axis z " + Math.Round(pzc));
    }
    sb.AppendLine("ВС1 members " + vs.Count + ": lower end minus Р2 bbox top (mm) histogram: " + string.Join(", ", gaps.OrderBy(q => q.Key).Select(q => q.Key + ":" + q.Value)) + "; without Р2 below " + nop);
    foreach (var s in ex) sb.AppendLine("  " + s);
    // gusset-bottom of ВС1 DS vs Р2 top
    var ds = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел" && (x.Name ?? "").StartsWith("Узел ВС1")).ToList();
    var gz = new Dictionary<int, int>();
    foreach (var d in ds) { var lst = new List<Pl>(); foreach (var go in d.get_Geometry(opt)) { var so = go as Solid; if (so == null || so.Volume < 1e-12) continue; var p = MkPl(d, so); if (p != null) lst.Add(p); } var G = Gsel(lst, d.Name); if (G == null || G.z0 > 13000) continue;
        double cx = (G.x0 + G.x1) / 2, cy = (G.y0 + G.y1) / 2; var P = p2.Where(q => { var bb = q.get_BoundingBox(null); return bb != null && cx > bb.Min.X * M - 20 && cx < bb.Max.X * M + 20 && Math.Abs(cy - (bb.Min.Y + bb.Max.Y) / 2 * M) < 60; }).FirstOrDefault(); if (P == null) continue; int k = (int)Math.Round(G.z0 - P.get_BoundingBox(null).Max.Z * M); gz[k] = gz.ContainsKey(k) ? gz[k] + 1 : 1; }
    sb.AppendLine("ВС1 bottom gusset z0 minus Р2 top (mm): " + string.Join(", ", gz.OrderBy(q => q.Key).Select(q => q.Key + ":" + q.Value)));
    return sb.ToString();
}
static void _end() {