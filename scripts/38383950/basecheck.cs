// READ-ONLY base check (checker's own script)
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\basecheck.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; string r;
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt")); r = Chk(nd); }
  catch (Exception ex) { r = "ERR " + ex; }
  System.IO.File.WriteAllText(log, r, System.Text.Encoding.UTF8); };
uiapp.Idling += hnd;
return "queued";
}

class SB { public Solid S; public double x0, y0, z0, x1, y1, z1, vol; }
static List<SB> Sol(Element el)
{
    const double M = 304.8; var res = new List<SB>(); var opt = new Options { DetailLevel = ViewDetailLevel.Fine };
    foreach (var go in el.get_Geometry(opt)) { IEnumerable<GeometryObject> objs = go is GeometryInstance gi ? gi.GetInstanceGeometry().Cast<GeometryObject>() : new[] { go };
        foreach (var s in objs.OfType<Solid>().Where(x => x.Volume > 1e-9)) { var bb = s.GetBoundingBox(); var a = bb.Transform.OfPoint(bb.Min); var b = bb.Transform.OfPoint(bb.Max);
            res.Add(new SB { S = s, x0 = Math.Min(a.X, b.X) * M, y0 = Math.Min(a.Y, b.Y) * M, z0 = Math.Min(a.Z, b.Z) * M, x1 = Math.Max(a.X, b.X) * M, y1 = Math.Max(a.Y, b.Y) * M, z1 = Math.Max(a.Z, b.Z) * M, vol = s.Volume * M * M * M }); } }
    return res;
}
static string Chk(Document nd)
{
    const double M = 304.8; var sb = new System.Text.StringBuilder();
    var cols = new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Symbol.Family.Name.StartsWith("(КМ)") && x.Location is LocationPoint && x.Category.Id.Value == (long)BuiltInCategory.OST_StructuralColumns).ToList();
    var DSs = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел").ToList();
    var baseDS = DSs.Where(x => x.ApplicationDataId == "база").Select(x => new { E = x, B = x.get_BoundingBox(null) }).Where(x => x.B != null).ToList();
    var nodeDS = DSs.Where(x => x.ApplicationDataId != "база").Select(x => new { E = x, B = x.get_BoundingBox(null) }).Where(x => x.B != null).ToList();
    var stats = new Dictionary<string, List<string>>(); var fails = new List<string>();
    foreach (var c in cols)
    {
        string blk = c.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? ""; string mk = blk.Split(' ')[0];
        var lp = ((LocationPoint)c.Location).Point; double cx = lp.X * M, cy = lp.Y * M;
        var cs = Sol(c); double cz0 = cs.Min(x => x.z0), cz1 = cs.Max(x => x.z1), cX0 = cs.Min(x => x.x0), cX1 = cs.Max(x => x.x1), cY0 = cs.Min(x => x.y0), cY1 = cs.Max(x => x.y1);
        string id = c.Id.Value + " " + blk + " @" + Math.Round(cx) + "," + Math.Round(cy);
        var mine = baseDS.Where(b => Math.Abs((b.B.Min.X + b.B.Max.X) / 2 * M - cx) < 40 && Math.Abs((b.B.Min.Y + b.B.Max.Y) / 2 * M - cy) < 40).ToList();
        var pDS = mine.Where(b => b.E.Name.StartsWith("База")).ToList(); var bDS = mine.Where(b => b.E.Name.StartsWith("Фундаментный")).ToList(); var wDS = mine.Where(b => b.E.Name.StartsWith("шов")).ToList();
        if (pDS.Count != 1 || bDS.Count != 1 || wDS.Count != 1) { fails.Add(id + " DS plate/bolt/weld = " + pDS.Count + "/" + bDS.Count + "/" + wDS.Count); continue; }
        string nm = pDS[0].E.Name.Substring(5, 2);
        var ps = Sol(pDS[0].E); var plate = ps.OrderByDescending(x => x.vol).First();
        var bs = Sol(bDS[0].E); var ws = Sol(wDS[0].E);
        double top = plate.z1;
        var errs = new List<string>();
        if (Math.Abs(plate.z0 - (-400)) > 0.5) errs.Add("plate bottom " + Math.Round(plate.z0, 1));
        if (Math.Abs(cz0 - top) > 0.5) errs.Add("col bottom " + Math.Round(cz0, 1) + " vs plate top " + Math.Round(top, 1));
        if (cX0 < plate.x0 - 0.5 || cX1 > plate.x1 + 0.5 || cY0 < plate.y0 - 0.5 || cY1 > plate.y1 + 0.5) errs.Add("column footprint outside plate");
        if (Math.Abs((plate.x0 + plate.x1) / 2 - cx) > 1 || Math.Abs((plate.y0 + plate.y1) / 2 - cy) > 1) errs.Add("plate not centred on column");
        int wash = ps.Count(x => Math.Abs(x.z0 - top) < 0.5 && Math.Abs((x.z1 - x.z0) - 20) < 0.5 && Math.Abs((x.x1 - x.x0) - (x.y1 - x.y0)) < 0.5 && (x.x1 - x.x0) < 130);
        int ribs = ps.Count - 1 - wash;
        int rods = bs.Count(x => (x.z1 - x.z0) > 800); int nuts = bs.Count - rods;
        int wcp = ws.Count(x => Math.Abs(x.z0 - top) < 1.5 && x.x0 >= cX0 - 14 && x.x1 <= cX1 + 14 && x.y0 >= cY0 - 14 && x.y1 <= cY1 + 14);
        int wAnch = ws.Count(x => Math.Abs(x.z0 - top) < 1.5 && Math.Abs((x.z1 - x.z0)) < 10 && (x.x1 - x.x0) < 130 && (x.y1 - x.y0) < 130 && !(x.x0 >= cX0 - 14 && x.x1 <= cX1 + 14 && x.y0 >= cY0 - 14 && x.y1 <= cY1 + 14));
        string key = nm + " " + mk;
        string sig = "plate " + Math.Round(plate.x1 - plate.x0) + "x" + Math.Round(plate.y1 - plate.y0) + "x" + Math.Round(plate.z1 - plate.z0) + " topZ " + Math.Round(top) + " | washers " + wash + " ribs " + ribs + " | rods " + rods + " nuts " + nuts + " | welds all " + ws.Count + " col-plate " + wcp + " anchor-welds " + wAnch;
        if (wash != 4) errs.Add("washers " + wash); if (rods != 4) errs.Add("rods " + rods); if (nuts != 12) errs.Add("nuts " + nuts);
        if (ws.Count == 0 || wcp == 0) errs.Add("no col-plate welds");
        string cov = "";
        if (mk == "К3" || mk == "СФ1")
        {
            int tot = 0, miss = 0; var gaps = new List<string>();
            Action<double, double> Pt = (px, py) => { tot++; bool hit = ws.Any(x => px >= x.x0 - 1.5 && px <= x.x1 + 1.5 && py >= x.y0 - 1.5 && py <= x.y1 + 1.5 && x.z0 < top + 12 && x.z1 > top + 1) || ps.Any(x => x != plate && x.z0 <= top + 1 && px >= x.x0 - 1.5 && px <= x.x1 + 1.5 && py >= x.y0 - 1.5 && py <= x.y1 + 1.5);
                if (!hit) { miss++; if (gaps.Count < 4) gaps.Add(Math.Round(px - cx) + "," + Math.Round(py - cy)); } };
            double ox = 5; for (double t = cX0; t <= cX1; t += 10) { Pt(t, cY0 - ox); Pt(t, cY1 + ox); } for (double t = cY0; t <= cY1; t += 10) { Pt(cX0 - ox, t); Pt(cX1 + ox, t); }
            cov = (tot - miss) + "/" + tot + (miss > 0 ? " gaps " + string.Join(";", gaps) : "");
            if (miss > 0) errs.Add("perimeter weld gaps " + miss + "/" + tot);
        }
        string topc = "";
        if (mk == "К3" || mk == "СФ1") { double zt = cz1; int near = nodeDS.Count(n => n.B.Min.Z * M <= zt + 5 && n.B.Max.Z * M >= zt - 5 && cx >= n.B.Min.X * M - 5 && cx <= n.B.Max.X * M + 5 && cy >= n.B.Min.Y * M - 5 && cy <= n.B.Max.Y * M + 5); topc = " topZ " + Math.Round(cz1) + " nodeDS at top " + near; }
        if (!stats.ContainsKey(key)) stats[key] = new List<string>();
        stats[key].Add(sig + (cov != "" ? " | perim " + cov : "") + topc + " || " + id + (errs.Count > 0 ? " ERR: " + string.Join("; ", errs) : ""));
        if (errs.Count > 0) fails.Add(nm + " " + id + ": " + string.Join("; ", errs));
    }
    sb.AppendLine("columns " + cols.Count + ", baseDS " + baseDS.Count);
    foreach (var kv in stats.OrderBy(k => k.Key))
    {
        sb.AppendLine("== " + kv.Key + " n=" + kv.Value.Count);
        foreach (var g in kv.Value.GroupBy(v => v.Substring(0, v.IndexOf(" || ")))) sb.AppendLine("   x" + g.Count() + " " + g.Key + "   e.g. " + g.First().Substring(g.First().IndexOf(" || ") + 4));
    }
    sb.AppendLine("FAILS " + fails.Count); foreach (var f in fails.Take(40)) sb.AppendLine("  " + f);
    return sb.ToString();
}
static void _end() {