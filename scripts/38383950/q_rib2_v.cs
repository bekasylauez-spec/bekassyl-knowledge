// READ-ONLY gusset coverage check (checker). Run WITHOUT -Lib.
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\q_rib2_v.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; string r;
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt")); r = Q(nd); }
  catch (Exception ex) { r = "ERR " + ex; }
  System.IO.File.WriteAllText(log, r, System.Text.Encoding.UTF8); };
uiapp.Idling += hnd;
return "queued";
}
const double M = 304.8;
class Pl { public long id; public string name; public double t; public XYZ n, o, e1, e2; public List<double[]> p2 = new List<double[]>(); public double x0, x1, y0, y1, z0, z1; public Solid so; }
static Pl MkPl(DirectShape d, Solid so)
{
    PlanarFace best = null; foreach (Face f in so.Faces) if (f is PlanarFace pf && (best == null || pf.Area > best.Area)) best = pf; if (best == null) return null;
    var r = new Pl { id = d.Id.Value, name = d.Name, so = so, t = so.Volume / best.Area * M, n = best.FaceNormal };
    var loops = best.GetEdgesAsCurveLoops(); var pts = new List<XYZ>();
    foreach (var cu in loops[0]) { var tz = cu.Tessellate(); for (int i = 0; i < tz.Count - 1; i++) pts.Add(tz[i]); }
    r.o = pts[0]; var z = Math.Abs(r.n.Z) < 0.9 ? XYZ.BasisZ : XYZ.BasisX; r.e1 = r.n.CrossProduct(z).Normalize(); r.e2 = r.n.CrossProduct(r.e1).Normalize();
    foreach (var p in pts) r.p2.Add(new[] { (p - r.o).DotProduct(r.e1), (p - r.o).DotProduct(r.e2) });
    var bb = so.GetBoundingBox(); var a = bb.Transform.OfPoint(bb.Min); var b = bb.Transform.OfPoint(bb.Max);
    r.x0 = Math.Min(a.X, b.X) * M; r.x1 = Math.Max(a.X, b.X) * M; r.y0 = Math.Min(a.Y, b.Y) * M; r.y1 = Math.Max(a.Y, b.Y) * M; r.z0 = Math.Min(a.Z, b.Z) * M; r.z1 = Math.Max(a.Z, b.Z) * M; return r;
}
static bool Pip(List<double[]> P, double x, double y) { bool c = false; for (int i = 0, j = P.Count - 1; i < P.Count; j = i++) if ((P[i][1] > y) != (P[j][1] > y) && x < (P[j][0] - P[i][0]) * (y - P[i][1]) / (P[j][1] - P[i][1]) + P[i][0]) c = !c; return c; }
static Pl Gsel(List<Pl> lst, string name) { var c = (name ?? "").Contains("ГС1") ? lst : lst.Where(p => Math.Abs(p.n.Z) < 0.5).ToList(); if (c.Count == 0) c = lst; return c.OrderByDescending(p => PolyA(p)).FirstOrDefault(); }
static double PolyA(Pl p) { double s = 0; for (int i = 0, j = p.p2.Count - 1; i < p.p2.Count; j = i++) s += p.p2[j][0] * p.p2[i][1] - p.p2[i][0] * p.p2[j][1]; return Math.Abs(s) / 2; }
static double EdgeD(List<double[]> P, double x, double y) { double m = 1e9; for (int i = 0, j = P.Count - 1; i < P.Count; j = i++) { double ax = P[j][0], ay = P[j][1], bx = P[i][0], by = P[i][1]; double dx = bx - ax, dy = by - ay, l2 = dx * dx + dy * dy; double t = l2 < 1e-12 ? 0 : Math.Max(0, Math.Min(1, ((x - ax) * dx + (y - ay) * dy) / l2)); m = Math.Min(m, Math.Sqrt((x - ax - t * dx) * (x - ax - t * dx) + (y - ay - t * dy) * (y - ay - t * dy))); } return m; }
class Tb2 { public XYZ a, b, u, e1, e2; public double len, hb, hb2; public string mk; public long id; }
static List<double[]> Hull2(List<double[]> pts) {
    var p = pts.OrderBy(q => q[0]).ThenBy(q => q[1]).ToList(); if (p.Count < 3) return p;
    Func<double[], double[], double[], double> cr = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
    var lo = new List<double[]>(); foreach (var q in p) { while (lo.Count >= 2 && cr(lo[lo.Count - 2], lo[lo.Count - 1], q) <= 0) lo.RemoveAt(lo.Count - 1); lo.Add(q); }
    var up = new List<double[]>(); foreach (var q in Enumerable.Reverse(p)) { while (up.Count >= 2 && cr(up[up.Count - 2], up[up.Count - 1], q) <= 0) up.RemoveAt(up.Count - 1); up.Add(q); }
    lo.RemoveAt(lo.Count - 1); up.RemoveAt(up.Count - 1); return lo.Concat(up).ToList(); }
