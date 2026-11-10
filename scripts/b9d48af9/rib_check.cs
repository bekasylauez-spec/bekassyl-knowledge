// READ-ONLY. T-insert rib check.
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\_rib.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; string r;
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt")); r = Run2(nd); }
  catch (Exception ex) { r = "ERR " + ex; }
  System.IO.File.WriteAllText(log, r, System.Text.Encoding.UTF8); };
uiapp.Idling += hnd;
return "queued";
}

const double M = 304.8;
class Pc { public Element El; public string Name; public int Kind; public Solid S; public double[] B; }
static List<Solid> SolidsOf(Element el)
{
    var r = new List<Solid>();
    var ge = el.get_Geometry(new Options { DetailLevel = ViewDetailLevel.Fine }); if (ge == null) return r;
    foreach (var go in ge) { IEnumerable<GeometryObject> objs = go is GeometryInstance gi ? gi.GetInstanceGeometry().Cast<GeometryObject>() : new[] { go }; r.AddRange(objs.OfType<Solid>().Where(x => x.Volume > 1e-9)); }
    return r;
}
static string P3(XYZ p) { return Math.Round(p.X * M) + "," + Math.Round(p.Y * M) + "," + Math.Round(p.Z * M); }
static void Ext(Solid s, XYZ ax, out double lo, out double hi)
{
    lo = 1e18; hi = -1e18;
    foreach (Edge e in s.Edges) { var c = e.AsCurve(); foreach (int k in new[] { 0, 1 }) { double t = c.GetEndPoint(k).DotProduct(ax) * M; if (t < lo) lo = t; if (t > hi) hi = t; } }
}
static void ExtF(Face f, XYZ ax, out double lo, out double hi)
{
    lo = 1e18; hi = -1e18;
    foreach (var cl in f.GetEdgesAsCurveLoops()) foreach (Curve c in cl) foreach (int k in new[] { 0, 1 }) { double t = c.GetEndPoint(k).DotProduct(ax) * M; if (t < lo) lo = t; if (t > hi) hi = t; }
}
static XYZ CentF(Face f)
{
    var pts = new List<XYZ>(); foreach (var cl in f.GetEdgesAsCurveLoops()) foreach (Curve c in cl) pts.Add(c.GetEndPoint(0));
    XYZ s = XYZ.Zero; foreach (var p in pts) s += p; return s / pts.Count;
}
static bool HasFace(Solid s, XYZ nrm, XYZ pt, double tolMm)
{
    foreach (Face fc in s.Faces) { var pf = fc as PlanarFace; if (pf == null) continue; if (Math.Abs(pf.FaceNormal.DotProduct(nrm)) < 0.9999) continue; if (Math.Abs((pf.Origin - pt).DotProduct(nrm)) * M < tolMm) return true; }
    return false;
}
static bool Ov(double[] a, double[] b, double tol) { return !(a[0] - tol > b[3] || b[0] - tol > a[3] || a[1] - tol > b[4] || b[1] - tol > a[4] || a[2] - tol > b[5] || b[2] - tol > a[5]); }
static string mkeyD(string mk, bool top) { return (mk.Length > 14 ? mk.Substring(0, 14) : mk) + (top ? "[lap]" : "[ax]"); }
static string Run2(Document nd)
{
    var sb = new System.Text.StringBuilder();
    var els = new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Symbol.Family.Name.StartsWith("(КМ)")).Cast<Element>()
        .Concat(new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел")).ToList();
    var pcs = new List<Pc>(); var byEl = new Dictionary<long, List<Pc>>();
    foreach (var el in els)
    {
        int kind; string nm;
        if (el is FamilyInstance fi) { kind = 0; nm = fi.Symbol.Family.Name + " " + (el.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? ""); }
        else { var ds = (DirectShape)el; long cat = el.Category.Id.Value; nm = ds.Name;
            if (cat == (long)BuiltInCategory.OST_StructConnectionBolts) kind = 3; else if (cat == (long)BuiltInCategory.OST_StructConnectionWelds) kind = 4;
            else if (nm.StartsWith("ПЛ3 заглушка")) kind = 2; else if (nm.StartsWith("Узел")) kind = 1; else kind = 5; }
        foreach (var s in SolidsOf(el))
        {
            var bb = s.GetBoundingBox(); var a = bb.Transform.OfPoint(bb.Min); var b = bb.Transform.OfPoint(bb.Max);
            var pc = new Pc { El = el, Name = nm, Kind = kind, S = s, B = new[] { Math.Min(a.X, b.X), Math.Min(a.Y, b.Y), Math.Min(a.Z, b.Z), Math.Max(a.X, b.X), Math.Max(a.Y, b.Y), Math.Max(a.Z, b.Z) } };
            pcs.Add(pc); if (!byEl.ContainsKey(el.Id.Value)) byEl[el.Id.Value] = new List<Pc>(); byEl[el.Id.Value].Add(pc);
        }
    }
    sb.AppendLine("solids " + pcs.Count + ", caps " + pcs.Count(p => p.Kind == 2) + ", node-plate solids " + pcs.Count(p => p.Kind == 1) + ", welds " + pcs.Count(p => p.Kind == 4) + ", bolt solids " + pcs.Count(p => p.Kind == 3));
    var planeCache = new Dictionary<long, XYZ[]>();
    Func<Element, XYZ[]> Plane = el =>
    {
        XYZ[] r; if (planeCache.TryGetValue(el.Id.Value, out r)) return r;
        double best = 0; XYZ ng = null, gc = null;
        foreach (var pc in byEl[el.Id.Value]) foreach (Face fc in pc.S.Faces) { var pf = fc as PlanarFace; if (pf != null && pf.Area > best) { best = pf.Area; ng = pf.FaceNormal; gc = pc.S.ComputeCentroid(); } }
        r = new[] { ng, gc }; planeCache[el.Id.Value] = r; return r;
    };
    int nCap = 0, noRib = 0, multiRib = 0, ribs = 0, notPerp = 0;
    int farBad = 0, hiBad = 0, wBadEnd = 0, wBadFlat = 0;
    double gMin = 1e9, gMax = -1e9, dMin = 1e9, dMax = -1e9;
    var hits = new Dictionary<string, int>(); var hitEx = new Dictionary<string, string>();
    var perDs = new Dictionary<long, List<string>>(); var perMk = new Dictionary<string, int[]>();
    var dbg = new List<string>(); var lines = new List<string>(); int topLap = 0, axisIns = 0;
    var capList = pcs.Where(p => p.Kind == 2).ToList(); var nodeList = pcs.Where(p => p.Kind == 1).ToList(); var weldList = pcs.Where(p => p.Kind == 4).ToList();
    foreach (var cap in capList)
    {
        nCap++; var K = cap.S;
        PlanarFace f1 = null; foreach (Face fc in K.Faces) { var pf = fc as PlanarFace; if (pf != null && (f1 == null || pf.Area > f1.Area)) f1 = pf; }
        if (f1 == null) continue; PlanarFace f2 = null; foreach (Face fc in K.Faces) { var pf = fc as PlanarFace; if (pf != null && pf != f1 && pf.FaceNormal.DotProduct(f1.FaceNormal) < -0.999 && (f2 == null || pf.Area > f2.Area)) f2 = pf; }
        var cc = K.ComputeCentroid(); var found = new List<object[]>();
        foreach (var f in new[] { f1, f2 })
        {
            if (f == null) continue; var fn = f.FaceNormal;
            var cands = new List<object[]>();
            foreach (var S in nodeList.Where(p => Ov(p.B, cap.B, 1 / M)))
            {
                foreach (Face fc in S.S.Faces)
                {
                    var g = fc as PlanarFace; if (g == null || g.FaceNormal.DotProduct(fn) > -0.9999) continue;
                    if (Math.Abs((g.Origin - f.Origin).DotProduct(fn)) * M > 0.06) continue;
                    var gc2 = CentF(g); var dd = gc2 - cc; dd = dd - fn * dd.DotProduct(fn); if (dd.GetLength() * M > 150) continue;
                    XYZ e1 = null; foreach (var cl0 in g.GetEdgesAsCurveLoops()) { foreach (Curve c0 in cl0) { e1 = (c0.GetEndPoint(1) - c0.GetEndPoint(0)).Normalize(); break; } break; }
                    var e2 = fn.CrossProduct(e1).Normalize(); double a1l, a1h, a2l, a2h; ExtF(g, e1, out a1l, out a1h); ExtF(g, e2, out a2l, out a2h);
                    double d1 = a1h - a1l, d2 = a2h - a2l; XYZ lng = null;
                    if (Math.Abs(d1 - 8) < 0.15 && d2 > 8.5) lng = e2; else if (Math.Abs(d2 - 8) < 0.15 && d1 > 8.5) lng = e1; if (lng == null) continue;
                    cands.Add(new object[] { S, f, lng, gc2, S.S.Volume });
                }
            }
            if (cands.Count == 0) continue;
            if (cands.Count == 1) { lines.Add("ONLY ONE plate on end-plate face (no rib/flat pair) cap #" + cap.El.Id + " @" + P3(cc)); continue; }
            var rib = cands.OrderBy(x => (double)x[4]).First(); var plate = cands.OrderByDescending(x => (double)x[4]).First();
            var Lng = (XYZ)rib[2]; var Nn = Lng; if (((XYZ)plate[3] - (XYZ)rib[3]).DotProduct(Nn) < 0) Nn = -Nn;
            found.Add(new object[] { rib[0], f, Nn, fn.CrossProduct(Nn).Normalize() });
            if (cands.Count > 2) lines.Add("cap #" + cap.El.Id + ": " + cands.Count + " plates on end-plate face @" + P3(cc));
        }
        if (found.Count == 0) { noRib++; lines.Add("NO RIB at cap #" + cap.El.Id + " " + cap.Name + " @" + P3(cc)); continue; }
        if (found.Count > 1) { multiRib++; lines.Add("MULTI RIB(" + found.Count + ") at cap #" + cap.El.Id + " @" + P3(cc)); }
        var R = (Pc)found[0][0]; var F = (PlanarFace)found[0][1]; var N = (XYZ)found[0][2]; var A2 = (XYZ)found[0][3]; var U = F.FaceNormal; ribs++;
        double c0N = cc.DotProduct(N) * M, c0U = F.Origin.DotProduct(U) * M, c0W = cc.DotProduct(A2) * M;
        double cl, ch; ExtF(F, N, out cl, out ch); double cw = (ch - cl) / 2; double b = 2 * (cw - 10);
        double rl, rh; Ext(R.S, N, out rl, out rh); rl -= c0N; rh -= c0N;
        double ul, uh; Ext(R.S, U, out ul, out uh); ul -= c0U; uh -= c0U;
        double wl, wh; Ext(R.S, A2, out wl, out wh); wl -= c0W; wh -= c0W;
        double D = rh - rl; double gFar = rl + cw; bool top = Math.Abs(rh - (cw - 10)) < 0.6; bool axis = Math.Abs(rh + 4) < 0.6;
        if (top) topLap++; else if (axis) axisIns++;
        gMin = Math.Min(gMin, gFar); gMax = Math.Max(gMax, gFar); dMin = Math.Min(dMin, D); dMax = Math.Max(dMax, D);
        string mk = R.Name; string pos = P3(cc);
        if (Math.Abs(gFar - 12) > 0.6) { farBad++; lines.Add("FAR-FACE: rib lo " + Math.Round(rl, 1) + " vs tube far face " + Math.Round(-(cw - 10), 1) + " (gap " + Math.Round(rl + cw - 10, 1) + ") " + mk + " @" + pos + " rib #" + R.El.Id); }
        if (!top && !axis) { hiBad++; lines.Add("RIB TOP not at flat plate: hi " + Math.Round(rh, 1) + " cw " + Math.Round(cw, 1) + " " + mk + " @" + pos); }
        if (Math.Abs(ul) > 0.3) lines.Add("RIB not on end plate: u0 " + Math.Round(ul, 2) + " " + mk + " @" + pos); if (dbg.Count(x => x.StartsWith(mkeyD(mk, top))) < 2 || Math.Abs(gFar - 12) > 0.6 && dbg.Count < 12) dbg.Add(mkeyD(mk, top) + " @" + pos + " ul " + Math.Round(ul, 2) + " uh " + Math.Round(uh, 1) + " rl " + Math.Round(rl, 1) + " rh " + Math.Round(rh, 1) + " wl " + Math.Round(wl, 2) + " wh " + Math.Round(wh, 2) + " cw " + Math.Round(cw, 1) + " solid#faces " + R.S.Faces.Size + " vol " + Math.Round(R.S.Volume * M * M * M) + " capFace " + (ReferenceEquals(F, f1) ? "f1" : "f2") + " capCentroid-vs-bb dU " + Math.Round((cc - F.Origin).DotProduct(U) * M, 2));
        if (!perDs.ContainsKey(R.El.Id.Value)) perDs[R.El.Id.Value] = new List<string>(); perDs[R.El.Id.Value].Add(pos + " " + (top ? "T" : "A") + " b" + Math.Round(b) + " D" + Math.Round(D, 1) + " u" + Math.Round(uh));
        string mkey = mk + (top ? " [lap]" : " [axis]"); if (!perMk.ContainsKey(mkey)) perMk[mkey] = new int[3]; perMk[mkey][0]++;
        var rb = R.B; var Wr = new List<Pc>();
        foreach (var w in weldList) if (Ov(w.B, rb, 2 / M)) Wr.Add(w);
        double wLoAbs = c0W + wl, wHiAbs = c0W + wh;
        bool sLoEnd = false, sHiEnd = false, sLoFlat = false, sHiFlat = false;
        foreach (var w in Wr)
        {
            double wnl, wnh; Ext(w.S, N, out wnl, out wnh); wnl -= c0N; wnh -= c0N; double wul, wuh; Ext(w.S, U, out wul, out wuh); wul -= c0U; wuh -= c0U;
            bool onLo = HasFace(w.S, A2, cc + A2 * ((wl) / M), 0.06), onHi = HasFace(w.S, A2, cc + A2 * ((wh) / M), 0.06);
            if (!onLo && !onHi) continue;
            bool onEnd = HasFace(w.S, U, F.Origin, 0.06); bool onFlat = HasFace(w.S, N, cc + N * (rh / M), 0.06);
            if (onEnd && wnh - wnl >= D - 12 && wnl >= rl - 1 && wnh <= rh + 1) { if (onLo) sLoEnd = true; if (onHi) sHiEnd = true; }
            if (onFlat && wuh - wul >= (uh - 8) - 6) { if (onLo) sLoFlat = true; if (onHi) sHiFlat = true; }
        }
        if (!sLoEnd || !sHiEnd) { wBadEnd++; lines.Add("NO WELD rib-end plate (lo " + sLoEnd + ", hi " + sHiEnd + ") " + mk + " @" + pos); }
        if (!sLoFlat || !sHiFlat) { wBadFlat++; lines.Add("NO WELD rib-flat plate (lo " + sLoFlat + ", hi " + sHiFlat + ") " + mk + " @" + pos); }
        var tests = new List<Pc>(); tests.Add(R); tests.AddRange(Wr);
        foreach (var t in tests)
        {
            foreach (var o in pcs)
            {
                if (ReferenceEquals(o, t) || (o.Kind == 4 && t.Kind == 4) || (o.Kind == 2 && o.El.Id == cap.El.Id)) continue;
                if (!Ov(t.B, o.B, 0)) continue; double v = 0;
                try { var x = BooleanOperationsUtils.ExecuteBooleanOperation(t.S, o.S, BooleanOperationsType.Intersect); if (x != null) v = x.Volume * M * M * M; } catch { }
                if (v < 0.05) continue;
                string kn = new[] { "tube/column", "node plate", "cap", "bolt", "weld", "other" }[o.Kind];
                string key = (t.Kind == 1 ? "RIB" : "WELD") + " x " + kn + (o.Kind == 1 || o.Kind == 5 ? " (" + (o.Name.Length > 28 ? o.Name.Substring(0, 28) : o.Name) + ")" : o.Kind == 0 ? " (" + o.Name.Split(' ')[0] + ")" : "");
                if (lines.Count(x => x.StartsWith("HIT")) < 40) lines.Add("HIT " + key + " " + Math.Round(v, 2) + " mm3 weldC " + P3(t.S.ComputeCentroid()) + " weldVol " + Math.Round(t.S.Volume * M * M * M, 1) + " otherC " + P3(o.S.ComputeCentroid()) + " otherVol " + Math.Round(o.S.Volume * M * M * M, 1) + " otherBB " + Math.Round((o.B[3] - o.B[0]) * M) + "x" + Math.Round((o.B[4] - o.B[1]) * M) + "x" + Math.Round((o.B[5] - o.B[2]) * M)); hits[key] = (hits.ContainsKey(key) ? hits[key] : 0) + 1; if (!hitEx.ContainsKey(key)) hitEx[key] = Math.Round(v, 2) + " mm3, t#" + t.El.Id + " o#" + o.El.Id + " " + o.Name + " @" + pos;
            }
        }
    }
    sb.AppendLine("caps " + nCap + ", ribs found " + ribs + " (lap " + topLap + ", axis-plane " + axisIns + "), caps without rib " + noRib + ", with >1 " + multiRib + ", DS-plane-not-perp skips " + notPerp);
    sb.AppendLine("far gap (cap edge to rib end) min " + Math.Round(gMin, 2) + " max " + Math.Round(gMax, 2) + " (expect 12 = tube far face - 2); rib depth D min " + Math.Round(dMin, 1) + " max " + Math.Round(dMax, 1));
    sb.AppendLine("far-face FAIL " + farBad + ", top-not-at-flat-plate " + hiBad + ", no weld to end plate " + wBadEnd + ", no weld to flat plate " + wBadFlat);
    sb.AppendLine("CLASH groups (rib or its welds vs others, > 0.05 mm3): " + hits.Count);
    foreach (var k in hits.OrderByDescending(x => x.Value)) sb.AppendLine("   " + k.Value + " x " + k.Key + "  e.g. " + hitEx[k.Key]);
    sb.AppendLine("== per mark (ribs)"); foreach (var k in perMk.OrderBy(x => x.Key)) sb.AppendLine("   " + k.Key + ": " + k.Value[0]);
    sb.AppendLine("== debug"); foreach (var l in dbg) sb.AppendLine("   " + l); sb.AppendLine("== problems"); foreach (var l in lines.Take(80)) sb.AppendLine("   " + l);
    sb.AppendLine("== node DS with >= 3 ribs");
    foreach (var kv in perDs.Where(x => x.Value.Count >= 3).Take(400)) { var el = nd.GetElement(new ElementId(kv.Key)); sb.AppendLine("   DS#" + kv.Key + " " + el.Name + " ribs " + kv.Value.Count + " | " + string.Join(" ; ", kv.Value)); }
    return sb.ToString();
}
static void _end() {