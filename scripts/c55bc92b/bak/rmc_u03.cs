// РМЦ КМ: УЗЕЛ 3 — ригель монтаждық стыгы Б1–Б2 (фланецті, ВП болт), A-дан 6,6 м және G-дан 6,6 м (y = 6600 / 29 400); осьтер 1…11 × A,G = 22 орын. Паспорт: _авто\spec\uzel_03.md (әр сан содан).
// ЖАЗЫЛҒАН 13.11.2026, Revit-те ІСКЕ ҚОСЫЛМАҒАН. Іске қосу: go.ps1 -Name rmc_u03 -Lib rmc_node_lib.cs   (лог: _авто\_rmc_u03.txt).
// Локаль: x — рама ⟂, y — A-дан G-ға (G қатарында айналы: Y = 36000 − y), z — абсолют. Әр орынға бөлек DirectShape «узел 3 | 6-A».
// МАҢЫЗДЫ (СҰРАҚ №1): паспорт фланецтерді y 6575…6600 (Б1) және 6600…6625 (Б2) қояды, ал каркас (frame_changes №7/№8) Б1 мен Б2-ні дәл y=6600-де түйістіреді → фланец Б1/Б2 ұштарының ішіне 25 мм кіреді.
// OVERLAP_MODE="SKIP" (әдепкі): қиылысу > 50 мм³ болса орын ӨТКІЗІЛЕДІ (логта көлемімен). Каркас түзетілгенше (Б1 ұшы 6575, Б2 басы 6625) скрипт ештеңе салмайды — бұл дұрыс күй. "CLEAN" — тек көру үшін (фланец ригель қимасымен тесіледі, дұрыс емес).
return RunU03(document);
}
const bool PILOT = true;                         // true: тек «6-A» (ось 6, A жағы); false: барлық 22 орын
static readonly string[] PILOT_LOCS = { "6-A" };
const string OVERLAP_MODE = "SKIP";
const bool BUILD_TODO_SURAQ = false;             // true қоюға БОЛМАЙДЫ

static double ZSB(double y) { return 8968 + 0.05 * y - 450; }     // Б1 (y ≥ 6000) және Б2 табаны: үсті − h 450
static double ZTP(double y) { return 8968 + 0.05 * y; }           // ригель үсті

static string RunU03(Document d)
{
    var sb = new StringBuilder();
    if (d == null || d.PathName == null || !d.PathName.EndsWith("РМЦ-КМ.rvt")) return "ABORT: белсенді құжат РМЦ-КМ.rvt емес: " + (d == null ? "null" : d.PathName);
    var targets = new List<Tuple<double, string, string>>();
    foreach (var row in new[] { "A", "G" }) foreach (double x in AXX) { string loc = AxisName(x, row); if (PILOT && Array.IndexOf(PILOT_LOCS, loc) < 0) continue; targets.Add(Tuple.Create(x, row, loc)); }
    sb.AppendLine("узел 3: орындар " + targets.Count + " [" + string.Join(",", targets.Select(q => q.Item3)) + "], PILOT=" + PILOT + ", OVERLAP_MODE=" + OVERLAP_MODE);
    int built = 0, skipped = 0;
    using (var t = new Transaction(d, "РМЦ: узел 3"))
    {
        t.Start(); var fo = t.GetFailureHandlingOptions(); fo.SetFailuresPreprocessor(new Swallow()); t.SetFailureHandlingOptions(fo);
        foreach (var tg in targets)
        {
            var sub = new SubTransaction(d); sub.Start();
            try
            {
                int rm = RemoveOld(d, "узел 3", new HashSet<string> { tg.Item3 });
                bool ok = BuildU03(d, sb, tg.Item1, tg.Item2, tg.Item3);
                if (ok) { sub.Commit(); built++; sb.AppendLine("  (бұрынғы өшірілді: " + rm + ")"); } else { sub.RollBack(); skipped++; }
            }
            catch (Exception ex) { sub.RollBack(); skipped++; sb.AppendLine("ERR " + tg.Item3 + ": " + ex); }
        }
        t.Commit();
    }
    sb.AppendLine("узел 3: салынды " + built + ", өткізілді " + skipped);
    if (built > 0) { d.Save(); sb.AppendLine("saved " + d.PathName); }
    return sb.ToString();
}

