// READ-ONLY gusset coverage check (checker). Run WITHOUT -Lib.
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\q_col_w.txt";
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
static double BoxGap(Pl a, Pl b) { double dx = Math.Max(0, Math.Max(a.x0 - b.x1, b.x0 - a.x1)), dy = Math.Max(0, Math.Max(a.y0 - b.y1, b.y0 - a.y1)), dz = Math.Max(0, Math.Max(a.z0 - b.z1, b.z0 - a.z1)); return Math.Sqrt(dx * dx + dy * dy + dz * dz); }
static string Q(Document nd)
{
    var sb = new System.Text.StringBuilder(); var opt = new Options { DetailLevel = ViewDetailLevel.Fine };
    double[] RY = { 0, 24000, 36000, 60000 }; string[] RL = { "A", "E", "H", "M" };
    var plates = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел" && x.Category.Id.Value == (long)BuiltInCategory.OST_StructConnections).ToList();
    var gusAll = new List<Pl>(); var tubeDs = new Dictionary<long, List<Pl>>(); var cand = new List<KeyValuePair<DirectShape, Pl>>(); var colPl = new Dictionary<string, List<Pl>>();
    foreach (var d in plates)
    {
        string n = d.Name ?? ""; bool tubeNode = n.StartsWith("Узел ") && n.Contains("вкладыши"); bool capDs = n.StartsWith("Оголовок К "); bool colNode = n.Contains(" к колонне ");
        if (!(tubeNode || n.StartsWith("Узел 9") || n.StartsWith("Площадка") || capDs || colNode || n.StartsWith("Узел ГС1"))) continue;
        var lst = new List<Pl>(); foreach (var go in d.get_Geometry(opt)) { var so = go as Solid; if (so == null || so.Volume < 1e-12) continue; var p = MkPl(d, so); if (p != null) lst.Add(p); }
        if (tubeNode) { tubeDs[d.Id.Value] = lst; var G = Gsel(lst, d.Name); if (G != null) gusAll.Add(G); }
        foreach (var p in lst) { cand.Add(new KeyValuePair<DirectShape, Pl>(d, p));
            if (colNode || capDs) { string key = null; var tk = n.Split(' '); if (colNode) key = tk[tk.Length - 3] + " " + tk[tk.Length - 2]; else if (capDs) key = tk[2] + " " + tk[3]; if (key != null) { if (!colPl.ContainsKey(key)) colPl[key] = new List<Pl>(); colPl[key].Add(p); } } }
    }
    // (1) column stiffeners: horizontal plates inside a column footprint, grouped by column / side / level
    var groups = new Dictionary<string, List<Pl>>(); int nPl = 0;
    foreach (var kv in cand)
    {
        var d = kv.Key; var p = kv.Value; string n = d.Name ?? ""; if (n.StartsWith("Оголовок") || n.StartsWith("Узел ГС1")) continue; if (Math.Abs(p.n.Z) < 0.98 || p.t < 7 || p.t > 21) continue;
        double axx = Math.Round((p.x0 + p.x1) / 2 / 6000) * 6000; if (p.x0 < axx - 152 || p.x1 > axx + 152) continue; int ri = -1; for (int i = 0; i < 4; i++) if (p.y0 >= RY[i] - 262 && p.y1 <= RY[i] + 262) ri = i; if (ri < 0) continue;
        if ((p.x1 - p.x0) < 30 || (p.y1 - p.y0) < 20) continue; if (p.x1 - p.x0 > 160) continue; // stiffener halves are ≈142 wide
        int side = ((p.x0 + p.x1) / 2 > axx) ? 1 : -1; string key = (long)axx + " " + RL[ri] + " s" + side + " z" + Math.Round((p.z0 + p.z1) / 2); if (!groups.ContainsKey(key)) groups[key] = new List<Pl>(); groups[key].Add(p); nPl++;
    }
    int dupGroups = 0; var dupEx = new List<string>(); foreach (var g in groups) { var L2 = g.Value; for (int a = 0; a < L2.Count; a++) for (int b = a + 1; b < L2.Count; b++) if (Math.Abs(L2[a].y0 - L2[b].y0) < 0.5 && Math.Abs(L2[a].y1 - L2[b].y1) < 0.5) { dupGroups++; if (dupEx.Count < 5) dupEx.Add(g.Key); a = L2.Count; break; } }
    sb.AppendLine("(1b) duplicated identical stiffener plates: groups " + dupGroups + " " + string.Join("; ", dupEx));
    var split = groups.Where(g => g.Value.Count > 1).ToList();
    var lvH = new Dictionary<string, int>(); int unslotted = 0; var ex = new List<string>(); int slotsChecked = 0, slotNoGus = 0;
    foreach (var g in split)
    {
        double zc = g.Value.Average(p => (p.z0 + p.z1) / 2); string lv = zc > 10000 && zc < 10400 ? "КН top +10.340" : "z" + Math.Round(zc / 100) * 100; lvH[lv] = lvH.ContainsKey(lv) ? lvH[lv] + 1 : 1;
        var k = g.Key.Split(' '); double ax = double.Parse(k[0]); int ri = Array.IndexOf(RL, k[1]); int side = k[2] == "s1" ? 1 : -1;
        var ord = g.Value.OrderBy(p => p.y0).ToList();
        if (!(zc > 10300 && zc < 10360)) { unslotted++; if (ex.Count < 10) ex.Add("SPLIT outside КН top: " + g.Key + " pieces " + g.Value.Count + " ids " + string.Join(",", g.Value.Select(p => p.id))); continue; }
        for (int j = 0; j + 1 < ord.Count; j++)
        {
            double gy0 = ord[j].y1, gy1 = ord[j + 1].y0; if (gy1 - gy0 < 1) continue; slotsChecked++; bool found = false;
            foreach (var G in gusAll) { if (Math.Abs(G.n.Y) < 0.98) continue; if (G.z0 > zc + 1 || G.z1 < zc - 1) continue; double gxa = Math.Min(G.x0, G.x1), gxb = Math.Max(G.x0, G.x1); if (side > 0) { if (gxb < ax + 20 || gxa > ax + 150) continue; } else { if (gxa > ax - 20 || gxb < ax - 150) continue; }
                if (G.y1 < gy0 - 0.6 || G.y0 > gy1 + 0.6) continue; if (Math.Abs(G.y0 - RY[ri]) > 40 && Math.Abs(G.y1 - RY[ri]) > 40) continue; found = true; break; }
            if (!found) { slotNoGus++; if (ex.Count < 10) ex.Add("SLOT WITHOUT GUSSET " + g.Key + " gap y " + Math.Round(gy0) + ".." + Math.Round(gy1)); }
        }
    }
    sb.AppendLine("(1) column stiffener plates found " + nPl + " in " + groups.Count + " (column, side, level) groups; groups with >1 piece (split): " + split.Count + " by level: " + string.Join(", ", lvH.Select(q => q.Key + " x" + q.Value)));
    sb.AppendLine("    split outside КН top (+10.340): " + unslotted + "; slots checked " + slotsChecked + ", slots with no gusset through them: " + slotNoGus);
    // also: КН top stiffeners that are whole although a row-plane gusset passes at that level would clash (clash 0), report counts of whole vs split at +10.340
    int kt = groups.Count(g => g.Value.Average(p => (p.z0 + p.z1) / 2) > 10300 && g.Value.Average(p => (p.z0 + p.z1) / 2) < 10360); sb.AppendLine("    КН top-level groups " + kt + " (split " + split.Count(g => { double z = g.Value.Average(p => (p.z0 + p.z1) / 2); return z > 10300 && z < 10360; }) + ")");
    foreach (var s in ex) sb.AppendLine("    " + s);
    var lenH = new Dictionary<int, int>(); foreach (var g in groups) foreach (var p in g.Value) { int lk = (int)(Math.Round((p.y1 - p.y0) / 50) * 50); lenH[lk] = lenH.ContainsKey(lk) ? lenH[lk] + 1 : 1; }
    sb.AppendLine("    stiffener piece length along y (mm, 50-bins): " + string.Join(", ", lenH.OrderBy(q => q.Key).Select(q => q.Key + ":" + q.Value)));
    // (2) ГС1 gussets with t=8 (over columns)
    var g8 = gusAll.Where(G => { var d = (DirectShape)nd.GetElement(new ElementId(G.id)); return d.Name.StartsWith("Узел ГС1") && Math.Abs(G.t - 8) < 0.7; }).ToList();
    sb.AppendLine("(2) ГС1 gussets t=8: " + g8.Count + "; ГС1 gussets t=10: " + gusAll.Count(G => ((DirectShape)nd.GetElement(new ElementId(G.id))).Name.StartsWith("Узел ГС1") && Math.Abs(G.t - 10) < 0.7));
    var area = new List<double>(); double minGap = 1e9; var gapBy = new Dictionary<string, double>(); int touch = 0; var gex = new List<string>(); var rowOff = new Dictionary<string, int>();
    foreach (var G in g8)
    {
        area.Add(PolyA(G) * M * M); double cx = (G.x0 + G.x1) / 2, cy = (G.y0 + G.y1) / 2; double ax = Math.Round(cx / 6000) * 6000; int ri = 0; double bdr = 1e9; for (int i = 0; i < 4; i++) if (Math.Abs(cy - RY[i]) < bdr) { bdr = Math.Abs(cy - RY[i]); ri = i; }
        string key = (long)ax + " " + RL[ri]; double off = Math.Min(Math.Abs(G.y0 - RY[ri]), Math.Abs(G.y1 - RY[ri])); string ok = "dy " + Math.Round(off / 50) * 50; rowOff[ok] = rowOff.ContainsKey(ok) ? rowOff[ok] + 1 : 1;
        List<Pl> neigh; if (!colPl.TryGetValue(key, out neigh)) continue;
        foreach (var p in neigh) { double gp = BoxGap(G, p); if (gp < minGap) minGap = gp; string nm = p.name.Contains("Оголовок") ? "cap" : p.name.Contains("шарнир") ? "ФФ1 node" : p.name.Contains("жёсткий") ? "БП node" : "other"; if (!gapBy.ContainsKey(nm) || gp < gapBy[nm]) gapBy[nm] = gp; if (gp < 0.5) { touch++; if (gex.Count < 8) gex.Add("bbox touch " + G.id + " with " + p.id + " " + p.name + " t=" + Math.Round(p.t, 1)); } }
    }
    sb.AppendLine("    gusset polygon area mm2: min " + Math.Round(area.Min()) + ", max " + Math.Round(area.Max()) + ", avg " + Math.Round(area.Average()) + "; bbox dims of first 3: " + string.Join(" | ", g8.Take(3).Select(G => Math.Round(G.x1 - G.x0) + "x" + Math.Round(G.y1 - G.y0) + "x" + Math.Round(G.z1 - G.z0))));
    sb.AppendLine("    min bbox gap to column-node plates/cap: " + Math.Round(minGap, 1) + " mm; by kind: " + string.Join(", ", gapBy.Select(q => q.Key + " " + Math.Round(q.Value, 1))) + "; gusset y-distance from row axis (nearest edge, 50-bins): " + string.Join(", ", rowOff.OrderBy(q => q.Key).Select(q => q.Key + ":" + q.Value)) + "; bbox-touching pairs " + touch);
    foreach (var s in gex) sb.AppendLine("    " + s);
    return sb.ToString();
}
static void _end() {