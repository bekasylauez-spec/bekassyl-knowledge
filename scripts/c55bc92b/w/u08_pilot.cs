// РМЦ КМ: УЗЕЛ 8 / 8а / 8б — К1-де +6,000 деңгейі: распорка Р1 + жоғарғы ярус связінің төменгі ұшы (СВ1 / СВ2) + (8а, 8б) төменгі ярус связінің жоғарғы ұшы (СВ3 / СВ5). Паспорт: _авто\spec\uzel_08.md (әр сан содан).
//   8  — A, D, G × осьтер 1, 2, 10, 11 (12 орын): СВ1 (A/G) немесе СВ2 (D) + Р1;   8а — A/4, A/5, D/4, D/5, D/7, D/8 (6): СВ1/СВ2 + СВ3 + Р1;   8б — A/7, A/8, G/4, G/5, G/7, G/8 (6): СВ1 + СВ5 + Р1.   Барлығы 24.
// Гусет −20 С245 К1 стенкасына (x = 4) — зауыттық kf 8 екі жағынан. Колоннаның екінші жағындағы Р1 ұшы — узел 12 (мұнда салынбайды).
// ЖАЗЫЛҒАН 13.11.2026, Revit-те ІСКЕ ҚОСЫЛМАҒАН (тек Roslyn-мен компиляцияланған). Іске қосу: go.ps1 -Name rmc_u08 -Lib rmc_brace_lib.cs   (лог: _авто\_rmc_u08.txt).
// ТАЛАП: каркас дайын (СВ ұштары паспорттағы «құбыр ұшы» нүктелерінде; Р1 төменгі осі Y_c + 28). Құбыр ұшы паспорттан > 1,5 мм ауытқыса — орын SKIP.
// Әр орынға бөлек DirectShape: ApplicationDataId «узел 8а | 4-A». Қайта іске қосқанда нысана орындардағы өз денелері өшіріледі.
// Локаль: x — колонна осінен связь аралығына (глобал ±X: ось 1,4,7,10 → +X; 2,5,8,11 → −X), y — глобал Y, z — абсолют. Жазықтықтар: СВ осі Y_c (A 266 / D 17 986 / G 35 734); гусет Y_c+4…+24 (орта Y_c+14); Р1 осі Y_c+28.
// Бақылау (python, ub_pass_check.py): вставка(СВ) ↔ Р1 құбыры арақашықтығы 0,1…0,5 мм (8 A/G 0,4; 8а-D 0,1; 8а-A 0,5; 8б 0,5) — паспорт «тимейді» дейді, бірақ саңылау өте аз (СҰРАҚ). CLEAN режимі қиылысқан көлемді алып тастайды (логта).
return RunU08(document);
}
const bool PILOT = true;                          // true: тек PILOT_LOCS (8: «1-A», 8а: «4-A», 8б: «7-A»); false: барлық 24 орын
static readonly string[] PILOT_LOCS = { "1-A", "4-A", "7-A" };
const string OVERLAP_MODE = "CLEAN";
const bool BUILD_TODO_SURAQ = false;

class U8Loc { public int ax; public string row, loc, key, v; public int sg; public bool bay12; public double xc, yc, ycol; }
// гусет контурлары (x;z), паспорт l.28–32
static readonly double[] G8A = { 4, 6100, 148, 6218, 240, 6257, 302, 6109, 270, 6075, 155, 6075, 155, 6085, 141, 6085, 141, 5936, 126, 5920, 4, 5900 };
static readonly double[] G8D = { 4, 6100, 84, 6210, 171, 6260, 251, 6122, 222, 6075, 155, 6075, 155, 6085, 141, 6085, 141, 5944, 126, 5920, 4, 5900 };
static readonly double[] G8aA = { 51, 5794, 4, 5900, 4, 6100, 154, 6218, 246, 6257, 307, 6109, 296, 6075, 155, 6075, 155, 6085, 141, 6085, 141, 5915, 155, 5915, 155, 5925, 248, 5925, 227, 5860, 130, 5733 };
static readonly double[] G8aD = { 51, 5794, 4, 5900, 4, 6100, 86, 6209, 173, 6259, 252, 6120, 248, 6075, 155, 6075, 155, 6085, 141, 6085, 141, 5915, 155, 5915, 155, 5925, 234, 5925, 227, 5860, 130, 5733 };
static readonly double[] G8b = { 183, 5779, 4, 5900, 4, 6100, 154, 6218, 246, 6257, 307, 6109, 311, 6075, 155, 6075, 155, 6085, 141, 6085, 141, 5915, 155, 5915, 155, 5925, 329, 5925, 332, 5895, 277, 5745 };

