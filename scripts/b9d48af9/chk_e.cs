var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\chk_e.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; string r;
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt")); r = D(nd); }
  catch (Exception ex) { r = "ERR " + ex; }
  System.IO.File.WriteAllText(log, r, System.Text.Encoding.UTF8); };
uiapp.Idling += hnd;
return "queued";
}
class Sp { public Element El; public string Name; public int Kind; public Solid S; public XYZ Mn, Mx; }
static void BB(Solid s, out XYZ mn, out XYZ mx) { var bb = s.GetBoundingBox(); double x0 = 1e18, y0 = 1e18, z0 = 1e18, x1 = -1e18, y1 = -1e18, z1 = -1e18;
    foreach (var cx in new[] { bb.Min.X, bb.Max.X }) foreach (var cy in new[] { bb.Min.Y, bb.Max.Y }) foreach (var cz in new[] { bb.Min.Z, bb.Max.Z }) { var p = bb.Transform.OfPoint(new XYZ(cx, cy, cz)); x0 = Math.Min(x0, p.X); y0 = Math.Min(y0, p.Y); z0 = Math.Min(z0, p.Z); x1 = Math.Max(x1, p.X); y1 = Math.Max(y1, p.Y); z1 = Math.Max(z1, p.Z); }
    mn = new XYZ(x0, y0, z0); mx = new XYZ(x1, y1, z1); }
static string Pt(XYZ p) { return "(" + Math.Round(p.X / MM) + "," + Math.Round(p.Y / MM) + "," + Math.Round(p.Z / MM) + ")"; }
static List<double[]> Seg(Solid s, XYZ a, XYZ b) { var r = new List<double[]>(); try { var res = s.IntersectWithCurve(Line.CreateBound(a, b), new SolidCurveIntersectionOptions()); if (res == null) return r;
    for (int i = 0; i < res.SegmentCount; i++) { var c = res.GetCurveSegment(i); r.Add(new[] { c.GetEndPoint(0).X / MM, c.GetEndPoint(1).X / MM, c.GetEndPoint(0).Z / MM, c.GetEndPoint(1).Z / MM }); } } catch { } return r; }
