// READ-ONLY bolt geometry check (checker). Run with -Lib b109_lib.cs.
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\chk_bolts.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; string r;
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt")); r = BoltChk(nd); }
  catch (Exception ex) { r = "ERR " + ex; }
  System.IO.File.WriteAllText(log, r, System.Text.Encoding.UTF8); };
uiapp.Idling += hnd;
return "queued";
}

class Sp { public Element El; public string Name; public int Kind; public Solid S; public XYZ Mn, Mx; }
class Bc { public Element El; public string Name; public Solid S; public XYZ Mn, Mx; public bool Cyl; public XYZ Ax, Org; public double R, Len, T0, T1; }
static void BB(Solid s, out XYZ mn, out XYZ mx) { var bb = s.GetBoundingBox(); double x0 = 1e18, y0 = 1e18, z0 = 1e18, x1 = -1e18, y1 = -1e18, z1 = -1e18;
    foreach (var cx in new[] { bb.Min.X, bb.Max.X }) foreach (var cy in new[] { bb.Min.Y, bb.Max.Y }) foreach (var cz in new[] { bb.Min.Z, bb.Max.Z }) { var p = bb.Transform.OfPoint(new XYZ(cx, cy, cz)); x0 = Math.Min(x0, p.X); y0 = Math.Min(y0, p.Y); z0 = Math.Min(z0, p.Z); x1 = Math.Max(x1, p.X); y1 = Math.Max(y1, p.Y); z1 = Math.Max(z1, p.Z); }
    mn = new XYZ(x0, y0, z0); mx = new XYZ(x1, y1, z1); }
static string Norm(string s) { return System.Text.RegularExpressions.Regex.Replace(s ?? "", @"-?\d+(\.\d+)?", "#"); }
static string Pt(XYZ p) { return "(" + Math.Round(p.X / MM) + "," + Math.Round(p.Y / MM) + "," + Math.Round(p.Z / MM) + ")"; }

