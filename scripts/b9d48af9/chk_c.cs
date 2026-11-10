var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\chk_c.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; string r;
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt")); r = C(nd); }
  catch (Exception ex) { r = "ERR " + ex; }
  System.IO.File.WriteAllText(log, r, System.Text.Encoding.UTF8); };
uiapp.Idling += hnd;
return "queued";
}
static string Pt(XYZ p) { return "(" + Math.Round(p.X / MM, 1) + "," + Math.Round(p.Y / MM, 1) + "," + Math.Round(p.Z / MM, 1) + ")"; }
static void BB(Solid s, out XYZ mn, out XYZ mx) { var bb = s.GetBoundingBox(); double x0 = 1e18, y0 = 1e18, z0 = 1e18, x1 = -1e18, y1 = -1e18, z1 = -1e18;
    foreach (var cx in new[] { bb.Min.X, bb.Max.X }) foreach (var cy in new[] { bb.Min.Y, bb.Max.Y }) foreach (var cz in new[] { bb.Min.Z, bb.Max.Z }) { var p = bb.Transform.OfPoint(new XYZ(cx, cy, cz)); x0 = Math.Min(x0, p.X); y0 = Math.Min(y0, p.Y); z0 = Math.Min(z0, p.Z); x1 = Math.Max(x1, p.X); y1 = Math.Max(y1, p.Y); z1 = Math.Max(z1, p.Z); }
    mn = new XYZ(x0, y0, z0); mx = new XYZ(x1, y1, z1); }
