// READ-ONLY gusset coverage check (checker). Run WITHOUT -Lib.
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\q_gus3.txt";
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
static double EdgeD(List<double[]> P, double x, double y) { double m = 1e9; for (int i = 0, j = P.Count - 1; i < P.Count; j = i++) { double ax = P[j][0], ay = P[j][1], bx = P[i][0], by = P[i][1]; double dx = bx - ax, dy = by - ay, l2 = dx * dx + dy * dy; double t = l2 < 1e-12 ? 0 : Math.Max(0, Math.Min(1, ((x - ax) * dx + (y - ay) * dy) / l2)); m = Math.Min(m, Math.Sqrt((x - ax - t * dx) * (x - ax - t * dx) + (y - ay - t * dy) * (y - ay - t * dy))); } return m; }
static string Q(Document nd)
{
    var sb = new System.Text.StringBuilder(); var opt = new Options { DetailLevel = ViewDetailLevel.Fine };
    var ids = new long[] { 3261949, 3262037 };
    var all = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел").ToList();
    foreach (long id in ids)
    {
        var d = (DirectShape)nd.GetElement(new ElementId(id)); var lst = new List<Pl>();
        foreach (var go in d.get_Geometry(opt)) { var so = go as Solid; if (so == null || so.Volume < 1e-12) continue; var p = MkPl(d, so); if (p != null) lst.Add(p); }
        var G = lst.First(p => Math.Abs(p.t - 10) < 0.7);
        sb.AppendLine("DS " + id + " " + d.Name + "; gusset n=" + G.n.X.ToString("0.000") + "," + G.n.Y.ToString("0.000") + "," + G.n.Z.ToString("0.000") + " bbox x " + Math.Round(G.x0) + ".." + Math.Round(G.x1) + " y " + Math.Round(G.y0) + ".." + Math.Round(G.y1) + " z " + Math.Round(G.z0) + ".." + Math.Round(G.z1));
        Func<Pl, string> poly = p => string.Join(" ", p.p2.Select(q => "(" + Math.Round(q[0] * M) + "," + Math.Round(q[1] * M) + ")"));
        // use G basis for all
        foreach (var p in lst)
        {
            var pts = new List<string>(); foreach (var q in p.p2) { var p3 = p.o + p.e1 * q[0] + p.e2 * q[1]; pts.Add("(" + Math.Round((p3 - G.o).DotProduct(G.e1) * M) + "," + Math.Round((p3 - G.o).DotProduct(G.e2) * M) + ")"); }
            sb.AppendLine("  t=" + Math.Round(p.t, 1) + " dotG=" + Math.Round(p.n.DotProduct(G.n), 2) + " poly(G basis mm): " + string.Join(" ", pts));
        }
        // tubes near
        var cen = G.so.ComputeCentroid();
        foreach (var f in new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Location is LocationCurve && x.Symbol.Family.Name.Contains("труба")))
        { var c = (f.Location as LocationCurve).Curve; foreach (int k in new[] { 0, 1 }) { var pe = c.GetEndPoint(k); if (pe.DistanceTo(cen) * M < 400) { var u = (k == 0 ? c.GetEndPoint(0) - c.GetEndPoint(1) : c.GetEndPoint(1) - c.GetEndPoint(0)).Normalize(); sb.AppendLine("  tube end " + f.Id.Value + " " + (f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString()) + " Pe(G)=(" + Math.Round((pe - G.o).DotProduct(G.e1) * M) + "," + Math.Round((pe - G.o).DotProduct(G.e2) * M) + ") U(G)=(" + Math.Round(u.DotProduct(G.e1), 2) + "," + Math.Round(u.DotProduct(G.e2), 2) + ")"); } } }
        foreach (var bd in all.Where(x => x.Category.Id.Value == (long)BuiltInCategory.OST_StructConnectionBolts && (x.Name ?? "").StartsWith("Болт М16 (")))
        {
            var bb0 = bd.get_BoundingBox(null); if (bb0 == null) continue; var mid = (bb0.Min + bb0.Max) / 2; if (mid.DistanceTo(cen) * M > 700) continue;
            int cnt = 0; foreach (var go in bd.get_Geometry(opt)) { var so = go as Solid; if (so == null) continue; foreach (Face f in so.Faces) if (f is CylindricalFace cf && Math.Abs(cf.get_Radius(0).GetLength() * M - 8) < 0.3) { var cc = so.ComputeCentroid(); if (cc.DistanceTo(cen) * M < 300) { sb.AppendLine("  bolt shaft in " + bd.Id.Value + " @G(" + Math.Round((cc - G.o).DotProduct(G.e1) * M) + "," + Math.Round((cc - G.o).DotProduct(G.e2) * M) + ")"); cnt++; } break; } }
        }
    }
    int sh = 0, solids = 0; foreach (var bd in all.Where(x => x.Category.Id.Value == (long)BuiltInCategory.OST_StructConnectionBolts && (x.Name ?? "").StartsWith("Болт М16 ("))) foreach (var go in bd.get_Geometry(opt)) { var so = go as Solid; if (so == null) continue; solids++; foreach (Face f in so.Faces) if (f is CylindricalFace cf && Math.Abs(cf.get_Radius(0).GetLength() * M - 8) < 0.3) { sh++; break; } }
    sb.AppendLine("bolt solids " + solids + " shafts " + sh);
    return sb.ToString();
}
static void _end() {