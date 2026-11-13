// РМЦ КМ: УЗЕЛ 1 — ригель Б1 → К1 басы (карниз), ригель колонна ҮСТІНЕ отырады; A және G қатарлары × осьтер 1…11 (22 орын). Паспорт: _авто\spec\uzel_01.md (әр сан содан).
// ЖАЗЫЛҒАН 13.11.2026, Revit-те ІСКЕ ҚОСЫЛМАҒАН. Іске қосу: go.ps1 -Name rmc_u01 -Lib rmc_node_lib.cs   (лог: _авто\_rmc_u01.txt). Тек КАРКАС ДАЙЫН болғанда (К1 басы +8,286; Б1 табаны +8,311 горизонталь y 0…600).
// Әр орынға бөлек DirectShape: ApplicationDataId «узел 1 | 6-A»; қайта іске қосқанда нысана орындардағы «узел 1» денелері алдымен өшіріледі (қосарланбайды).
// Локаль: x — рама ⟂ (глобал X), y — A-дан G-ға (G қатарында айналы: Y = 36000 − y), z — абсолют. Каркас геометриясы ӨЗГЕРТІЛМЕЙДІ; бөлшектер каркасқа/бір-біріне қарсы булев айырмамен тазаланады (clash 0 конструкциясы бойынша), тазалау көлемі логқа жазылады.
return RunU01(document);
}
const bool PILOT = true;                         // true: тек PILOT_LOCS («6-A»); false: барлық 22 орын
static readonly string[] PILOT_LOCS = { "6-A" };
const string OVERLAP_MODE = "SKIP";              // "SKIP": каркаспен >50 мм³ қиылысатын «hard» бөлшек салынбайды (логта); "CLEAN": булев айырмамен кесіліп салынады
const bool BUILD_TODO_SURAQ = false;             // true қоюға БОЛМАЙДЫ: сұрақтар шешілмейінше TODO_SURAQ бөлшектері салынбайды

static string RunU01(Document d)
{
    var sb = new StringBuilder();
    if (d == null || d.PathName == null || !d.PathName.EndsWith("РМЦ-КМ.rvt")) return "ABORT: белсенді құжат РМЦ-КМ.rvt емес: " + (d == null ? "null" : d.PathName);
    var cols = ColsK1(d); var targets = new List<Tuple<double, string, string>>();
    foreach (var row in new[] { "A", "G" }) foreach (double x in AXX) { string loc = AxisName(x, row); if (PILOT && Array.IndexOf(PILOT_LOCS, loc) < 0) continue; targets.Add(Tuple.Create(x, row, loc)); }
    sb.AppendLine("узел 1: орындар " + targets.Count + " [" + string.Join(",", targets.Select(q => q.Item3)) + "], PILOT=" + PILOT + ", OVERLAP_MODE=" + OVERLAP_MODE + ", К1 моделде " + cols.Count);
    int built = 0, skipped = 0;
    using (var t = new Transaction(d, "РМЦ: узел 1"))
    {
        t.Start(); var fo = t.GetFailureHandlingOptions(); fo.SetFailuresPreprocessor(new Swallow()); t.SetFailureHandlingOptions(fo);
        foreach (var tg in targets)
        {
            var sub = new SubTransaction(d); sub.Start();
            try
            {
                int rm = RemoveOld(d, "узел 1", new HashSet<string> { tg.Item3 });
                bool ok = BuildU01(d, sb, tg.Item1, tg.Item2, tg.Item3, cols);
                if (ok) { sub.Commit(); built++; sb.AppendLine("  (бұрынғы өшірілді: " + rm + ")"); } else { sub.RollBack(); skipped++; }
            }
            catch (Exception ex) { sub.RollBack(); skipped++; sb.AppendLine("ERR " + tg.Item3 + ": " + ex); }
        }
        t.Commit();
    }
    sb.AppendLine("узел 1: салынды " + built + ", өткізілді " + skipped);
    if (built > 0) { d.Save(); sb.AppendLine("saved " + d.PathName); }
    return sb.ToString();
}

