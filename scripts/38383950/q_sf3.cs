// READ-ONLY gusset coverage check (checker). Run WITHOUT -Lib.
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\q_sf3.txt";
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
static double MinDist(Solid a, Solid b)
{
    double m = 1e9;
    foreach (var v in Verts(a)) foreach (Face f in b.Faces) { var r = f.Project(v); if (r != null) m = Math.Min(m, r.Distance); }
    foreach (var v in Verts(b)) foreach (Face f in a.Faces) { var r = f.Project(v); if (r != null) m = Math.Min(m, r.Distance); }
    return m;
}
static List<XYZ> Verts(Solid so) { var v = new List<XYZ>(); foreach (Edge ed in so.Edges) { var c = ed.AsCurve(); v.Add(c.GetEndPoint(0)); v.Add(c.GetEndPoint(1)); } return v; }
static double BoxG(Pl a, Pl b) { double dx = Math.Max(0, Math.Max(a.x0 - b.x1, b.x0 - a.x1)), dy = Math.Max(0, Math.Max(a.y0 - b.y1, b.y0 - a.y1)), dz = Math.Max(0, Math.Max(a.z0 - b.z1, b.z0 - a.z1)); return Math.Sqrt(dx * dx + dy * dy + dz * dz); }
static string Q(Document nd)
{
    var sb = new System.Text.StringBuilder(); var opt = new Options { DetailLevel = ViewDetailLevel.Fine };
    Func<FamilyInstance, string> Cm = f => f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "";
    var posts = new List<FamilyInstance>(); var beams = new List<FamilyInstance>();
    foreach (var f in new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>()) { string c = Cm(f); if (c == "СФ") posts.Add(f); else if (c == "БП1") beams.Add(f); }
    var all = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел").ToList();
    var sfDs = all.Where(d => (d.Name ?? "").StartsWith("Узел 5 СФ") && d.Category.Id.Value == (long)BuiltInCategory.OST_StructConnections).ToList();
    sb.AppendLine("posts СФ " + posts.Count + ", beams БП1 " + beams.Count + ", node-5 plate DS " + sfDs.Count + "; all node-5 DS names/categories: " + string.Join("; ", all.Where(d => (d.Name ?? "").StartsWith("Узел 5 СФ")).GroupBy(d => d.Category.Name).Select(g => g.Key + " x" + g.Count())));
    var others = new List<KeyValuePair<DirectShape, Pl>>();
    foreach (var d in all.Where(x => x.Category.Id.Value == (long)BuiltInCategory.OST_StructConnections && !(x.Name ?? "").StartsWith("Узел 5 СФ") && !(x.Name ?? "").StartsWith("База") && x.ApplicationDataId != "база"))
    { var bb0 = d.get_BoundingBox(null); if (bb0 == null) continue; if (!(bb0.Min.X * M < 600 || bb0.Max.X * M > 162000 - 600)) continue; foreach (var go in d.get_Geometry(opt)) { var so = go as Solid; if (so == null || so.Volume < 1e-12) continue; var p = MkPl(d, so); if (p != null) others.Add(new KeyValuePair<DirectShape, Pl>(d, p)); } }
    sb.AppendLine("neighbour plate solids at the end axes: " + others.Count);
    var kinds = new Dictionary<string, double>(); var zt = new List<double>(); int n = 0; var rows = new List<string>(); double minW = 1e9, maxW = -1e9, minT = 1e9, maxT = -1e9; var gapsA = new List<double>(); var gapsB = new List<double>(); var dzBot = new List<double>(); var dzTop = new List<double>(); var dxc = new List<double>(); var dyc = new List<double>(); int nInt = 0; double minNb = 1e9; string minNbName = ""; var hs = new List<double>();
    foreach (var d in sfDs)
    {
        var lst = new List<Pl>(); foreach (var go in d.get_Geometry(opt)) { var so = go as Solid; if (so == null || so.Volume < 1e-12) continue; var p = MkPl(d, so); if (p != null) lst.Add(p); }
        foreach (var P in lst)
        {
            n++; double w = P.x1 - P.x0, th = P.y1 - P.y0, h = P.z1 - P.z0; minW = Math.Min(minW, w); maxW = Math.Max(maxW, w); minT = Math.Min(minT, th); maxT = Math.Max(maxT, th); hs.Add(h);
            double cx = (P.x0 + P.x1) / 2, cy = (P.y0 + P.y1) / 2; { double yy = Math.Min(cy, 60000 - cy); zt.Add(P.z1 - (14490 + 750.0 / 29705.5 * (yy - 294.5))); } double ax = Math.Round(cx / 162000) * 162000;
            FamilyInstance post = posts.OrderBy(f => { var l = ((LocationPoint)f.Location).Point; return Math.Abs(l.X * M - ax) + Math.Abs(l.Y * M - cy); }).FirstOrDefault();
            var pl = ((LocationPoint)post.Location).Point; double px = pl.X * M, py = pl.Y * M; var pbb = post.get_BoundingBox(null); double ptop = pbb.Max.Z * M;
            dxc.Add(cx - px); dyc.Add(cy - py); dzBot.Add(P.z0 - ptop);
            double btop = -1e9, bgA = 1e9, bgB = 1e9; foreach (var b in beams) { var bb = b.get_BoundingBox(null); if (bb == null) continue; double bx = (bb.Min.X + bb.Max.X) / 2 * M; if (Math.Abs(bx - px) > 100) continue; double y0 = bb.Min.Y * M, y1 = bb.Max.Y * M; if (y1 < py - 3000 || y0 > py + 3000) continue;
                if (y1 <= py + 1) { double g = P.y0 - y1; if (g < bgA && g > -50) { bgA = g; btop = Math.Max(btop, bb.Max.Z * M); } } else if (y0 >= py - 1) { double g = y0 - P.y1; if (g < bgB && g > -50) { bgB = g; btop = Math.Max(btop, bb.Max.Z * M); } } }
            gapsA.Add(bgA); gapsB.Add(bgB); dzTop.Add(P.z1 - btop);
            rows.Add(d.Id.Value + " " + d.Name + " dims x" + Math.Round(w, 1) + " y" + Math.Round(th, 1) + " z" + Math.Round(h, 1) + " | centre dx " + Math.Round(cx - px, 1) + " dy " + Math.Round(cy - py, 1) + " | z0-postTop " + Math.Round(P.z0 - ptop, 2) + " | z1-beamTop " + Math.Round(P.z1 - btop, 2) + " | gap to beam end -Y " + Math.Round(bgA, 2) + " +Y " + Math.Round(bgB, 2));
            foreach (var kv in others) { var Q2 = kv.Value; double bg = BoxG(P, Q2); if (bg > 60) continue; double iv = 0; try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(P.so, Q2.so, BooleanOperationsType.Intersect); iv = r == null ? 0 : r.Volume * M * M * M; } catch { } if (iv > 1) nInt++; double dd = iv > 1 ? 0 : MinDist(P.so, Q2.so) * M; string kk = kv.Key.Name.StartsWith("Пр1") ? "purlin plate" : kv.Key.Name.StartsWith("Узел ГС1") ? "ГС1 gusset" : kv.Key.Name.StartsWith("Узел 9") ? "КН node" : kv.Key.Name.Split(new[] { (char)32 })[0] + " " + (kv.Key.Name.Split(new[] { (char)32 }).Length > 1 ? kv.Key.Name.Split(new[] { (char)32 })[1] : ""); if (!kinds.ContainsKey(kk) || dd < kinds[kk]) kinds[kk] = dd; if (dd < minNb) { minNb = dd; minNbName = kv.Key.Name + " id " + kv.Key.Id.Value; } }
        }
    }
    sb.AppendLine("(1) plates " + n + "; width x " + Math.Round(minW, 1) + ".." + Math.Round(maxW, 1) + ", thickness y " + Math.Round(minT, 1) + ".." + Math.Round(maxT, 1) + ", height z " + Math.Round(hs.Min(), 1) + ".." + Math.Round(hs.Max(), 1));
    sb.AppendLine("    centre offset from the post axis: dx " + Math.Round(dxc.Min(), 2) + ".." + Math.Round(dxc.Max(), 2) + ", dy " + Math.Round(dyc.Min(), 2) + ".." + Math.Round(dyc.Max(), 2) + "; bottom minus post top " + Math.Round(dzBot.Min(), 2) + ".." + Math.Round(dzBot.Max(), 2) + "; top minus beam top " + Math.Round(dzTop.Min(), 2) + ".." + Math.Round(dzTop.Max(), 2));
    sb.AppendLine("    gap plate face -> beam end face: -Y beam " + Math.Round(gapsA.Min(), 2) + ".." + Math.Round(gapsA.Max(), 2) + ", +Y beam " + Math.Round(gapsB.Min(), 2) + ".." + Math.Round(gapsB.Max(), 2));
    sb.AppendLine("    plate top minus roof-top plane at its y: " + Math.Round(zt.Min(), 2) + ".." + Math.Round(zt.Max(), 2)); sb.AppendLine("    nearest neighbour distance by kind: " + string.Join("; ", kinds.Select(q => q.Key + " " + Math.Round(q.Value, 2)))); sb.AppendLine("(2) neighbour plates: intersecting " + nInt + ", nearest distance " + Math.Round(minNb, 2) + " mm (" + minNbName + ")");
    foreach (var s in rows.Take(12)) sb.AppendLine("  " + s);
    return sb.ToString();
}
static void _end() {