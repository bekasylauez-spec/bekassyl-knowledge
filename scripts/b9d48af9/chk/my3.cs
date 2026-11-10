var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\_my3.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; string r;
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt")); r = Run2(nd); }
  catch (Exception ex) { r = "ERR " + ex; }
  System.IO.File.WriteAllText(log, r, System.Text.Encoding.UTF8); };
uiapp.Idling += hnd;
return "queued";
}
const double M = 304.8;
static List<Solid> SolidsOf(Element el)
{
    var r = new List<Solid>();
    var ge = el.get_Geometry(new Options { DetailLevel = ViewDetailLevel.Fine }); if (ge == null) return r;
    foreach (var go in ge) { IEnumerable<GeometryObject> objs = go is GeometryInstance gi ? gi.GetInstanceGeometry().Cast<GeometryObject>() : new[] { go }; r.AddRange(objs.OfType<Solid>().Where(x => x.Volume > 1e-9)); }
    return r;
}
static string P3(XYZ p) { return Math.Round(p.X * M) + "," + Math.Round(p.Y * M) + "," + Math.Round(p.Z * M); }
static string F1(double v) { return Math.Round(v, 1).ToString(System.Globalization.CultureInfo.InvariantCulture); }
static List<XYZ> Pts(Solid s) { var l = new List<XYZ>(); foreach (Edge ed in s.Edges) { var c = ed.AsCurve(); l.Add(c.GetEndPoint(0)); l.Add(c.Evaluate(0.5, true)); l.Add(c.Evaluate(0.25, true)); l.Add(c.Evaluate(0.75, true)); } return l; }
static double OneWay(Solid a, Solid b) { double dm = 1e9; foreach (var p in Pts(a)) foreach (Face f in b.Faces) { var r = f.Project(p); if (r != null && r.Distance < dm) dm = r.Distance; } return dm * M; }
static double MinDist(Solid a, Solid b) { return Math.Min(OneWay(a, b), OneWay(b, a)); }
static double IntVol(Solid a, Solid b) { try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(a, b, BooleanOperationsType.Intersect); return r == null ? 0 : r.Volume * M * M * M; } catch { return -1; } }
static bool BB(BoundingBoxXYZ a, BoundingBoxXYZ b, double tol) { return !(a.Min.X - tol > b.Max.X || a.Max.X + tol < b.Min.X || a.Min.Y - tol > b.Max.Y || a.Max.Y + tol < b.Min.Y || a.Min.Z - tol > b.Max.Z || a.Max.Z + tol < b.Min.Z); }
static PlanarFace BigFace(Solid s, XYZ dirHint = null)
{ PlanarFace best = null; foreach (Face f in s.Faces) { var pf = f as PlanarFace; if (pf == null) continue; if (dirHint != null && Math.Abs(pf.FaceNormal.DotProduct(dirHint)) < 0.99) continue; if (best == null || pf.Area > best.Area) best = pf; } return best; }
static List<XYZ[]> Segs(PlanarFace pf) { var l = new List<XYZ[]>(); foreach (var cl in pf.GetEdgesAsCurveLoops()) foreach (Curve c in cl) { var t = c.Tessellate(); for (int i = 0; i < t.Count - 1; i++) l.Add(new[] { t[i], t[i + 1] }); } return l; }
static bool Inside(PlanarFace pf, XYZ q)
{
    double x = (q - pf.Origin).DotProduct(pf.XVector), y = (q - pf.Origin).DotProduct(pf.YVector); bool inside = false;
    foreach (var sg in Segs(pf)) { double xi = (sg[0] - pf.Origin).DotProduct(pf.XVector), yi = (sg[0] - pf.Origin).DotProduct(pf.YVector), xj = (sg[1] - pf.Origin).DotProduct(pf.XVector), yj = (sg[1] - pf.Origin).DotProduct(pf.YVector);
        if (((yi > y) != (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) inside = !inside; }
    return inside;
}
static double EdgeDist(PlanarFace pf, XYZ p)
{
    double dm = 1e9; foreach (var sg in Segs(pf)) { var a = sg[0]; var ab = sg[1] - a; double l2 = ab.DotProduct(ab); double t = l2 < 1e-12 ? 0 : Math.Max(0, Math.Min(1, (p - a).DotProduct(ab) / l2)); double d = (p - (a + ab * t)).GetLength(); if (d < dm) dm = d; }
    return dm * M;
}
class Bolt { public long id; public double r; public XYZ O, u; public double t0, t1; }
static List<Bolt> BoltsOf(DirectShape ds)
{
    var res = new List<Bolt>();
    foreach (var s in SolidsOf(ds))
        foreach (Face fc in s.Faces)
        {
            var cf = fc as CylindricalFace; if (cf == null) continue; double rr = cf.get_Radius(0).GetLength() * M;
            if (Math.Abs(rr - 8) > 0.3 && Math.Abs(rr - 12) > 0.3) continue;
            var u = cf.Axis.Normalize(); var O = cf.Origin; double t0 = 1e9, t1 = -1e9;
            foreach (Edge ed in s.Edges) { var c = ed.AsCurve(); foreach (int k in new[] { 0, 1 }) { double t = (c.GetEndPoint(k) - O).DotProduct(u); t0 = Math.Min(t0, t); t1 = Math.Max(t1, t); } }
            res.Add(new Bolt { id = ds.Id.Value, r = rr, O = O, u = u, t0 = t0, t1 = t1 }); break;
        }
    return res;
}
static double Thick(Solid s, XYZ n) { double a = 1e9, b = -1e9; foreach (Edge ed in s.Edges) { var c = ed.AsCurve(); foreach (int k in new[] { 0, 1 }) { double t = c.GetEndPoint(k).DotProduct(n); a = Math.Min(a, t); b = Math.Max(b, t); } } return (b - a) * M; }
static string F3(double v) { return Math.Round(v, 3).ToString(System.Globalization.CultureInfo.InvariantCulture); }
class PlateF { public long dsId; public string dsName; public PlanarFace pf; public double area; }
static string Run2(Document nd)
{
    var sb = new System.Text.StringBuilder();
    double[] bxs = { 6000, 48000, 108000, 150000 }; double[] rys = { 0, 24000, 36000, 60000 };
    var allEl = new FilteredElementCollector(nd).WhereElementIsNotElementType().Where(e => e.Category != null && (e is DirectShape || e is FamilyInstance) && e.get_BoundingBox(null) != null).ToList();
    var bbs = new Dictionary<long, BoundingBoxXYZ>(); foreach (var e in allEl) bbs[e.Id.Value] = e.get_BoundingBox(null);
    var cnt = new Dictionary<string, double[]>();
    double min16 = 1e9, min24 = 1e9; string w16 = "", w24 = ""; int n16 = 0, n24 = 0, f16 = 0, f24 = 0, noPlate = 0; int orphans = 0; int gClash = 0, gChecked = 0;
    var lowL = new List<string>();
    foreach (double bx in bxs) foreach (double ry in rys)
    {
        string tag = "zone x" + bx + " y" + ry;
        var zmin = new XYZ(bx - 350, ry - 700, -1500) / M; var zmax = new XYZ(bx + 6350, ry + 700, 15200) / M; var zb = new BoundingBoxXYZ { Min = zmin, Max = zmax };
        var inz = allEl.Where(e => BB(bbs[e.Id.Value], zb, 0)).ToList();
        var nodes = inz.OfType<DirectShape>().Where(d => d.Name.StartsWith("Узел") && d.Name.Contains("фасонка")).ToList();
        var members = inz.OfType<FamilyInstance>().ToList();
        // plate faces
        var plates = new List<PlateF>(); var plateSolids = new Dictionary<long, List<Solid>>();
        foreach (var nd0 in nodes) { var ss = SolidsOf(nd0); plateSolids[nd0.Id.Value] = ss; foreach (var so in ss) foreach (Face f in so.Faces) { var pf = f as PlanarFace; if (pf != null && pf.Area * M * M > 1500) plates.Add(new PlateF { dsId = nd0.Id.Value, dsName = nd0.Name, pf = pf, area = pf.Area * M * M }); } }
        var bolts = new List<Bolt>(); foreach (var d in inz.OfType<DirectShape>().Where(d => d.Name.StartsWith("Болт"))) bolts.AddRange(BoltsOf(d));
        int zf = 0;
        foreach (var bo in bolts)
        {
            bool is16 = bo.r < 10; double best = 1e9; int pc = 0; long bestDs = 0;
            foreach (var pl in plates)
            {
                double dn = bo.u.DotProduct(pl.pf.FaceNormal); if (Math.Abs(dn) < 0.99) continue;
                double tt = (pl.pf.Origin - bo.O).DotProduct(pl.pf.FaceNormal) / dn; if (tt < bo.t0 - 0.3 / M || tt > bo.t1 + 0.3 / M) continue;
                var pt = bo.O + bo.u * tt; if (!Inside(pl.pf, pt)) continue; pc++; double ed = EdgeDist(pl.pf, pt); if (ed < best) { best = ed; bestDs = pl.dsId; }
            }
            if (pc == 0) { noPlate++; zf++; lowL.Add("   bolt without plate M" + (is16 ? 16 : 24) + " ds#" + bo.id + " at " + P3(bo.O) + " " + tag); continue; }
            if (is16) { n16++; if (best < min16) { min16 = best; w16 = "node#" + bestDs + " " + P3(bo.O); } if (best < 24.99) { f16++; lowL.Add("   M16 edge " + F1(best) + " node#" + bestDs + " at " + P3(bo.O)); } }
            else { n24++; if (best < min24) { min24 = best; w24 = "node#" + bestDs + " " + P3(bo.O); } if (best < 35.99) { f24++; lowL.Add("   M24 edge " + F1(best) + " node#" + bestDs + " at " + P3(bo.O)); } }
        }
        // gusset vs members clash
        foreach (var nd0 in nodes)
        {
            var G = plateSolids[nd0.Id.Value].OrderByDescending(x => x.Volume).First(); var nb0 = bbs[nd0.Id.Value]; gChecked++;
            foreach (var m in members) { if (!BB(bbs[m.Id.Value], nb0, 0)) continue; foreach (var ms in SolidsOf(m)) { double v = IntVol(G, ms); if (v > 0.5) { gClash++; lowL.Add("   !! gusset " + nd0.Name + " #" + nd0.Id.Value + " ∩ " + m.Name + " #" + m.Id.Value + " vol " + F1(v)); } } }
        }
        // orphans (bbox neighbours)
        int zo = 0;
        foreach (var e in inz.OfType<DirectShape>())
        {
            var b = bbs[e.Id.Value]; bool nb = false;
            foreach (var o in inz) { if (o.Id == e.Id) continue; if (BB(bbs[o.Id.Value], b, 1.0 / M)) { nb = true; break; } }
            if (!nb) { orphans++; zo++; lowL.Add("   ORPHAN (no neighbour) " + e.Name + " #" + e.Id.Value + " " + P3(b.Min) + ".." + P3(b.Max)); }
        }
        // columns +5.020 signature in this zone
        foreach (double cx in new[] { bx, bx + 6000 })
        {
            foreach (double zlo in new[] { 4400.0, 9900.0 })
            {
                var sel = inz.OfType<DirectShape>().Where(d => { var b = bbs[d.Id.Value]; var c0 = (b.Min + b.Max) * 0.5 * M; return Math.Abs(c0.X - cx) < 330 && Math.Abs(c0.Y - ry) < 330 && c0.Z > zlo && c0.Z < zlo + 1300; }).ToList();
                string sig = string.Join(" ; ", sel.GroupBy(d => d.Name.Substring(0, Math.Min(34, d.Name.Length)) + "|" + d.Category.Name.Substring(0, 3)).OrderBy(g => g.Key).Select(g => g.Key + " x" + g.Count()));
                sb.AppendLine("COL x" + cx + " y" + ry + " z" + zlo + "..: " + sig);
            }
        }
        sb.AppendLine(tag + ": nodes(gusset) " + nodes.Count + ", bolts " + bolts.Count + ", bolts w/o plate " + zf + ", orphans " + zo);
    }
    sb.AppendLine("=== BOLT EDGE: M16 n " + n16 + " min " + F1(min16) + " @" + w16 + " fails(<25) " + f16 + " | M24 n " + n24 + " min " + F1(min24) + " @" + w24 + " fails(<36) " + f24 + " | bolts w/o plate " + noPlate + " | gussets checked " + gChecked + " clash-with-member " + gClash + " | orphans " + orphans);
    foreach (var l in lowL.Take(120)) sb.AppendLine(l);
    return sb.ToString();
}
static void _end() {
