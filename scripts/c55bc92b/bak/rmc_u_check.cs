// РМЦ КМ: узелдер 1…4 параметрленген ТЕКСЕРІСІ — тек оқиды (модельге ештеңе жазбайды). ЖАЗЫЛҒАН 13.11.2026, Revit-те ІСКЕ ҚОСЫЛМАҒАН.
// Іске қосу: go.ps1 -Name rmc_u_check -Lib rmc_node_lib.cs. Узел нөмірі — төмендегі NODE тұрақтысы (0 = моделде бар барлық «узел 1…4»; 1…4 = біреуі; уақытша көшірмеде ауыстыруға болады).
// Нәтиже: _авто\uzel_check_<NODE|all>.txt және қайтарылатын мәтін. Бөліктер: 1) паспорт бөлшектері: саны + bbox өлшемдері (солидтен), тесік саны; 2) clash (көлем > 50 мм³): өз бөлшектері, каркас (ВП стержені бөлек), көрші узелдер/базалар;
// 3) шов кемінде екі бөлшекке тие ме (bbox саңылауы ≤ 1 мм). Өлшем — солидтің нақты геометриясынан, комментарий мәтінінен емес.
return RunCheck(document);
}
const int NODE = 0;

class It { public string key, loc, kind, name; public Solid s; public double[] bb; public int idx; }
class Exp { public int node; public string match; public int n; public List<double[]> alts = new List<double[]>(); public double tol; public int holes; public double holeDia; }
static Exp E(int node, string match, int n, double tol, params double[][] alts) { var e = new Exp { node = node, match = match, n = n, tol = tol }; e.alts.AddRange(alts); return e; }
static double[] D3(double a, double b, double c) { var q = new[] { a, b, c }; Array.Sort(q); return q; }
static string KindOf(string nm) {
    return nm.Contains(" шов ") ? "шов" : nm.Contains("стержень") ? "стержень" : nm.Contains("бастиек") ? "бастиек" : nm.Contains("гайка") ? "гайка" : nm.Contains("шайба") ? "шайба" : "бөлшек"; }
// тесік саны: Ø dia радиустағы дөңгелек қырлардың бірегей осьтері (ось сызығы бойынша жиналады)
static int HoleCount(Solid s, double dia) {
    var keys = new HashSet<string>();
    foreach (Edge e in s.Edges) { var a = e.AsCurve() as Arc; if (a == null) continue; if (Math.Abs(a.Radius / MM * 2 - dia) > 0.2) continue;
        XYZ n = a.Normal; if (n.X < -1e-6 || (Math.Abs(n.X) <= 1e-6 && (n.Y < -1e-6 || (Math.Abs(n.Y) <= 1e-6 && n.Z < 0)))) n = n.Negate();
        XYZ p = a.Center - n * a.Center.DotProduct(n); keys.Add(F(n.X) + "," + F(n.Y) + "," + F(n.Z) + "|" + F(p.X / MM) + "," + F(p.Y / MM) + "," + F(p.Z / MM)); }
    return keys.Count; }

static double SL2 = 0.0318;
static double ZL(double y) { return 9293 - SL2 * Math.Abs(y - 18000); }
static double ZS(double y) { return 9318 - SL2 * Math.Abs(y - 18000); }
static double ZTOP(double y) { return 9868 - 0.05 * Math.Abs(y - 18000); }
static double ZSB(double y) { return 8968 + 0.05 * y - 450; }
static double ZS3(double y) { return 9143 + 175.0 / 5500.0 * (y - 12500); }

