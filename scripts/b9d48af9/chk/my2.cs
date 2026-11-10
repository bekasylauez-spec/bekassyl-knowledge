var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\_my2.txt";
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
static string Run2(Document nd)
{
    var sb = new System.Text.StringBuilder();
    var dss = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().ToList();
    foreach (long nid in new long[] { 3612462, 3613006 })
    {
        var node = nd.GetElement(new ElementId(nid)); var nb = node.get_BoundingBox(null); string mk = node.Name.Substring(5, 3);
        var ns = SolidsOf(node); var G = ns.OrderByDescending(x => x.Volume).First(); var gpf = BigFace(G); var n = gpf.FaceNormal;
        var rel = dss.Where(d => d.Id != node.Id && d.get_BoundingBox(null) != null && BB(d.get_BoundingBox(null), nb, 3 / M) && d.Name.Contains(mk)).ToList();
        var all = new List<KeyValuePair<string, Solid>>();
        foreach (var c in ns) if (c != G) all.Add(new KeyValuePair<string, Solid>("node-solid vol" + F1(c.Volume * M * M * M) + " ctr" + P3(c.ComputeCentroid()), c));
        foreach (var d in rel) { if (d.Name.StartsWith("Болт")) continue; foreach (var c in SolidsOf(d)) all.Add(new KeyValuePair<string, Solid>(d.Name.Substring(0, Math.Min(6, d.Name.Length)) + " vol" + F1(c.Volume * M * M * M) + " ctr" + P3(c.ComputeCentroid()), c)); }
        sb.AppendLine("NODE " + nid + " solids " + all.Count);
        var res = new List<Tuple<double, string, string>>();
        for (int i = 0; i < all.Count; i++) for (int j = i + 1; j < all.Count; j++)
            { double xi = all[i].Value.ComputeCentroid().X * M, xj = all[j].Value.ComputeCentroid().X * M; if ((xi - 9000) * (xj - 9000) >= 0) continue; double d0 = MinDist(all[i].Value, all[j].Value); res.Add(Tuple.Create(d0, all[i].Key, all[j].Key)); }
        foreach (var r in res.OrderBy(r => r.Item1).Take(6)) sb.AppendLine("   " + F3(r.Item1) + " mm : " + r.Item2 + "  <->  " + r.Item3);
        var flats = new List<Solid>(); foreach (var c in ns) { if (c == G) continue; var cpf = BigFace(c, n); if (cpf != null && Thick(c, n) <= 12 && cpf.Area * M * M > 2000) flats.Add(c); }
        var gplane = gpf.Origin;
        foreach (var d in rel.Where(d => d.Name.StartsWith("Болт"))) foreach (var bo in BoltsOf(d))
        {
            double tt = (gplane - bo.O).DotProduct(n) / bo.u.DotProduct(n); var pt = bo.O + bo.u * tt;
            foreach (var fsol in flats) { var fpf = BigFace(fsol, n); var q2 = pt - n * ((pt - fpf.Origin).DotProduct(n)); if (Inside(fpf, q2)) sb.AppendLine("   bolt " + P3(pt) + " insert-edge " + F3(EdgeDist(fpf, q2)) + " gusset-edge " + F3(EdgeDist(gpf, pt))); }
        }
    }
    return sb.ToString();
}
static void _end() {
