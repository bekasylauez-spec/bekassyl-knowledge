// READ-ONLY gusset coverage check (checker). Run WITHOUT -Lib.
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\q_r2.txt";
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
    Func<Solid, double> thick = so => { double af = 0; foreach (Face f in so.Faces) if (f is PlanarFace) af = Math.Max(af, f.Area); return af > 0 ? so.Volume / af * M : 0; };
    Action<Element, string> dump = (d, lab) => { foreach (var go in d.get_Geometry(opt)) { var so = go as Solid; if (so == null || so.Volume < 1e-12) continue; var bb = so.GetBoundingBox(); var a = bb.Transform.OfPoint(bb.Min); var b = bb.Transform.OfPoint(bb.Max);
        sb.AppendLine("   " + lab + " t=" + Math.Round(thick(so), 1) + " x " + Math.Round(Math.Min(a.X, b.X) * M) + ".." + Math.Round(Math.Max(a.X, b.X) * M) + " y " + Math.Round(Math.Min(a.Y, b.Y) * M) + ".." + Math.Round(Math.Max(a.Y, b.Y) * M) + " z " + Math.Round(Math.Min(a.Z, b.Z) * M) + ".." + Math.Round(Math.Max(a.Z, b.Z) * M) + " vol " + Math.Round(so.Volume * M * M * M)); } };
    foreach (long id in new long[] { 3412266, 3412262 }) { var d = nd.GetElement(new ElementId(id)); sb.AppendLine("DS " + id + " " + d.Name); dump(d, "plate"); }
    var bolt = nd.GetElement(new ElementId(3412264)); sb.AppendLine("BOLT DS " + bolt.Id.Value + " " + bolt.Name); foreach (var go in bolt.get_Geometry(opt)) { var so = go as Solid; if (so == null || so.Volume < 1e-12) continue; var bb = so.GetBoundingBox(); var a = bb.Transform.OfPoint(bb.Min); var b = bb.Transform.OfPoint(bb.Max); if (Math.Abs(so.Volume * M * M * M - 9045) < 60) sb.AppendLine("   shaft x " + Math.Round(Math.Min(a.X, b.X) * M) + ".." + Math.Round(Math.Max(a.X, b.X) * M) + " y " + Math.Round(Math.Min(a.Y, b.Y) * M) + ".." + Math.Round(Math.Max(a.Y, b.Y) * M) + " z " + Math.Round(Math.Min(a.Z, b.Z) * M) + ".." + Math.Round(Math.Max(a.Z, b.Z) * M)); }
    Func<FamilyInstance, string> Cm = f => f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "";
    foreach (var f in new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>())
    { var bb = f.get_BoundingBox(null); if (bb == null) continue; double cx = (bb.Min.X + bb.Max.X) / 2 * M; double cy = (bb.Min.Y + bb.Max.Y) / 2 * M;
      string c = Cm(f); if ((c == "Р2" && Math.Abs(bb.Min.X * M - 6000) < 400 && bb.Min.Y * M > 2900 && bb.Max.Y * M < 3200) || (c == "ФФ1 НП" && Math.Abs(cx - 6000) < 5 && bb.Min.Y * M < 3050 && bb.Max.Y * M > 3050) || (c == "Р2" && Math.Abs(cx - 9000) < 3100 && Math.Abs(cy - 3050) < 80 && sb.Length < 100000 && f.Id.Value < 3402090))
        sb.AppendLine("MEMBER " + c + " id " + f.Id.Value + " " + f.Symbol.Name + " bbox x " + Math.Round(bb.Min.X * M) + ".." + Math.Round(bb.Max.X * M) + " y " + Math.Round(bb.Min.Y * M) + ".." + Math.Round(bb.Max.Y * M) + " z " + Math.Round(bb.Min.Z * M) + ".." + Math.Round(bb.Max.Z * M)); }
    // ВС1 bottoms vs lower Р2 top: ВС1 ends near z 12200..12300
    return sb.ToString();
}
static void _end() {