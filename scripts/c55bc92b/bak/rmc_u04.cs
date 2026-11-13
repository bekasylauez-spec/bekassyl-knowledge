// РМЦ КМ: УЗЕЛ 4 — ригель монтаждық стыгы Б2–Б3 (фланецті, ВП болт), A-дан 12,5 м және G-дан 12,5 м (y = 12 500 / 23 500); осьтер 1…11 × A,G = 22 орын. Паспорт: _авто\spec\uzel_04.md (құрылым uzel_03.md-дегідей).
// ЖАЗЫЛҒАН 13.11.2026, Revit-те ІСКЕ ҚОСЫЛМАҒАН. Іске қосу: go.ps1 -Name rmc_u04 -Lib rmc_node_lib.cs   (лог: _авто\_rmc_u04.txt).
// Локаль: x — рама ⟂, y — A-дан G-ға (G қатарында айналы: Y = 36000 − y), z — абсолют. Әр орынға бөлек DirectShape «узел 4 | 6-A».
// МАҢЫЗДЫ (СҰРАҚ №1): фланецтер y 12475…12500 (Б2) және 12500…12525 (Б3), ал каркаста Б2 мен Б3 дәл y=12500-де түйіседі → фланец ұштардың ішіне 25 мм кіреді. Әдепкі OVERLAP_MODE="SKIP": қиылысу > 50 мм³ болса орын өткізіледі.
return RunU04(document);
}
const bool PILOT = true;                         // true: тек «6-A» (ось 6, A жағы); false: барлық 22 орын
static readonly string[] PILOT_LOCS = { "6-A" };
const string OVERLAP_MODE = "SKIP";
const bool BUILD_TODO_SURAQ = false;             // true қоюға БОЛМАЙДЫ

static double ZS2(double y) { return 8968 + 0.05 * y - 450; }                      // Б2 табаны (h 450)
static double ZS3(double y) { return 9143 + 175.0 / 5500.0 * (y - 12500); }        // Б3 табаны: 12 500-де 9143 (h 450) → 18 000-де 9318 (h 550)
static double ZTP(double y) { return 8968 + 0.05 * y; }                            // ригель үсті

static string RunU04(Document d)
{
    var sb = new StringBuilder();
    if (d == null || d.PathName == null || !d.PathName.EndsWith("РМЦ-КМ.rvt")) return "ABORT: белсенді құжат РМЦ-КМ.rvt емес: " + (d == null ? "null" : d.PathName);
    var targets = new List<Tuple<double, string, string>>();
    foreach (var row in new[] { "A", "G" }) foreach (double x in AXX) { string loc = AxisName(x, row); if (PILOT && Array.IndexOf(PILOT_LOCS, loc) < 0) continue; targets.Add(Tuple.Create(x, row, loc)); }
    sb.AppendLine("узел 4: орындар " + targets.Count + " [" + string.Join(",", targets.Select(q => q.Item3)) + "], PILOT=" + PILOT + ", OVERLAP_MODE=" + OVERLAP_MODE);
    int built = 0, skipped = 0;
    using (var t = new Transaction(d, "РМЦ: узел 4"))
    {
        t.Start(); var fo = t.GetFailureHandlingOptions(); fo.SetFailuresPreprocessor(new Swallow()); t.SetFailureHandlingOptions(fo);
        foreach (var tg in targets)
        {
            var sub = new SubTransaction(d); sub.Start();
            try
            {
                int rm = RemoveOld(d, "узел 4", new HashSet<string> { tg.Item3 });
                bool ok = BuildU04(d, sb, tg.Item1, tg.Item2, tg.Item3);
                if (ok) { sub.Commit(); built++; sb.AppendLine("  (бұрынғы өшірілді: " + rm + ")"); } else { sub.RollBack(); skipped++; }
            }
            catch (Exception ex) { sub.RollBack(); skipped++; sb.AppendLine("ERR " + tg.Item3 + ": " + ex); }
        }
        t.Commit();
    }
    sb.AppendLine("узел 4: салынды " + built + ", өткізілді " + skipped);
    if (built > 0) { d.Save(); sb.AppendLine("saved " + d.PathName); }
    return sb.ToString();
}

