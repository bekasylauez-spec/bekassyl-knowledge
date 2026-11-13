// РМЦ КМ: УЗЕЛ 2 — ригель Б3 + Б3 → К1 басы, жота (конёк) колонна үстінде; D қатары × осьтер 1…11 (11 орын). Паспорт: _авто\spec\uzel_02.md (+ жота пластинасының құлақтары: uzel_13.md, uzel_07.md 7а).
// ЖАЗЫЛҒАН 13.11.2026, Revit-те ІСКЕ ҚОСЫЛМАҒАН. Іске қосу: go.ps1 -Name rmc_u02 -Lib rmc_node_lib.cs   (лог: _авто\_rmc_u02.txt). Каркас дайын болғанда: К1 (D) басы +9,293, Б3 жотада тік ұшпен 17 990 / 18 010.
// Локаль: x — рама ⟂ (глобал X), y — ГЛОБАЛ Y (жота y = 18000), z — абсолют. Әр орынға бөлек DirectShape: «узел 2 | 6-D». Қайта іске қосқанда нысана орындағы «узел 2» денелері өшіріледі.
// Каркас геометриясы ӨЗГЕРТІЛМЕЙДІ: frame_changes.md бойынша К1 (D) үсті ЖАЗЫҚ +9,293 (Λ-кесу «узел бөлшегі» болып қалған) → оголовок асты Λ, каркас жазық үсті → булев тазалау оголовоктан сына алады (логта), СҰРАҚ №1.
return RunU02(document);
}
const bool PILOT = true;                         // true: тек «6-D»; false: барлық 11 орын
static readonly string[] PILOT_LOCS = { "5-D" };
const string OVERLAP_MODE = "SKIP";              // осы узелде hard бөлшек жоқ (Λ-сына әрқашан тазаланады), тұрақты ортақ интерфейс үшін қалдырылған
const bool BUILD_TODO_SURAQ = false;             // true қоюға БОЛМАЙДЫ

const double SL = 175.0 / 5500.0;                                           // табан еңісі 3,18 % = (9318 − 9143) / 5500 (паспорт l.10; ригель семействосымен және Λ-кесумен БІРДЕЙ)
static double ZL(double y) { return 9293 - SL * Math.Abs(y - 18000); }      // К1 басы (Λ): шың 9293, y=18000±266 → 9284,5
static double ZS(double y) { return 9318 - SL * Math.Abs(y - 18000); }      // ригель (Б3) табаны
static double ZTOP(double y) { return 9868 - 0.05 * Math.Abs(y - 18000); }  // ригель үсті (жотада 9868, еңіс 5 %)

// жота пластинасының оң жақ тізбегі (x;z), төменнен жоғары (CCW). kind: none / P2 (uzel_13) / SV (Р2+СВ2, uzel_02 l.36); bay12: 1–2, 10–11 аралықтарындағы өзгерген екі төбе
static List<double[]> RightChain(string kind, bool bay12)
{
    var r = new List<double[]>();
    if (kind == "none") { r.Add(new[] { 185.0, 9318 }); r.Add(new[] { 185.0, 9868 }); }
    else if (kind == "P2") { r.Add(new[] { 185.0, 9318 }); r.Add(new[] { 301.0, 9508 }); r.Add(new[] { 301.0, 9678 }); r.Add(new[] { 185.0, 9868 }); }
    else
    {
        r.Add(new[] { 172.0, 9318 }); r.Add(new[] { 172.0, 9292 }); r.Add(bay12 ? new[] { 270.0, 9244 } : new[] { 268.0, 9250 }); r.Add(bay12 ? new[] { 351.0, 9382 } : new[] { 348.0, 9389 });
        r.Add(new[] { 329.0, 9503 }); r.Add(new[] { 316.0, 9503 }); r.Add(new[] { 316.0, 9585 }); r.Add(new[] { 301.0, 9678 }); r.Add(new[] { 185.0, 9868 });
    }
    return r;
}
// ось № (1…11), жақ (+1 / −1) → «SV» (связь аралығы жағы), «P2», «none» (ось 1 сыртқы −X, ось 11 сыртқы +X жағында Р2 жоқ: uzel_13 «ось 1 — +X, ось 11 — −X»)
static string EarKind(int ax, int side)
{
    int sv = (ax == 1 || ax == 4 || ax == 7 || ax == 10) ? 1 : (ax == 2 || ax == 5 || ax == 8 || ax == 11) ? -1 : 0;     // связь аралығы 1–2, 4–5, 7–8, 10–11 (uzel_02 l.37)
    if (sv == side) return "SV"; if ((ax == 1 && side == -1) || (ax == 11 && side == 1)) return "none"; return "P2";
}

