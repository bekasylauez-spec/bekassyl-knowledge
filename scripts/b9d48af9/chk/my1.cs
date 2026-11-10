var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\_my.txt";
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
static string Run2(Document nd)
{
    var sb = new System.Text.StringBuilder();
    double[] bxs = { 6000, 48000, 108000, 150000 }; double[] rys = { 0, 24000, 36000, 60000 };
    var fi = new FilteredElementCollector(nd).OfCategory(BuiltInCategory.OST_StructuralFraming).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().ToList();
    var sv = fi.Where(x => x.Name.StartsWith("СВ")).ToList(); var p1all = fi.Where(x => x.Name == "Р1").ToList();
    var dss = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().ToList();
    var dsBB = new Dictionary<long, BoundingBoxXYZ>(); foreach (var d in dss) { var b = d.get_BoundingBox(null); if (b != null) dsBB[d.Id.Value] = b; }
    Func<Element, XYZ[]> ends = m => { var c = ((LocationCurve)m.Location).Curve; return new[] { c.GetEndPoint(0) * M, c.GetEndPoint(1) * M }; };
    int nFail = 0; double minG16 = 1e9, minI16 = 1e9; string wG16 = "", wI16 = ""; int nB16 = 0, nB24 = 0; double minG24 = 1e9, minI24 = 1e9; string wG24 = "", wI24 = "";
    double minPair = 1e9; string wPair = ""; double maxProt = 0; string wProt = ""; double minProtOther = 0;
    foreach (double bx in bxs) foreach (double ry in rys)
    {
        double xc = bx + 3000; string tag = "bay x" + bx + " y" + ry;
        var mem = sv.Where(m => { var e = ends(m); return Math.Abs(e[0].Y - ry) < 100 && Math.Abs(e[1].Y - ry) < 100 && Math.Min(e[0].X, e[1].X) >= bx - 400 && Math.Max(e[0].X, e[1].X) <= bx + 6400; }).ToList();
        sb.AppendLine("== " + tag + ": СВ members " + mem.Count + " (" + string.Join(",", mem.GroupBy(m => m.Name).Select(g => g.Key + "x" + g.Count())) + ")");
        foreach (var m in mem.OrderBy(m => Math.Min(ends(m)[0].Z, ends(m)[1].Z)).ThenBy(m => ends(m)[0].X)) { var e = ends(m); sb.AppendLine("   " + m.Name + " #" + m.Id.Value + " axis " + P3(e[0] / M) + " -> " + P3(e[1] / M)); }
        // Р1 at +5.020 / +10.340 inside bay
        foreach (double zl in new[] { 5020.0, 10340.0 })
        {
            var pp = p1all.Where(m => { var e = ends(m); return Math.Abs(e[0].Z - zl) < 5 && Math.Abs(e[1].Z - zl) < 5 && Math.Abs(e[0].Y - ry) < 100 && Math.Max(e[0].X, e[1].X) > xc - 100 && Math.Min(e[0].X, e[1].X) < xc + 100; }).ToList();
            sb.AppendLine("   Р1 z" + zl + " pieces crossing mid-bay: " + pp.Count + " " + string.Join(" ", pp.Select(m => "#" + m.Id.Value + " " + F1(ends(m)[0].X) + ".." + F1(ends(m)[1].X))));
        }
        // apex nodes
        var apex = dss.Where(d => d.Name.StartsWith("Узел СВ") && dsBB.ContainsKey(d.Id.Value)).Where(d => { var b = dsBB[d.Id.Value]; var c = (b.Min + b.Max) * 0.5 * M; return Math.Abs(c.X - xc) < 250 && Math.Abs(c.Y - ry) < 150; }).ToList();
        sb.AppendLine("   apex nodes " + apex.Count + ": " + string.Join(" | ", apex.Select(d => "#" + d.Id.Value + " " + d.Name.Replace("фасонка ", "ф").Replace("вкладыши ", "в") + " z" + F1(dsBB[d.Id.Value].Min.Z * M) + ".." + F1(dsBB[d.Id.Value].Max.Z * M))));
        foreach (var node in apex.OrderBy(d => dsBB[d.Id.Value].Min.Z))
        {
            string mk = node.Name.Substring(5, 3); var nb = dsBB[node.Id.Value]; double nz0 = nb.Min.Z * M, nz1 = nb.Max.Z * M;
            var ns = SolidsOf(node); var G = ns.OrderByDescending(x => x.Volume).First();
            var gpf = BigFace(G); if (gpf == null) { sb.AppendLine("   !! no gusset face " + node.Id.Value); continue; }
            var n = gpf.FaceNormal; var gb = G.GetBoundingBox(); var gA = gb.Transform.OfPoint(gb.Min) * M; var gB = gb.Transform.OfPoint(gb.Max) * M;
            double gz0 = Math.Min(gA.Z, gB.Z), gz1 = Math.Max(gA.Z, gB.Z), gy0 = Math.Min(gA.Y, gB.Y), gy1 = Math.Max(gA.Y, gB.Y), gx0 = Math.Min(gA.X, gB.X), gx1 = Math.Max(gA.X, gB.X);
            bool below = nz1 > 0 && (gz1 > 4900 && gz1 < 5000 || gz1 > 10300 && gz1 < 10389) && node.Name.Contains("−10") && Math.Abs(gz1 - (nz1)) < 1;
            // contact z: top of gusset (bottom tier) or bottom (mid / top tiers)
            bool lowerTier = nz1 < 5000; double Zf = lowerTier ? gz1 : gz0;
            var P1 = p1all.Where(m => { var e = ends(m); return Math.Abs(e[0].Y - ry) < 100 && Math.Max(e[0].X, e[1].X) > xc && Math.Min(e[0].X, e[1].X) < xc && Math.Abs(e[0].Z - (Zf + (lowerTier ? 50 : -50))) < 3; }).FirstOrDefault();
            string head = "   NODE #" + node.Id.Value + " " + node.Name + " tier " + (lowerTier ? "lower(Λ, Р1 bottom face)" : (nz0 < 6000 ? "mid(V, Р1+5020 top face)" : "top(" + mk + ", Р1+10340 top face)"));
            sb.AppendLine(head);
            sb.AppendLine("      gusset vol " + F1(G.Volume * M * M * M) + " thick " + F1(Thick(G, n)) + " normal " + F1(n.X) + "," + F1(n.Y) + "," + F1(n.Z) + " bbox x" + F1(gx0) + ".." + F1(gx1) + " y" + F1(gy0) + ".." + F1(gy1) + " z" + F1(gz0) + ".." + F1(gz1) + " contact Z " + F1(Zf));
            if (P1 == null) { sb.AppendLine("      !! Р1 not found"); nFail++; continue; }
            var P1s = SolidsOf(P1); var pb = P1.get_BoundingBox(null);
            double faceZ = lowerTier ? pb.Min.Z * M : pb.Max.Z * M;
            double iv = 0; foreach (var ps in P1s) iv += Math.Max(0, IntVol(G, ps));
            sb.AppendLine("      Р1 #" + P1.Id.Value + " face z " + F1(faceZ) + " gap " + F1(Zf - faceZ) + " y" + F1(pb.Min.Y * M) + ".." + F1(pb.Max.Y * M) + " ; gusset∩Р1 volume " + F1(iv) + " mm3 ; gusset top-edge inside tube face: x " + (gx0 >= pb.Min.X * M && gx1 <= pb.Max.X * M) + ", y " + (gy0 >= pb.Min.Y * M + 5 && gy1 <= pb.Max.Y * M - 5));
            if (Math.Abs(Zf - faceZ) > 0.05 || iv > 0.5) nFail++;
            // contact edge length of gusset (vertices at Zf)
            double ca = 1e9, cb = -1e9; foreach (Edge ed in G.Edges) { var c = ed.AsCurve(); foreach (int k in new[] { 0, 1 }) { var q = c.GetEndPoint(k) * M; if (Math.Abs(q.Z - Zf) < 0.2) { ca = Math.Min(ca, q.X); cb = Math.Max(cb, q.X); } } }
            double Lg = cb - ca; double gyc = (gy0 + gy1) / 2;
            // related DS
            var rel = dss.Where(d => d.Id != node.Id && dsBB.ContainsKey(d.Id.Value) && BB(dsBB[d.Id.Value], nb, 3 / M) && (d.Name.Contains(mk))).ToList();
            double wm = 0, wp = 0; var capS = new List<Solid>(); var braceWeld = new List<Solid>();
            foreach (var d in rel)
            {
                if (d.Name.StartsWith("шов")) foreach (var ws in SolidsOf(d))
                    {
                        var wbb = ws.GetBoundingBox(); var w0 = wbb.Transform.OfPoint(wbb.Min) * M; var w1 = wbb.Transform.OfPoint(wbb.Max) * M; double wz0 = Math.Min(w0.Z, w1.Z), wz1 = Math.Max(w0.Z, w1.Z), wx0 = Math.Min(w0.X, w1.X), wx1 = Math.Max(w0.X, w1.X), wy0 = Math.Min(w0.Y, w1.Y), wy1 = Math.Max(w0.Y, w1.Y);
                        bool onFace = (lowerTier ? Math.Abs(wz1 - Zf) < 0.6 : Math.Abs(wz0 - Zf) < 0.6) && wz1 - wz0 < 8 && wx1 - wx0 > 100 && wx0 >= ca - 5 && wx1 <= cb + 5;
                        if (onFace) { if ((wy0 + wy1) / 2 < gyc) wm += wx1 - wx0; else wp += wx1 - wx0; double iw = 0; foreach (var ps in P1s) iw += Math.Max(0, IntVol(ws, ps)); if (iw > 0.5) { sb.AppendLine("      !! face weld intersects Р1 " + F1(iw)); nFail++; } }
                        else braceWeld.Add(ws);
                    }
                else if (d.Name.StartsWith("ПЛ3")) capS.AddRange(SolidsOf(d));
            }
            sb.AppendLine("      welds on Р1 face: side y<" + F1(gyc) + " " + F1(wm) + " mm, side y>" + F1(gyc) + " " + F1(wp) + " mm, gusset contact edge " + F1(Lg) + " (x" + F1(ca) + ".." + F1(cb) + ")");
            if (wm < Lg * 0.9 || wp < Lg * 0.9) { nFail++; sb.AppendLine("      !! weld not both sides along full length"); }
            // pair clearance
            var br = mem.Where(m => { var e = ends(m); var ap = Math.Abs(e[0].X - xc) < Math.Abs(e[1].X - xc) ? e[0] : e[1]; return Math.Abs(ap.X - xc) < 400 && (lowerTier ? Math.Max(e[0].Z, e[1].Z) < 5000 : (nz0 < 6000 ? (Math.Min(e[0].Z, e[1].Z) > 5000 && Math.Max(e[0].Z, e[1].Z) < 10400) : Math.Min(e[0].Z, e[1].Z) > 10400)) && m.Name == mk; }).ToList();
            sb.AppendLine("      braces of this node: " + br.Count + " " + string.Join(" ", br.Select(m => "#" + m.Id.Value)));
            if (br.Count == 2)
            {
                var Ls = new List<Solid>(); var Rs = new List<Solid>();
                foreach (var m in br) { var ms = SolidsOf(m); double cx = (m.get_BoundingBox(null).Min.X + m.get_BoundingBox(null).Max.X) / 2 * M; (cx < xc ? Ls : Rs).AddRange(ms); }
                Func<Solid, double> cxf = s => { var b2 = s.GetBoundingBox(); return (b2.Transform.OfPoint(b2.Min).X + b2.Transform.OfPoint(b2.Max).X) / 2 * M; };
                foreach (var c in capS) (cxf(c) < xc ? Ls : Rs).Add(c);
                foreach (var c in braceWeld) (cxf(c) < xc ? Ls : Rs).Add(c);
                foreach (var c in ns) { if (c == G) continue; (cxf(c) < xc ? Ls : Rs).Add(c); }
                double dmin = 1e9; foreach (var a in Ls) foreach (var b in Rs) { var ba = a.GetBoundingBox(); var bb2 = b.GetBoundingBox(); double d0 = MinDist(a, b); if (d0 < dmin) dmin = d0; }
                double ivp = 0; foreach (var a in Ls.Take(3)) foreach (var b in Rs.Take(3)) ivp += Math.Max(0, IntVol(a, b));
                sb.AppendLine("      L/R pair: solids " + Ls.Count + "/" + Rs.Count + " min distance between left and right sets " + F1(dmin) + " mm ; brace∩brace vol " + F1(ivp));
                if (dmin < minPair) { minPair = dmin; wPair = tag + " " + P3(new XYZ(xc, ry, Zf) / M); }
                if (dmin < 1) nFail++;
            }
            // bolts and inserts
            var flats = new List<Solid>(); var gplane = gpf.Origin;
            foreach (var c in ns) { if (c == G) continue; var cpf = BigFace(c, n); if (cpf == null) continue; double th = Thick(c, n); if (th < 6 && th > 12) continue; if (th <= 12 && cpf.Area * M * M > 2000) flats.Add(c); }
            // insert protrusion beyond gusset outline
            foreach (var fsol in flats)
            {
                var fpf = BigFace(fsol, n); double mp = 0; XYZ wp0 = null;
                foreach (var sg in Segs(fpf)) for (int k = 0; k <= 4; k++)
                    { var q = sg[0] + (sg[1] - sg[0]) * (k / 4.0); double dist = (q - gplane).DotProduct(n); var qq = q - n * dist; double pr = Inside(gpf, qq) ? 0 : EdgeDist(gpf, qq); if (pr > mp) { mp = pr; wp0 = qq; } }
                sb.AppendLine("      insert plate vol " + F1(fsol.Volume * M * M * M) + " thick " + F1(Thick(fsol, n)) + " max protrusion beyond gusset outline " + F1(mp) + (wp0 != null ? " at " + P3(wp0) : ""));
                if (mp > maxProt) { maxProt = mp; wProt = tag + " " + P3(wp0 == null ? XYZ.Zero : wp0); }
            }
            var bolts = new List<Bolt>(); foreach (var d in rel.Where(d => d.Name.StartsWith("Болт"))) bolts.AddRange(BoltsOf(d));
            sb.AppendLine("      bolts " + bolts.Count + " (r " + string.Join("/", bolts.Select(b => F1(b.r)).Distinct()) + ")");
            foreach (var bo in bolts)
            {
                if (Math.Abs(bo.u.DotProduct(n)) < 0.99) { sb.AppendLine("      !! bolt not ⟂ plate"); nFail++; continue; }
                double tt = (gplane - bo.O).DotProduct(n) / bo.u.DotProduct(n); var pt = bo.O + bo.u * tt;
                bool ins = Inside(gpf, pt); double eg = EdgeDist(gpf, pt); double ei = 1e9; bool insIns = false;
                foreach (var fsol in flats) { var fpf = BigFace(fsol, n); var q2 = pt - n * ((pt - fpf.Origin).DotProduct(n)); if (Inside(fpf, q2)) { insIns = true; ei = Math.Min(ei, EdgeDist(fpf, q2)); } }
                bool is16 = bo.r < 10; if (is16) nB16++; else nB24++;
                double egv = ins ? eg : -eg;
                if (is16) { if (egv < minG16) { minG16 = egv; wG16 = tag + " " + P3(pt); } if (insIns && ei < minI16) { minI16 = ei; wI16 = tag + " " + P3(pt); } }
                sb.AppendLine("        bolt M" + (is16 ? 16 : 24) + " at " + P3(pt) + " edge-to-gusset " + F1(egv) + " edge-to-insert " + (insIns ? F1(ei) : "NO INSERT"));
                if ((is16 && (egv < 25 || !insIns || ei < 25))) nFail++;
            }
        }
    }
    sb.AppendLine("=== SUMMARY (mid-bay nodes) M16 bolts " + nB16 + " min gusset-edge " + F1(minG16) + " @" + wG16 + " ; min insert-edge " + F1(minI16) + " @" + wI16 + " ; min L-R clearance " + F1(minPair) + " @" + wPair + " ; max insert protrusion " + F1(maxProt) + " @" + wProt + " ; failing items " + nFail);
    return sb.ToString();
}
static void _end() {
