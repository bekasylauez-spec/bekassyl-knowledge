// READ-ONLY extra checks (a)-(d) for B109 brace-end nodes. Output: scratchpad\_ext.txt, _ext_ends.tsv, _ext_gus.tsv
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\_ext.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; string r;
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt")); r = Ext(nd); }
  catch (Exception ex) { r = "ERR " + ex; }
  System.IO.File.WriteAllText(log, r, System.Text.Encoding.UTF8); };
uiapp.Idling += hnd;
return "queued";
}

const double M = 304.8;
class Sd { public Solid S; public double[] B; public Element El; public string Nm; public double T, Area, V; public PlanarFace Pf; public bool Prim; public string Kind; }
class Bl { public XYZ C, A; public double L, Ar; public Sd Sh; public En E; public double q0, q1, tIns = -1, tGus = -1, eIns = -1, eGus = -1; public long Ds; }
class En { public FamilyInstance F; public string Mk, Cm; public XYZ Pe, U; public double B; public List<Bl> Bolts = new List<Bl>(); public Sd Gus, Ins; public double dNear = -1, reach = -1, outL = -1; public string Arr; }
static double[] BBx(Solid s) { var bb = s.GetBoundingBox(); var a = bb.Transform.OfPoint(bb.Min); var b = bb.Transform.OfPoint(bb.Max);
    return new[] { Math.Min(a.X, b.X), Math.Min(a.Y, b.Y), Math.Min(a.Z, b.Z), Math.Max(a.X, b.X), Math.Max(a.Y, b.Y), Math.Max(a.Z, b.Z) }; }
static Sd MkSd(Solid s, Element el, string nm) {
    var o = new Sd { S = s, El = el, Nm = nm, B = BBx(s), V = s.Volume }; double best = 0;
    foreach (Face f in s.Faces) { var pf = f as PlanarFace; if (pf == null) continue; double a = pf.Area; if (a > best) { best = a; o.Pf = pf; } }
    o.Area = best; o.T = best > 0 ? s.Volume / best * M : 0; return o; }
static List<Solid> Sol(Element el, Options opt) { var r = new List<Solid>();
    foreach (var go in el.get_Geometry(opt)) { IEnumerable<GeometryObject> objs = go is GeometryInstance gi ? gi.GetInstanceGeometry().Cast<GeometryObject>() : new[] { go };
        r.AddRange(objs.OfType<Solid>().Where(x => x.Volume > 1e-9)); } return r; }
static bool Ov(double[] a, double[] b, double m) { return a[0] <= b[3] + m && a[3] >= b[0] - m && a[1] <= b[4] + m && a[4] >= b[1] - m && a[2] <= b[5] + m && a[5] >= b[2] - m; }
static double Iv(Solid a, Solid b) { try { var x = BooleanOperationsUtils.ExecuteBooleanOperation(a, b, BooleanOperationsType.Intersect); return x == null ? 0 : x.Volume * M * M * M; } catch { return 0; } }
static double DistPt(Solid s, XYZ p) { double best = 1e9;
    foreach (Edge e in s.Edges) { double d = e.AsCurve().Distance(p); if (d < best) best = d; }
    foreach (Face f in s.Faces) { if (!(f is PlanarFace)) continue; var pr = f.Project(p); if (pr == null) continue; try { if (f.IsInside(pr.UVPoint) && pr.Distance < best) best = pr.Distance; } catch { } }
    return best * M; }
static double EdgeDist(Sd pl, XYZ c) { if (pl.Pf == null) return -1; var n = pl.Pf.FaceNormal; var p = c - n * ((c - pl.Pf.Origin).DotProduct(n)); double best = 1e9;
    foreach (EdgeArray ea in pl.Pf.EdgeLoops) foreach (Edge e in ea) { double d = e.AsCurve().Distance(p); if (d < best) best = d; } return best * M; }