static bool BuildU04(Document d, StringBuilder sb, double fx, string row, string loc)
{
    const double YJ = 12500;                                  // стык орны (паспорт l.1)
    var f = new Frm(fx, row == "A" ? 0 : 36000, row == "A" ? 1 : -1);
    double g0 = f.Gy(12000), g1 = f.Gy(13000);
    var fr = FrameAround(d, new[] { fx - 450, Math.Min(g0, g1), 8800, fx + 450, Math.Max(g0, g1), 9800 });
    double s1 = ProbeZ(fr, fx + 100, f.Gy(12400), 8800, 9800, true), s2 = ProbeZ(fr, fx + 100, f.Gy(12600), 8800, 9800, true);
    if (double.IsNaN(s1) || double.IsNaN(s2) || Math.Abs(s1 - ZS2(12400)) > 0.8 || Math.Abs(s2 - ZS3(12600)) > 0.8)
    { sb.AppendLine("SKIP " + loc + ": ригель табаны Б2 y=12400: " + F(s1) + " (күтілетін " + F(ZS2(12400)) + "), Б3 y=12600: " + F(s2) + " (күтілетін " + F(ZS3(12600)) + ") — каркас қайта салынбаған"); return false; }
    var c = new Ctx { D = d, L = sb, F = f, Key = "узел 4", Loc = loc, Mode = OVERLAP_MODE }; c.FrameObst = fr; c.Obst = new List<Sx>(fr);
    var cS = BuiltInCategory.OST_StructConnections; var cW = BuiltInCategory.OST_StructConnectionWelds; var soW = So(d, "шов");
    sb.AppendLine("== " + loc + ": Б2 табаны y=12400: " + F(s1) + ", Б3 y=12600: " + F(s2) + ", каркас " + FrameDiag(fr));

    // ---- поз.1 фланец −25×370×600 С345 ×2: x ±185, z 9028…9628 (үсті = 9593 + 35), 10 тесік Ø27: x ±60; z 9543, 9463, 9328, 9195, 9078
    double[] zr = { 9543, 9463, 9328, 9195, 9078 };
    var pFl = Part(c, "fl", cS, "Узел 4: фланец −25×370×600", "поз.1 фланец −25×370×600 С345, 10 тесік Ø27 (2 дана: Б2 y 12475…12500, Б3 y 12500…12525)");
    foreach (double y0 in new[] { YJ - 25, YJ })
    {
        var holes = new List<Hole>(); foreach (double z in zr) foreach (double hx in new[] { -60.0, 60.0 }) holes.Add(new Hole(f.Pt(hx, y0, z), 27));
        bool ok = Put(c, pFl, Prism(Poly(f, -185, y0, 9028, 185, y0, 9028, 185, y0, 9628, -185, y0, 9628), f.V(0, 1, 0), 25, So(d, "фланец"), holes, sb, "фланец"), true, true);
        if (!ok) { sb.AppendLine("SKIP " + loc + ": фланец (y0=" + F(y0) + ") салынбады — каркас Б2/Б3 ұштары фланец қалыңдығына қысқартылмаған (СҰРАҚ №1)"); return false; }
    }

    // ---- поз.2 ребро −10×300×115 С245 ×2: Б2 жағы y 12175…12475 (ZS2), Б3 жағы y 12525…12825 (ZS3); фланецте төменгі z 9028, ұшында 20 тік
    var pRb = Part(c, "rb", cS, "Узел 4: ребро −10×300×115", "поз.2 ребро −10×300×115 С245, трапеция (ұшында 20 тік; фланецте биіктік 113,75 / 115,8 — табан еңісінен; паспорт 115) (2 дана)");
    Put(c, pRb, Prism(Poly(f, -5, 12475, 9028, -5, 12475, ZS2(12475), -5, 12175, ZS2(12175), -5, 12175, ZS2(12175) - 20), f.V(1, 0, 0), 10, So(d, "ребро"), null, sb, "ребро Б2"), true, false);
    Put(c, pRb, Prism(Poly(f, -5, 12525, 9028, -5, 12525, ZS3(12525), -5, 12825, ZS3(12825), -5, 12825, ZS3(12825) - 20), f.V(1, 0, 0), 10, So(d, "ребро"), null, sb, "ребро Б3"), true, false);

    // ---- поз.3 болт ВП М24×90 ×10: бастиек Б2 жағында (y 12475 беті), гайка Б3 жағында; пакет 50 (СҰРАҚ №5: бастиек жағы жорамал)
    var bs = new BoltSet(); var soB = So(d, "болт");
    foreach (double z in zr) foreach (double hx in new[] { -60.0, 60.0 }) BoltVP(bs, f.Mm(hx, YJ - 25, z), f.V(0, 1, 0), 50, 90, soB, sb);
    double bov = BoltFrameOverlap(c, bs); if (bov > 50) sb.AppendLine("  WARN болт шайба/бастиек/гайка ↔ каркас " + F(bov) + " мм3");
    EmitBolts(c, bs, "4", "90", 10);

    // ---- швтар: Б2 стенкасы (x ±3) kf 6; Б3 стенкасы (x ±4) kf 8 (паспорт l.18: «2 × kf 6 / 2 × kf 8»; l.14 кестесінде «6…8» — СҰРАҚ №6); ребро–фланец және ребро–полка асты kf 6
    var pW6 = Part(c, "w6", cW, "Узел 4: шов зауыттық kf6", "поз.1 Б2 стенкасы 2×kf 6, поз.2 ребро–фланец және ребро–астыңғы полка — зауыттық kf 6");
    var pW8 = Part(c, "w8", cW, "Узел 4: шов зауыттық kf8 (Б3 стенкасы)", "поз.1 Б3 стенкасы (8) 2×kf 8 — зауыттық");
    Action<PartDS, double, double[], double[], double[], double[]> W = (p, kf, a, b, la, lb) => { Put(c, p, WeldS(f, a, b, la, lb, kf, soW), false, false); };
    foreach (double sx in new[] { 1.0, -1.0 })
    {
        W(pW6, 6, V3(sx * 3, YJ - 25, ZS2(YJ - 25) + 14), V3(sx * 3, YJ - 25, ZTP(YJ - 25) - 14), V3(0, -1, 0), V3(sx, 0, 0));      // Б2 стенкасы (полка 14)
        W(pW8, 8, V3(sx * 4, YJ + 25, ZS3(YJ + 25) + 18), V3(sx * 4, YJ + 25, ZTP(YJ + 25) - 18), V3(0, 1, 0), V3(sx, 0, 0));      // Б3 стенкасы (полка 18, стенка 8)
        W(pW6, 6, V3(sx * 5, YJ - 25, 9028), V3(sx * 5, YJ - 25, ZS2(YJ - 25)), V3(0, -1, 0), V3(sx, 0, 0));                         // ребро Б2–фланец
        W(pW6, 6, V3(sx * 5, YJ - 25, ZS2(YJ - 25)), V3(sx * 5, 12175, ZS2(12175)), V3(0, 0, -1), V3(sx, 0, 0));                     // ребро Б2–полка асты
        W(pW6, 6, V3(sx * 5, YJ + 25, 9028), V3(sx * 5, YJ + 25, ZS3(YJ + 25)), V3(0, 1, 0), V3(sx, 0, 0));                          // ребро Б3–фланец
        W(pW6, 6, V3(sx * 5, YJ + 25, ZS3(YJ + 25)), V3(sx * 5, 12825, ZS3(12825)), V3(0, 0, -1), V3(sx, 0, 0));                     // ребро Б3–полка асты
    }
    if (BUILD_TODO_SURAQ)
    {
        // TODO_SURAQ №3: белдеу–фланец «толық провар» (стыковой) шовтарының геометриясы (разделка) паспортта жоқ — салынбайды
    }
    int n = Emit(c);
    sb.AppendLine("  салынды: DS " + n + ", өткізілген бөлшек " + c.SkippedParts + ", тазалау Σ " + F(c.Removed) + " мм3");
    return true;
}
