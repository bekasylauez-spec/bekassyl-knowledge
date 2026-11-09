// READ-ONLY node signature query (checker). Run WITHOUT -Lib.
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\q_nodes_ro.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; string r;
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt")); r = Q(nd); }
  catch (Exception ex) { r = "ERR " + ex; }
  System.IO.File.WriteAllText(log, r, System.Text.Encoding.UTF8); };
uiapp.Idling += hnd;
return "queued";
}

static double Sn(double y) { double yy = y <= 30000 ? y : 60000 - y; return 14490 + 750.0 / 29705.5 * (yy - 294.5); }
static string Q(Document nd)
{
    const double M = 304.8; var sb = new System.Text.StringBuilder(); var opt = new Options { DetailLevel = ViewDetailLevel.Fine };
    var all = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел").ToList();
    var bolts = new Dictionary<string, int>(); var welds = new Dictionary<string, int>();
    foreach (var d in all) { string n = d.Name ?? ""; var cat = d.Category.Id.Value;
        if (cat == (long)BuiltInCategory.OST_StructConnectionBolts) { int c = 0; foreach (var go in d.get_Geometry(opt)) if (go is Solid) c++; bolts[n.StartsWith("Болт ") ? n.Substring(5) : n] = c; }
        else if (cat == (long)BuiltInCategory.OST_StructConnectionWelds) { int c = 0; foreach (var go in d.get_Geometry(opt)) if (go is Solid) c++; welds[n.StartsWith("шов ") ? n.Substring(4) : n] = c; } }
    var plates = all.Where(d => d.Category.Id.Value == (long)BuiltInCategory.OST_StructConnections).ToList();
    sb.AppendLine("DS total " + all.Count + ", plate DS " + plates.Count + ", bolt DS " + bolts.Count + ", weld DS " + welds.Count);
    var hist = new Dictionary<string, List<string>>();
    Func<Solid, double> thick = so => { double af = 0; foreach (Face f in so.Faces) if (f is PlanarFace) af = Math.Max(af, f.Area); return af > 0 ? so.Volume / af * M : 0; };
    int capBad = 0; var capList = new List<string>();
    var gsTop = new Dictionary<int, int>(); var svBand = new Dictionary<int, int>();
    foreach (var d in plates)
    {
        string n = d.Name ?? ""; string pre = null; string key = null;
        string[] tk = n.Split(' ');
        if (n.StartsWith("Узел 20Ш1 шарнир к колонне")) { pre = "ФФ1-шарнир row " + tk[tk.Length - 2]; }
        else if (n.StartsWith("Узел 40Б1 жёсткий к колонне") || n.StartsWith("Узел 30Б1 жёсткий к колонне")) { pre = tk[1] + " жёсткий row " + tk[tk.Length - 2] + (tk[tk.Length - 3] == "0" || tk[tk.Length - 3] == "162000" ? " ось1/28" : ""); }
        else if (n.StartsWith("Оголовок К ")) { pre = n.Contains("связь") ? "Оголовок связь (ребро под оголовком)" : "Оголовок К"; }
        else if (n.StartsWith("Узел 9 КН")) { pre = "Узел 9 КН"; }
        else if (n.StartsWith("Пр1 опора")) { pre = "Пр1 опора"; }
        else if (n.StartsWith("Узел ГС1")) pre = "Узел ГС1";
        else if (n.StartsWith("Узел СВ1")) pre = "Узел СВ1";
        else if (n.StartsWith("Узел СВ2")) pre = "Узел СВ2";
        else if (n.StartsWith("Узел СВ3")) pre = "Узел СВ3";
        else if (n.StartsWith("Узел Р1")) pre = "Узел Р1";
        else if (n.StartsWith("Узел 5")) pre = "Узел 5 (plates)";
        if (pre == null) continue;
        var ts = new List<double>(); var sols = new List<Solid>();
        foreach (var go in d.get_Geometry(opt)) { var so = go as Solid; if (so == null || so.Volume < 1e-12) continue; sols.Add(so); ts.Add(Math.Round(thick(so) * 2) / 2); }
        if (pre == "Оголовок К")
        {
            double x = double.Parse(tk[2]); string r = tk[3]; double want = (r == "E" || r == "H" || x == 0 || x == 162000) ? 16 : 14;
            double got = ts.Count > 0 ? ts.Max() : 0; if (Math.Abs(got - want) > 0.6) { capBad++; if (capList.Count < 6) capList.Add(d.Id.Value + " " + n + " t=" + got + " want " + want); }
            key = "t=" + got; if (!hist.ContainsKey(pre)) hist[pre] = new List<string>(); hist[pre].Add(key + "§" + d.Id.Value + " " + n); continue;
        }
        var ord = ts.OrderBy(v => v).ToList(); key = string.Join(",", ord);
        int nb = 0; bolts.TryGetValue(n, out nb); int nw = 0; welds.TryGetValue(n, out nw);
        if (pre.StartsWith("ФФ1") || pre.Contains("жёсткий") || pre == "Узел 9 КН" || pre == "Пр1 опора" || pre.StartsWith("Оголовок связь")) key += " | болтов " + (nb / 5.0) + " | швов-тел " + (nw > 0 ? "есть" : "НЕТ");
        else if (pre.StartsWith("Узел ГС1") || pre.StartsWith("Узел СВ") || pre == "Узел Р1") { key = string.Join(",", ord.GroupBy(v => v).OrderBy(g => g.Key).Select(g => g.Key + "x" + g.Count())) + " | болтов " + (nb / 5.0); }
        if (!hist.ContainsKey(pre)) hist[pre] = new List<string>(); hist[pre].Add(key + "§" + d.Id.Value + " " + n);
        if (pre == "Узел ГС1")
            foreach (var so in sols) { if (Math.Abs(thick(so) - 10) > 0.6) continue; var bb = so.GetBoundingBox(); var a = bb.Transform.OfPoint(bb.Min); var b = bb.Transform.OfPoint(bb.Max); double zt = Math.Max(a.Z, b.Z) * M, yc = (a.Y + b.Y) / 2 * M;
                if (Math.Abs(Math.Max(a.X, b.X) - Math.Min(a.X, b.X)) * M > 20 && Math.Abs(Math.Max(a.Y, b.Y) - Math.Min(a.Y, b.Y)) * M > 20) { int k = (int)Math.Round(zt - Sn(yc)); gsTop[k] = gsTop.ContainsKey(k) ? gsTop[k] + 1 : 1; } }
        if (pre == "Узел СВ2" || pre == "Узел СВ3")
            foreach (var so in sols) { if (Math.Abs(thick(so) - 10) > 0.6) continue; var bb = so.GetBoundingBox(); var a = bb.Transform.OfPoint(bb.Min); var b = bb.Transform.OfPoint(bb.Max);
                double x0 = Math.Min(a.X, b.X) * M, x1 = Math.Max(a.X, b.X) * M; double ax = Math.Round((x0 + x1) / 2 / 6000) * 6000; if (Math.Abs((x0 + x1) / 2 - ax) < 30 && x1 - x0 < 30) { int dz = (int)(Math.Round((Math.Max(a.Z, b.Z) - Math.Min(a.Z, b.Z)) * M / 10) * 10); svBand[dz] = svBand.ContainsKey(dz) ? svBand[dz] + 1 : 1; } }
    }
    foreach (var kv in hist.OrderBy(k => k.Key))
    {
        sb.AppendLine("== " + kv.Key + " (groups " + kv.Value.Count + ")");
        foreach (var g in kv.Value.GroupBy(v => v.Split((char)167)[0]).OrderByDescending(g => g.Count()).Take(8))
            sb.AppendLine("   " + g.Count() + " x [" + g.Key + "]  e.g. " + g.First().Split((char)167)[1]);
    }
    sb.AppendLine("== cap thickness mismatches: " + capBad + " " + string.Join("; ", capList));
    sb.AppendLine("== GS1 gusset top Z minus beam-top(ztop) histogram mm: " + string.Join(", ", gsTop.OrderBy(k => k.Key).Select(k => k.Key + ":" + k.Value)));
    sb.AppendLine("== SV2/SV3 column-web gusset Z extent (mm) histogram: " + string.Join(", ", svBand.OrderBy(k => k.Key).Select(k => k.Key + ":" + k.Value)));
    return sb.ToString();
}
static void _end() {