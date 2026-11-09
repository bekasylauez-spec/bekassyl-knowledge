// READ-ONLY end-plate / insert-inside-tube check (checker). Run WITHOUT -Lib.
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\q_end2.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; string r;
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt")); r = Q(nd); }
  catch (Exception ex) { r = "ERR " + ex; }
  System.IO.File.WriteAllText(log, r, System.Text.Encoding.UTF8); };
uiapp.Idling += hnd;
return "queued";
}
class Tb { public FamilyInstance f; public XYZ a, b, u, e1, e2; public double len, hb, hb2; public string mk; }
class Cs { public XYZ c; public double t, af; public XYZ n; public long id; public string name; public bool used; }
static string Q(Document nd)
{
    const double M = 304.8; var sb = new System.Text.StringBuilder(); var opt = new Options { DetailLevel = ViewDetailLevel.Fine };
    Func<FamilyInstance, string> Cm = f => f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "";
    var tubes = new List<Tb>();
    foreach (var f in new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Location is LocationCurve && x.Symbol.Family.Name.Contains("труба")))
    {
        var c = (f.Location as LocationCurve).Curve; var t = new Tb { f = f, mk = Cm(f) }; t.a = c.GetEndPoint(0); t.b = c.GetEndPoint(1); t.len = t.a.DistanceTo(t.b); t.u = (t.b - t.a).Normalize();
        double bb = f.Symbol.LookupParameter("b").AsDouble(); var hp = f.Symbol.LookupParameter("h"); t.hb = bb / 2; t.hb2 = (hp != null && hp.AsDouble() > 0.01) ? hp.AsDouble() / 2 : bb / 2;
        var tr = f.GetTransform(); var cand = new[] { tr.BasisX, tr.BasisY, tr.BasisZ }.Where(v => Math.Abs(v.DotProduct(t.u)) < 0.2).ToList();
        if (cand.Count >= 2) { t.e1 = cand[0]; t.e2 = t.u.CrossProduct(cand[0]).Normalize(); } else { var z = Math.Abs(t.u.Z) > 0.9 ? XYZ.BasisX : XYZ.BasisZ; t.e1 = t.u.CrossProduct(z).Normalize(); t.e2 = t.u.CrossProduct(t.e1).Normalize(); }
        tubes.Add(t);
    }
    sb.AppendLine("tube members " + tubes.Count + "; by mark: " + string.Join(", ", tubes.GroupBy(x => x.mk.Split(' ')[0]).Select(g => g.Key + " " + g.Count())));
    var plates = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел" && x.Category.Id.Value == (long)BuiltInCategory.OST_StructConnections).ToList();
    Func<Solid, double> afOf = so => { double af = 0; foreach (Face f in so.Faces) if (f is PlanarFace) af = Math.Max(af, f.Area); return af; };
    Func<Solid, XYZ> nOf = so => { double af = 0; XYZ n = XYZ.BasisZ; foreach (Face f in so.Faces) if (f is PlanarFace pf && pf.Area > af) { af = pf.Area; n = pf.FaceNormal; } return n; };
    var caps = new List<Cs>(); var insertSolids = new List<KeyValuePair<DirectShape, Solid>>();
    var capNames = new Dictionary<string, Dictionary<double, int>>();
    foreach (var d in plates)
    {
        string n = d.Name ?? "";
        bool isCap = n.IndexOf("заглушка", StringComparison.OrdinalIgnoreCase) >= 0 || n.IndexOf("торц", StringComparison.OrdinalIgnoreCase) >= 0;
        bool isIns = n.StartsWith("Узел ") && n.Contains("вкладыши");
        if (!isCap && !isIns) continue;
        foreach (var go in d.get_Geometry(opt)) { var so = go as Solid; if (so == null || so.Volume < 1e-12) continue; double af = afOf(so); double tt = so.Volume / af * M;
            if (isCap) { caps.Add(new Cs { c = so.ComputeCentroid(), t = tt, af = af * M * M, n = nOf(so), id = d.Id.Value, name = n });
                string pre = n.Contains("(") ? n.Substring(0, n.IndexOf('(')) : n; if (!capNames.ContainsKey(pre)) capNames[pre] = new Dictionary<double, int>(); double rt = Math.Round(tt); capNames[pre][rt] = capNames[pre].ContainsKey(rt) ? capNames[pre][rt] + 1 : 1; }
            else insertSolids.Add(new KeyValuePair<DirectShape, Solid>(d, so)); }
    }
    sb.AppendLine("cap-like solids " + caps.Count + "; names/thickness: " + string.Join(" | ", capNames.Select(kv => kv.Key + ": " + string.Join(",", kv.Value.Select(q => q.Key + "mm x" + q.Value)))));
    // (1) end plates
    var grid = new Dictionary<string, List<Cs>>(); Func<XYZ, int, int, int, string> K = (p, i, j, k) => ((int)Math.Floor(p.X * M / 50) + i) + "_" + ((int)Math.Floor(p.Y * M / 50) + j) + "_" + ((int)Math.Floor(p.Z * M / 50) + k);
    foreach (var c in caps) { string k = K(c.c, 0, 0, 0); if (!grid.ContainsKey(k)) grid[k] = new List<Cs>(); grid[k].Add(c); }
    int ends = 0, ok = 0, miss = 0, badT = 0, badDim = 0, badN = 0; var ex = new List<string>(); var perMk = new Dictionary<string, int[]>();
    foreach (var t in tubes)
    {
        string mk = t.mk.StartsWith("ФФ1 НП") ? "ФФ1 НП" : t.mk.Split(' ')[0]; bool want = mk == "СВ1" || mk == "СВ2" || mk == "СВ3" || mk == "ГС1" || mk == "Р1" || mk == "ВС1" || mk == "ВФ1" || mk == "ФФ1 НП";
        if (!want) continue; if (!perMk.ContainsKey(mk)) perMk[mk] = new int[3];
        for (int k = 0; k < 2; k++)
        {
            var pe = k == 0 ? t.a : t.b; var u = k == 0 ? -t.u : t.u; double b = t.hb * 2 * M;
            if (mk == "ФФ1 НП" && false) continue;
            var exp = pe + u * (4 / M); Cs best = null; double bd = 1e9;
            for (int i = -1; i <= 1; i++) for (int j = -1; j <= 1; j++) for (int l = -1; l <= 1; l++) { List<Cs> lst; if (!grid.TryGetValue(K(exp, i, j, l), out lst)) continue; foreach (var c in lst) { double dd = c.c.DistanceTo(exp) * M; if (dd < bd) { bd = dd; best = c; } } }
            ends++; perMk[mk][0]++;
            if (best == null || bd > 2.0) { miss++; perMk[mk][1]++; if (ex.Count < 10) ex.Add("MISS " + t.f.Id.Value + " " + t.mk + " end" + k + " @" + Math.Round(pe.X * M) + "," + Math.Round(pe.Y * M) + "," + Math.Round(pe.Z * M) + " nearest " + Math.Round(bd, 1)); continue; }
            bool fine = true;
            if (Math.Abs(best.t - 8) > 0.3) { badT++; fine = false; if (ex.Count < 10) ex.Add("T " + best.id + " " + best.name + " t=" + Math.Round(best.t, 2) + " tube " + t.f.Id.Value + " " + t.mk); }
            double wantA = (b + 20) * (b + 20); if (Math.Abs(best.af - wantA) / wantA > 0.02) { badDim++; fine = false; if (ex.Count < 10) ex.Add("DIM " + best.id + " " + best.name + " area " + Math.Round(best.af) + " want " + Math.Round(wantA) + " (b+20=" + Math.Round(b + 20) + ") tube " + t.f.Id.Value + " " + t.mk); }
            if (Math.Abs(best.n.DotProduct(u)) < 0.98) { badN++; fine = false; if (ex.Count < 10) ex.Add("N " + best.id + " " + best.name + " tube " + t.f.Id.Value + " " + t.mk + " dot " + Math.Round(best.n.DotProduct(u), 3)); }
            if (fine) { ok++; } else perMk[mk][2]++;
        }
    }
    sb.AppendLine("(1) tube ends checked " + ends + ": OK " + ok + ", no plate " + miss + ", wrong t " + badT + ", wrong size " + badDim + ", wrong normal " + badN);
    sb.AppendLine("    per mark [ends, missing, bad]: " + string.Join("; ", perMk.Select(kv => kv.Key + " " + kv.Value[0] + "/" + kv.Value[1] + "/" + kv.Value[2])));
    foreach (var s in ex) sb.AppendLine("    " + s);
    // (2) inserts/tabs: any vertex inside a tube envelope (s in (0.5, len-0.5), lateral < half-width - 1 mm)
    int nIns = 0, bad = 0, minS = 0; var ex2 = new List<string>(); double minSval = 1e9;
    foreach (var kv in insertSolids)
    {
        var so = kv.Value; if (Math.Abs(so.Volume / afOf(so) * M - 8) > 0.6) continue; nIns++;
        var bb = so.GetBoundingBox(); var tr = bb.Transform; var lo = tr.OfPoint(bb.Min); var hi = tr.OfPoint(bb.Max);
        var vs = new List<XYZ>(); foreach (Edge ed in so.Edges) { var cu = ed.AsCurve(); vs.Add(cu.GetEndPoint(0)); vs.Add(cu.GetEndPoint(1)); }
        bool hit = false;
        foreach (var t in tubes)
        {
            foreach (var p in vs)
            {
                var r = p - t.a; double s = r.DotProduct(t.u);
                if (s <= 0.5 / M || s >= t.len - 0.5 / M) continue; if (t.mk.StartsWith("ФФ1") && (s < 150.5 / M || s > t.len - 150.5 / M)) continue;
                if (Math.Abs(r.DotProduct(t.e1)) < t.hb - 1.0 / M && Math.Abs(r.DotProduct(t.e2)) < t.hb2 - 1.0 / M)
                { hit = true; if (ex2.Count < 10) ex2.Add(kv.Key.Id.Value + " " + kv.Key.Name + " vertex inside tube " + t.f.Id.Value + " " + t.mk + " s=" + Math.Round(s * M) + "/" + Math.Round(t.len * M) + " @" + Math.Round(p.X * M) + "," + Math.Round(p.Y * M) + "," + Math.Round(p.Z * M)); break; }
            }
            if (hit) break;
        }
        if (hit) bad++;
    }
    sb.AppendLine("(2) insert/tab/rib -8 solids checked " + nIns + ": with a vertex inside a tube " + bad);
    foreach (var s in ex2) sb.AppendLine("    " + s);
    // (2b) deepest inward reach of insert/tab -8 solids relative to the nearest tube end (a), for solids touching an end plate zone: vertices within 60 mm of an end, min axial coordinate
    var endList = new List<KeyValuePair<XYZ, XYZ>>();
    foreach (var t in tubes) { string mk = t.mk.Split(' ')[0]; if (!(mk == "СВ1" || mk == "СВ2" || mk == "СВ3" || mk == "ГС1" || mk == "Р1" || mk == "ВС1" || mk == "ВФ1")) continue; endList.Add(new KeyValuePair<XYZ, XYZ>(t.a, -t.u)); endList.Add(new KeyValuePair<XYZ, XYZ>(t.b, t.u)); }
    var hist = new Dictionary<int, int>();
    foreach (var kv in insertSolids)
    {
        var so = kv.Value; if (Math.Abs(so.Volume / afOf(so) * M - 8) > 0.6) continue;
        var ctr = so.ComputeCentroid(); KeyValuePair<XYZ, XYZ> bestE = default(KeyValuePair<XYZ, XYZ>); double bd = 1e9; foreach (var e in endList) { double dd = ctr.DistanceTo(e.Key); if (dd < bd) { bd = dd; bestE = e; } }
        if (bd * M > 250) continue; double mn = 1e9; foreach (Edge ed in so.Edges) { var cu = ed.AsCurve(); foreach (int q in new[] { 0, 1 }) mn = Math.Min(mn, (cu.GetEndPoint(q) - bestE.Key).DotProduct(bestE.Value)); }
        int bk = (int)Math.Round(mn * M); hist[bk] = hist.ContainsKey(bk) ? hist[bk] + 1 : 1;
    }
    sb.AppendLine("(2b) min axial coordinate a (mm from nearest tube end, + = outside) of insert/tab solids near ends: " + string.Join(", ", hist.OrderBy(q => q.Key).Select(q => q.Key + ":" + q.Value)));
    return sb.ToString();
}
static void _end() {