static IEnumerable<XYZ> Verts(Solid s) { foreach (Edge e in s.Edges) { var c = e.AsCurve(); yield return c.GetEndPoint(0); yield return c.GetEndPoint(1); } }
static string F1(double v) { return Math.Round(v, 1).ToString(System.Globalization.CultureInfo.InvariantCulture); }
static string P3(XYZ p) { return Math.Round(p.X * M) + "," + Math.Round(p.Y * M) + "," + Math.Round(p.Z * M); }

static string Ext(Document nd)
{
    var sb = new System.Text.StringBuilder(); var opt = new Options { DetailLevel = ViewDetailLevel.Fine };
    string dir = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\";
    Func<Element, string> Cm = f => f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "";
    var fi = new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Symbol.Family.Name.StartsWith("(КМ)")
        && (x.Category.Id.Value == (long)BuiltInCategory.OST_StructuralFraming || x.Category.Id.Value == (long)BuiltInCategory.OST_StructuralColumns)).ToList();
    var brace = new HashSet<string> { "СВ1", "СВ2", "СВ3", "ГС1", "ВС1", "ВФ1" };
    var ends = new List<En>();
    foreach (var f in fi.Where(f => f.Location is LocationCurve && f.Symbol.Family.Name.Contains("труба") && (Cm(f).StartsWith("СВ") || Cm(f) == "ГС1" || Cm(f) == "Р1" || Cm(f) == "ВС1" || Cm(f) == "ВФ1")))
    {
        var c = (f.Location as LocationCurve).Curve; double b = f.Symbol.LookupParameter("b").AsDouble();
        for (int k = 0; k < 2; k++) { var pe = c.GetEndPoint(k); var po = c.GetEndPoint(1 - k); ends.Add(new En { F = f, Mk = Cm(f).Split(' ')[0], Cm = Cm(f), Pe = pe, U = (pe - po).Normalize(), B = b }); }
    }
    sb.AppendLine("tube ends " + ends.Count + ": " + string.Join(", ", ends.GroupBy(x => x.Mk).Select(g => g.Key + " " + g.Count())));
    var sup = new List<Sd>(); var nodePl = new List<Sd>(); var boltDS = new List<DirectShape>();
    foreach (var f in fi) { string mk = Cm(f).Split(' ')[0]; if (brace.Contains(mk)) continue; foreach (var s in Sol(f, opt)) { var sd = MkSd(s, f, "M:" + Cm(f)); sd.Kind = "M:" + Cm(f); sup.Add(sd); } }
    var DSs = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел").ToList();
    foreach (var ds in DSs)
    {
        long cat = ds.Category == null ? 0 : ds.Category.Id.Value;
        if (cat == (long)BuiltInCategory.OST_StructConnectionWelds) continue;
        if (cat == (long)BuiltInCategory.OST_StructConnectionBolts) { if (ds.Name.StartsWith("Болт М16")) boltDS.Add(ds); continue; }
        bool tubeNode = ds.ApplicationDataId == "трубы" && ds.Name.StartsWith("Узел");
        foreach (var s in Sol(ds, opt)) { var sd = MkSd(s, ds, ds.Name); sd.Kind = "DS:" + ds.Name; if (tubeNode) nodePl.Add(sd); if (sd.T >= 9) sup.Add(sd); }
    }
    foreach (var g in nodePl.Where(x => x.T > 9.5 && x.T < 10.5).GroupBy(x => x.El.Id.Value)) { var mx = g.OrderByDescending(x => x.V).First(); mx.Prim = true; }
    var gus = nodePl.Where(x => x.T > 9.5 && x.T < 10.5).ToList(); var prim = gus.Where(x => x.Prim).ToList(); var ins = nodePl.Where(x => x.T > 7.5 && x.T < 8.5).ToList();
    sb.AppendLine("node DS solids " + nodePl.Count + ", gusset-type (t10) " + gus.Count + " (primary " + prim.Count + "), inserts (t8) " + ins.Count + ", support candidates " + sup.Count);
    var bolts = new List<Bl>();
    foreach (var ds in boltDS) foreach (var s in Sol(ds, opt))
    {
        int nf = 0; foreach (Face f in s.Faces) nf++; if (nf > 4 || s.Volume * M * M * M < 5000) continue;
        PlanarFace pf = null; foreach (Face f in s.Faces) if (f is PlanarFace) { pf = (PlanarFace)f; break; } if (pf == null) continue;
        var sd = MkSd(s, ds, "bolt"); bolts.Add(new Bl { C = s.ComputeCentroid(), A = pf.FaceNormal, L = s.Volume / pf.Area * M, Ar = pf.Area * M * M, Sh = sd, Ds = ds.Id.Value });
    }
    sb.AppendLine("bolt DS " + boltDS.Count + ", shanks " + bolts.Count + ", shank diameter(mm) " + (bolts.Count > 0 ? F1(2 * Math.Sqrt(bolts[0].Ar / Math.PI)) : "-") + ", L min/max " + F1(bolts.Min(b => b.L)) + "/" + F1(bolts.Max(b => b.L)));
    int unassigned = 0; var unEx = new List<string>();
    foreach (var bl in bolts)
    {
        En bestE = null; double bq = 1e9;
        foreach (var e in ends)
        {
            if (Math.Abs(e.U.DotProduct(bl.A)) > 0.05) continue; var d = (bl.C - e.Pe) * M; var W = bl.A.CrossProduct(e.U).Normalize();
            double q0 = d.DotProduct(e.U), q1 = d.DotProduct(W), qn = d.DotProduct(bl.A);
            if (q0 < -5 || q0 > 200 || qn < -15 || qn > 60 || Math.Abs(q1) > e.B * M / 2 + 5) continue;
            if (Math.Abs(q1) < bq) { bq = Math.Abs(q1); bestE = e; bl.q0 = q0; bl.q1 = q1; }
        }
        if (bestE == null) { unassigned++; if (unEx.Count < 8) unEx.Add(P3(bl.C)); } else { bl.E = bestE; bestE.Bolts.Add(bl); }
    }
    foreach (var e in ends)
    {
        Sd bestG = null; double bd = 1e9;
        var pm = e.Pe * M;
        foreach (var g in prim) { if (pm.X < g.B[0] * M - 250 || pm.X > g.B[3] * M + 250 || pm.Y < g.B[1] * M - 250 || pm.Y > g.B[4] * M + 250 || pm.Z < g.B[2] * M - 250 || pm.Z > g.B[5] * M + 250) continue;
            double d = DistPt(g.S, e.Pe); if (d < bd) { bd = d; bestG = g; } }
        e.Gus = bestG; if (bestG != null) { e.dNear = bd; e.reach = Verts(bestG.S).Max(v => (v - e.Pe).DotProduct(e.U)) * M; }
        if (bestG != null) { Sd bi = null; double bdi = 1e9; foreach (var s in ins.Where(x => x.El.Id == bestG.El.Id)) { double d = DistPt(s.S, e.Pe); if (d < bdi) { bdi = d; bi = s; } }
            if (bi != null && bdi < 6) { e.Ins = bi; e.outL = Verts(bi.S).Max(v => (v - e.Pe).DotProduct(e.U)) * M; } }
        var q = e.Bolts; string arr;
        if (q.Count == 0) arr = "none"; else if (q.Count != 2) arr = "n" + q.Count;
        else if (Math.Abs(q[0].q1) < 3 && Math.Abs(q[1].q1) < 3 && Math.Abs(Math.Abs(q[0].q0 - q[1].q0) - 65) < 3) arr = "along";
        else if (Math.Abs(q[0].q0 - q[1].q0) < 3 && q[0].q1 * q[1].q1 < 0) arr = "across"; else arr = "other";
        e.Arr = arr;
    }
    int bOk = 0, bBad = 0; var bBadEx = new List<string>();
    foreach (var bl in bolts)
    {
        var box = bl.Sh.B;
        foreach (var pl in nodePl)
        {
            if (!Ov(pl.B, box, 2 / M)) continue; double v = Iv(bl.Sh.S, pl.S); if (v < 0.5) continue; double t = v / bl.Ar;
            if (pl.T > 7.5 && pl.T < 8.5) { if (t > bl.tIns) { bl.tIns = t; bl.eIns = EdgeDist(pl, bl.C); } }
            else if (pl.T > 9.5 && pl.T < 10.5) { if (t > bl.tGus) { bl.tGus = t; bl.eGus = EdgeDist(pl, bl.C); } }
        }
        bool ok = bl.tIns > 7.9 && bl.tGus > 9.9; if (ok) bOk++; else { bBad++; if (bBadEx.Count < 15) bBadEx.Add((bl.E == null ? "?" : bl.E.Mk) + " @" + P3(bl.C) + " ins " + F1(bl.tIns) + " gus " + F1(bl.tGus)); }
    }
    var gl = new System.Text.StringBuilder(); gl.AppendLine("ds\tname\tprim\tbbox\tsupport\tshift\tgap\tarea\tcands");
    int cOk = 0, cFloat = 0, cWeak = 0, cGapBig = 0; var cFloatEx = new List<string>(); var cWeakEx = new List<string>(); var supKinds = new Dictionary<string, int>();
    var dirs = new[] { XYZ.BasisX, -XYZ.BasisX, XYZ.BasisY, -XYZ.BasisY, XYZ.BasisZ, -XYZ.BasisZ };
    foreach (var g in gus)
    {
        var bq = g.B;
        var cands = sup.Where(c => c.El.Id != g.El.Id && Ov(c.B, bq, 7 / M)).ToList();
        Sd bestS = null; double bestA = 0, bestGap = 0, bestShift = -1;
        foreach (double s in new[] { 0.5, 1, 2, 3, 5 })
        {
            XYZ bd = null; Sd bc = null; double bv = 0;
            foreach (var dv in dirs)
            {
                var ts = SolidUtils.CreateTransformed(g.S, Transform.CreateTranslation(dv * (s / M)));
                var sb2 = new[] { bq[0] + Math.Min(0, dv.X * s / M), bq[1] + Math.Min(0, dv.Y * s / M), bq[2] + Math.Min(0, dv.Z * s / M), bq[3] + Math.Max(0, dv.X * s / M), bq[4] + Math.Max(0, dv.Y * s / M), bq[5] + Math.Max(0, dv.Z * s / M) };
                foreach (var c in cands) { if (!Ov(c.B, sb2, 0)) continue; double v = Iv(ts, c.S); if (v > 0.3 && v > bv) { bv = v; bc = c; bd = dv; } }
            }
            if (bc != null)
            {
                var ts2 = SolidUtils.CreateTransformed(g.S, Transform.CreateTranslation(bd * ((s + 1) / M))); double v2 = Iv(ts2, bc.S);
                double area = Math.Max(v2 - bv, 0); double gap = area > 1 ? Math.Max(0, s - bv / area) : s;
                bestS = bc; bestA = area; bestGap = gap; bestShift = s; break;
            }
        }
        string kind = bestS == null ? "-" : (bestS.Kind.StartsWith("M:") ? bestS.Kind : bestS.Kind.Substring(0, Math.Min(40, bestS.Kind.Length)));
        gl.AppendLine(g.El.Id.Value + "\t" + g.Nm + "\t" + (g.Prim ? "prim" : "stand") + "\t" + P3(new XYZ(g.B[0], g.B[1], g.B[2])) + ".." + P3(new XYZ(g.B[3], g.B[4], g.B[5])) + "\t" + kind + "\t" + F1(bestShift) + "\t" + F1(bestGap) + "\t" + F1(bestA) + "\t" + cands.Count);
        string sk = (g.Prim ? "prim " : "stand ") + (bestS == null ? "NONE" : bestS.Kind.StartsWith("M:") ? bestS.Kind : "DS-plate"); supKinds[sk] = supKinds.ContainsKey(sk) ? supKinds[sk] + 1 : 1;
        if (bestS == null) { cFloat++; if (cFloatEx.Count < 12) cFloatEx.Add(g.El.Id.Value + " " + g.Nm + " " + (g.Prim ? "prim" : "stand") + " @" + P3(new XYZ(g.B[0], g.B[1], g.B[2]))); }
        else if (bestGap > 2.5) { cGapBig++; if (cFloatEx.Count < 12) cFloatEx.Add(g.El.Id.Value + " gap " + F1(bestGap) + " " + g.Nm + " @" + P3(new XYZ(g.B[0], g.B[1], g.B[2]))); }
        else if (bestA < 150) { cWeak++; if (cWeakEx.Count < 12) cWeakEx.Add(g.El.Id.Value + " area " + F1(bestA) + " vs " + bestS.Kind + " @" + P3(new XYZ(g.B[0], g.B[1], g.B[2]))); }
        else cOk++;
    }
    sb.AppendLine("=== (a) bolt arrangement per tube end");
    foreach (var gp in ends.GroupBy(x => x.Mk).OrderBy(x => x.Key)) sb.AppendLine("  " + gp.Key + ": ends " + gp.Count() + " | " + string.Join(", ", gp.GroupBy(x => x.Arr).OrderBy(x => x.Key).Select(g => g.Key + " " + g.Count())));
    sb.AppendLine("  TOTAL ends " + ends.Count + " | " + string.Join(", ", ends.GroupBy(x => x.Arr).OrderBy(x => x.Key).Select(g => g.Key + " " + g.Count())) + "; bolts " + bolts.Count + ", bolts not assigned to an end " + unassigned + (unEx.Count > 0 ? " e.g. " + string.Join("; ", unEx) : ""));
    int expAlong = ends.Count(x => x.outL >= 145), expAcross = ends.Count(x => x.outL >= 0 && x.outL < 145), noIns = ends.Count(x => x.outL < 0);
    int mism = ends.Count(x => (x.outL >= 145 && x.Arr != "along") || (x.outL >= 0 && x.outL < 145 && x.Arr != "across"));
    sb.AppendLine("  insert outL (from insert geometry): >=145 " + expAlong + " ends, <145 " + expAcross + " ends, insert not found " + noIns + "; arrangement does not match outL rule: " + mism);
    var outls = ends.Where(x => x.outL >= 0).ToList(); if (outls.Count > 0) sb.AppendLine("  outL min/max " + F1(outls.Min(x => x.outL)) + "/" + F1(outls.Max(x => x.outL)) + "; ends with outL<145 by mark: " + string.Join(", ", outls.Where(x => x.outL < 145).GroupBy(x => x.Mk).Select(g => g.Key + " " + g.Count())));
    foreach (var e in ends.Where(x => (x.outL >= 145 && x.Arr != "along") || (x.outL >= 0 && x.outL < 145 && x.Arr != "across")).Take(10)) sb.AppendLine("    mismatch: " + e.Mk + " end @" + P3(e.Pe) + " arr " + e.Arr + " outL " + F1(e.outL));
    sb.AppendLine("=== (b) bolts through insert AND gusset (shank intersection thickness: insert 8, gusset 10): OK " + bOk + ", BAD " + bBad);
    foreach (var s in bBadEx) sb.AppendLine("    " + s);
    var eI = bolts.Where(x => x.eIns >= 0).ToList(); var eG = bolts.Where(x => x.eGus >= 0).ToList();
    if (eI.Count > 0) sb.AppendLine("  edge distance bolt axis -> insert edge: min " + F1(eI.Min(x => x.eIns)) + ", <24: " + eI.Count(x => x.eIns < 24) + ", <28.5: " + eI.Count(x => x.eIns < 28.5));
    if (eG.Count > 0) sb.AppendLine("  edge distance bolt axis -> gusset edge: min " + F1(eG.Min(x => x.eGus)) + ", <24: " + eG.Count(x => x.eGus < 24) + ", <28.5: " + eG.Count(x => x.eGus < 28.5));
    foreach (var x in bolts.Where(x => x.eGus >= 0 && x.eGus < 24).Take(6)) sb.AppendLine("    gusset edge " + F1(x.eGus) + " @" + P3(x.C) + " " + (x.E == null ? "?" : x.E.Mk));
    foreach (var x in bolts.Where(x => x.eIns >= 0 && x.eIns < 24).Take(6)) sb.AppendLine("    insert edge " + F1(x.eIns) + " @" + P3(x.C) + " " + (x.E == null ? "?" : x.E.Mk));
    sb.AppendLine("=== (c) gussets (t10 solids " + gus.Count + ") touch a support within 5 mm: OK(area>=150) " + cOk + ", weak " + cWeak + ", gap>2.5 " + cGapBig + ", FLOATING(no support within 5 mm) " + cFloat);
    sb.AppendLine("  support kinds: " + string.Join("; ", supKinds.OrderBy(x => x.Key).Select(x => x.Key + " " + x.Value)));
    foreach (var s in cFloatEx) sb.AppendLine("    float/gap: " + s); foreach (var s in cWeakEx) sb.AppendLine("    weak: " + s);
    var dn = ends.Where(x => x.dNear >= 0).ToList(); int nog = ends.Count(x => x.Gus == null);
    sb.AppendLine("=== (d) tube end -> its gusset: ends without gusset within 250 " + nog + "; nearest gusset edge: min " + (dn.Count > 0 ? F1(dn.Min(x => x.dNear)) : "-") + ", max " + (dn.Count > 0 ? F1(dn.Max(x => x.dNear)) : "-") + ", >200: " + dn.Count(x => x.dNear > 200) +
        "; far edge reach along axis: max " + (dn.Count > 0 ? F1(dn.Max(x => x.reach)) : "-") + ", >200: " + dn.Count(x => x.reach > 200));
    sb.AppendLine("  reach by mark (max/min/ >200): " + string.Join("; ", dn.GroupBy(x => x.Mk).Select(g => g.Key + " " + F1(g.Max(x => x.reach)) + "/" + F1(g.Min(x => x.reach)) + "/" + g.Count(x => x.reach > 200))));
    foreach (var e in ends.Where(x => x.Gus == null || x.dNear > 200).Take(10)) sb.AppendLine("    no/far gusset: " + e.Mk + " @" + P3(e.Pe) + " d " + F1(e.dNear));
    foreach (var e in dn.Where(x => x.reach > 200).OrderByDescending(x => x.reach).Take(8)) sb.AppendLine("    reach>200: " + e.Mk + " @" + P3(e.Pe) + " reach " + F1(e.reach) + " outL " + F1(e.outL));
    var tsv = new System.Text.StringBuilder(); tsv.AppendLine("mk\tcomment\tPe\tU\tnb\tarr\tq0a\tq0b\toutL\ttIns\ttGus\teIns\teGus\tdNear\treach\tgusDS");
    foreach (var e in ends) tsv.AppendLine(e.Mk + "\t" + e.Cm + "\t" + P3(e.Pe) + "\t" + F1(e.U.X) + "," + F1(e.U.Y) + "," + F1(e.U.Z) + "\t" + e.Bolts.Count + "\t" + e.Arr + "\t" + (e.Bolts.Count > 0 ? F1(e.Bolts[0].q0) : "") + "\t" + (e.Bolts.Count > 1 ? F1(e.Bolts[1].q0) : "") + "\t" + F1(e.outL) + "\t" + string.Join("/", e.Bolts.Select(b => F1(b.tIns))) + "\t" + string.Join("/", e.Bolts.Select(b => F1(b.tGus))) + "\t" + string.Join("/", e.Bolts.Select(b => F1(b.eIns))) + "\t" + string.Join("/", e.Bolts.Select(b => F1(b.eGus))) + "\t" + F1(e.dNear) + "\t" + F1(e.reach) + "\t" + (e.Gus == null ? "" : e.Gus.El.Id.Value.ToString()));
    System.IO.File.WriteAllText(dir + "_ext_ends.tsv", tsv.ToString(), System.Text.Encoding.UTF8); System.IO.File.WriteAllText(dir + "_ext_gus.tsv", gl.ToString(), System.Text.Encoding.UTF8);
    return sb.ToString();
}
static void _end() {