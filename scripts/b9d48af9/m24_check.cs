// READ-ONLY. M24 bolt edge / rib / insert-vs-gusset / intrusion check.
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\_m24.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; string r;
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt")); r = Run2(nd); }
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
static string Run2(Document nd)
{
    var sb = new System.Text.StringBuilder();
    var DSs = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел").ToList();
    var bolts = new List<Bolt24>(); int nM16 = 0;
    foreach (var ds in DSs.Where(x => x.Category != null && x.Category.Id.Value == (long)BuiltInCategory.OST_StructConnectionBolts))
        foreach (var s in SolidsOf(ds))
        {
            foreach (Face fc in s.Faces)
            {
                var cf = fc as CylindricalFace; if (cf == null) continue; double rr = cf.get_Radius(0).GetLength() * M;
                if (Math.Abs(rr - 8) < 0.3) { nM16++; break; }
                if (Math.Abs(rr - 12) > 0.3) continue;
                var u = cf.Axis.Normalize(); var O = cf.Origin; double t0 = 1e9, t1 = -1e9;
                foreach (Edge ed in s.Edges) { var c = ed.AsCurve(); foreach (int k in new[] { 0, 1 }) { double t = (c.GetEndPoint(k) - O).DotProduct(u); t0 = Math.Min(t0, t); t1 = Math.Max(t1, t); } }
                bolts.Add(new Bolt24 { ds = ds, O = O, u = u, tmin = t0, tmax = t1 }); break;
            }
        }
    sb.AppendLine("M24 bolts " + bolts.Count + ", M16 " + nM16);
    double minGE = 1e9, minIE = 1e9, minRib = 1e9; string wGE = "", wIE = "", wRib = "";
    var fails = new List<string>(); var nodeSet = new Dictionary<long, DirectShape>();
    var lines = new List<string>();
    foreach (var b in bolts)
    {
        var mid = b.O + b.u * ((b.tmin + b.tmax) / 2);
        var ol = new Outline(mid - new XYZ(120, 120, 120) / M, mid + new XYZ(120, 120, 120) / M);
        var near = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).WherePasses(new BoundingBoxIntersectsFilter(ol)).Cast<DirectShape>()
            .Where(x => x.ApplicationId == "БК_узел" && x.Name.Contains("вкладыши")).ToList();
        var recs = new List<string>(); double gE = 1e9, iE = 1e9, rib = 1e9; bool anyG = false, anyI = false; string ribId = ""; XYZ gCP = null, iCP = null;
        foreach (var ds in near)
        {
            foreach (var s in SolidsOf(ds))
            {
                if (!BBhas(s, mid, 0.4)) continue;
                double bestA = 0, bestD = 0; double tA = 1e9, tB = -1e9; int cnt = 0; XYZ bestCP = null;
                foreach (Face fc in s.Faces)
                {
                    var pf = fc as PlanarFace; if (pf == null) continue; var nf = pf.FaceNormal;
                    if (Math.Abs(nf.DotProduct(b.u)) < 0.999) continue;
                    double t0 = (pf.Origin - b.O).DotProduct(nf) / b.u.DotProduct(nf); if (t0 < b.tmin - 2 / M || t0 > b.tmax + 2 / M) continue;
                    var q = b.O + b.u * t0; bool ins = InsideF(pf, q); double d = EdgeDist(pf, q) * M; var cpL = LastCP; if (!ins) d = -d;
                    double area = pf.Area * M * M; tA = Math.Min(tA, t0); tB = Math.Max(tB, t0); cnt++;
                    if (area > bestA) { bestA = area; bestD = d; bestCP = cpL; }
                }
                if (cnt >= 2 && bestA > 8000)
                {
                    double th = (tB - tA) * M; bool pierced = bestD > 0; recs.Add("#" + ds.Id.Value + " t" + Math.Round(th, 1) + " A" + Math.Round(bestA) + " edge " + Math.Round(bestD, 1).ToString(System.Globalization.CultureInfo.InvariantCulture) + (pierced ? "" : " (NOT under bolt)") + " nearest-edge-pt " + (bestCP == null ? "?" : P3(bestCP)));
                    if (!pierced) continue;
                    if (th > 9) { if (bestD < gE) { gE = bestD; gCP = bestCP; } anyG = true; } else if (th > 5) { if (bestD < iE) { iE = bestD; iCP = bestCP; } anyI = true; }
                    nodeSet[ds.Id.Value] = ds;
                }
            }
        }
        foreach (var ds in near)
            foreach (var s in SolidsOf(ds))
            {
                PlanarFace bigF = null; foreach (Face fc in s.Faces) { var pf = fc as PlanarFace; if (pf != null && (bigF == null || pf.Area > bigF.Area)) bigF = pf; }
                if (bigF == null || Math.Abs(bigF.FaceNormal.DotProduct(b.u)) > 0.02) continue;
                foreach (Face fc in s.Faces)
                {
                    var pf = fc as PlanarFace; if (pf == null || Math.Abs(pf.FaceNormal.DotProduct(b.u)) > 0.02 || pf.Area * M * M < 300) continue;
                    for (double t = b.tmin; t <= b.tmax + 1e-9; t += 4 / M)
                    {
                        var p = b.O + b.u * t; var nf = pf.FaceNormal; double dpl = Math.Abs((p - pf.Origin).DotProduct(nf)); var q = p - nf * (p - pf.Origin).DotProduct(nf);
                        double d = InsideF(pf, q) ? dpl : EdgeDist(pf, p); d *= M; if (d < rib) { rib = d; ribId = "#" + ds.Id.Value; }
                    }
                }
            }
        if (anyG && gE < minGE) { minGE = gE; wGE = "bolt#" + b.ds.Id.Value + " @" + P3(mid); }
        if (anyI && iE < minIE) { minIE = iE; wIE = "bolt#" + b.ds.Id.Value + " @" + P3(mid); }
        if (rib < minRib) { minRib = rib; wRib = "bolt#" + b.ds.Id.Value + " @" + P3(mid) + " rib " + ribId; }
        string ln = (gCP == null ? "" : "gCP " + P3(gCP) + " ") + (iCP == null ? "" : "iCP " + P3(iCP) + " ") + "bolt#" + b.ds.Id.Value + " @" + P3(mid) + " axis " + Math.Round(b.u.X, 2) + "," + Math.Round(b.u.Y, 2) + "," + Math.Round(b.u.Z, 2) + " gusset-edge " + (anyG ? Math.Round(gE, 1).ToString() : "none") + " insert-edge " + (anyI ? Math.Round(iE, 1).ToString() : "none") + " rib " + Math.Round(rib, 1) + " | " + string.Join("; ", recs);
        lines.Add(ln);
        if (!anyG || !anyI || gE < 36 || iE < 36 || rib < 24) fails.Add(ln);
        if (nodeSet.Count > 0 && !(anyG && anyI)) { }
    }
    sb.AppendLine("MIN gusset-edge " + Math.Round(minGE, 1) + " (" + wGE + ")  MIN insert-edge " + Math.Round(minIE, 1) + " (" + wIE + ")  MIN rib " + Math.Round(minRib, 1) + " (" + wRib + ")");
    sb.AppendLine("FAIL bolts (edge<36 / rib<24 / missing plate): " + fails.Count);
    foreach (var f in fails.Where(x => x.Contains("gusset-edge") && !x.Contains("gusset-edge none") ).Take(60)) sb.AppendLine("  " + f);
    sb.AppendLine("== node DS with M24: " + nodeSet.Count);
    int nProt = 0, nIntr = 0, nSplit = 0; double maxProt = 0;
    foreach (var kv in nodeSet)
    {
        var ds = kv.Value; var sol = SolidsOf(ds); Solid G = null; double gv = 0;
        foreach (var s in sol) { if (s.Volume > gv) { bool plate = false; foreach (Face fc in s.Faces) { var pf = fc as PlanarFace; if (pf != null && pf.Area * M * M > 5000) plate = true; } if (plate) { G = s; gv = s.Volume; } } }
        if (G == null) { sb.AppendLine("DS#" + ds.Id.Value + " no gusset solid"); continue; }
        PlanarFace gf = null; foreach (Face fc in G.Faces) { var pf = fc as PlanarFace; if (pf != null && (gf == null || pf.Area > gf.Area)) gf = pf; }
        var ng = gf.FaceNormal; int nBig = 0; foreach (Face fc in G.Faces) { var pf = fc as PlanarFace; if (pf != null && Math.Abs(pf.FaceNormal.DotProduct(ng)) > 0.999 && pf.Area * M * M > 1500) nBig++; }
        var gbb = G.GetBoundingBox(); var a0 = gbb.Transform.OfPoint(gbb.Min); var a1 = gbb.Transform.OfPoint(gbb.Max); var gc = (a0 + a1) / 2;
        string head = "DS#" + ds.Id.Value + " " + ds.Name + " G vol " + Math.Round(gv * M * M * M) + " big faces " + nBig + " @" + P3(gc);
        if (nBig != 2) { nSplit++; head += "  <<< BIG FACES " + nBig + " (expect 2: one connected plate)"; }
        sb.AppendLine(head);
        Solid prism = null;
        try { var loops = gf.GetEdgesAsCurveLoops(); var moved = loops.Select(l => CurveLoop.CreateViaTransform(l, Transform.CreateTranslation(ng * (-40 / M)))).ToList(); prism = GeometryCreationUtilities.CreateExtrusionGeometry(moved, ng, 80 / M); } catch (Exception ex) { sb.AppendLine("   prism fail " + ex.Message); }
        foreach (var s in sol)
        {
            if (s == G) continue; PlanarFace big = null; foreach (Face fc in s.Faces) { var pf = fc as PlanarFace; if (pf != null && Math.Abs(pf.FaceNormal.DotProduct(ng)) > 0.999 && pf.Area * M * M > 800 && (big == null || pf.Area > big.Area)) big = pf; }
            if (big == null || prism == null) continue;
            double iv = s.Volume * M * M * M, outV = iv; Solid dif = null;
            try { dif = BooleanOperationsUtils.ExecuteBooleanOperation(s, prism, BooleanOperationsType.Difference); outV = dif == null ? 0 : dif.Volume * M * M * M; } catch { }
            if (outV > 1)
            {
                double mx = 0; XYZ at = null; if (dif != null) foreach (Edge ed in dif.Edges) foreach (int k in new[] { 0, 1 }) { var p = ed.AsCurve().GetEndPoint(k); var pp = p - ng * (p - gf.Origin).DotProduct(ng); double d = InsideF(gf, pp) ? 0 : EdgeDist(gf, pp) * M; if (d > mx) { mx = d; at = p; } }
                var ib = s.GetBoundingBox(); var ic = ib.Transform.OfPoint((ib.Min + ib.Max) / 2);
                sb.AppendLine("   insert-like solid vol " + Math.Round(iv) + " outside gusset outline " + Math.Round(outV) + " mm3 (" + Math.Round(100 * outV / iv) + "%), max protrusion " + Math.Round(mx, 1) + " mm at " + (at == null ? "?" : P3(at)) + " (solid centre " + P3(ic) + ")");
                nProt++; maxProt = Math.Max(maxProt, mx);
            }
        }
        try
        {
            var ol2 = new Outline(new XYZ(Math.Min(a0.X, a1.X), Math.Min(a0.Y, a1.Y), Math.Min(a0.Z, a1.Z)), new XYZ(Math.Max(a0.X, a1.X), Math.Max(a0.Y, a1.Y), Math.Max(a0.Z, a1.Z)));
            var nbs = new FilteredElementCollector(nd).WherePasses(new BoundingBoxIntersectsFilter(ol2)).ToList();
            foreach (var el in nbs)
            {
                bool fam = el is FamilyInstance fi && fi.Symbol.Family.Name.StartsWith("(КМ)"); bool dsn = el is DirectShape d2 && d2.ApplicationId == "БК_узел";
                if (!fam && !dsn) continue; if (dsn) { var cat = el.Category.Id.Value; if (cat == (long)BuiltInCategory.OST_StructConnectionBolts || cat == (long)BuiltInCategory.OST_StructConnectionWelds) continue; }
                foreach (var s in SolidsOf(el))
                {
                    if (s == G) continue;
                    double v = 0; try { var x = BooleanOperationsUtils.ExecuteBooleanOperation(G, s, BooleanOperationsType.Intersect); if (x != null) v = x.Volume * M * M * M; } catch { }
                    if (v > 0.05) { nIntr++; var sb2 = s.GetBoundingBox(); var c2 = sb2.Transform.OfPoint((sb2.Min + sb2.Max) / 2); sb.AppendLine("   INTRUSION gusset ∩ #" + el.Id.Value + " " + (el is FamilyInstance fi2 ? fi2.Symbol.Family.Name + " " + (el.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "") : ((DirectShape)el).Name) + " vol " + Math.Round(v, 2) + " mm3 @" + P3(c2) + (el.Id == ds.Id ? " (own DS)" : "")); }
                }
            }
        }
        catch (Exception ex) { sb.AppendLine("   intr fail " + ex.Message); }
    }
    sb.AppendLine("SUMMARY: nodes " + nodeSet.Count + ", inserts with part outside gusset outline " + nProt + " (max protrusion " + Math.Round(maxProt, 1) + " mm), intrusions " + nIntr + ", gusset not single plate " + nSplit);
    sb.AppendLine("== all bolts");
    foreach (var l in lines) sb.AppendLine(l);
    return sb.ToString();
}
static void _end() {