static string RunU08(Document d)
{
    var targets = new List<BTarget>();
    foreach (string row in new[] { "A", "D", "G" }) for (int ax = 1; ax <= 11; ax++)
    {
        string v = null;
        if (ax == 1 || ax == 2 || ax == 10 || ax == 11) v = "8";
        else if (row == "A" && (ax == 4 || ax == 5)) v = "8а"; else if (row == "D" && (ax == 4 || ax == 5 || ax == 7 || ax == 8)) v = "8а";
        else if (row == "A" && (ax == 7 || ax == 8)) v = "8б"; else if (row == "G" && (ax == 4 || ax == 5 || ax == 7 || ax == 8)) v = "8б";
        if (v == null) continue;
        var L = new U8Loc { ax = ax, row = row, v = v, loc = ax + "-" + row, key = "узел " + v, sg = (ax == 1 || ax == 4 || ax == 7 || ax == 10) ? 1 : -1, bay12 = (ax == 1 || ax == 2 || ax == 10 || ax == 11), xc = BL.AXX[ax - 1],
            yc = row == "A" ? 266 : row == "G" ? 35734 : 17986, ycol = row == "A" ? 266 : row == "G" ? 35734 : 18000 };
        if (PILOT && Array.IndexOf(PILOT_LOCS, L.loc) < 0) continue;
        targets.Add(new BTarget { Loc = L.loc, Key = L.key, Data = L });
    }
    var tubes = BL.Tubes(d); var cols = BL.ColsK1(d);
    return BL.Drive(d, "узел 8/8а/8б (PILOT=" + PILOT + ", Mode=" + OVERLAP_MODE + ")", targets, (tg, sb) => BuildU08(d, sb, tg, tubes, cols));
}

