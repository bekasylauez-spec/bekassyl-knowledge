// READ-ONLY. Insert strip analysis.
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\_dump.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; string r;
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt")); r = Run4(nd); }
  catch (Exception ex) { r = "ERR " + ex; }
  System.IO.File.WriteAllText(log, r, System.Text.Encoding.UTF8); };
uiapp.Idling += hnd;
return "queued";
}
const double M = 304.8;
class Bolt24 { public DirectShape ds; public XYZ O, u; public double tmin, tmax; }
static bool InsideF(PlanarFace pf, XYZ q)
{
    double x = (q - pf.Origin).DotProduct(pf.XVector), y = (q - pf.Origin).DotProduct(pf.YVector); bool inside = false;
    foreach (var cl in pf.GetEdgesAsCurveLoops())
    {
        var pts = new List<XYZ>(); foreach (Curve c in cl) { var t = c.Tessellate(); for (int i = 0; i < t.Count - 1; i++) pts.Add(t[i]); }
        for (int i = 0, j = pts.Count - 1; i < pts.Count; j = i++)
        {
            double xi = (pts[i] - pf.Origin).DotProduct(pf.XVector), yi = (pts[i] - pf.Origin).DotProduct(pf.YVector), xj = (pts[j] - pf.Origin).DotProduct(pf.XVector), yj = (pts[j] - pf.Origin).DotProduct(pf.YVector);
            if (((yi > y) != (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) inside = !inside;
        }
    }
    return inside;
}
static XYZ LastCP;
static double EdgeDist(PlanarFace pf, XYZ p)
{
    double dm = 1e9;
    foreach (var cl in pf.GetEdgesAsCurveLoops()) foreach (Curve c in cl)
    {
        var t = c.Tessellate();
        for (int i = 0; i < t.Count - 1; i++)
        {
            var a = t[i]; var b = t[i + 1]; var ab = b - a; double l2 = ab.DotProduct(ab); double s = l2 < 1e-12 ? 0 : Math.Max(0, Math.Min(1, (p - a).DotProduct(ab) / l2));
            var cp0 = a + ab * s; double dd0 = (p - cp0).GetLength(); if (dd0 < dm) { dm = dd0; LastCP = cp0; }
        }
    }
    return dm;
}
static List<Solid> SolidsOf(Element el)
{
    var r = new List<Solid>();
    var ge = el.get_Geometry(new Options { DetailLevel = ViewDetailLevel.Fine }); if (ge == null) return r;
    foreach (var go in ge) { IEnumerable<GeometryObject> objs = go is GeometryInstance gi ? gi.GetInstanceGeometry().Cast<GeometryObject>() : new[] { go }; r.AddRange(objs.OfType<Solid>().Where(x => x.Volume > 1e-9)); }
    return r;
}
static string P3(XYZ p) { return Math.Round(p.X * M) + "," + Math.Round(p.Y * M) + "," + Math.Round(p.Z * M); }
static bool BBhas(Solid s, XYZ mid, double tol)
{
    var bb = s.GetBoundingBox(); var pa = bb.Transform.OfPoint(bb.Min); var pb = bb.Transform.OfPoint(bb.Max);
    return !(Math.Min(pa.X, pb.X) - tol > mid.X || Math.Max(pa.X, pb.X) + tol < mid.X || Math.Min(pa.Y, pb.Y) - tol > mid.Y || Math.Max(pa.Y, pb.Y) + tol < mid.Y || Math.Min(pa.Z, pb.Z) - tol > mid.Z || Math.Max(pa.Z, pb.Z) + tol < mid.Z);
}
static string Run4(Document nd)
{
    var sb = new System.Text.StringBuilder();
    foreach (long id in new long[]{3564741, 3561041, 3561057})
    {
        var ds = nd.GetElement(new ElementId(id)) as DirectShape; if (ds == null) { sb.AppendLine("no " + id); continue; }
        sb.AppendLine("== DS#" + id + " " + ds.Name);
        int n = 0;
        foreach (var s in SolidsOf(ds))
        {
            n++; var bb = s.GetBoundingBox(); var a = bb.Transform.OfPoint(bb.Min); var b = bb.Transform.OfPoint(bb.Max);
            PlanarFace big = null; foreach (Face fc in s.Faces) { var pf = fc as PlanarFace; if (pf != null && (big == null || pf.Area > big.Area)) big = pf; }
            string nm = big == null ? "nobig" : "n(" + Math.Round(big.FaceNormal.X,2) + "," + Math.Round(big.FaceNormal.Y,2) + "," + Math.Round(big.FaceNormal.Z,2) + ") A" + Math.Round(big.Area*M*M) + " t" + Math.Round(s.Volume/big.Area*M,1) + " org " + P3(big.Origin);
            sb.AppendLine("  S" + n + " vol " + Math.Round(s.Volume*M*M*M) + " bb " + P3(a) + " .. " + P3(b) + " " + nm);
        }
    }
    return sb.ToString();
}
static void _end() {