static bool BuildU01(Document d, StringBuilder sb, double fx, string row, string loc, List<FamilyInstance> cols)
{
    const double ZC = 8286, ZB = 8311;                       // К1 басы / Б1 табаны (паспорт l.35, l.39)
    var f = new Frm(fx, row == "A" ? 0 : 36000, row == "A" ? 1 : -1); XYZ Z = XYZ.BasisZ;
    var col = FindCol(cols, fx, f.Gy(266), 5);
    if (col == null) { sb.AppendLine("SKIP " + loc + ": (" + F(fx) + "; " + F(f.Gy(266)) + ") нүктесінде К1 жоқ"); return false; }
    double zt = col.get_BoundingBox(null).Max.Z / MM;
    if (Math.Abs(zt - ZC) > 0.4) { sb.AppendLine("SKIP " + loc + ": К1 басы " + F(zt) + " ≠ " + ZC + " (каркас қайта салынбаған)"); return false; }
    double ya = f.Gy(-50), yb = f.Gy(750);
    var fr = FrameAround(d, new[] { fx - 400, Math.Min(ya, yb), 7700, fx + 400, Math.Max(ya, yb), 9100 });
    double sz = ProbeZ(fr, fx + 100, f.Gy(100), 7900, 9100, true);
    if (double.IsNaN(sz) || Math.Abs(sz - ZB) > 0.5) { sb.AppendLine("SKIP " + loc + ": Б1 табаны y=100-де " + (double.IsNaN(sz) ? "табылмады" : F(sz)) + " ≠ " + ZB + " (каркас қайта салынбаған)"); return false; }
    var c = new Ctx { D = d, L = sb, F = f, Key = "узел 1", Loc = loc, Mode = OVERLAP_MODE }; c.FrameObst = fr; c.Obst = new List<Sx>(fr);
    var cS = BuiltInCategory.OST_StructConnections; var cW = BuiltInCategory.OST_StructConnectionWelds;
    sb.AppendLine("== " + loc + ": К1 басы " + F(zt) + ", Б1 табаны " + F(sz) + ", каркас " + FrameDiag(fr));

    // ---- поз.1 оголовок −25×320×684 С345, 6 тесік Ø27: x −160…160, y 0…684, z 8286…8311
    var pPl = Part(c, "pl", cS, "Узел 1: оголовок −25×320×684", "поз.1 оголовок −25×320×684 С345, 6 тесік Ø27 (1 дана)");
    var holes = new List<Hole>(); foreach (double hy in new[] { 96.0, 436.0, 616.0 }) foreach (double hx in new[] { -65.0, 65.0 }) holes.Add(new Hole(f.Pt(hx, hy, ZC), 27));
    Put(c, pPl, Prism(Poly(f, -160, 0, ZC, 160, 0, ZC, 160, 684, ZC, -160, 684, ZC), Z, 25, So(d, "плита"), holes, sb, "оголовок"), true, false);

    // ---- поз.2 кронштейн −10 С245: x −5…5, контур (y;z): (532;8286)→(684;8286)→(684;8266)→(532;7986)
    var pBr = Part(c, "br", cS, "Узел 1: кронштейн −10×152×300", "поз.2 кронштейн −10×152×300 С245, трапеция (үсті 152, колонна бойы 300, ұшында 20 тік) (1 дана)");
    Put(c, pBr, Prism(Poly(f, -5, 532, ZC, -5, 684, ZC, -5, 684, 8266, -5, 532, 7986), f.V(1, 0, 0), 10, So(d, "столик"), null, sb, "кронштейн"), true, false);

    // ---- поз.3 диафрагма −14 С245 ×2: z 7972…7986, x 4…150 / −150…−4, y 16…516, стенка жағындағы бұрыштар 20×20 срез (жорамал: 45° срез, «СҰРАҚ» №4)
    var pDi = Part(c, "di", cS, "Узел 1: диафрагма колонны −14×146×500", "поз.3 диафрагма колонны −14×146×500 С245, бұрыштары 20×20 срез (2 дана)");
    foreach (double s in new[] { 1.0, -1.0 })
        Put(c, pDi, Prism(Poly(f, s * 24, 16, 7972, s * 150, 16, 7972, s * 150, 516, 7972, s * 24, 516, 7972, s * 4, 496, 7972, s * 4, 36, 7972), Z, 14, So(d, "ребро"), null, sb, "диафрагма"), true, false);

    // ---- поз.4 торцевое ребро (АР тік лист) −20×250×645 С245: y 0…20, x ±125, z 8323…8968. HARD: Б1 ұшы y=0 моделінде ригель дәл осы көлемді алып жатыр (СҰРАҚ №1)
    var pTr = Part(c, "tr", cS, "Узел 1: ребро торцевое −20×250×645", "поз.4 торцевое ребро ригеля (АР тік лист) −20×250×645 С245 (1 дана)");
    bool trOk = Put(c, pTr, Prism(Poly(f, -125, 0, 8323, 125, 0, 8323, 125, 0, 8968, -125, 0, 8968), f.V(0, 1, 0), 20, So(d, "ребро"), null, sb, "торцевое ребро"), true, true);

    // ---- поз.5 ребро ригеля −14×122 С245 ×2: y 517…531, x 3…125 / −125…−3, z 8323 → үстіңгі полка астына (8968+0,05·517−12 = 8981,85), бұрыштары 15×15
    double ZT = 8968 + 0.05 * 517 - 12;
    var pRb = Part(c, "rb", cS, "Узел 1: ребро ригеля −14×122×659", "поз.5 ребро ригеля −14×122×659 С245, бұрыштары 15×15, колонна ішкі полкасы үстінде (2 дана)");
    foreach (double s in new[] { 1.0, -1.0 })
        Put(c, pRb, Prism(Poly(f, s * 18, 517, 8323, s * 125, 517, 8323, s * 125, 517, ZT, s * 18, 517, ZT, s * 3, 517, ZT - 15, s * 3, 517, 8338), f.V(0, 1, 0), 14, So(d, "ребро"), null, sb, "ребро ригеля"), true, false);

    // ---- поз.6 болт ВП М24×90 ×6: x ±65, y 96/436/616; бастиек Б1 астыңғы полкасы үстінде (z 8323), гайка оголовок астында; пакет 25+12 = 37
    var bs = new BoltSet(); var soB = So(d, "болт");
    foreach (double hy in new[] { 96.0, 436.0, 616.0 }) foreach (double hx in new[] { -65.0, 65.0 }) BoltVP(bs, f.Mm(hx, hy, 8323), new XYZ(0, 0, -1), 37, 90, soB, sb);
    double bov = BoltFrameOverlap(c, bs);
    if (bov > 50) sb.AppendLine("  WARN болт шайба/бастиек/гайка ↔ каркас " + F(bov) + " мм3: y=616 болтының астында Б1 вуты (y>600, еңіс ≈5,4°) басталады — СҰРАҚ №2");
    EmitBolts(c, bs, "1", "90", 6);

    // ---- швтар (үшбұрыш белдік; каркасқа және алдыңғы бөлшектерге булев тазалау)
    var soW = So(d, "шов");
    var pW8 = Part(c, "w8", cW, "Узел 1: шов зауыттық kf8 (оголовок–К1)", "поз.1 — К1 торцына зауыттық kf 8 контур бойынша (y=0 қыры колонна полкасымен тегіс — шов жоқ)");
    var pW6 = Part(c, "w6", cW, "Узел 1: шов зауыттық kf6", "поз.2 кронштейн, поз.3 диафрагма, поз.5 ребро ригеля — зауыттық kf 6");
    Action<PartDS, double[], double[], double[], double[], double> W = (p, a, b, la, lb, kf) => { Put(c, p, WeldS(f, a, b, la, lb, kf, soW), false, false); };
    double zp = ZC;
    W(pW8, V3(-150, 532, zp), V3(150, 532, zp), V3(0, 1, 0), V3(0, 0, -1), 8);                                   // ішкі полканың сыртқы беті (y=532), оголовок шығысы астында
    foreach (double sx in new[] { 1.0, -1.0 })
    {
        W(pW8, V3(sx * 150, 516, zp), V3(sx * 150, 532, zp), V3(sx, 0, 0), V3(0, 0, -1), 8);                      // ішкі полка ұшы (x=±150)
        W(pW8, V3(sx * 150, 0, zp), V3(sx * 150, 16, zp), V3(sx, 0, 0), V3(0, 0, -1), 8);                         // сыртқы полка ұшы (x=±150)
        W(pW8, V3(sx * 4, 16, zp), V3(sx * 150, 16, zp), V3(0, 1, 0), V3(0, 0, -1), 8);                           // сыртқы полканың ішкі беті (y=16)
        W(pW8, V3(sx * 4, 516, zp), V3(sx * 150, 516, zp), V3(0, -1, 0), V3(0, 0, -1), 8);                        // ішкі полканың ішкі беті (y=516)
        W(pW8, V3(sx * 4, 16, zp), V3(sx * 4, 516, zp), V3(sx, 0, 0), V3(0, 0, -1), 8);                           // стенка беттері (x=±4)
        // кронштейн–К1 полка (тік, kf 6) және кронштейн–оголовок асты (көлденең, kf 6)
        W(pW6, V3(sx * 5, 532, 7986), V3(sx * 5, 532, zp), V3(0, 1, 0), V3(sx, 0, 0), 6);
        W(pW6, V3(sx * 5, 532, zp), V3(sx * 5, 684, zp), V3(sx, 0, 0), V3(0, 0, -1), 6);
        // диафрагма: стенкаға және полкалардың ішкі бетіне, жоғарғы (z 7986) және астыңғы (z 7972) бетінен
        foreach (double zf in new[] { 7986.0, 7972.0 })
        {
            double dz = zf > 7980 ? 1 : -1;
            W(pW6, V3(sx * 4, 36, zf), V3(sx * 4, 496, zf), V3(sx, 0, 0), V3(0, 0, dz), 6);
            W(pW6, V3(sx * 24, 16, zf), V3(sx * 150, 16, zf), V3(0, 1, 0), V3(0, 0, dz), 6);
            W(pW6, V3(sx * 24, 516, zf), V3(sx * 150, 516, zf), V3(0, -1, 0), V3(0, 0, dz), 6);
        }
        // ребро ригеля: стенкаға (x=±3), астыңғы полка үстіне (z 8323), үстіңгі полка астына (z=ZT); әр ребро қалыңдығының екі бетінде (y 517 / 531)
        foreach (double yf in new[] { 517.0, 531.0 })
        {
            double oy = yf < 520 ? -1 : 1;
            W(pW6, V3(sx * 3, yf, 8338), V3(sx * 3, yf, ZT - 15), V3(0, oy, 0), V3(sx, 0, 0), 6);
            W(pW6, V3(sx * 18, yf, 8323), V3(sx * 125, yf, 8323), V3(0, oy, 0), V3(0, 0, 1), 6);
            W(pW6, V3(sx * 18, yf, ZT), V3(sx * 125, yf, ZT), V3(0, oy, 0), V3(0, 0, -1), 6);
        }
    }
    if (BUILD_TODO_SURAQ)
    {
        // TODO_SURAQ №3: поз.4 торцевое ребро −20 швтарының катеті паспортта жоқ («зауыттық», kf көрсетілмеген; Б1 полкасы 12 → kf ≤ 14, стенка 6 → kf ≤ 7,2) — салынбайды
    }
    int n = Emit(c);
    sb.AppendLine("  салынды: DS " + n + ", өткізілген бөлшек " + c.SkippedParts + (trOk ? "" : " (торцевое ребро)") + ", тазалау Σ " + F(c.Removed) + " мм3");
    return true;
}
