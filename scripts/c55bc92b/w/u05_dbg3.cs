// РМЦ КМ: УЗЕЛ 5 — кран консолі КБ1 → К1 (колоннада листер, ребро под ПБ), ПБ1 тірелуі консольге (тірек қабырғасы, прокладка, шайба-пластина, 2 М20), ПБ1 жоғарғы белдеуінің стыгы (накладка), колоннаға тартпа (тартпа + ∟110×8), рельс Р24 (шартты).
// Паспорт: _авто\spec\uzel_05.md («Модельдеушіге»; әр сан содан). ЖАЗЫЛҒАН 13.11.2026, Revit-те ІСКЕ ҚОСЫЛМАҒАН. Іске қосу: go.ps1 -Name rmc_u05 -Lib rmc_misc_lib.cs   (лог: _авто\_rmc_u05.txt).
// Тек КАРКАС v3 дайын болғанда (К1, КБ1, ПБ1 моделде). Орын = бір консоль: A, G × осьтер 1…11 («узел 5 | 3-A»), D × 1…11 екі консоль («3-D-1» = −Y жақ, рельс 17 400; «3-D-2» = +Y жақ, рельс 18 600) → 44 орын.
// Локаль жүйе (консоль үшін): x — ПБ бойы, рама осінен (ось 11-де айналы: +x әрқашан ішке); y — К1 колоннасының СЫРТҚЫ бетінен (колонна осінен 266) ішке қарай (A: глобал Y; G: 36 000 − Y; D-1: 18 266 − Y; D-2: Y − 17 734); z абсолют. Колоннаның ішкі полка беті (консоль басы) y = 532.
// Консоль: A/G ұзындығы 468 (532 → 1000), рельс y = 800, ұшы 1000; D: ұзындығы 534 (532 → 1066), рельс y = 866 (глобал 17 400 / 18 600), ұшы 1066 (глобал 17 200 / 18 800); астыңғы полка асты +4,760 (колонна бетінде) → +4,940 (ұшында).
// Паспорттан тыс/екіұшты тұстар (TODO_SURAQ / TODO_KRAN) САЛЫНБАЙДЫ — әр жерде комментте; жауап мәтініндегі СҰРАҚ тізімінде нөмірленген (№1 торцевое ребро, №2 тірек қабырғасы шовы, №3 накладка болттары, №4 тартпа болттары, №5 x 150…185 полкадан тыс).
return RunU05(document);
}
const bool PILOT = true;                       // true: тек PILOT_LOCS («6-A»: ось 6, A консолі, екі жақты ПБ); D үшін {"6-D-1","6-D-2"} қосуға болады
static readonly string[] PILOT_LOCS = { "1-A" };
const string OVERLAP_MODE = "SKIP";               // "SKIP": «hard» бөлшек каркаспен >50 мм³ қиылысса салынбайды (логта); "CLEAN": булев айырмамен кесіліп салынады
const bool BUILD_TODO_SURAQ = true;                // шешімдер 13.11 (_шешімдер_узел_5-6_17-20.md) №1: торцевое ребро КБ1 ұшынан СЫРТТА y YT…YT+12; №3: накладка болттарының КБ-ға қарсы екеуі тартпа арқылы (l 60, пакет 42)
const bool BUILD_TODO_KRAN = false;                // true қоюға БОЛМАЙДЫ: рельс бекітпесі, буфер, тартпа болттары (шешім №4) — кран паспорты жоқ (TODO_KRAN)
const double RAIL_HALF = 300;                     // рельс кесіндісінің жарты ұзындығы (шартты; паспортта жоқ): ПБ стыгы ±300; 1/11 осьтерінде x 334…934
const double RAIL_HEAD_TOP = 6093;                // паспорт: рельс басы +6,093 (Р24 шартты: табан 92, бас 51, стенка ~11 — ГОСТ 6368-тен жуық, паспортта жоқ)