static bool BuildU03(Document d, StringBuilder sb, double fx, string row, string loc)
{
    const double YJ = 6600;                                   // стык орны (паспорт l.1)
    var f = new Frm(fx, row == "A" ? 0 : 36000, row == "A" ? 1 : -1);
    double g0 = f.Gy(6000), g1 = f.Gy(7200);
    var fr = FrameAround(d, new[] { fx - 450, Math.Min(g0, g1), 8600, fx + 450, Math.Max(g0, g1), 9500 });
    double s1 = ProbeZ(fr, fx + 100, f.Gy(6500), 8000, 9600, true), s2 = ProbeZ(fr, fx + 100, f.Gy(6700), 8000, 9600, true);
    if (double.IsNaN(s1) || double.IsNaN(s2) || Math.Abs(s1 - ZSB(6500)) > 0.8 || Math.Abs(s2 - ZSB(6700)) > 0.8)
    { sb.AppendLine("SKIP " + loc + ": ригель табаны Б1 y=6500: " + F(s1) + " (күтілетін " + F(ZSB(6500)) + "), Б2 y=6700: " + F(s2) + " (күтілетін " + F(ZSB(6700)) + ") — каркас қайта салынбаған"); return false; }
    var c = new Ctx { D = d, L = sb, F = f, Key = "узел 3", Loc = loc, Mode = OVERLAP_MODE }; c.FrameObst = fr; c.Obst = new List<Sx>(fr);
    var cS = BuiltInCategory.OST_StructConnections; var cW = BuiltInCategory.OST_StructConnectionWelds; var soW = So(d, "шов");
    sb.AppendLine("== " + loc + ": Б1 табаны y=6500: " + F(s1) + ", Б2 y=6700: " + F(s2) + ", каркас " + FrameDiag(fr));

    // ---- поз.1 фланец −25×300×600 С345 ×2: x ±150, z 8733…9333 (үсті = ригель үсті 9298 + 35), 10 тесік Ø27: x ±60; z 9248, 9168, 9033, 8896, 8783
    double[] zr = { 9248, 9168, 9033, 8896, 8783 };
    var pFl = Part(c, "fl", cS, "Узел 3: фланец −25×300×600", "поз.1 фланец (торцевая пластина) −25×300×600 С345, 10 тесік Ø27 (2 дана: Б1 y 6575…6600, Б2 y 6600…6625)");
    foreach (double y0 in new[] { YJ - 25, YJ })
    {
        var holes = new List<Hole>(); foreach (double z in zr) foreach (double hx in new[] { -60.0, 60.0 }) holes.Add(new Hole(f.Pt(hx, y0, z), 27));
        bool ok = Put(c, pFl, Prism(Poly(f, -150, y0, 8733, 150, y0, 8733, 150, y0, 9333, -150, y0, 9333), f.V(0, 1, 0), 25, So(d, "фланец"), holes, sb, "фланец"), true, true);
        if (!ok) { sb.AppendLine("SKIP " + loc + ": фланец (y0=" + F(y0) + ") салынбады — каркас Б1/Б2 ұштары фланец қалыңдығына қысқартылмаған (СҰРАҚ №1)"); return false; }
    }

    // ---- поз.2 ребро −10×300×115 С245 ×2 (стенка жазықтығы, x ±5): Б1 жағы y 6275…6575, Б2 жағы 6625…6925; фланецте төменгі z 8733, үсті = ригель табаны (ZSB), ұшында 20 тік
    var pRb = Part(c, "rb", cS, "Узел 3: ребро −10×300×115", "поз.2 ребро −10×300×115 С245, трапеция (ұшында 20 тік; фланецте биіктік 113,75 / 116,25 — табанның 5 % еңісінен; паспорт 115) (2 дана)");
    Put(c, pRb, Prism(Poly(f, -5, 6575, 8733, -5, 6575, ZSB(6575), -5, 6275, ZSB(6275), -5, 6275, ZSB(6275) - 20), f.V(1, 0, 0), 10, So(d, "ребро"), null, sb, "ребро Б1"), true, false);
    Put(c, pRb, Prism(Poly(f, -5, 6625, 8733, -5, 6625, ZSB(6625), -5, 6925, ZSB(6925), -5, 6925, ZSB(6925) - 20), f.V(1, 0, 0), 10, So(d, "ребро"), null, sb, "ребро Б2"), true, false);

    // ---- поз.3 болт ВП М24×90 ×10: бастиек Б1 жағында (y 6575 беті), гайка Б2 жағында; пакет 25+25 = 50 (СҰРАҚ №5: бастиек жағы паспортта жоқ — Б1 жағы жорамал)
    var bs = new BoltSet(); var soB = So(d, "болт");
    foreach (double z in zr) foreach (double hx in new[] { -60.0, 60.0 }) BoltVP(bs, f.Mm(hx, YJ - 25, z), f.V(0, 1, 0), 50, 90, soB, sb);
    double bov = BoltFrameOverlap(c, bs); if (bov > 50) sb.AppendLine("  WARN болт шайба/бастиек/гайка ↔ каркас " + F(bov) + " мм3");
    EmitBolts(c, bs, "3", "90", 10);

    // ---- швтар (барлығы kf 6): Б1/Б2 стенкасы (x ±3) фланецке екі жағынан; ребро фланецке және ригель полкасы астына
    var pW6 = Part(c, "w6", cW, "Узел 3: шов зауыттық kf6", "поз.1 стенка 2×kf 6 (Б1, Б2), поз.2 ребро–фланец және ребро–астыңғы полка — зауыттық kf 6");
    Action<double[], double[], double[], double[]> W6 = (a, b, la, lb) => { Put(c, pW6, WeldS(f, a, b, la, lb, 6, soW), false, false); };
    foreach (double sx in new[] { 1.0, -1.0 })
    {
        W6(V3(sx * 3, YJ - 25, ZSB(YJ - 25) + 12), V3(sx * 3, YJ - 25, ZTP(YJ - 25) - 12), V3(0, -1, 0), V3(sx, 0, 0));      // Б1 стенкасы (полка 12)
        W6(V3(sx * 3, YJ + 25, ZSB(YJ + 25) + 14), V3(sx * 3, YJ + 25, ZTP(YJ + 25) - 14), V3(0, 1, 0), V3(sx, 0, 0));      // Б2 стенкасы (полка 14)
        W6(V3(sx * 5, YJ - 25, 8733), V3(sx * 5, YJ - 25, ZSB(YJ - 25)), V3(0, -1, 0), V3(sx, 0, 0));                        // ребро Б1–фланец
        W6(V3(sx * 5, YJ - 25, ZSB(YJ - 25)), V3(sx * 5, 6275, ZSB(6275)), V3(0, 0, -1), V3(sx, 0, 0));                      // ребро Б1–полка асты
        W6(V3(sx * 5, YJ + 25, 8733), V3(sx * 5, YJ + 25, ZSB(YJ + 25)), V3(0, 1, 0), V3(sx, 0, 0));                         // ребро Б2–фланец
        W6(V3(sx * 5, YJ + 25, ZSB(YJ + 25)), V3(sx * 5, 6925, ZSB(6925)), V3(0, 0, -1), V3(sx, 0, 0));                      // ребро Б2–полка асты
    }
    if (BUILD_TODO_SURAQ)
    {
        // TODO_SURAQ №3: белдеу–фланец «толық провар» (стыковой) шовтарының геометриясы (разделка) паспортта жоқ — салынбайды
    }
    int n = Emit(c);
    sb.AppendLine("  салынды: DS " + n + ", өткізілген бөлшек " + c.SkippedParts + ", тазалау Σ " + F(c.Removed) + " мм3");
    return true;
}