static string D(Document nd)
{
    var sb = new System.Text.StringBuilder(); double CELL = 800 * MM;
    var dss = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел").ToList();
    var all = new List<Sp>();
    foreach (var ds in dss) { string nm = ds.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? ds.Name; long cid = ds.Category.Id.Value; int kd = cid == (long)BuiltInCategory.OST_StructConnectionBolts ? 3 : cid == (long)BuiltInCategory.OST_StructConnectionWelds ? 1 : 0;
        foreach (var s in Solids(ds)) { XYZ a, b; BB(s, out a, out b); all.Add(new Sp { El = ds, Name = nm, Kind = kd, S = s, Mn = a, Mx = b }); } }
    var fr = new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Symbol.Family.Name.StartsWith("(КМ)")).ToList();
    Func<FamilyInstance, string> Cm = f => f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "";
    foreach (var f in fr) foreach (var s in Solids(f)) { XYZ a, b; BB(s, out a, out b); all.Add(new Sp { El = f, Name = Cm(f), Kind = 2, S = s, Mn = a, Mx = b }); }
    // ---- Р1 gaps along the top wall
    sb.AppendLine("== Р1 top-wall continuity (line along the member, z = top wall middle, y = axis)");
    var r1 = fr.Where(f => Cm(f) == "Р1" && f.Location is LocationCurve).ToList(); int nGap = 0, nOther = 0; var gaps = new List<string>(); var lens = new List<double>(); var slotPos = new List<double[]>();
    foreach (var f in r1)
    {
        var c = ((LocationCurve)f.Location).Curve; var a = c.GetEndPoint(0); var b = c.GetEndPoint(1); double bb = f.Symbol.LookupParameter("b").AsDouble(), tt = f.Symbol.LookupParameter("t").AsDouble();
        double zo = bb / 2 - tt / 2; var oa = new XYZ(a.X, a.Y + 9 * MM, a.Z + zo); var ob = new XYZ(b.X, b.Y + 9 * MM, b.Z + zo); var u = (ob - oa).Normalize(); oa = oa - u * 100 * MM; ob = ob + u * 100 * MM;
        var segs = new List<double[]>(); foreach (var s in Solids(f)) segs.AddRange(Seg(s, oa, ob));
        var iv = segs.Select(q => new[] { Math.Min(q[0], q[1]), Math.Max(q[0], q[1]) }).OrderBy(q => q[0]).ToList();
        for (int i = 0; i + 1 < iv.Count; i++) { double g = iv[i + 1][0] - iv[i][1]; if (g > 0.5) { nGap++; lens.Add(g); slotPos.Add(new[] { (iv[i][1] + iv[i + 1][0]) / 2, a.Y / MM + 9, a.Z / MM, g }); gaps.Add("Р1 id" + f.Id.Value + " y" + Math.Round(a.Y / MM) + " z" + Math.Round(a.Z / MM) + " gap x " + Math.Round(iv[i][1]) + ".." + Math.Round(iv[i + 1][0]) + " = " + Math.Round(g, 1)); } }
        if (iv.Count == 0) nOther++;
    }
    sb.AppendLine("  Р1 members " + r1.Count + ", top-wall gaps " + nGap + " (lengths " + string.Join(",", lens.Select(x => Math.Round(x, 1)).Distinct()) + "), members with no hit " + nOther);
    foreach (var g in gaps.Take(20)) sb.AppendLine("   " + g);
    // ---- gusset through each slot
    sb.AppendLine("== node 6 gusset at slots");
    var cand = all.Where(p => p.Kind == 0 && p.Name.StartsWith("Узел СВ1")).ToList();
    foreach (var sp in slotPos.Take(100))
    {
        double sx = sp[0], sy = sp[1], sz = sp[2];
        var gs = cand.Where(p => p.Mn.X / MM < sx && p.Mx.X / MM > sx && p.Mn.Y / MM < sy + 12 && p.Mx.Y / MM > sy - 12 && p.Mn.Z / MM < sz + 150 && p.Mx.Z / MM > sz - 150).ToList();
        // gusset extent at the Р1 top-wall height: line along X at y, z = top wall middle
        double zt = sz + 47.5; var oa = new XYZ((sx - 400) * MM, sy * MM, zt * MM); var ob = new XYZ((sx + 400) * MM, sy * MM, zt * MM);
        var gseg = new List<double[]>(); foreach (var g in gs) foreach (var q in Seg(g.S, oa, ob)) gseg.Add(new[] { Math.Min(q[0], q[1]), Math.Max(q[0], q[1]) });
        string gi = gseg.Count == 0 ? "no gusset at top-wall height" : "gusset x " + Math.Round(gseg.Min(q => q[0])) + ".." + Math.Round(gseg.Max(q => q[1]));
        // slot x range
        var rr = r1.First(f => { var c = ((LocationCurve)f.Location).Curve; return Math.Abs(c.GetEndPoint(0).Y / MM + 9 - sy) < 1 && Math.Abs(c.GetEndPoint(0).Z / MM - sz) < 1 && Math.Min(c.GetEndPoint(0).X, c.GetEndPoint(1).X) / MM < sx && Math.Max(c.GetEndPoint(0).X, c.GetEndPoint(1).X) / MM > sx; });
        double sl0 = sx - sp[3] / 2, sl1 = sx + sp[3] / 2;
        string ex = gseg.Count == 0 ? "" : " ; slot-gusset margin lo " + Math.Round(gseg.Min(q => q[0]) - sl0, 1) + " hi " + Math.Round(sl1 - gseg.Max(q => q[1]), 1);
        // gusset solids: count, bbox, thickness
        var one = gs.Where(g => (g.Mx.Z - g.Mn.Z) / MM > 150).ToList();
        string gd = string.Join("; ", one.Select(g => "#" + g.El.Id.Value + " bbox " + Pt(g.Mn) + ".." + Pt(g.Mx) + " vol " + Math.Round(g.S.Volume / (MM * MM * MM))));
        sb.AppendLine("  slot x " + Math.Round(sl0, 1) + ".." + Math.Round(sl1, 1) + " (" + Math.Round(sp[3], 1) + ") y" + Math.Round(sy) + " ; " + gi + ex + " ; big gusset solids " + one.Count + ": " + gd);
        // welds on the gusset faces around the Р1 top / bottom
        var ws = all.Where(p => p.Kind == 1 && p.Name.StartsWith("шов узел СВ1") && p.Mn.X / MM < sx + 300 && p.Mx.X / MM > sx - 300 && p.Mn.Y / MM < sy + 20 && p.Mx.Y / MM > sy - 20 && p.Mn.Z / MM < sz + 80 && p.Mx.Z / MM > sz - 80).ToList();
        int wt = ws.Count(w => w.Mn.Z / MM > sz + 30), wbt = ws.Count(w => w.Mx.Z / MM < sz - 30), wyp = ws.Count(w => (w.Mn.Y + w.Mx.Y) / 2 / MM > sy), wym = ws.Count(w => (w.Mn.Y + w.Mx.Y) / 2 / MM < sy);
        sb.AppendLine("     welds near " + ws.Count + ": top " + wt + ", bottom " + wbt + ", +y face " + wyp + ", -y face " + wym);
    }
    // ---- Р1 ends vs column axes
    sb.AppendLine("== Р1 end distance from column axis (mm) / cap outer face");
    var dist = new Dictionary<string, int>();
    foreach (var f in r1) { var c = ((LocationCurve)f.Location).Curve; double e0 = f.get_Parameter(BuiltInParameter.START_EXTENSION)?.AsDouble() ?? 0, e1 = f.get_Parameter(BuiltInParameter.END_EXTENSION)?.AsDouble() ?? 0;
        for (int k = 0; k < 2; k++) { var u = (c.GetEndPoint(k) - c.GetEndPoint(1 - k)).Normalize(); var pe = c.GetEndPoint(k) + u * (k == 0 ? e0 : e1); double x = pe.X / MM; double d = Math.Abs(x - Math.Round(x / 6000) * 6000); string key = Math.Round(d, 1).ToString(); dist[key] = (dist.ContainsKey(key) ? dist[key] : 0) + 1; } }
    sb.AppendLine("  " + string.Join("; ", dist.OrderBy(k => k.Key).Select(k => k.Key + " x" + k.Value)));
    return sb.ToString();
}