class U5Loc { public string Loc, Row; public int Ai; public double Fx, LC, YR, YT, ColY; public QFrm F; public bool Plates; }
static List<U5Loc> U5Targets()
{
    var r = new List<U5Loc>();
    for (int ai = 0; ai < QAXX.Length; ai++)
    {
        double fx = QAXX[ai], ax = ai == QAXX.Length - 1 ? -1 : 1; string n = (ai + 1).ToString();
        r.Add(new U5Loc { Loc = n + "-A", Row = "A", Ai = ai, Fx = fx, LC = 468, YR = 800, YT = 1000, ColY = 266, F = new QFrm(fx, 0, ax, 0, 0, 1), Plates = true });
        r.Add(new U5Loc { Loc = n + "-G", Row = "G", Ai = ai, Fx = fx, LC = 468, YR = 800, YT = 1000, ColY = 35734, F = new QFrm(fx, 36000, ax, 0, 0, -1), Plates = true });
        r.Add(new U5Loc { Loc = n + "-D-1", Row = "D", Ai = ai, Fx = fx, LC = 534, YR = 866, YT = 1066, ColY = 18000, F = new QFrm(fx, 18266, ax, 0, 0, -1), Plates = true });   // D-1: колонна плиталары осы орында (4 дана, D-да ортақ)
        r.Add(new U5Loc { Loc = n + "-D-2", Row = "D", Ai = ai, Fx = fx, LC = 534, YR = 866, YT = 1066, ColY = 18000, F = new QFrm(fx, 17734, ax, 0, 0, 1), Plates = false });
    }
    return r;
}

static string RunU05(Document d)
{
    var sb = new StringBuilder();
    if (d == null || d.PathName == null || !d.PathName.EndsWith("РМЦ-КМ.rvt")) return "ABORT: белсенді құжат РМЦ-КМ.rvt емес: " + (d == null ? "null" : d.PathName);
    var targets = U5Targets().Where(t => !PILOT || Array.IndexOf(PILOT_LOCS, t.Loc) >= 0).ToList();
    sb.AppendLine("узел 5: орындар " + targets.Count + (targets.Count <= 12 ? " [" + string.Join(",", targets.Select(q => q.Loc)) + "]" : "") + ", PILOT=" + PILOT + ", OVERLAP_MODE=" + OVERLAP_MODE + ", BUILD_TODO_SURAQ=" + BUILD_TODO_SURAQ);
    var cols = QByMark(d, "К1"); sb.AppendLine("К1 моделде " + cols.Count + ", КБ1 " + QByMark(d, "КБ1").Count + ", ПБ1 " + QByMark(d, "ПБ1").Count);
    int built = 0, skipped = 0;
    using (var t = new Transaction(d, "РМЦ: узел 5"))
    {
        t.Start(); var fo = t.GetFailureHandlingOptions(); fo.SetFailuresPreprocessor(new QSwallow()); t.SetFailureHandlingOptions(fo);
        foreach (var tg in targets)
        {
            var sub = new SubTransaction(d); sub.Start();
            try
            {
                int rm = QRemoveOld(d, "узел 5", new HashSet<string> { tg.Loc });
                bool ok = BuildU05(d, sb, tg, cols);
                if (ok) { sub.Commit(); built++; sb.AppendLine("  (бұрынғы өшірілді: " + rm + ")"); } else { sub.RollBack(); skipped++; }
            }
            catch (Exception ex) { sub.RollBack(); skipped++; sb.AppendLine("ERR " + tg.Loc + ": " + ex); }
        }
        if (!QCommit(t, sb)) built = 0;
    }
    sb.AppendLine("узел 5: салынды " + built + ", өткізілді " + skipped);
    if (built > 0) { d.Save(); sb.AppendLine("saved " + d.PathName); }
    return sb.ToString();
}