static string RunU02(Document d)
{
    var sb = new StringBuilder();
    if (d == null || d.PathName == null || !d.PathName.EndsWith("РМЦ-КМ.rvt")) return "ABORT: белсенді құжат РМЦ-КМ.rvt емес: " + (d == null ? "null" : d.PathName);
    var cols = ColsK1(d); var targets = new List<Tuple<double, string>>();
    foreach (double x in AXX) { string loc = AxisName(x, "D"); if (PILOT && Array.IndexOf(PILOT_LOCS, loc) < 0) continue; targets.Add(Tuple.Create(x, loc)); }
    sb.AppendLine("узел 2: орындар " + targets.Count + " [" + string.Join(",", targets.Select(q => q.Item2)) + "], PILOT=" + PILOT + ", OVERLAP_MODE=" + OVERLAP_MODE + ", К1 моделде " + cols.Count);
    int built = 0, skipped = 0;
    using (var t = new Transaction(d, "РМЦ: узел 2"))
    {
        t.Start(); var fo = t.GetFailureHandlingOptions(); fo.SetFailuresPreprocessor(new Swallow()); t.SetFailureHandlingOptions(fo);
        foreach (var tg in targets)
        {
            var sub = new SubTransaction(d); sub.Start();
            try
            {
                int rm = RemoveOld(d, "узел 2", new HashSet<string> { tg.Item2 });
                bool ok = BuildU02(d, sb, tg.Item1, tg.Item2, cols);
                if (ok) { sub.Commit(); built++; sb.AppendLine("  (бұрынғы өшірілді: " + rm + ")"); } else { sub.RollBack(); skipped++; }
            }
            catch (Exception ex) { sub.RollBack(); skipped++; sb.AppendLine("ERR " + tg.Item2 + ": " + ex); }
        }
        t.Commit();
    }
    sb.AppendLine("узел 2: салынды " + built + ", өткізілді " + skipped);
    if (built > 0) { d.Save(); sb.AppendLine("saved " + d.PathName); }
    return sb.ToString();
}

// К1 контурын оголовок астына (Λ-бет zp(y)) дәнекерлеу: сыртқы беттер, полка ұштары, полкалардың ішкі беттері, стенка (yMid-те бөлінеді)
static void ColWelds(Ctx c, PartDS p, SolidOptions soW, Func<double, double> zp, double y0, double y1, double yMid, double kf)
{
    Func<double, double> dz = y => (zp(y + 0.5) - zp(y - 0.5));
    Action<double[], double[], double[], double[]> W = (a, b, la, lb) => { Put(c, p, WeldS(c.F, a, b, la, lb, kf, soW), true, false); };
    W(V3(-150, y1, zp(y1)), V3(150, y1, zp(y1)), V3(0, 1, dz(y1)), V3(0, 0, -1));
    W(V3(-150, y0, zp(y0)), V3(150, y0, zp(y0)), V3(0, -1, -dz(y0)), V3(0, 0, -1));
    foreach (double sx in new[] { 1.0, -1.0 })
    {
        W(V3(sx * 150, y0, zp(y0)), V3(sx * 150, y0 + 16, zp(y0 + 16)), V3(sx, 0, 0), V3(0, 0, -1));
        W(V3(sx * 150, y1 - 16, zp(y1 - 16)), V3(sx * 150, y1, zp(y1)), V3(sx, 0, 0), V3(0, 0, -1));
        W(V3(sx * 4, y0 + 16, zp(y0 + 16)), V3(sx * 150, y0 + 16, zp(y0 + 16)), V3(0, 1, dz(y0 + 16)), V3(0, 0, -1));
        W(V3(sx * 4, y1 - 16, zp(y1 - 16)), V3(sx * 150, y1 - 16, zp(y1 - 16)), V3(0, -1, -dz(y1 - 16)), V3(0, 0, -1));
        W(V3(sx * 4, y0 + 16, zp(y0 + 16)), V3(sx * 4, yMid, zp(yMid)), V3(sx, 0, 0), V3(0, 0, -1));
        W(V3(sx * 4, yMid, zp(yMid)), V3(sx * 4, y1 - 16, zp(y1 - 16)), V3(sx, 0, 0), V3(0, 0, -1));
    }
}