static string C(Document nd)
{
    var sb = new System.Text.StringBuilder();
    var dss = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел").ToList();
    sb.AppendLine("== names of 'Узел' DS (normalised) x count");
    foreach (var g in dss.Where(d => d.Category.Id.Value == (long)BuiltInCategory.OST_StructConnections && d.Name.StartsWith("Узел")).GroupBy(d => System.Text.RegularExpressions.Regex.Replace(d.Name, @"к колонне.*|\d{3,}.*", "")).OrderBy(g => g.Key)) sb.AppendLine("  " + g.Key + " x" + g.Count());
    // gusset thickness at column nodes: smallest bbox dimension of plate solids in 'Узел Р1' / 'Узел СВ1' DS by level
    sb.AppendLine("== gusset thickness (smallest bbox side of the biggest-area solid), per DS name and level");
    var th = new Dictionary<string, int>();
    foreach (var ds in dss.Where(d => d.Category.Id.Value == (long)BuiltInCategory.OST_StructConnections && d.Name.StartsWith("Узел") && d.Name.Contains("фасонка")))
    { var sol = Solids(ds); Solid best = null; double ba = -1; foreach (var s in sol) { double v = s.Volume; if (v > ba) { ba = v; best = s; } } if (best == null) continue; XYZ a, b; BB(best, out a, out b);
      // gusset: use volume / projected area proxy → thickness ≈ smallest face-pair distance: take min over planar faces pairs by solid volume / max planar face area
      double amax = 0; foreach (Face f in best.Faces) if (f is PlanarFace) amax = Math.Max(amax, f.Area); double t = best.Volume / amax / MM; var c = (a + b) / 2;
      string key = System.Text.RegularExpressions.Regex.Replace(ds.Name, @"\d{3,}.*", "") + " | level " + (Math.Abs(c.Z / MM - 5020) < 900 ? "+5.020" : Math.Abs(c.Z / MM - 10340) < 900 ? "+10.340" : c.Z / MM < 1500 ? "base" : "other") + " | t≈" + Math.Round(t * 2) / 2;
      th[key] = (th.ContainsKey(key) ? th[key] : 0) + 1; }
    foreach (var kv in th.OrderBy(k => k.Key)) sb.AppendLine("  " + kv.Key + " x" + kv.Value);
    // node 9
    sb.AppendLine("== node 9: КН tip vs БМ1 end stiffeners / bolts");
    var kn = new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => (x.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "").StartsWith("КН")).ToList();
    double dB = 1e9, dS = 1e9, dB24 = 1e9, dKNedge = 1e9; string exB = "", exS = "", exK = ""; int nk = 0;
    foreach (var f in kn)
    { var bb = f.get_BoundingBox(null); var lc = ((LocationCurve)f.Location).Curve; double x = lc.GetEndPoint(0).X / MM; double y0 = lc.GetEndPoint(0).Y / MM, y1 = lc.GetEndPoint(1).Y / MM; double sy = y1 > y0 ? 1 : -1; double tip = sy > 0 ? bb.Max.Y / MM : bb.Min.Y / MM; double yAxisRow = Math.Round(y0 / 3000) * 3000;
      // find DS "Узел 9 КН x r" bolts and plates near: use bbox filter on DS elements
      foreach (var ds in dss.Where(d => d.Name.Contains("КН") && d.Name.StartsWith("Болт Узел") || d.Name.StartsWith("Узел 9 КН")))
      { var db = ds.get_BoundingBox(null); if (db == null) continue; if (db.Min.X / MM > x + 200 || db.Max.X / MM < x - 200) continue; double lo = Math.Min(y0, y1) - 5, hi = Math.Max(y0, y1) + 5; if (db.Min.Y / MM > hi || db.Max.Y / MM < lo) continue;
        foreach (var s in Solids(ds)) { XYZ a, b; BB(s, out a, out b);
          if (ds.Category.Id.Value == (long)BuiltInCategory.OST_StructConnectionBolts) { CylindricalFace cf = null; foreach (Face fc in s.Faces) { cf = fc as CylindricalFace; if (cf != null) break; } if (cf == null) continue; if (Math.Abs(cf.Axis.Z) < 0.9) continue; double r = cf.get_Radius(0).GetLength() / MM; if (r > 12.5 && r < 16) continue;
            double yb = cf.Origin.Y / MM; double d = sy * (tip - yb) - 18.5; if (d < dB) { dB = d; exB = "КН x" + x + " tip y" + Math.Round(tip, 1) + " bolt y" + Math.Round(yb, 1) + " x" + Math.Round(cf.Origin.X / MM, 1); } }
          else if (ds.Category.Id.Value == (long)BuiltInCategory.OST_StructConnections) { double ymax = sy > 0 ? b.Y / MM : -a.Y / MM; double zmid = (a.Z + b.Z) / 2 / MM; if (zmid > 10345 && (b.Z - a.Z) / MM > 500 && (b.X - a.X) / MM < 22) { double d = sy * tip - (sy > 0 ? b.Y / MM : -a.Y / MM); if (d < dS) { dS = d; exS = "КН x" + x + " tip " + Math.Round(tip, 1) + " БМ1 end stiffener y.." + Math.Round(sy > 0 ? b.Y / MM : a.Y / MM, 1); } } } }
      }
      nk++; }
    sb.AppendLine("  consoles " + nk + "; min (tip - M20/M24 bolt axis - washer r18.5): " + Math.Round(dB, 1) + " " + exB + "; min (tip - БМ1 end stiffener end): " + Math.Round(dS, 1) + " " + exS);
    // node 5: head plates flush with the post top
    sb.AppendLine("== node 5 СФ: head plates −16 vs post top");
    var sf = new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => (x.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "").StartsWith("СФ ") || (x.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "") == "СФ").ToList();
    int np = 0; var dz = new List<double>(); var cnt = new Dictionary<int, int>(); string exn = "";
    foreach (var ds in dss.Where(d => d.Name.StartsWith("Узел 5 СФ")))
    { var sol = Solids(ds).Where(s => { XYZ a, b; BB(s, out a, out b); return Math.Abs((b.Z - a.Z) / MM - 16) < 0.5; }).ToList(); int n = sol.Count; cnt[n] = (cnt.ContainsKey(n) ? cnt[n] : 0) + 1;
      var bbx = ds.get_BoundingBox(null); var c = (bbx.Min + bbx.Max) / 2;
      foreach (var s in sol) { XYZ a, b; BB(s, out a, out b); var p = sf.FirstOrDefault(f => { var fb = f.get_BoundingBox(null); return fb != null && fb.Min.X <= (a.X + b.X) / 2 && fb.Max.X >= (a.X + b.X) / 2 && fb.Min.Y <= (a.Y + b.Y) / 2 && fb.Max.Y >= (a.Y + b.Y) / 2; });
        if (p != null) { double top = p.get_BoundingBox(null).Max.Z; dz.Add((top - b.Z) / MM); if (Math.Abs((top - b.Z) / MM) > 0.6 && exn.Length < 300) exn += " [" + ds.Name + " plate top " + Math.Round(b.Z / MM, 2) + " post top " + Math.Round(top / MM, 2) + "]"; } } np += n; }
    sb.AppendLine("  plates −16 " + np + "; plates per node: " + string.Join(", ", cnt.Select(kv => kv.Key + "→" + kv.Value)) + "; post top − plate top: min " + (dz.Count > 0 ? Math.Round(dz.Min(), 2) : 0) + " max " + (dz.Count > 0 ? Math.Round(dz.Max(), 2) : 0) + exn);
    return sb.ToString();
}