static List<XYZ> Verts(Solid so) { var v = new List<XYZ>(); foreach (Edge ed in so.Edges) { var c = ed.AsCurve(); v.Add(c.GetEndPoint(0)); v.Add(c.GetEndPoint(1)); } return v; }
static string Q(Document nd)
{
    var sb = new System.Text.StringBuilder(); var opt = new Options { DetailLevel = ViewDetailLevel.Fine };
    Func<FamilyInstance, string> Cm = f => f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "";
    var tubes = new List<Tb2>(); var ends = new List<KeyValuePair<XYZ, XYZ>>(); var endMk = new List<string>(); var endTube = new List<long>();
    foreach (var f in new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Location is LocationCurve && x.Symbol.Family.Name.Contains("труба")))
    {
        var c = (f.Location as LocationCurve).Curve; var t = new Tb2 { mk = Cm(f), id = f.Id.Value }; t.a = c.GetEndPoint(0); t.b = c.GetEndPoint(1); t.len = t.a.DistanceTo(t.b); t.u = (t.b - t.a).Normalize();
        double bb = f.Symbol.LookupParameter("b").AsDouble(); var hp = f.Symbol.LookupParameter("h"); t.hb = bb / 2; t.hb2 = (hp != null && hp.AsDouble() > 0.01) ? hp.AsDouble() / 2 : bb / 2;
        var tr = f.GetTransform(); var cand = new[] { tr.BasisX, tr.BasisY, tr.BasisZ }.Where(v => Math.Abs(v.DotProduct(t.u)) < 0.2).ToList();
        if (cand.Count >= 2) { t.e1 = cand[0]; t.e2 = t.u.CrossProduct(cand[0]).Normalize(); } else { var z = Math.Abs(t.u.Z) > 0.9 ? XYZ.BasisX : XYZ.BasisZ; t.e1 = t.u.CrossProduct(z).Normalize(); t.e2 = t.u.CrossProduct(t.e1).Normalize(); }
        tubes.Add(t); string mk = t.mk.Split(' ')[0];
        if (mk == "СВ1" || mk == "СВ2" || mk == "СВ3" || mk == "ГС1" || mk == "Р1" || mk == "ВС1" || mk == "ВФ1") { ends.Add(new KeyValuePair<XYZ, XYZ>(t.a, -t.u)); endMk.Add(mk); endTube.Add(t.id); ends.Add(new KeyValuePair<XYZ, XYZ>(t.b, t.u)); endMk.Add(mk); endTube.Add(t.id); }
    }
    var plates = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел" && x.Category.Id.Value == (long)BuiltInCategory.OST_StructConnections && (x.Name ?? "").StartsWith("Узел ") && x.Name.Contains("вкладыши")).ToList();
    var ribsAt = new Dictionary<int, List<Pl>>(); var flatAt = new Dictionary<int, Pl>(); var perDs = new Dictionary<long, List<Pl>>(); var gOf = new Dictionary<long, Pl>(); var gus = new List<Pl>();
    foreach (var d in plates) { var lst = new List<Pl>(); foreach (var go in d.get_Geometry(opt)) { var so = go as Solid; if (so == null || so.Volume < 1e-12) continue; var p = MkPl(d, so); if (p != null) lst.Add(p); }
        perDs[d.Id.Value] = lst; var G = Gsel(lst, d.Name); if (G != null) { gOf[d.Id.Value] = G; gus.Add(G); } }
    sb.AppendLine("tube-node DS " + plates.Count + ", tube ends " + ends.Count);
    // associate ribs and flat plates with ends
    var depthH = new Dictionary<int, int>(); var amaxH = new Dictionary<int, int>(); int noRib = 0, multi = 0, wrongSide = 0, noFlat = 0, ribInTube = 0, ribBad = 0; var ex = new List<string>(); var ribOf = new Dictionary<int, Pl>(); var flatOf = new Dictionary<int, Pl>(); var gOfEnd = new Dictionary<int, Pl>();
    var cand2 = new List<Pl>(); var candFlat = new List<Pl>();
    foreach (var d in plates) { var G = gOf[d.Id.Value]; foreach (var p in perDs[d.Id.Value]) { if (object.ReferenceEquals(p, G) || Math.Abs(p.t - 8) > 0.6) continue; double dn = Math.Abs(p.n.DotProduct(G.n)); if (dn > 0.98) candFlat.Add(p); else if (dn < 0.1) cand2.Add(p); } }
    sb.AppendLine("flat -8 plates " + candFlat.Count + ", rib-like -8 plates (perpendicular) " + cand2.Count);
    var ribCount = new int[ends.Count]; var ribOfEnd = new Pl[ends.Count]; var flatOfEnd = new Pl[ends.Count]; var gOfEndArr = new Pl[ends.Count];
    foreach (var p in cand2)
    {
        var G = gOf[p.id]; var vs = Verts(p.so); var c = p.so.ComputeCentroid(); int best = -1; double bd = 1e9;
        for (int i = 0; i < ends.Count; i++)
        {
            var Pe = ends[i].Key; var U = ends[i].Value; if (c.DistanceTo(Pe) * M > 300) continue; if (Math.Abs(p.n.DotProduct(U)) > 0.15) continue;
            double amin = vs.Min(v => (v - Pe).DotProduct(U)) * M; if (Math.Abs(amin - 8) > 1.5) continue;
            var W = G.n.CrossProduct(U).Normalize(); double wl = Math.Abs((c - Pe).DotProduct(W)) * M; if (wl > 6) continue; double dd = c.DistanceTo(Pe); if (dd < bd) { bd = dd; best = i; }
        }
        if (best >= 0) { ribCount[best]++; ribOfEnd[best] = p; }
    }
    foreach (var p in candFlat)
    {
        var G = gOf[p.id]; var vs = Verts(p.so); var c = p.so.ComputeCentroid(); int best = -1; double bd = 1e9;
        for (int i = 0; i < ends.Count; i++) { var Pe = ends[i].Key; var U = ends[i].Value; if (c.DistanceTo(Pe) * M > 300) continue; double amin = vs.Min(v => (v - Pe).DotProduct(U)) * M; if (Math.Abs(amin - 8) > 1.5 && Math.Abs(amin - 8) > 40) continue; var W = G.n.CrossProduct(U).Normalize(); if (Math.Abs((c - Pe).DotProduct(W)) * M > 45) continue; double dd = c.DistanceTo(Pe); if (dd < bd) { bd = dd; best = i; } }
        if (best >= 0) { flatOfEnd[best] = p; gOfEndArr[best] = G; }
    }
    int okEnd = 0; var perMk = new Dictionary<string, int[]>();
    for (int i = 0; i < ends.Count; i++)
    {
        string mk = endMk[i]; if (!perMk.ContainsKey(mk)) perMk[mk] = new int[3]; perMk[mk][0]++;
        bool bad = false;
        if (ribCount[i] == 0) { noRib++; bad = true; if (ex.Count < 12) ex.Add("NO RIB end " + endTube[i] + " " + mk + " @" + Math.Round(ends[i].Key.X * M) + "," + Math.Round(ends[i].Key.Y * M) + "," + Math.Round(ends[i].Key.Z * M)); }
        else if (ribCount[i] > 1) { multi++; bad = true; if (ex.Count < 12) ex.Add("MULTI RIB(" + ribCount[i] + ") end " + endTube[i] + " " + mk); }
        if (flatOfEnd[i] == null) { noFlat++; bad = true; if (ex.Count < 12) ex.Add("NO FLAT end " + endTube[i] + " " + mk); }
        if (!bad)
        {
            var R = ribOfEnd[i]; var F = flatOfEnd[i]; var G = gOfEndArr[i]; var rc = R.so.ComputeCentroid(); var fc = F.so.ComputeCentroid(); var gc = G.so.ComputeCentroid();
            double sr = (rc - fc).DotProduct(G.n), sg = (gc - fc).DotProduct(G.n);
            if (sr * sg >= 0) { wrongSide++; bad = true; if (ex.Count < 12) ex.Add("RIB ON GUSSET SIDE end " + endTube[i] + " " + mk + " rib " + R.id); }
            var vs = Verts(R.so); double dep = (vs.Max(v => v.DotProduct(G.n)) - vs.Min(v => v.DotProduct(G.n))) * M; int bk = (int)(Math.Round(dep / 5) * 5); depthH[bk] = depthH.ContainsKey(bk) ? depthH[bk] + 1 : 1;
            double amx = vs.Max(v => (v - ends[i].Key).DotProduct(ends[i].Value)) * M; int ak = (int)(Math.Round(amx / 20) * 20); amaxH[ak] = amaxH.ContainsKey(ak) ? amaxH[ak] + 1 : 1;
            foreach (var t in tubes)
            {
                bool hit = false; foreach (var p in vs) { var r = p - t.a; double s = r.DotProduct(t.u); if (s <= 0.5 / M || s >= t.len - 0.5 / M) continue; if (t.mk.StartsWith("ФФ1") && (s < 150.5 / M || s > t.len - 150.5 / M)) continue;
                    if (Math.Abs(r.DotProduct(t.e1)) < t.hb - 1.0 / M && Math.Abs(r.DotProduct(t.e2)) < t.hb2 - 1.0 / M) { hit = true; break; } }
                if (hit) { ribInTube++; bad = true; if (ex.Count < 12) ex.Add("RIB INSIDE TUBE " + t.id + " " + t.mk + " rib " + R.id + " end " + endTube[i]); break; }
            }
        }
        if (bad) perMk[mk][1]++; else okEnd++;
    }
    sb.AppendLine("(1) ends " + ends.Count + ": OK " + okEnd + "; no rib " + noRib + ", >1 rib " + multi + ", no flat plate " + noFlat + ", rib on gusset side " + wrongSide + ", rib inside a tube " + ribInTube);
    sb.AppendLine("    per mark [ends, bad]: " + string.Join("; ", perMk.Select(kv => kv.Key + " " + kv.Value[0] + "/" + kv.Value[1])));
    sb.AppendLine("    rib depth (mm, 5-bins): " + string.Join(", ", depthH.OrderBy(q => q.Key).Select(q => q.Key + ":" + q.Value)) + "; rib far end a (mm, 20-bins): " + string.Join(", ", amaxH.OrderBy(q => q.Key).Select(q => q.Key + ":" + q.Value)));
    foreach (var s in ex) sb.AppendLine("    " + s);
    // (2) bolts
    var allRibsByDs = new Dictionary<long, List<Pl>>(); foreach (var p in cand2) { if (!allRibsByDs.ContainsKey(p.id)) allRibsByDs[p.id] = new List<Pl>(); allRibsByDs[p.id].Add(p); }
    var flatsByDs = new Dictionary<long, List<Pl>>(); foreach (var p in candFlat) { if (!flatsByDs.ContainsKey(p.id)) flatsByDs[p.id] = new List<Pl>(); flatsByDs[p.id].Add(p); }
    int nb = 0, noG = 0, noF = 0, tooEdgeG = 0, tooEdgeF = 0, nearRib = 0; double minEg = 1e9, minEf = 1e9, minRib = 1e9; var zbad = new Dictionary<string, int>(); var bex = new List<string>(); var perEnd = new Dictionary<int, int>(); var ribH = new Dictionary<int, int>();
    foreach (var d in new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел" && x.Category.Id.Value == (long)BuiltInCategory.OST_StructConnectionBolts && (x.Name ?? "").StartsWith("Болт М16 (")))
        foreach (var go in d.get_Geometry(opt))
        {
            var so = go as Solid; if (so == null || Math.Abs(so.Volume * M * M * M - 9045) > 60) continue; nb++; var c = so.ComputeCentroid();
            Pl bestG = null; double bestPd = 1e9; double gx = 0, gy = 0;
            foreach (var G in gus) { if (c.X * M < G.x0 - 150 || c.X * M > G.x1 + 150 || c.Y * M < G.y0 - 150 || c.Y * M > G.y1 + 150 || c.Z * M < G.z0 - 150 || c.Z * M > G.z1 + 150) continue;
                double pd = Math.Abs((c - G.o).DotProduct(G.n)) * M; if (pd > 40) continue; double x = (c - G.o).DotProduct(G.e1), y = (c - G.o).DotProduct(G.e2); if (!Pip(G.p2, x, y)) continue; if (pd < bestPd) { bestPd = pd; bestG = G; gx = x; gy = y; } }
            if (bestG == null) { noG++; if (bex.Count < 10) bex.Add("BOLT outside gusset @" + Math.Round(c.X * M) + "," + Math.Round(c.Y * M) + "," + Math.Round(c.Z * M)); continue; }
            double eg = EdgeD(bestG.p2, gx, gy) * M; minEg = Math.Min(minEg, eg); if (eg < 25 - 0.5) { tooEdgeG++; if (bex.Count < 10) bex.Add("BOLT gusset edge " + Math.Round(eg, 1) + " @" + Math.Round(c.X * M) + "," + Math.Round(c.Y * M) + "," + Math.Round(c.Z * M)); }
            // flat plate in the same DS containing the point
            Pl bestF = null; double ef = 0; List<double[]> fpoly = null;
            List<Pl> fl; if (flatsByDs.TryGetValue(bestG.id, out fl)) foreach (var F in fl)
            { var fp = new List<double[]>(); foreach (var q in F.p2) { var p3 = F.o + F.e1 * q[0] + F.e2 * q[1]; fp.Add(new[] { (p3 - bestG.o).DotProduct(bestG.e1), (p3 - bestG.o).DotProduct(bestG.e2) }); }
              if (Pip(fp, gx, gy)) { bestF = F; fpoly = fp; ef = EdgeD(fp, gx, gy) * M; break; } }
            if (bestF == null) { noF++; if (bex.Count < 10) bex.Add("BOLT outside flat plate @" + Math.Round(c.X * M) + "," + Math.Round(c.Y * M) + "," + Math.Round(c.Z * M)); continue; }
            minEf = Math.Min(minEf, ef); if (ef < 25 - 0.5) { int zl = (int)(Math.Round(c.Z * M / 100) * 100); string kz = "z" + zl + " dz" + (int)Math.Round(ef / 5) * 5; zbad[kz] = zbad.ContainsKey(kz) ? zbad[kz] + 1 : 1; tooEdgeF++; if (bex.Count < 10) bex.Add("BOLT flat-plate edge " + Math.Round(ef, 1) + " @" + Math.Round(c.X * M) + "," + Math.Round(c.Y * M) + "," + Math.Round(c.Z * M)); }
            // rib clearance: shank axis to rib face
            List<Pl> rl; double md = 1e9; if (allRibsByDs.TryGetValue(bestG.id, out rl)) foreach (var R in rl)
            { var pts = new List<double[]>(); foreach (var v in Verts(R.so)) pts.Add(new[] { (v - bestG.o).DotProduct(bestG.e1), (v - bestG.o).DotProduct(bestG.e2) }); var h = Hull2(pts); double dd = h.Count >= 3 ? (Pip(h, gx, gy) ? 0 : EdgeD(h, gx, gy)) : 1e9; if (h.Count < 3) { foreach (var q in pts) md = Math.Min(md, Math.Sqrt((q[0] - gx) * (q[0] - gx) + (q[1] - gy) * (q[1] - gy)) * M); } else md = Math.Min(md, dd * M); }
            minRib = Math.Min(minRib, md); int rk = (int)Math.Floor(md / 5) * 5; ribH[rk] = ribH.ContainsKey(rk) ? ribH[rk] + 1 : 1; if (md - 8 < 12 - 0.5) { nearRib++; if (bex.Count < 10) bex.Add("BOLT too close to rib: axis-to-rib-face " + Math.Round(md, 1) + " @" + Math.Round(c.X * M) + "," + Math.Round(c.Y * M) + "," + Math.Round(c.Z * M)); }
            // per-end count
            int be = -1; double bdd = 1e9; for (int i = 0; i < ends.Count; i++) { var Pe = ends[i].Key; var U = ends[i].Value; var r = c - Pe; double a = r.DotProduct(U) * M; if (a < 0 || a > 320) continue; var lat = r - U * r.DotProduct(U); double l = lat.GetLength() * M; if (l < bdd) { bdd = l; be = i; } }
            if (be >= 0) perEnd[be] = perEnd.ContainsKey(be) ? perEnd[be] + 1 : 1;
        }
    sb.AppendLine("(2) bolt shafts " + nb + ": outside gusset " + noG + ", outside flat plate " + noF + ", gusset edge <25: " + tooEdgeG + ", flat-plate edge <25: " + tooEdgeF + ", shank-to-rib clearance <12: " + nearRib);
    sb.AppendLine("    min edge to gusset " + Math.Round(minEg, 1) + ", min edge to flat plate " + Math.Round(minEf, 1) + ", min axis-to-rib-face " + Math.Round(minRib, 1) + " (shank-radius clearance = this-8); axis-to-rib-face hist (5 mm bins): " + string.Join(", ", ribH.OrderBy(q => q.Key).Select(q => q.Key + ":" + q.Value)));
    int e2 = 0, eo = 0; for (int i = 0; i < ends.Count; i++) { int k; if (perEnd.TryGetValue(i, out k) && k == 2) e2++; else eo++; }
    sb.AppendLine("    ends with exactly 2 bolts (nearest-axis assignment) " + e2 + ", other " + eo);
    sb.AppendLine("    bad flat-edge bolts by level/edge: " + string.Join("; ", zbad.OrderBy(q => q.Key).Select(q => q.Key + " x" + q.Value)));
    foreach (var s in bex) sb.AppendLine("    " + s);
    return sb.ToString();
}
static void _end() {