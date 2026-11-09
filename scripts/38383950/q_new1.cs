// READ-ONLY gusset coverage check (checker). Run WITHOUT -Lib.
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\q_new1.txt";
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
    var all = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел").ToList();
    // 1. bolt diameters
    var bd = new Dictionary<string, Dictionary<int, int>>();
    foreach (var d in all.Where(x => x.Category.Id.Value == (long)BuiltInCategory.OST_StructConnectionBolts && !(x.Name ?? "").StartsWith("Фундаментный")))
    {
        string nm = d.Name ?? ""; string key = nm.StartsWith("Болт М16 (") ? nm : nm.StartsWith("Болт Узел 9") ? "Болт Узел 9 КН" : nm.StartsWith("Болт Узел") ? "Болт Узел (шарнир/жёсткий)" : nm.StartsWith("Болт Пр1") ? "Болт Пр1 опора" : nm.Split(' ')[0] + " " + (nm.Split(' ').Length > 1 ? nm.Split(' ')[1] : "");
        foreach (var go in d.get_Geometry(opt)) { var so = go as Solid; if (so == null || so.Volume < 1e-12) continue; double best = 0, rr = 0; foreach (Face f in so.Faces) if (f is CylindricalFace cf && cf.Area > best) { best = cf.Area; rr = cf.get_Radius(0).GetLength(); }
            if (best * M * M < 800) continue; int dia = (int)Math.Round(rr * M * 2); if (!bd.ContainsKey(key)) bd[key] = new Dictionary<int, int>(); bd[key][dia] = bd[key].ContainsKey(dia) ? bd[key][dia] + 1 : 1; }
    }
    sb.AppendLine("== bolt shaft diameters by DS group (shaft count)"); foreach (var kv in bd.OrderBy(q => q.Key)) sb.AppendLine("   " + kv.Key + ": " + string.Join(", ", kv.Value.OrderBy(q => q.Key).Select(q => "M" + q.Key + "x" + q.Value)));
    // 2. signature histograms for selected DS groups
    Func<Solid, double> thick = so => { double af = 0; foreach (Face f in so.Faces) if (f is PlanarFace) af = Math.Max(af, f.Area); return af > 0 ? so.Volume / af * M : 0; };
    foreach (var pref in new[] { "Узел Р2", "Узел 9 КН", "Упор крановый 40Б2" })
    {
        var h = new Dictionary<string, List<long>>();
        foreach (var d in all.Where(x => x.Category.Id.Value == (long)BuiltInCategory.OST_StructConnections && (x.Name ?? "").StartsWith(pref)))
        { var ts = new List<string>(); foreach (var go in d.get_Geometry(opt)) { var so = go as Solid; if (so == null || so.Volume < 1e-12) continue; ts.Add(Math.Round(thick(so)).ToString()); } string k = string.Join(",", ts.GroupBy(q => q).OrderBy(g => double.Parse(g.Key)).Select(g => g.Key + "x" + g.Count())); if (!h.ContainsKey(k)) h[k] = new List<long>(); h[k].Add(d.Id.Value); }
        sb.AppendLine("== thickness signatures (mm x count) for DS «" + pref + "»");
        foreach (var kv in h.OrderByDescending(q => q.Value.Count).Take(8)) sb.AppendLine("   " + kv.Value.Count + " x [" + kv.Key + "] e.g. id " + kv.Value[0] + " " + all.First(x => x.Id.Value == kv.Value[0]).Name);
    }
    // names of the extra KN groups
    sb.AppendLine("== distinct 'Узел 9 КН' DS name shapes: " + string.Join(" | ", all.Where(x => (x.Name ?? "").StartsWith("Узел 9 КН") && x.Category.Id.Value == (long)BuiltInCategory.OST_StructConnections).Select(x => System.Text.RegularExpressions.Regex.Replace(x.Name, @"\d+", "#")).Distinct()));
    // 3. members
    Func<FamilyInstance, string> Cm = f => f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "";
    var fi = new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Location is LocationCurve).ToList();
    sb.AppendLine("== БМ2 members:"); foreach (var f in fi.Where(x => Cm(x) == "БМ2").Take(12)) { var c = (f.Location as LocationCurve).Curve; var a = c.GetEndPoint(0) * M; var b = c.GetEndPoint(1) * M; sb.AppendLine("   id " + f.Id.Value + " " + f.Symbol.Name + " a(" + Math.Round(a.X) + "," + Math.Round(a.Y) + "," + Math.Round(a.Z) + ") b(" + Math.Round(b.X) + "," + Math.Round(b.Y) + "," + Math.Round(b.Z) + ") len " + Math.Round(c.Length * M)); }
    sb.AppendLine("== БМ1 first members: " + string.Join("; ", fi.Where(x => Cm(x) == "БМ1").Take(3).Select(f => { var c = (f.Location as LocationCurve).Curve; var a = c.GetEndPoint(0) * M; return f.Id.Value + " x" + Math.Round(a.X) + " y" + Math.Round(a.Y) + " len " + Math.Round(c.Length * M); })));
    // top tier СВ2/СВ3: per (bay, row) pattern
    var tiers = fi.Where(x => Cm(x).StartsWith("СВ2") || Cm(x).StartsWith("СВ3")).GroupBy(x => { var c = (x.Location as LocationCurve).Curve; var a = c.GetEndPoint(0) * M; var b = c.GetEndPoint(1) * M; return Math.Round(((a.X + b.X) / 2) / 6000 - 0.5) + " " + Math.Round(a.Y); }).ToList();
    var pat = new Dictionary<string, int>(); XYZ ex1 = null; string exs = "";
    foreach (var g in tiers) { var ls = g.Select(f => (f.Location as LocationCurve).Curve.Length * M).OrderByDescending(v => v).ToList(); string p = g.Count() + " members: through " + ls.Count(v => v > 5500) + ", others " + string.Join("/", ls.Where(v => v <= 5500).Select(v => Math.Round(v / 50) * 50)); pat[p] = pat.ContainsKey(p) ? pat[p] + 1 : 1; if (exs == "") exs = g.Key + ": " + string.Join(" ; ", g.Select(f => { var c = (f.Location as LocationCurve).Curve; var a = c.GetEndPoint(0) * M; var b = c.GetEndPoint(1) * M; return f.Id.Value + " (" + Math.Round(a.X) + "," + Math.Round(a.Z) + ")->(" + Math.Round(b.X) + "," + Math.Round(b.Z) + ")"; })); }
    sb.AppendLine("== СВ2/СВ3 tiers (bay,row) " + tiers.Count + "; patterns: " + string.Join(" | ", pat.Select(q => q.Value + " x [" + q.Key + "]")));
    sb.AppendLine("   example tier " + exs);
    return sb.ToString();
}
static void _end() {