static string BoltChk(Document nd)
{
    var sb = new System.Text.StringBuilder(); double CELL = 800 * MM;
    var dss = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел").ToList();
    var others = new List<Sp>(); var bcs = new List<Bc>();
    foreach (var ds in dss)
    {
        string nm = ds.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? ds.Name; long cid = ds.Category.Id.Value;
        bool bolt = cid == (long)BuiltInCategory.OST_StructConnectionBolts, weld = cid == (long)BuiltInCategory.OST_StructConnectionWelds;
        foreach (var s in Solids(ds))
        {
            XYZ mn, mx; BB(s, out mn, out mx);
            if (!bolt) { others.Add(new Sp { El = ds, Name = nm, Kind = weld ? 1 : 0, S = s, Mn = mn, Mx = mx }); continue; }
            var b = new Bc { El = ds, Name = nm, S = s, Mn = mn, Mx = mx };
            foreach (Face f in s.Faces) { var cf = f as CylindricalFace; if (cf == null) continue; b.Cyl = true; b.Ax = cf.Axis.Normalize(); b.Org = cf.Origin; b.R = cf.get_Radius(0).GetLength() / MM; break; }
            if (b.Cyl) { double t0 = 1e18, t1 = -1e18; foreach (Edge ed in s.Edges) { var c = ed.AsCurve(); foreach (var q in new[] { c.GetEndPoint(0), c.GetEndPoint(1) }) { double t = (q - b.Org).DotProduct(b.Ax); t0 = Math.Min(t0, t); t1 = Math.Max(t1, t); } } b.T0 = t0; b.T1 = t1; b.Len = (t1 - t0) / MM; }
            bcs.Add(b);
        }
    }
    foreach (var el in new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Symbol.Family.Name.StartsWith("(КМ)")))
    { string nm = el.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? el.Name;
      foreach (var s in Solids(el)) { XYZ mn, mx; BB(s, out mn, out mx); others.Add(new Sp { El = el, Name = nm, Kind = 2, S = s, Mn = mn, Mx = mx }); } }
    sb.AppendLine("DS " + dss.Count + ", bolt solids " + bcs.Count + ", others " + others.Count);
    var grid = new Dictionary<long, List<int>>();
    Func<int, int, int, long> K = (i, j, k) => ((long)(i + 5000) * 20000 + (j + 5000)) * 20000 + (k + 5000);
    for (int n = 0; n < others.Count; n++) { var o = others[n];
        for (int i = (int)Math.Floor(o.Mn.X / CELL); i <= (int)Math.Floor(o.Mx.X / CELL); i++) for (int j = (int)Math.Floor(o.Mn.Y / CELL); j <= (int)Math.Floor(o.Mx.Y / CELL); j++) for (int k = (int)Math.Floor(o.Mn.Z / CELL); k <= (int)Math.Floor(o.Mx.Z / CELL); k++)
        { List<int> l; long key = K(i, j, k); if (!grid.TryGetValue(key, out l)) { l = new List<int>(); grid[key] = l; } l.Add(n); } }
    Func<XYZ, XYZ, List<int>> Cand = (mn, mx) => { var hs = new HashSet<int>();
        for (int i = (int)Math.Floor(mn.X / CELL); i <= (int)Math.Floor(mx.X / CELL); i++) for (int j = (int)Math.Floor(mn.Y / CELL); j <= (int)Math.Floor(mx.Y / CELL); j++) for (int k = (int)Math.Floor(mn.Z / CELL); k <= (int)Math.Floor(mx.Z / CELL); k++)
        { List<int> l; if (grid.TryGetValue(K(i, j, k), out l)) foreach (var q in l) hs.Add(q); } return hs.ToList(); };
    var shanks = bcs.Where(b => b.Cyl && b.Len >= 20).ToList();
    sb.AppendLine("== 1. shank diameters by site (name pattern, dia -> count)");
    foreach (var g in shanks.GroupBy(b => Norm(b.Name) + " |Ø" + Math.Round(b.R * 2, 1)).OrderBy(g => g.Key)) sb.AppendLine("  " + g.Key + "  x" + g.Count());
    sb.AppendLine("  other cyl (washers etc.): " + string.Join(", ", bcs.Where(b => b.Cyl && b.Len < 20).GroupBy(b => Math.Round(b.R * 2, 1) + "/t" + Math.Round(b.Len, 1)).Select(g => "Ø" + g.Key + " x" + g.Count())));
    sb.AppendLine("  non-cyl (heads/nuts): " + bcs.Count(b => !b.Cyl));
    sb.AppendLine("== 1b. СВ1/СВ2/СВ3 tube ends: bolt diameters within 450 of the end");
    var sv = new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Symbol.Family.Name.StartsWith("(КМ)") && x.Location is LocationCurve && (x.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "").StartsWith("СВ")).ToList();
    int ends = 0, no24 = 0, mixed = 0; var bad = new List<string>(); var dcount = new Dictionary<string, int>();
    foreach (var f in sv)
    { var c = ((LocationCurve)f.Location).Curve; string mk = (f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "").Split(' ')[0];
      for (int k = 0; k < 2; k++)
      { var pe = c.GetEndPoint(k); var po = c.GetEndPoint(1 - k); var u = (pe - po).Normalize(); ends++;
        var near = shanks.Where(b => { var m = b.Org + b.Ax * ((b.T0 + b.T1) / 2); double along = (m - pe).DotProduct(u); var perp = (m - pe) - u * along; return along < 20 * MM && along > -450 * MM && perp.GetLength() < 110 * MM; }).ToList();
        var ds2 = near.Select(b => Math.Round(b.R * 2)).Distinct().OrderBy(x => x).ToList();
        string ks = mk + ":" + string.Join("/", ds2); dcount[ks] = (dcount.ContainsKey(ks) ? dcount[ks] : 0) + 1;
        if (!ds2.Contains(24)) { no24++; if (bad.Count < 8) bad.Add(mk + " end " + Pt(pe) + " dias " + string.Join("/", ds2)); }
        else if (ds2.Any(x => x != 24)) { mixed++; if (bad.Count < 8) bad.Add("MIXED " + mk + " end " + Pt(pe) + " dias " + string.Join("/", ds2)); } } }
    sb.AppendLine("  ends " + ends + ", without Ø24 " + no24 + ", mixed " + mixed + "; " + string.Join("; ", dcount.Select(kv => kv.Key + " x" + kv.Value)));
    foreach (var x in bad) sb.AppendLine("   " + x);
    sb.AppendLine("== 2. M24 edge distance (axis to boundary of the pierced plate face), per site");
    var m24 = shanks.Where(b => Math.Abs(b.R * 2 - 24) < 0.6).ToList(); sb.AppendLine("  M24 shanks " + m24.Count);
    var edge = new Dictionary<string, List<Tuple<double, string>>>(); int nPierce = 0, noPierce = 0;
    foreach (var b in m24)
    {
        var p0 = b.Org + b.Ax * b.T0; var p1 = b.Org + b.Ax * b.T1; var line = Line.CreateBound(p0 - b.Ax * 5 * MM, p1 + b.Ax * 5 * MM);
        XYZ mn = new XYZ(Math.Min(p0.X, p1.X) - 30 * MM, Math.Min(p0.Y, p1.Y) - 30 * MM, Math.Min(p0.Z, p1.Z) - 30 * MM), mx = new XYZ(Math.Max(p0.X, p1.X) + 30 * MM, Math.Max(p0.Y, p1.Y) + 30 * MM, Math.Max(p0.Z, p1.Z) + 30 * MM);
        bool any = false;
        foreach (var ci in Cand(mn, mx))
        { var o = others[ci]; if (o.Kind != 0) continue;
          foreach (Face f in o.S.Faces) { var pf = f as PlanarFace; if (pf == null || Math.Abs(pf.FaceNormal.DotProduct(b.Ax)) < 0.999) continue;
            IntersectionResultArray ira; SetComparisonResult r; try { r = pf.Intersect(line, out ira); } catch { continue; }
            if (r != SetComparisonResult.Overlap || ira == null || ira.Size == 0) continue; var pt = ira.get_Item(0).XYZPoint;
            double md = 1e18; foreach (EdgeArray ea in pf.EdgeLoops) foreach (Edge ed in ea) { var pr = ed.AsCurve().Project(pt); if (pr != null) md = Math.Min(md, pr.Distance); }
            md /= MM; any = true; string key = Norm(o.Name) + " [" + Norm(b.Name) + "]"; List<Tuple<double, string>> l; if (!edge.TryGetValue(key, out l)) { l = new List<Tuple<double, string>>(); edge[key] = l; }
            l.Add(Tuple.Create(md, "bolt@" + Pt(pt) + " ds#" + o.El.Id.Value)); } }
        if (any) nPierce++; else noPierce++;
    }
    sb.AppendLine("  shanks piercing >=1 plate face " + nPierce + ", none " + noPierce);
    foreach (var kv in edge.OrderBy(k => k.Key)) { var mi = kv.Value.OrderBy(t => t.Item1).First(); int lt = kv.Value.Count(t => t.Item1 < 35.5); sb.AppendLine("  " + kv.Key + ": n=" + kv.Value.Count + " min " + Math.Round(mi.Item1, 1) + " (" + mi.Item2 + "), <36: " + lt); }
    sb.AppendLine("  -- all <35.5:");
    foreach (var kv in edge.OrderBy(k => k.Key)) foreach (var t in kv.Value.Where(t => t.Item1 < 35.5).OrderBy(t => t.Item1).Take(4)) sb.AppendLine("   " + Math.Round(t.Item1, 1) + "  " + kv.Key + " " + t.Item2);
    sb.AppendLine("== 3. bolt solids intersecting plates / welds / frame (volume mm3 > 1)");
    var hit = new Dictionary<string, int>(); var ex = new Dictionary<string, string>(); int tested = 0;
    foreach (var b in bcs)
    {
        bool isShank = b.Cyl && b.Len >= 20; string part = isShank ? "shank" : (b.Cyl ? "washer" : "head/nut");
        foreach (var ci in Cand(b.Mn, b.Mx))
        { var o = others[ci];
          if (isShank && o.Kind != 1) continue;
          if (o.Mx.X < b.Mn.X || o.Mn.X > b.Mx.X || o.Mx.Y < b.Mn.Y || o.Mn.Y > b.Mx.Y || o.Mx.Z < b.Mn.Z || o.Mn.Z > b.Mx.Z) continue;
          tested++; double v = 0; try { var x = BooleanOperationsUtils.ExecuteBooleanOperation(b.S, o.S, BooleanOperationsType.Intersect); if (x != null) v = x.Volume; } catch { }
          double mm3 = v / (MM * MM * MM); if (mm3 < 1) continue;
          string kind = o.Kind == 0 ? "plate" : o.Kind == 1 ? "weld" : "frame"; string key = part + " ∩ " + kind + " " + Norm(o.Name) + " [" + Norm(b.Name) + "]";
          hit[key] = (hit.ContainsKey(key) ? hit[key] : 0) + 1; if (!ex.ContainsKey(key)) ex[key] = Math.Round(mm3) + " mm3 at " + Pt((b.Mn + b.Mx) / 2) + " Ø" + Math.Round(b.R * 2, 1) + " ds#" + b.El.Id.Value + "/" + o.El.Id.Value; }
    }
    sb.AppendLine("  boolean tests " + tested + ", hit groups " + hit.Count);
    foreach (var kv in hit.OrderBy(k => k.Key)) sb.AppendLine("  " + kv.Value + " x " + kv.Key + "   e.g. " + ex[kv.Key]);
    return sb.ToString();
}