static bool BuildU08(Document d, StringBuilder sb, BTarget tg, List<FamilyInstance> tubes, List<FamilyInstance> cols)
{
    var L = (U8Loc)tg.Data; string loc = L.loc; bool D = L.row == "D";
    var col = cols.FirstOrDefault(c => { var p = ((LocationPoint)c.Location).Point; return Math.Abs(p.X / BL.MM - L.xc) < 5 && Math.Abs(p.Y / BL.MM - L.ycol) < 5; });
    if (col == null) { sb.AppendLine("SKIP " + tg.Key + " | " + loc + ": К1 (" + BL.F(L.xc) + "; " + BL.F(L.ycol) + ") нүктесінде жоқ"); return false; }
    var f = BL.VertF(L.xc, L.sg); double yc = L.yc; XYZ Y = new XYZ(0, 1, 0);
    // ---- нұсқа: гусет контуры, жоғарғы диагональ ұшы, төменгі диагональ
    double[] gxz, eUp, eLo = null; string upMark = D ? "СВ2" : "СВ1", loMark = null;
    if (L.v == "8") { gxz = D ? G8D : G8A; eUp = D ? new[] { 231.7, 6203.6 } : new[] { 293.1, 6192.5 }; }
    else if (L.v == "8а") { gxz = D ? G8aD : G8aA; eUp = D ? new[] { 233.2, 6201.1 } : new[] { 298.9, 6191.7 }; eLo = new[] { 197.9, 5781.8 }; loMark = "СВ3"; }
    else { gxz = G8b; eUp = new[] { 298.9, 6191.7 }; eLo = new[] { 327.1, 5811.8 }; loMark = "СВ5"; }
    // q20 (13.11.2026, шешім): бір қырымен пісірілген гусет шығысы ≤ 15 t → қалыңдық сортамент қатарынан арттырылады: 8б (328 мм) және 8а-A (303 мм) −25 (бұрын −20); қалғандары −20 (298/248/247 мм ≤ 15·20).
    // Контур өзгермейді; гусет ОРТА жазықтығы орнында (yc+14), вставкалар гусет бетіне тақалады (СВ вставкасы yg0−8…yg0, Р1 вставкасы yg0+t…yg0+t+8; құбыр осьтері өзгермейді → вставка құбыр осінен (t−20)/2 ығысады); болт l = пакет + 30, 5-ке дейін жоғары.
    double tg20 = (L.v == "8б" || (L.v == "8а" && !D)) ? 25 : 20, ymid = yc + 14, yg0 = ymid - tg20 / 2;
    var gmm = BL.PolyXZmm(f, yg0, gxz);
    // М20 8.8 (связь), пакет t + 8 (l 60 / t25: 65); М16 8.8 (Р1), пакет t + 8 (l 55 / t25: 65)
    double lbSv = tg20 == 20 ? 60 : 5 * Math.Ceiling((tg20 + 8 + 30) / 5), lbR = tg20 == 20 ? 55 : 5 * Math.Ceiling((tg20 + 8 + 30) / 5);
    Func<string, double[], BSpec> sv = (mk, e) => new BSpec { Tag = mk, Mark = mk, E = f.Mm(e[0], yc, e[1]), PlaneP = new XYZ(L.xc, yg0 - 4, 0), N = Y, B = 140, Ti = 8, Wi = 160, CapW = 160, CapH = 160, Bolt = 20, Ebolt = 30, Lbolt = lbSv, Tg = tg20, GPoly = gmm };
    var spUp = sv(upMark, eUp); var spLo = loMark == null ? null : sv(loMark, eLo);
    var spR = new BSpec { Tag = "Р1", Mark = "Р1", E = f.Mm(150, yc + 28, 6000), PlaneP = new XYZ(L.xc, yg0 + tg20 + 4, 0), N = -Y, B = 140, Ti = 8, Wi = 160, CapW = 160, CapH = 160, Bolt = 16, Ebolt = 30, Lbolt = lbR, Tg = tg20, GPoly = gmm };
    var allPts = new List<XYZ>(gmm); allPts.Add(spUp.E); allPts.Add(spR.E); if (spLo != null) allPts.Add(spLo.E);
    var c = new BCtx { D = d, L = sb, Key = tg.Key, Loc = loc, Lbl = L.v, Mode = OVERLAP_MODE }; c.Obst = BL.Obstacles(d, BL.BBoxOf(allPts, 400), tg.Key, loc);
    var cS = BuiltInCategory.OST_StructConnections; var cW = BuiltInCategory.OST_StructConnectionWelds; var soW = BL.So(d, "шов");
    sb.AppendLine("== " + tg.Key + " | " + loc + ": К1 табылды, кедергі солидтер " + c.Obst.Count + ", жоғарғы " + upMark + " ұшы (" + BL.F(spUp.E.X) + "; " + BL.F(spUp.E.Y) + "; " + BL.F(spUp.E.Z) + ")" + (spLo != null ? ", төменгі " + loMark : "") + ", Р1 ұшы (" + BL.F(spR.E.X) + "; " + BL.F(spR.E.Y) + "; " + BL.F(spR.E.Z) + ")");
    var rUp = BL.BuildEnd(d, spUp, tubes, sb); var rLo = spLo == null ? null : BL.BuildEnd(d, spLo, tubes, sb); var rR = BL.BuildEnd(d, spR, tubes, sb);
    if (rUp == null || rR == null || (spLo != null && rLo == null)) { sb.AppendLine("SKIP " + tg.Key + " | " + loc + ": құбыр ұшы(тар) табылмады (каркас қайта салынбаған?) — ештеңе салынбайды"); return false; }
    // ---- поз.1 гусет −20 С245: y = yc+4 … yc+24 (орта Y_c+14); тесіктер: СВ Ø23 (×2 немесе ×4), Р1 Ø18 (×2)
    var holes = BL.HolesOn(new[] { rUp, rLo, rR }, new XYZ(L.xc, yg0, 0), Y);
    string gab = BL.Gab(tg20, gxz);
    var pG = BL.Part(c, "gus", cS, "Узел " + L.v + ": гусет " + gab, "поз.1 гусет " + gab + " С245 (1 дана), контур uzel_08 (" + L.v + (D ? ", D" : "") + "), К1 стенкасына (x=4) зауыттық kf 8 екі жағынан; " + holes.Count + " тесік");
    BL.Put(c, pG, BL.Prism(BL.PolyXZ(f, yg0, gxz), Y, tg20, BL.So(d, "фасонка"), holes, sb, "гусет " + L.v), true);
    // ---- гусет–стенка шовы: x = 4, z 5900…6100, екі бетінен kf 8 (зауыттық)
    var pW8 = BL.Part(c, "w8g", cW, "Узел " + L.v + ": шов зауыттық kf8 (гусет–К1)", "поз.1 гусет–К1 стенкасы — зауыттық kf 8, екі жағынан (К1 маркасымен)");
    foreach (double yf in new[] { yg0, yg0 + tg20 }) { double o = yf < ymid ? -1 : 1; BW.Add(pW8, f.Mm(4, yf, 5900), f.Mm(4, yf, 6100), f.V(0, o, 0), f.V(1, 0, 0), 8, soW); }
    BL.PutEnd(c, rUp, spUp); if (rLo != null) BL.PutEnd(c, rLo, spLo); BL.PutEnd(c, rR, spR);
    int n = BL.Emit(c);
    sb.AppendLine("  салынды: DS " + n + ", өткізілген бөлшек " + c.Skipped + ", тазалау Σ " + BL.F(c.Removed) + " мм3");
    return true;
}
