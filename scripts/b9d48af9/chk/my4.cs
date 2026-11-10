var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\_my4.txt";
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
static double PtDist(Element e, XYZ p)
{ double dm = 1e9; foreach (var s in SolidsOf(e)) foreach (Face f in s.Faces) { var r = f.Project(p); if (r != null && r.Distance < dm) dm = r.Distance; } return dm * M; }
static string Run2(Document nd)
{
    var sb = new System.Text.StringBuilder();
    double[] bxs = { 6000, 48000, 108000, 150000 }; double[] rys = { 0, 24000, 36000, 60000 };
    var allEl = new FilteredElementCollector(nd).WhereElementIsNotElementType().Where(e => e.Category != null && (e is DirectShape || e is FamilyInstance) && e.get_BoundingBox(null) != null).ToList();
    var bbs = new Dictionary<long, BoundingBoxXYZ>(); foreach (var e in allEl) bbs[e.Id.Value] = e.get_BoundingBox(null);
    sb.AppendLine("elements (members+DS) " + allEl.Count);
    // (a) old X crossing points
    int hits = 0;
    foreach (double bx in bxs) foreach (double ry in rys) foreach (double zc in new[] { 2360.0, 7680.0, 12415.0, 5020.0 - 0, 10340.0 })
    {
        var p = new XYZ(bx + 3000, ry, zc) / M; var ol = new BoundingBoxXYZ { Min = p - new XYZ(350, 350, 350) / M, Max = p + new XYZ(350, 350, 350) / M };
        foreach (var e in allEl) { if (!BB(bbs[e.Id.Value], ol, 0)) continue; double d = PtDist(e, p); if (d < 350) { if ((zc == 5020.0 || zc == 10340.0)) continue; hits++; sb.AppendLine("   crossing leftover? x" + (bx + 3000) + " y" + ry + " z" + zc + ": " + e.Name + " #" + e.Id.Value + " dist " + F1(d)); } }
    }
    sb.AppendLine("(a) elements within 350 mm of old X crossing points (tier mid 2360 / 7680 / 12415): " + hits);
    // (b) bolts without plate by name
    // (c) base and top-band signature per braced column
    var sigs = new Dictionary<string, int>();
    foreach (double bx in bxs) foreach (double ry in rys) foreach (double cx in new[] { bx, bx + 6000 })
        foreach (var zr in new[] { new[] { -1500.0, 700.0 }, new[] { 14000.0, 15200.0 } })
        {
            var sel = allEl.OfType<DirectShape>().Where(d => { var b = bbs[d.Id.Value]; var c0 = (b.Min + b.Max) * 0.5 * M; return Math.Abs(c0.X - cx) < 330 && Math.Abs(c0.Y - ry) < 330 && c0.Z > zr[0] && c0.Z < zr[1]; });
            string sig = (zr[0] < 0 ? "BASE " : "TOP  ") + string.Join(" ; ", sel.GroupBy(d => System.Text.RegularExpressions.Regex.Replace(d.Name, @"\d{4,6} [A-Z]", "#")).OrderBy(g => g.Key).Select(g => g.Key + " x" + g.Count()));
            sigs.TryGetValue(sig, out int k); sigs[sig] = k + 1;
        }
    foreach (var kv in sigs.OrderByDescending(k => k.Value)) sb.AppendLine("(c) " + kv.Value + " columns: " + kv.Key);
    // (d) whole-model orphan DS (no member/DS bbox within 1 mm)
    int orph = 0; var list = allEl.ToList(); var arr = list.Select(e => bbs[e.Id.Value]).ToArray();
    // sort by min X sweep
    var idx = Enumerable.Range(0, list.Count).OrderBy(k => arr[k].Min.X).ToArray();
    for (int ii = 0; ii < idx.Length; ii++)
    {
        int a = idx[ii]; if (!(list[a] is DirectShape)) continue; bool nb = false;
        for (int jj = ii - 1; jj >= 0 && !nb; jj--) { int b = idx[jj]; if (arr[b].Min.X + 20000 / M < arr[a].Min.X - 2 / M && false) break; if (arr[b].Max.X + 1.0 / M >= arr[a].Min.X && BB(arr[a], arr[b], 1.0 / M)) nb = true; if (arr[b].Min.X < arr[a].Min.X - 60000 / M) break; }
        for (int jj = ii + 1; jj < idx.Length && !nb; jj++) { int b = idx[jj]; if (arr[b].Min.X > arr[a].Max.X + 1.0 / M) break; if (BB(arr[a], arr[b], 1.0 / M)) nb = true; }
        if (!nb) { orph++; if (orph < 40) sb.AppendLine("   ORPHAN " + list[a].Name + " #" + list[a].Id.Value + " " + P3(arr[a].Min) + ".." + P3(arr[a].Max)); }
    }
    sb.AppendLine("(d) whole-model DS with no neighbour element within 1 mm: " + orph);
    // (e) bolts without plate: tally of DS name roots in braced zones
    return sb.ToString();
}
static void _end() {