static List<Exp> Expected(int node, string loc, int ax)
{
    var L = new List<Exp>(); double[] bolt = D3(24, 24, 90), head = D3(15, 36, 41.57), nut = D3(19, 36, 41.57), wash = D3(4, 44, 44);
    if (node == 1)
    {
        var o = E(1, "оголовок", 1, 0.3, D3(25, 320, 684)); o.holes = 6; o.holeDia = 27; L.Add(o);
        L.Add(E(1, "кронштейн", 1, 0.3, D3(10, 152, 300))); L.Add(E(1, "диафрагма", 2, 0.3, D3(14, 146, 500)));
        L.Add(E(1, "ребро торцевое", 1, 0.3, D3(20, 250, 645))); L.Add(E(1, "ребро ригеля", 2, 0.5, D3(14, 122, 8968 + 0.05 * 517 - 12 - 8323)));
        L.Add(E(1, "стержень", 6, 0.2, bolt)); L.Add(E(1, "бастиек", 6, 0.3, head)); L.Add(E(1, "гайка", 6, 0.3, nut)); L.Add(E(1, "шайба", 12, 0.2, wash));
    }
    else if (node == 2)
    {
        // жота пластинасының габариті: құлақ түріне қарай (RightChain-мен бірдей логика: uzel_02 l.35–36, uzel_13, uzel_07 7а)
        Func<int, int, string> kind = (a, side) => { int sv = (a == 1 || a == 4 || a == 7 || a == 10) ? 1 : (a == 2 || a == 5 || a == 8 || a == 11) ? -1 : 0; if (sv == side) return "SV"; if ((a == 1 && side == -1) || (a == 11 && side == 1)) return "none"; return "P2"; };
        bool b12 = (ax == 1 || ax == 2 || ax == 10 || ax == 11); Func<string, double> xr = k => k == "SV" ? (b12 ? 351 : 348) : k == "P2" ? 301 : 185; Func<string, double> zm = k => k == "SV" ? (b12 ? 9244 : 9250) : 9318;
        string kr = kind(ax, 1), kl = kind(ax, -1);
        L.Add(E(2, "жота пластинасы", 1, 0.3, D3(xr(kr) + xr(kl), 20, 9868 - Math.Min(zm(kr), zm(kl)))));
        var og = E(2, "оголовок", 2, 0.5, D3(320, 420, 25 + SL2 * 420)); og.holes = 4; og.holeDia = 27; L.Add(og);
        L.Add(E(2, "кронштейн", 2, 0.3, D3(10, 154, 300))); L.Add(E(2, "диафрагма", 2, 0.3, D3(14, 146, 500)));
        L.Add(E(2, "ребро ригеля", 4, 0.5, D3(14, 171, ZTOP(17735) - 18 - (ZS(17749) + 18))));
        double sa = Math.Atan(SL2), ca = Math.Cos(sa), sn = Math.Sin(sa);
        L.Add(E(2, "стержень", 8, 1.0, D3(24, 100 * sn + 24 * ca, 100 * ca + 24 * sn))); L.Add(E(2, "бастиек", 8, 2.5, head)); L.Add(E(2, "гайка", 8, 2.5, nut)); L.Add(E(2, "шайба", 16, 1.5, D3(4 * ca + 44 * sn, 44, 44)));
    }
    else if (node == 3 || node == 4)
    {
        double w = node == 3 ? 300 : 370; double zb = node == 3 ? 8733 : 9028;
        var fl = E(node, "фланец", 2, 0.3, D3(25, w, 600)); fl.holes = 10; fl.holeDia = 27; L.Add(fl);
        double[] r1 = node == 3 ? new[] { 6575.0, 6275.0 } : new[] { 12475.0, 12175.0 }; double[] r2 = node == 3 ? new[] { 6625.0, 6925.0 } : new[] { 12525.0, 12825.0 };
        double h1 = node == 3 ? ZSB(r1[0]) - zb : ZSB(r1[0]) - zb;                                     // Б1/Б2 жағы: ең үлкен z = фланец жағында
        double h2 = node == 3 ? ZSB(r2[1]) - zb : ZS3(r2[1]) - zb;                                      // Б2/Б3 жағы: ең үлкен z = ұшында
        L.Add(E(node, "ребро", 2, 0.3, D3(10, 300, h1), D3(10, 300, h2)));
        L.Add(E(node, "стержень", 10, 0.2, bolt)); L.Add(E(node, "бастиек", 10, 0.3, head)); L.Add(E(node, "гайка", 10, 0.3, nut)); L.Add(E(node, "шайба", 20, 0.2, wash));
    }
    return L;
}

