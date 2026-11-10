// READ-ONLY. Insert strip analysis.
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\_strip.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; string r;
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt")); r = Run3(nd); }
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
static string Run3(Document nd)
{
    var sb = new System.Text.StringBuilder();
    var DSs = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел" && x.Name.Contains("вкладыши")).ToList();
    sb.AppendLine("nodes with inserts " + DSs.Count);
    var stat = new Dictionary<string,int>(); int nIns=0, nOut=0, bad=0, skipped=0;
    foreach (var ds in DSs)
    {
        var sol = SolidsOf(ds); var Gs = new List<Solid>(); var gfs = new List<PlanarFace>();
        double tg = 10; { var mm = System.Text.RegularExpressions.Regex.Match(ds.Name, "фасонка −(\\d+)"); if (mm.Success) tg = double.Parse(mm.Groups[1].Value); }
        foreach (var s in sol) { PlanarFace gb = null; foreach (Face fc in s.Faces) { var pf = fc as PlanarFace; if (pf != null && pf.Area * M * M > 5000 && (gb == null || pf.Area > gb.Area)) gb = pf; } if (gb != null && Math.Abs(s.Volume / gb.Area - tg / M) * M < 0.7) { Gs.Add(s); gfs.Add(gb); } }
        if (Gs.Count == 0) continue;
        foreach (var s in sol)
        {
            if (Gs.Contains(s)) continue;
            PlanarFace gf = gfs[0]; var ng = gf.FaceNormal; double bestMx = 1e18;
            for (int gi = 0; gi < Gs.Count; gi++) { var g2 = gfs[gi]; double mx2 = 0; foreach (Edge ed in s.Edges) foreach (int k in new[]{0,1}) { var p = ed.AsCurve().GetEndPoint(k); var pp = p - g2.FaceNormal * (p - g2.Origin).DotProduct(g2.FaceNormal); double dpl2 = Math.Abs((p-g2.Origin).DotProduct(g2.FaceNormal))*M; double d = (InsideF(g2, pp) ? 0 : EdgeDist(g2, pp) * M) + dpl2*0.001; if (d > mx2) mx2 = d; } if (mx2 < bestMx) { bestMx = mx2; gf = g2; } }
            ng = gf.FaceNormal; PlanarFace big = null; foreach (Face fc in s.Faces) { var pf = fc as PlanarFace; if (pf != null && Math.Abs(pf.FaceNormal.DotProduct(ng)) > 0.999 && pf.Area * M * M > 800 && (big == null || pf.Area > big.Area)) big = pf; }
            if (big == null) continue;
            var bb0 = s.GetBoundingBox(); var cen = bb0.Transform.OfPoint((bb0.Min + bb0.Max) / 2);
            // plane distance: use the nearest face plane of s
            double dpl = 1e9; foreach (Face fc in s.Faces) { var pf = fc as PlanarFace; if (pf != null && Math.Abs(pf.FaceNormal.DotProduct(ng)) > 0.999) dpl = Math.Min(dpl, Math.Abs((pf.Origin - gf.Origin).DotProduct(ng)) * M); }
            if (dpl > 40) { skipped++; continue; }
            nIns++;
            XYZ e = null; double bl = 0; foreach (CurveLoop cl in big.GetEdgesAsCurveLoops()) foreach (Curve c in cl) { double l = c.Length; if (l > bl) { bl = l; e = (c.GetEndPoint(1) - c.GetEndPoint(0)).Normalize(); } }
            var pts = new List<XYZ>(); foreach (Edge ed in s.Edges) { var c = ed.AsCurve(); pts.Add(c.GetEndPoint(0)); pts.Add(c.GetEndPoint(1)); pts.Add(c.Evaluate(0.5, true)); }
            double s0=1e9,s1=-1e9; foreach (var p in pts) { double a=p.DotProduct(e); s0=Math.Min(s0,a); s1=Math.Max(s1,a); }
            double o0=1e9,o1=-1e9,mxd=0; XYZ at=null; int no=0;
            foreach (var p in pts) { var pp = p - ng * (p - gf.Origin).DotProduct(ng); if (InsideF(gf, pp)) continue; double d = EdgeDist(gf, pp) * M; if (d < 0.3) continue; no++; double a=p.DotProduct(e); o0=Math.Min(o0,a); o1=Math.Max(o1,a); if (d>mxd){mxd=d;at=p;} }
            if (no == 0) { stat["inside"] = (stat.ContainsKey("inside")?stat["inside"]:0)+1; continue; }
            nOut++;
            bool atLow = (o1 - s0) * M <= 14, atHigh = (s1 - o0) * M <= 14;
            string plate = "none";
            if (atLow ^ atHigh)
            {
                double eEnd = atLow ? s0 : s1;
                var pe = cen + e * (eEnd - cen.DotProduct(e));
                var ol = new Outline(pe - new XYZ(40,40,40)/M, pe + new XYZ(40,40,40)/M);
                foreach (var el in new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).WherePasses(new BoundingBoxIntersectsFilter(ol)).Cast<DirectShape>())
                    foreach (var s2 in SolidsOf(el)) foreach (Face fc in s2.Faces)
                    {
                        var pf = fc as PlanarFace; if (pf == null || Math.Abs(Math.Abs(pf.FaceNormal.DotProduct(e)) - 1) > 0.001) continue;
                        if (Math.Abs(pf.Origin.DotProduct(e) - eEnd) * M > 0.6) continue;
                        var q = pe - pf.FaceNormal * (pe - pf.Origin).DotProduct(pf.FaceNormal);
                        if (EdgeDist(pf, q)*M < 60) plate = el.Name;
                    }
            }
            string cls = (atLow ^ atHigh) ? "end-strip" : "NOT-AT-ONE-END";
            string key = cls + " maxd " + Math.Round(mxd,1) + " plate:" + (plate=="none"?"NO":"YES(ПЛ3 touches insert end)");
            stat[key] = (stat.ContainsKey(key)?stat[key]:0)+1;
            if (cls != "end-strip" || plate == "none") { bad++; if (bad<=40) sb.AppendLine("ANOM DS#"+ds.Id.Value+" "+ds.Name+" ins vol "+Math.Round(s.Volume*M*M*M)+" insL "+Math.Round((s1-s0)*M,1)+" outside-e-range from low end "+Math.Round((o0-s0)*M,1)+".."+Math.Round((o1-s0)*M,1)+" maxd "+Math.Round(mxd,1)+" plate "+plate+" @"+P3(at)); }
        }
    }
    sb.AppendLine("inserts-like (adjacent to gusset plane) " + nIns + ", skipped other-plane " + skipped + ", with part outside gusset outline " + nOut + ", anomalies " + bad);
    foreach (var kv in stat.OrderBy(k=>k.Key)) sb.AppendLine("  " + kv.Key + " : " + kv.Value);
    return sb.ToString();
}
static void _end() {