static bool BuildU02(Document d, StringBuilder sb, double fx, string loc, List<FamilyInstance> cols)
{
    const double YR = 18000;
    var f = new Frm(fx, 0, 1); XYZ Z = XYZ.BasisZ; int ax = AxisNo(fx);
    var col = FindCol(cols, fx, YR, 5);
    if (col == null) { sb.AppendLine("SKIP " + loc + ": (" + F(fx) + "; 18000) нүктесінде К1 жоқ"); return false; }
    double zt = col.get_BoundingBox(null).Max.Z / MM;
    if (Math.Abs(zt - 9293) > 0.4) { sb.AppendLine("SKIP " + loc + ": К1 (D) басы " + F(zt) + " ≠ 9293 (каркас қайта салынбаған)"); return false; }
    var fr = FrameAround(d, new[] { fx - 450, 17400, 8800, fx + 450, 18600, 10000 });
    double sz = ProbeZ(fr, fx + 100, 17900, 9000, 10000, true);
    if (double.IsNaN(sz) || Math.Abs(sz - ZS(17900)) > 0.8) { sb.AppendLine("SKIP " + loc + ": Б3 табаны y=17900-де " + (double.IsNaN(sz) ? "табылмады" : F(sz)) + " ≠ " + F(ZS(17900)) + " (каркас қайта салынбаған)"); return false; }
    var c = new Ctx { D = d, L = sb, F = f, Key = "узел 2", Loc = loc, Mode = OVERLAP_MODE }; c.FrameObst = fr; c.Obst = new List<Sx>(fr);
    var cS = BuiltInCategory.OST_StructConnections; var cW = BuiltInCategory.OST_StructConnectionWelds; var soW = So(d, "шов");
    sb.AppendLine("== " + loc + ": К1 басы " + F(zt) + ", Б3 табаны y=17900: " + F(sz) + ", каркас " + FrameDiag(fr) + ", ось " + ax);

    // ---- поз.1 жота пластинасы −20 С245: y 17990…18010; контур uzel_02 «Жота пластинасының контуры» + құлақтар (uzel_13 / uzel_07 7а)
    string kR = EarKind(ax, 1), kL = EarKind(ax, -1); bool bay12 = (ax == 1 || ax == 2 || ax == 10 || ax == 11);
    var chR = RightChain(kR, bay12 && kR == "SV"); var chL = RightChain(kL, bay12 && kL == "SV");
    var pts = new List<double>(); foreach (var q in chR) { pts.Add(q[0]); pts.Add(17990); pts.Add(q[1]); }
    for (int i = chL.Count - 1; i >= 0; i--) { pts.Add(-chL[i][0]); pts.Add(17990); pts.Add(chL[i][1]); }
    var allX = chR.Select(q => q[0]).Concat(chL.Select(q => -q[0])); var allZ = chR.Concat(chL).Select(q => q[1]);
    string rt = "−20×" + F(allX.Max() - allX.Min()) + "×" + F(allZ.Max() - allZ.Min());
    var pRg = Part(c, "rg", cS, "Узел 2: жота пластинасы " + rt, "поз.1 жота пластинасы −20 С245, y 17990…18010; құлақ: x+ " + kR + ", x− " + kL + " (1 дана)");
    Put(c, pRg, Prism(Poly(f, pts.ToArray()), f.V(0, 1, 0), 20, So(d, "фасонка"), null, sb, "жота пластинасы"), true, false);

    // ---- поз.2 оголовок −25 С345, екі бөлік 420(еңіс бойы)×320, әрқайсысында 4 тесік Ø27 (еңіске ⟂): асты Λ (ZL), үсті ригель табаны (ZS), тік қалыңдығы 25
    var pOg = Part(c, "og", cS, "Узел 2: оголовок −25×320×420", "поз.2 оголовок −25×320×420 С345, екі бөлік, 4 тесік Ø27 әрқайсысында (2 дана); жотадағы стыковой шов — СҰРАҚ №3");
    var bs = new BoltSet(); var soB = So(d, "болт");
    foreach (int sg in new[] { 1, -1 })      // +1: G жағы (y 18000…18420), −1: A жағы (y 17580…18000)
    {
        double yE = YR + sg * 420;
        XYZ nUp = new XYZ(0, sg * SL, 1).Normalize();
        var half = Prism(Poly(f, -160, YR, ZL(YR), -160, yE, ZL(yE), -160, yE, ZS(yE), -160, YR, ZS(YR)), f.V(1, 0, 0), 320, So(d, "плита"), null, sb, "оголовок");
        double[] ybs = sg > 0 ? new[] { 18170.0, 18350.0 } : new[] { 17830.0, 17650.0 };
        foreach (double yb in ybs) foreach (double hx in new[] { -65.0, 65.0 })
        {
            XYZ cs = f.Mm(hx, yb, ZS(yb));                                   // ось еңіске ⟂, y — оголовок үсті (ригель табаны) жазықтығында
            half = Drill(half, cs, nUp, 27);
            BoltVP(bs, cs + nUp * 18, -nUp, 43, 100, soB, sb);                // бастиек ригель астыңғы полкасы үстінде (полка 18), гайка оголовок астында; пакет 25 + 18 = 43
        }
        Put(c, pOg, half, true, false);
    }
    double bov = BoltFrameOverlap(c, bs); if (bov > 50) sb.AppendLine("  WARN болт шайба/бастиек/гайка ↔ каркас " + F(bov) + " мм3");
    EmitBolts(c, bs, "2", "100", 8);

    // ---- поз.3 кронштейн −12 С245 ×2 (q20: шығыс 154 ≤ 15·12; бұрын −10, 15,4 t): x ±6; y 18266…18420 (айналы 17580…17734); колоннада биіктік 300; ұшында 20 тік; үсті оголовок асты (ZL)
    var pBr = Part(c, "br", cS, "Узел 2: кронштейн −12×154×300", "поз.3 кронштейн −12×154×300 С245, трапеция, ұшында 20 тік (2 дана)");
    foreach (int sg in new[] { 1, -1 })
    {
        double yf = YR + sg * 266, yE = YR + sg * 420;
        Put(c, pBr, Prism(Poly(f, -6, yf, ZL(yf), -6, yE, ZL(yE), -6, yE, ZL(yE) - 20, -6, yf, ZL(yf) - 300), f.V(1, 0, 0), 12, So(d, "столик"), null, sb, "кронштейн"), true, false);
    }

    // ---- поз.4 диафрагма колонны −14 С245 ×2: z 8971…8985 (колонна ішінде), x 4…150 / −150…−4, y 17750…18250, стенка жағындағы бұрыштар 20×20 срез (жорамал)
    var pDi = Part(c, "di", cS, "Узел 2: диафрагма колонны −14×146×500", "поз.4 диафрагма колонны −14×146×500 С245, бұрыштары 20×20 срез (2 дана)");
    foreach (double s in new[] { 1.0, -1.0 })
        Put(c, pDi, Prism(Poly(f, s * 24, 17750, 8971, s * 150, 17750, 8971, s * 150, 18250, 8971, s * 24, 18250, 8971, s * 4, 18230, 8971, s * 4, 17770, 8971), Z, 14, So(d, "ребро"), null, sb, "диафрагма"), true, false);

    // ---- поз.5 ребро ригеля −14×171 С245 ×4: y 17735…17749 және 18251…18265; x 4…175 / −175…−4; төменгі = астыңғы полка үстінің ЖОҒАРҒЫ шамасы (ZS+18), жоғарғы = үстіңгі полка астының ТӨМЕНГІ шамасы (ZTOP−18); бұрыштар 15×15
    var pRb = Part(c, "rb", cS, "Узел 2: ребро ригеля −14×171×509", "поз.5 ребро ригеля −14×171 (полкалар арасы y-ге байланысты ≈509; паспорт «≈520»), бұрыштары 15×15 С245 (4 дана)");
    var ribs = new List<double[]>();     // y0 (жиек), zb0, zt0 (референс: қалыңдық ортасында), толығымен еңіс жазықтықтарға тақалады
    Func<double, double> zbF = y => ZS(y) + 18, ztF = y => ZTOP(y) - 18 / 0.99875234;      // астыңғы полка үсті / үстіңгі полка асты (еңісті)
    ribs.Add(new[] { 17735.0, zbF(17742), ztF(17742) }); ribs.Add(new[] { 18251.0, zbF(18258), ztF(18258) });
    var soR = So(d, "ребро");
    foreach (var rb in ribs)
    {
        double ya = rb[0], yb2 = rb[0] + 14;
        var slab = Prism(Poly(f, -300, ya - 6, zbF(ya - 6), -300, yb2 + 6, zbF(yb2 + 6), -300, yb2 + 6, ztF(yb2 + 6), -300, ya - 6, ztF(ya - 6)), f.V(1, 0, 0), 600, soR, null, sb, "ребро слаб");
        foreach (double s in new[] { 1.0, -1.0 })
        {
            var rib0 = Prism(Poly(f, s * 4, ya, rb[1] + 15, s * 4, ya, rb[2] - 15, s * 19, ya, rb[2], s * 19, ya, rb[2] + 1.5, s * 175, ya, rb[2] + 1.5, s * 175, ya, rb[1] - 1.5, s * 19, ya, rb[1] - 1.5, s * 19, ya, rb[1]), f.V(0, 1, 0), 14, soR, null, sb, "ребро ригеля");
            Put(c, pRb, BooleanOperationsUtils.ExecuteBooleanOperation(rib0, slab, BooleanOperationsType.Intersect), true, false);
        }
    }

    // ---- швтар
    var pW8 = Part(c, "w8", cW, "Узел 2: шов зауыттық kf8 (оголовок–К1)", "поз.2 — К1 торцына зауыттық kf 8 контур бойынша");
    var pW6 = Part(c, "w6", cW, "Узел 2: шов зауыттық kf6", "поз.1 стенка 2×kf 6, поз.3 кронштейн, поз.4 диафрагма, поз.5 ребро — зауыттық kf 6");
    Action<double[], double[], double[], double[]> W6 = (a, b, la, lb) => { Put(c, pW6, WeldS(f, a, b, la, lb, 6, soW), true, false); };
    ColWelds(c, pW8, soW, ZL, 17734, 18266, YR, 8);
    foreach (int sg in new[] { 1, -1 })
    {
        double yf = YR + sg * 266, yE = YR + sg * 420;
        foreach (double sx in new[] { 1.0, -1.0 })
        {
            W6(V3(sx * 6, yf, ZL(yf) - 300), V3(sx * 6, yf, ZL(yf)), V3(0, sg, 0), V3(sx, 0, 0));          // кронштейн–К1 полкасының сыртқы беті
            W6(V3(sx * 6, yf, ZL(yf)), V3(sx * 6, yE, ZL(yE)), V3(sx, 0, 0), V3(0, 0, -1));                // кронштейн–оголовок асты
        }
    }
    foreach (double sx in new[] { 1.0, -1.0 })
    {
        foreach (double zf in new[] { 8985.0, 8971.0 })
        {
            double dz = zf > 8980 ? 1 : -1;
            W6(V3(sx * 4, 17770, zf), V3(sx * 4, 18230, zf), V3(sx, 0, 0), V3(0, 0, dz));
            W6(V3(sx * 24, 17750, zf), V3(sx * 150, 17750, zf), V3(0, 1, 0), V3(0, 0, dz));
            W6(V3(sx * 24, 18250, zf), V3(sx * 150, 18250, zf), V3(0, -1, 0), V3(0, 0, dz));
        }
        foreach (var rb in ribs) foreach (double yf in new[] { rb[0], rb[0] + 14 })
        {
            double oy = yf < rb[0] + 7 ? -1 : 1, sgn = Math.Sign(yf - 18000), sB = -SL * sgn, sT = -0.05 * sgn;     // полка беттерінің dz/dy
            W6(V3(sx * 4, yf, zbF(yf) + 15), V3(sx * 4, yf, ztF(yf) - 15), V3(0, oy, 0), V3(sx, 0, 0));
            W6(V3(sx * 19, yf, zbF(yf)), V3(sx * 175, yf, zbF(yf)), V3(0, oy, oy * sB), V3(0, 0, 1));
            W6(V3(sx * 19, yf, ztF(yf)), V3(sx * 175, yf, ztF(yf)), V3(0, oy, oy * sT), V3(0, 0, -1));
        }
        // жота пластинасы–Б3 стенкасы (стенка 8: x ±4), екі ригельге (A: y 17990, G: y 18010), екі жағынан kf 6
        W6(V3(sx * 4, 17990, ZS(17990) + 18), V3(sx * 4, 17990, ZTOP(17990) - 18.0225), V3(0, -1, 0), V3(sx, 0, 0));
        W6(V3(sx * 4, 18010, ZS(18010) + 18), V3(sx * 4, 18010, ZTOP(18010) - 18.0225), V3(0, 1, 0), V3(sx, 0, 0));
    }
    if (BUILD_TODO_SURAQ)
    {
        // TODO_SURAQ №3: оголовоктың екі бөлігі арасындағы жотадағы стыковой шов (V, толық провар) — разделка бұрышы/саңылау/биіктік паспортта жоқ → салынбайды
        // TODO_SURAQ №4: жота пластинасы–Б3 полкалары «толық провар» (стыковой) — геометриясы (разделка) паспортта жоқ → салынбайды
    }
    int n = Emit(c);
    sb.AppendLine("  салынды: DS " + n + ", өткізілген бөлшек " + c.SkippedParts + ", тазалау Σ " + F(c.Removed) + " мм3");
    return true;
}