static string RunCheck(Document d)
{
    var sb = new StringBuilder(); string auto = @"D:\Бекасыл КЖ КМ\РМЦ_КМ\_авто\";
    if (d == null || d.PathName == null || !d.PathName.EndsWith("РМЦ-КМ.rvt")) return "ABORT: белсенді құжат РМЦ-КМ.rvt емес: " + (d == null ? "null" : d.PathName);
    var allDs = new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел" && (x.ApplicationDataId ?? "").Contains("|")).ToList();
    var items = new List<It>();
    foreach (var e in allDs) { string[] pr = e.ApplicationDataId.Split('|'); string key = pr[0].Trim(), loc = pr[1].Trim(); int k = 0; foreach (var s in SolidsOf(e)) items.Add(new It { key = key, loc = loc, name = e.Name, kind = KindOf(e.Name), s = s, bb = BBox(s), idx = k++ }); }
    var nodes = (NODE == 0 ? new[] { 1, 2, 3, 4 } : new[] { NODE }).Where(n => items.Any(i => i.key == "узел " + n)).ToList();
    sb.AppendLine("DS (БК_узел, барлығы) " + allDs.Count + ", солидтер " + items.Count + "; тексерілетін узелдер: " + (nodes.Count == 0 ? "— (моделде «узел N» жоқ)" : string.Join(",", nodes)));
    var frameAll = new FilteredElementCollector(d).WherePasses(new ElementMulticategoryFilter(new List<BuiltInCategory> { BuiltInCategory.OST_StructuralColumns, BuiltInCategory.OST_StructuralFraming })).WhereElementIsNotElementType().ToList();
    int ok1 = 0, bad1 = 0; var rows = new List<string>(); var clashRows = new List<string>(); var weldRows = new List<string>(); double mm3 = Math.Pow(304.8, 3);
    foreach (int node in nodes)
    {
        string key = "узел " + node; var locs = items.Where(i => i.key == key).Select(i => i.loc).Distinct().OrderBy(l => l).ToList();
        sb.AppendLine("=== УЗЕЛ " + node + ": орындар " + locs.Count + " [" + string.Join(",", locs) + "]");
        int okL = 0, badL = 0;
        foreach (var loc in locs)
        {
            int ax = int.Parse(loc.Split('-')[0]); var mine = items.Where(i => i.key == key && i.loc == loc).ToList();
            // ---- 1. паспорт бөлшектері
            foreach (var ex in Expected(node, loc, ax))
            {
                var sel = mine.Where(i => i.name.Contains(ex.match) && i.kind != "шов").ToList();
                if (ex.match == "ребро" || ex.match == "оголовок") sel = sel.Where(i => i.name.Contains("−")).ToList();
                if (ex.match == "ребро") sel = sel.Where(i => !i.name.Contains("ребро торцевое") && !i.name.Contains("ребро ригеля")).ToList();
                bool good = sel.Count == ex.n; string dm = "";
                foreach (var i in sel) { var m = D3(i.bb[3] - i.bb[0], i.bb[4] - i.bb[1], i.bb[5] - i.bb[2]); dm += (dm == "" ? "" : " | ") + F(m[0]) + "×" + F(m[1]) + "×" + F(m[2]);
                    if (!ex.alts.Any(a => Math.Abs(a[0] - m[0]) <= ex.tol && Math.Abs(a[1] - m[1]) <= ex.tol && Math.Abs(a[2] - m[2]) <= ex.tol)) good = false; }
                string hs = "";
                if (ex.holes > 0 && sel.Count > 0) { int hc = sel.Sum(i => HoleCount(i.s, ex.holeDia)); int hexp = ex.holes * ex.n; hs = " ; тесік Ø" + F(ex.holeDia) + ": " + hc + "/" + hexp; if (hc != hexp) good = false; }
                rows.Add(loc + "\t" + key + "\t" + ex.match + "\tсаны " + sel.Count + "/" + ex.n + "\tөлшем " + dm + "\tкүтілетін " + string.Join(" немесе ", ex.alts.Select(a => F(a[0]) + "×" + F(a[1]) + "×" + F(a[2]))) + hs + "\t" + (good ? "✓" : "ҚАТЕ"));
                if (good) okL++; else badL++;
            }
            // шов саны мен материал (ақпарат)
            var wl = mine.Where(i => i.kind == "шов").ToList(); weldRows.Add(loc + "\t" + key + "\tшов солидтері: " + wl.Count + " (" + string.Join("; ", wl.GroupBy(i => i.name).Select(g => g.Key + " ×" + g.Count())) + ")");
            // ---- 2. clash
            var gl = new[] { mine.Min(i => i.bb[0]), mine.Min(i => i.bb[1]), mine.Min(i => i.bb[2]), mine.Max(i => i.bb[3]), mine.Max(i => i.bb[4]), mine.Max(i => i.bb[5]) };
            var frame = new List<It>();
            foreach (var f in frameAll) { var b = f.get_BoundingBox(null); if (b == null) continue; var q = new[] { b.Min.X / MM, b.Min.Y / MM, b.Min.Z / MM, b.Max.X / MM, b.Max.Y / MM, b.Max.Z / MM }; if (!Ovl(q, gl, 300)) continue;
                string mk = f.get_Parameter(BuiltInParameter.ALL_MODEL_MARK) != null ? f.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString() : "?"; int k = 0; foreach (var s in SolidsOf(f)) frame.Add(new It { key = "каркас", loc = loc, name = mk, kind = "каркас", s = s, bb = BBox(s), idx = k++ }); }
            var neigh = items.Where(i => !(i.key == key && i.loc == loc) && Ovl(i.bb, gl, 300)).ToList();
            var every = mine.Concat(frame).Concat(neigh).OrderBy(i => i.bb[0]).ToList();
            int cOwn = 0, cFrame = 0, cNeigh = 0, packFrame = 0, errs = 0;
            for (int a = 0; a < every.Count; a++) for (int c = a + 1; c < every.Count; c++)
            {
                var A = every[a]; var B = every[c]; if (B.bb[0] > A.bb[3] + 0.5) break;
                bool am = A.key == key && A.loc == loc, bm = B.key == key && B.loc == loc; if (!am && !bm) continue;
                if (B.bb[1] > A.bb[4] + 0.5 || A.bb[1] > B.bb[4] + 0.5 || B.bb[2] > A.bb[5] + 0.5 || A.bb[2] > B.bb[5] + 0.5) continue;
                double v = 0; try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(A.s, B.s, BooleanOperationsType.Intersect); if (r != null) v = r.Volume * mm3; } catch { errs++; clashRows.Add(loc + " " + key + " BOOLEAN ERROR " + A.kind + "#" + A.idx + " ↔ " + B.kind + "#" + B.idx); continue; }
                if (v <= 50) continue;
                var mn = am ? A : B; var ot = am ? B : A; string line = loc + " " + key + " " + mn.kind + "(" + mn.name.Split('-')[0].Trim() + ")#" + mn.idx + " ↔ " + ot.kind + "(" + ot.key + (ot.kind == "каркас" ? " " + ot.name : " " + ot.loc) + ") " + F(v) + " мм3";
                if (am && bm) { cOwn++; clashRows.Add("[өз бөлшектері] " + line); }
                else if (ot.kind == "каркас") { if (mn.kind == "стержень") packFrame++; else { cFrame++; clashRows.Add("[каркас] " + line); } }
                else { cNeigh++; clashRows.Add("[көрші узел/база] " + line); }
            }
            sb.AppendLine(loc + ": clash > 50 мм3 — өз бөлшектері " + cOwn + ", каркас " + cFrame + ", көрші узел/база " + cNeigh + "; ВП стержені ↔ каркас (пакет, тесік модельденбейді, clash емес) " + packFrame + "; boolean қате " + errs + "; көрші каркас " + frame.Select(i => i.name).Distinct().Count() + " элемент, көрші DS солид " + neigh.Count);
            if (cOwn + cFrame + cNeigh == 0) okL++; else badL++;
            // ---- 3. шов кемінде екі бөлшекке тие ме (өз бөлшектері + каркас)
            int loose = 0; var nonW = mine.Where(i => i.kind != "шов").Concat(frame).ToList();
            foreach (var w in mine.Where(i => i.kind == "шов"))
            {
                int tc = nonW.Count(p => Ovl(p.bb, w.bb, 1.0)); if (tc < 2) { loose++; if (loose <= 6) weldRows.Add("  " + loc + " ШОВ ЖЕТІМСІЗ: " + w.name.Split('-')[0].Trim() + "#" + w.idx + " bb " + string.Join(",", w.bb.Select(F)) + " тиетін бөлшек " + tc); } }
            weldRows.Add(loc + "\t" + key + "\tшов: екі бөлшекке тимегені " + loose + " / " + wl.Count); if (loose == 0) okL++; else badL++;
        }
        sb.AppendLine("УЗЕЛ " + node + ": ✓ тексерістер " + okL + ", ҚАТЕ " + badL); ok1 += okL; bad1 += badL;
    }
    sb.AppendLine("=== 1. ПАСПОРТ БӨЛШЕКТЕРІ (орын, узел, бөлшек, саны, өлшем (сұрыпталған bbox), күтілетін, нәтиже)"); foreach (var r in rows) sb.AppendLine(r);
    sb.AppendLine("=== 2. CLASH тізімі (көлем > 50 мм3)"); foreach (var r in clashRows.Take(120)) sb.AppendLine("  " + r); if (clashRows.Count > 120) sb.AppendLine("  … тағы " + (clashRows.Count - 120));
    sb.AppendLine("=== 3. ШОВТАР"); foreach (var r in weldRows) sb.AppendLine(r);
    sb.AppendLine("=== ҚОРЫТЫНДЫ: ✓ " + ok1 + ", ҚАТЕ " + bad1 + (nodes.Count == 0 ? " (тексеретін узел жоқ — алдымен rmc_u0N іске қосылсын)" : ""));
    System.IO.File.WriteAllText(auto + "uzel_check_" + (NODE == 0 ? "all" : NODE.ToString()) + ".txt", sb.ToString(), new UTF8Encoding(false));
    return sb.ToString();
}