static bool BuildU05(Document d, StringBuilder sb, U5Loc L, List<FamilyInstance> cols)
{
    var f = L.F; double LC = L.LC, YR = L.YR, YT = L.YT; double slope = 180.0 / LC;       // астыңғы полка еңісі dz/dy
    Func<double, double> zl = y => 4760 + (y - 532) * slope;                                // астыңғы полка астыңғы беті (паспорт l.43)
    bool axEnd = L.Ai == 0 || L.Ai == QAXX.Length - 1; int[] expSides = axEnd ? new[] { 1 } : new[] { 1, -1 };
    // ---- preflight: колонна, КБ1 (екі полка), ПБ1 (қай жақта бар)
    var col = cols.FirstOrDefault(cc => { var p = (cc.Location as LocationPoint).Point; return Math.Abs(p.X / QMM - L.Fx) < 5 && Math.Abs(p.Y / QMM - L.ColY) < 5; });
    if (col == null) { sb.AppendLine("SKIP " + L.Loc + ": (" + QF(L.Fx) + "; " + QF(L.ColY) + ") нүктесінде К1 жоқ"); return false; }
    double gy0 = f.Gy(0), gy1 = f.Gy(YT + 30), gx0 = f.Gx(-400), gx1 = f.Gx(400);
    var fr = QFrameAround(d, new[] { Math.Min(gx0, gx1), Math.Min(gy0, gy1), 4400, Math.Max(gx0, gx1), Math.Max(gy0, gy1), 6300 });
    double yPr = YR + 160;     // ПБ астыңғы полкасы (YR ± 150) сыртында — КБ1 полкалары ПБ-мен қосылып кетпейді (ПБ табаны дәл КБ1 үстінде +5200)
    var kbS = QProbeSegs(fr, f.Gx(100), f.Gy(yPr), 4400, 5300); double zlExp = zl(yPr);
    bool kbOk = kbS.Count >= 2 && Math.Abs(kbS[0][0] - zlExp) <= 0.8 && Math.Abs(kbS[0][1] - kbS[0][0] - 18) <= 0.6 && QSegHas(kbS, 5182, 5200, 0.5);
    if (!kbOk) { sb.AppendLine("SKIP " + L.Loc + ": КБ1 y=" + QF(yPr) + "-де полкалар " + QSegStr(kbS) + " ≠ күтілетін [" + QF(zlExp) + "…" + QF(zlExp + 18) + "] [5182…5200]"); return false; }
    var sides = new List<int>();
    foreach (int sx in new[] { 1, -1 }) { var ps = QProbeSegs(fr, f.Gx(sx * 100), f.Gy(YR + 50), 5201, 6100); if (ps.Any(q => Math.Abs(q[1] - 5218) <= 0.5) && QSegHas(ps, 5968, 5986, 0.5)) sides.Add(sx); }
    if (sides.Count != expSides.Length || !expSides.All(sides.Contains)) { sb.AppendLine("SKIP " + L.Loc + ": ПБ1 жақтары [" + string.Join(",", sides) + "] ≠ күтілетін [" + string.Join(",", expSides) + "] (ось 1/11 — бір жақты, қалғаны — екі жақты)"); return false; }
    bool two = sides.Count == 2;
    var c = new QCtx { D = d, L = sb, F = f, Key = "узел 5", Loc = L.Loc, Mode = OVERLAP_MODE }; c.FrameObst = fr; c.Obst = new List<QSx>(fr);
    var cS = BuiltInCategory.OST_StructConnections; var cW = BuiltInCategory.OST_StructConnectionWelds; var cB = BuiltInCategory.OST_StructConnectionBolts;
    var soW = QSo(d, "шов"); var soR = QSo(d, "ребро"); var soB = QSo(d, "болт");
    sb.AppendLine("== " + L.Loc + ": КБ1 полкалары " + QSegStr(kbS) + ", ПБ жақтары [" + string.Join(",", sides) + "], каркас " + fr.Count + " солид");
    var pW8 = QPart(c, "w8", cW, "Узел 5: шов зауыттық kf8", "поз.1 лист колонны (стенка + полкалар) және КБ1 стенкасы–К1 полкасы — зауыттық kf 8 (КБ1 белдеулері — толық провар: шартты, дене емес)");
    var pW6 = QPart(c, "w6", cW, "Узел 5: шов kf6", "поз.2 ребро консоли, поз.4а прокладка (монтаждық), поз.9 тартпа, поз.10 ∟110×8 — kf 6 (тартпа/уголок — К1/ПБ1 маркасымен зауыттық)");
    Action<QPartDS, double[], double[], double[], double[], double> W = (p, a, b, la, lb, kf) => { QPut(c, p, QWeldS(f, a, b, la, lb, kf, soW), true, false); };

    // ---- поз.1 лист колонны −18×146×500, бұрыштары 20×20 (4 дана; D-да ортақ → тек D-1): z +5,182…+5,200 және +4,760…+4,778; x 4…150 / −150…−4; y 16…516 (стенка жағындағы бұрыштар 20×20 срез, 45°)
    if (L.Plates)
    {
        var pPl = QPart(c, "pl", cS, "Узел 5: лист колонны −18×146×500", "поз.1 лист колонны −18×146×500 С245, бұрыштары 20×20 срез (4 дана; D-да екі консольге ортақ), К1 стенкасы мен полкаларына зауыттық kf 8");
        foreach (double z0 in new[] { 5182.0, 4760.0 }) foreach (double s in new[] { 1.0, -1.0 })
        {
            QPut(c, pPl, QExtrude(f, 'z', z0, 18, new[] { s * 24, 16, s * 150, 16, s * 150, 516, s * 24, 516, s * 4, 496, s * 4, 36 }, soR, null, sb, "лист колонны"), true, true);
            foreach (var zf in new[] { Tuple.Create(z0 + 18, 1.0), Tuple.Create(z0, -1.0) })
            {
                W(pW8, QV3(s * 4, 36, zf.Item1), QV3(s * 4, 496, zf.Item1), QV3(s, 0, 0), QV3(0, 0, zf.Item2), 8);
                W(pW8, QV3(s * 24, 16, zf.Item1), QV3(s * 150, 16, zf.Item1), QV3(0, 1, 0), QV3(0, 0, zf.Item2), 8);
                W(pW8, QV3(s * 24, 516, zf.Item1), QV3(s * 150, 516, zf.Item1), QV3(0, -1, 0), QV3(0, 0, zf.Item2), 8);
            }
        }
    }
    // ---- КБ1 стенкасы–К1 полкасы: стенка 2 × kf 8 (колонна полкасының сыртқы беті y = 532, стенка x ±5, z 4778…5182)
    foreach (double s in new[] { 1.0, -1.0 }) W(pW8, QV3(s * 5, 532, zl(532) + 18), QV3(s * 5, 532, 5182), QV3(s, 0, 0), QV3(0, 1, 0), 8);

    // ---- поз.2 ребро консоли под ПБ −12×170×(h−36) ×2: y = YR ± 6, x 5…175 және −175…−5, астыңғы полка үстінен (еңіс) үстіңгі полка астына дейін
    double hr = 5182 - (zl(YR) + 18);
    var pRb = QPart(c, "rb", cS, "Узел 5: ребро консоли −12×170×" + QF(Math.Round(hr)), "поз.2 ребро консоли под ПБ −12×170×" + QF(Math.Round(hr)) + " С245 (h − 36), рельс осінде y=" + QF(YR) + ", КБ1 стенкасының екі жағында (2 дана), КБ1 стенкасы мен полкаларына зауыттық kf 6");
    double[] ribPq = { YR - 6, zl(YR - 6) + 18, YR + 6, zl(YR + 6) + 18, YR + 6, 5182, YR - 6, 5182 };
    foreach (double s in new[] { 1.0, -1.0 }) QPut(c, pRb, QExtrude(f, 'x', s > 0 ? 5 : -175, 170, ribPq, soR, null, sb, "ребро консоли"), true, true);
    foreach (double s in new[] { 1.0, -1.0 }) foreach (double o in new[] { -1.0, 1.0 })
    {
        double y = YR + 6 * o, zb = zl(y) + 18;
        W(pW6, QV3(s * 5, y, zb), QV3(s * 5, y, 5182), QV3(0, o, 0), QV3(s, 0, 0), 6);                       // ребро–стенка
        W(pW6, QV3(s * 5, y, 5182), QV3(s * 175, y, 5182), QV3(0, o, 0), QV3(0, 0, -1), 6);                  // ребро–үстіңгі полка асты
        W(pW6, QV3(s * 5, y, zb), QV3(s * 175, y, zb), QV3(0, o, o * slope), QV3(0, 0, 1), 6);               // ребро–астыңғы полка үсті (еңіс бойымен)
    }
    // ---- поз.3 торцевое ребро −12×350×260: паспорт y 988…1000 (D: 17 200…17 212) — КБ1 денесінің ішінде (КБ1 y=1000-ге дейін) → 100 % қиылысу → САЛЫНБАЙДЫ (TODO_SURAQ №1)
    if (BUILD_TODO_SURAQ)
    {
        var pTr = QPart(c, "tr", cS, "Узел 5: ребро торцевое −12×350×260", "поз.3 торцевое ребро −12×350×260 С245: КБ1 ұшынан СЫРТТА y " + QF(YT) + "…" + QF(YT + 12) + " (шешім №1: консоль ұзындығы өзгермейді, ребро торецке қойылады), КБ1 ұшына зауыттық kf 6 (шов денесі салынбайды: ребро беті КБ1 қимасымен тегіс — бет сүйеу/толық провар) (1 дана)");
        QPut(c, pTr, QBoxA(f, 'y', YT, YT + 12, -175, 175, 4940, 5200, soR, null, sb, "торцевое ребро"), true, true);
    }
    else sb.AppendLine("  TODO_SURAQ: поз.3 торцевое ребро (y " + QF(YT - 12) + "…" + QF(YT) + ") КБ1 денесінің ішінде — салынбады");

    foreach (int sx in sides)
    {
        // ---- поз.4 тірек қабырғасы ПБ −20×300×750 (x ±10…±30; стенка y ±6 арқылы қақ бөлінеді → екі жарты, стенканың екі жағында), табаны строгать; z 5218…5968
        var pSr = QPart(c, "sr", cS, "Узел 5: тірек қабырғасы ПБ −20×300×750", "поз.4 тірек қабырғасы −20×300×750 С245, табаны строгать, ПБ1 ұшында x ±10…±30 (ПБ стенкасы y ±6 арқылы өтеді → екі жарты y 6…150 және −150…−6; әр ПБ ұшына 1 қабырға = 2 жарты); ПБ ұшына зауыттық (kf паспортта жоқ — TODO_SURAQ №2, шов салынбайды)");
        double xa = Math.Min(sx * 10.0, sx * 30.0), xb = Math.Max(sx * 10.0, sx * 30.0);
        QPut(c, pSr, QBox(f, xa, xb, YR + 6, YR + 150, 5218, 5968, soR, sb, "тірек қабырғасы"), true, true);
        QPut(c, pSr, QBox(f, xa, xb, YR - 150, YR - 6, 5218, 5968, soR, sb, "тірек қабырғасы"), true, true);
    }
    var soP = QSo(d, "прокладка");
    if (two)
    {
        // ---- поз.4а прокладка −20×280×740: x −10…10, y = YR ± 140, z 5223…5963; монтаждық kf 6 тек +x жақтағы тірек қабырғасына (жиегінен 10/5 мм — катет 6 тек тік қырларда сыяды; көлденең қырлар салынбайды)
        var pPr = QPart(c, "pr", cS, "Узел 5: прокладка −20×280×740", "поз.4а прокладка −20×280×740 С245, екі ПБ ұшы арасындағы 20 саңылауда, +x жақтағы тірек қабырғасына монтаждық kf 6 (1 дана; 1 және 11 осьтерінде жоқ)");
        QPut(c, pPr, QBox(f, -10, 10, YR - 140, YR + 140, 5223, 5963, soP, sb, "прокладка"), true, true);
        foreach (double yy in new[] { -140.0, 140.0 }) W(pW6, QV3(10, YR + yy, 5223), QV3(10, YR + yy, 5963), QV3(0, Math.Sign(yy), 0), QV3(-1, 0, 0), 6);
    }
    // ---- поз.5 шайба-пластина −12×70×70, тесік Ø23 (ПБ табаны үстінде, z 5218…5230) және поз.6 болт М20 кл. 8.8 l70 (ПБ табаны + консоль үстіңгі полкасы; бастиек жоғарыда пластинада, гайка консоль полкасы астында, шайба Ø37)
    var pWp = QPart(c, "wp", cB, "Узел 5: шайба-пластина −12×70×70", "поз.5 шайба-пластина −12×70×70 С245, тесік Ø23 (ПБ табанына монтаждық, ретке келтірген соң; kf паспортта жоқ — шов салынбайды) (" + (sides.Count * 2) + " дана)");
    var bsA = new QBoltSet();
    foreach (int sx in sides) foreach (double ys in new[] { -100.0, 100.0 })
    {
        double bx = sx * 80, by = YR + ys;
        QPut(c, pWp, QBoxA(f, 'z', 5218, 5230, bx - 35, bx + 35, by - 35, by + 35, soB, new[] { new[] { bx, by, 23.0 } }, sb, "шайба-пластина"), true, true);
        QBolt(bsA, f.Mm(bx, by, 5230), new XYZ(0, 0, -1), 48, 70, 20, false, true, soB, sb);        // пакет 12 + 18 + 18 = 48; гайка астында шайба 3 + гайка 16 = 67 ≤ 70
    }
    double bov = QBoltFrameOverlap(c, bsA); if (bov > 50) sb.AppendLine("  WARN болт (ПБ–консоль) шайба/бастиек/гайка ↔ каркас " + QF(bov) + " мм3");
    QEmitBolts(c, bsA, "bA", "5", 20, 70, sides.Count * 2, "8.8", "ПБ табаны Ø33 + консоль Ø23 (каркаста тесік модельденбейді)");
    // ---- поз.7 белдеу накладкасы −12×100×240 ×2 (тек екі жақты: стык бар) + поз.8 болт М20 l50 (пакет 12 + 18 = 30; гайка ПБ жоғарғы белдеуінің астында)
    if (two)
    {
        var pNk = QPart(c, "nk", cS, "Узел 5: накладка белдеу −12×100×240", "поз.7 белдеу накладкасы −12×100×240 С245, ПБ жоғарғы белдеуі үстінде рельс табанының екі жағында, x −120…120, y = рельс ± (60…160), 2 тесік Ø23 (2 дана)");
        foreach (double sy in new[] { 1.0, -1.0 })
            QPut(c, pNk, QBoxA(f, 'z', 5986, 5998, -120, 120, sy > 0 ? YR + 60 : YR - 160, sy > 0 ? YR + 160 : YR - 60, QSo(d, "накладка"), new[] { new[] { -80.0, YR + sy * 110, 23.0 }, new[] { 80.0, YR + sy * 110, 23.0 } }, sb, "накладка"), true, true);
        var bsB = new QBoltSet(); int nB = 0;
        foreach (int sx in sides)
        {
            QBolt(bsB, f.Mm(sx * 80, YR + 110, 5998), new XYZ(0, 0, -1), 30, 50, 20, false, true, soB, sb); nB++;
        }
        QEmitBolts(c, bsB, "bB", "5", 20, 50, nB, "8.8", "накладка + ПБ белдеуі, пакет 12 + 18");
        double bov2 = QBoltFrameOverlap(c, bsB); if (bov2 > 50) sb.AppendLine("  WARN болт (накладка) шайба/бастиек/гайка ↔ каркас " + QF(bov2) + " мм3");
        if (BUILD_TODO_SURAQ)
        {
            var bsC = new QBoltSet(); int nC = 0;
            foreach (int sx in sides) { QBolt(bsC, f.Mm(sx * 80, YR - 110, 5998), new XYZ(0, 0, -1), 42, 60, 20, false, false, soB, sb); nC++; }       // шешім №3: l 60, пакет 42; гайка астында шайба жоқ (42 + 16 = 58 ≤ 60; шайбамен 61 > 60)
            QEmitBolts(c, bsC, "bC", "5", 20, 60, nC, "8.8", "шешім №3: накладка 12 + ПБ белдеуі 18 + тартпа 12 = пакет 42, l 60, гайка астында шайба жоқ (42 + 16 = 58 ≤ 60); тартпа тесігі жиекке 1,5 мм шығады");
        }
        else sb.AppendLine("  TODO_SURAQ: накладка болттары y = рельс − 110 (" + sides.Count + " дана): гайка/бастиек тартпамен (y ≤ рельс − 100) қиылысады — салынбады");
    }
    // ---- поз.9 тартпа −12×150×L (A/G 160, D 226): ШЕШІМ №5 (13.11) — x 0…150 (sx<0: −150…0) (бұрын 35…185: К1 полкасынан (±150) 35 мм шығатын); y 540 … (ПБ белдеуі шеті + 100) = YR − 100, z 5956…5968 (ПБ жоғарғы белдеуі астына зауыттық kf 6 — ПБ маркасымен); тесік Ø23 (колонна болттары үшін, x ±35 және ±115 — 35 мм-ге бірге жылжыған; болттар САЛЫНБАЙДЫ — шешім №4, TODO_KRAN), y 595 (колонна бетінен 63)
    double tEnd = YR - 100, yFl = YR - 200;
    var soT = QSo(d, "тартпа"); var soU = QSo(d, "уголок");
    var pendWelds = new List<Action>();      // ПБ тірек қабырғасының швтары: тартпа мен уголоктан КЕЙІН салынады (шов қиылысқанда шов кесіледі)
    foreach (int sx in sides)
    {
        double xa = Math.Min(sx * 0.0, sx * 150.0), xb = Math.Max(sx * 0.0, sx * 150.0);
        var pTp = QPart(c, "tp", cS, "Узел 5: тартпа −12×150×" + QF(tEnd - 540), "поз.9 тартпа −12×150×" + QF(tEnd - 540) + " С245, x " + (sx > 0 ? "0…150" : "−150…0") + " (шешім №5: К1 полкасы ±150 ішінде), y 540…" + QF(tEnd) + ", z 5956…5968 (ПБ жоқарғы белдеуі астында), 2 тесік Ø23 (колонна болттары: САЛЫНБАЙДЫ, TODO_KRAN) + накладка болтына тесік Ø23 (y = рельс − 110, жиекке 1,5 мм шығады); тірек қабырғасы мен прокладкамен қиылысатын жері кесілген (2 дана)");
        var tp = QBoxA(f, 'z', 5956, 5968, xa, xb, 540, tEnd, soT, new[] { new[] { sx * 35.0, 595.0, 23.0 }, new[] { sx * 115.0, 595.0, 23.0 } }, sb, "тартпа");
        if (two) { try { tp = QDrill(tp, f.Mm(sx * 80, YR - 110, 5962), new XYZ(0, 0, 1), 23); } catch (Exception ex) { sb.AppendLine("  WARN тартпа тесігі (накладка болты) салынбады: " + ex.Message); } }
        QPut(c, pTp, tp, true, true);
        W(pW6, QV3(sx * 150, yFl, 5968), QV3(sx * 150, tEnd, 5968), QV3(sx, 0, 0), QV3(0, 0, -1), 6);          // сыртқы ұшы (x = ±150); ішкі ұшы (x = 0) екі тартпаның түйісуі — шов салынбайды
        W(pW6, QV3(sx * 0, tEnd, 5968), QV3(sx * 150, tEnd, 5968), QV3(0, 1, 0), QV3(0, 0, -1), 6);
        // ---- поз.10 ∟110×8 l150: тік полка К1 полкасының бетінде (y 532…540, z 5948…6058), көлденең полка z 5948…5956 (y 540…642); сопақ тесік 50 (x) × 28 (y), x ±35, ±115 (шешім №5), y 595; К1 полкасына зауыттық kf 6
        var pUg = QPart(c, "ug", cS, "Узел 5: уголок ∟110×8 l150", "поз.10 уголок ∟110×8 l150 С245, К1 полкасының бетінде (x " + (sx > 0 ? "0…150" : "−150…0") + ", шешім №5); көлденең полка тартпа астында (z 5948…5956), сопақ тесік 50×28 (X бойы) ×2 (x ±35, ±115: тесік жиегінен уголок ұшына 10 мм < 1,5d — шешім №5 бойынша есепте «бұзушылық»), К1 полкасына зауыттық kf 6 (2 дана)");
        var ug = QExtrude(f, 'x', xa, 150, new[] { 532.0, 5948, 642, 5948, 642, 5956, 540, 5956, 540, 6058, 532, 6058 }, soU, null, sb, "уголок");
        try { foreach (double hx in new[] { sx * 35.0, sx * 115.0 }) ug = QDiff(ug, QSlotCutter(f, hx, 595, 5940, 24, 50, 28)); }
        catch (Exception ex) { sb.AppendLine("  WARN сопақ тесік салынбады (" + ex.Message + ") — уголок тесіксіз"); }
        QPut(c, pUg, ug, true, true);
        W(pW6, QV3(sx * 0, 532, 6058), QV3(sx * 150, 532, 6058), QV3(0, 0, 1), QV3(0, 1, 0), 6);              // перо бойымен (жоғарғы қыр); ішкі ұшы (x = 0) — екі уголок түйісуі, шов салынбайды; сыртқы ұшы x = ±150 = К1 полкасының шеті — шов салынбайды (полкадан тыс)
        // ПБ тірек қабырғасы шовтары (шешім №2: kf 6 зауыттық): қабырғаның ішкі беті x = ±30 бойынша — стенка мен екі белдеумен; шов бұрышында (стенка шовы — белдеу шовымен қиылыспасын, 6 мм қысқарған)
        foreach (double sgn in new[] { 1.0, -1.0 })
        {
            double xs = sx * 30, ys = YR + sgn * 6, ye = YR + sgn * 150; double sxx = sx, sg0 = sgn;
            pendWelds.Add(() => {
                W(pW6, QV3(xs, ys, 5224), QV3(xs, ys, 5962), QV3(0, sg0, 0), QV3(sxx, 0, 0), 6);                // қабырға–ПБ стенкасы
                W(pW6, QV3(xs, ys, 5968), QV3(xs, ye, 5968), QV3(sxx, 0, 0), QV3(0, 0, -1), 6);                 // қабырға–жоғарғы белдеу асты
                W(pW6, QV3(xs, ys, 5218), QV3(xs, ye, 5218), QV3(sxx, 0, 0), QV3(0, 0, 1), 6); });              // қабырға–астыңғы белдеу үсті
        }
    }
    foreach (var pw in pendWelds) pw();
    sb.AppendLine("  шешім №5: тартпа/уголок x 0…150 (К1 полкасы ±150 ішінде); сопақ тесік жиегінен уголок ұшына 10 мм (< 1,5d = 30) — бұзушылық; шешім №2: тірек қабырғасы шовы kf 6 (ішкі бет x ±30 бойынша)");
    sb.AppendLine("  TODO_KRAN: поз.11 тартпа болттары (М20 l50 ×" + (sides.Count * 2) + ") салынбады (шешім №4); тартпа тесігі Ø23");
    // ---- поз.12 рельс Р24 (шартты профиль), ПБ осінде: z 5986…6093; кесінді x −300…300 (екі жақты) немесе 334…934 (ось 1/11: рельс ұшы x 334 — uzel_06). TODO_KRAN: бекітпе, буфер
    double rx0 = two ? -RAIL_HALF : 334, rx1 = two ? RAIL_HALF : 334 + 2 * RAIL_HALF;
    double rh = RAIL_HEAD_TOP;
    var pRl = QPart(c, "rl", cS, "Узел 5: рельс Р24 l" + QF(rx1 - rx0), "поз.12 рельс Р24 ГОСТ 6368 (шартты профиль: табан 92×12, стенка 10,9, бас 51×31; z 5986…" + QF(rh) + "), ПБ осінде, бекітуі — кран паспорты (TODO_KRAN; кесінді ұзындығы шартты)");
    double[] rp = { -46, 5986, 46, 5986, 46, 5998, 5.45, 5998, 5.45, rh - 31, 25.5, rh - 31, 25.5, rh, -25.5, rh, -25.5, rh - 31, -5.45, rh - 31, -5.45, 5998, -46, 5998 };
    var rq = new double[rp.Length]; for (int i = 0; i < rp.Length; i += 2) { rq[i] = YR + rp[i]; rq[i + 1] = rp[i + 1]; }
    QPut(c, pRl, QExtrude(f, 'x', rx0, rx1 - rx0, rq, QSo(d, "рельс"), null, sb, "рельс"), true, true);
    int n = QEmit(c);
    sb.AppendLine("  салынды: DS " + n + ", өткізілген бөлшек " + c.SkippedParts + ", тазалау Σ " + QF(c.Removed) + " мм3, clean-булев құлаулары " + c.CleanFail);
    return true;
}
