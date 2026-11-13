// ===== rmc_misc_lib.cs — РМЦ КМ узелдері 5, 6, 17/17а, 18, 19/19а, 20 үшін өз көмекшім. ЖАЗЫЛҒАН 13.11.2026, Revit-те ІСКЕ ҚОСЫЛМАҒАН (тек Roslyn компиляциясы).
// rmc_node_lib.cs-ке ТӘУЕЛСІЗ: керек көмекшілер сол үлгіден көшірілген (қайта атау префиксі «Q»; қақтығыс жоқ — екі lib бірге қосылса да).
// Қолдану: go.ps1 -Name rmc_u05 -Lib rmc_misc_lib.cs   (run.ps1 скриптке осы файлды тіркейді; соңғы әдіс _libEnd әдейі ашық — runner жабады).
// Ережелер: КМ_стандарт 03 §6 — әр орынға бөлек DirectShape, ApplicationDataId «узел N | <орын>», №117 түстер «КМ_уз_*», шов = үшбұрыш белдік,
// қайта іске қосқанда нысана орындардағы «узел N» денелері өшіріледі, белсенді құжат тексеріледі. Каркас ӨЗГЕРТІЛМЕЙДІ (тек 19/20-да колонна/балка басын void-пен кесу).
const double QMM = 1 / 304.8;
static readonly System.Globalization.CultureInfo QCI = System.Globalization.CultureInfo.InvariantCulture;
static XYZ QP(double x, double y, double z) { return new XYZ(x * QMM, y * QMM, z * QMM); }
static string QF(double v) { return (Math.Round(v, 2) + 0.0).ToString(QCI); }     // + 0.0: «-0» → «0»
class QSwallow : IFailuresPreprocessor { public static List<string> Errs = new List<string>(); public FailureProcessingResult PreprocessFailures(FailuresAccessor a) {
    bool bad = false; foreach (var m in a.GetFailureMessages()) { if (m.GetSeverity() == FailureSeverity.Warning) a.DeleteWarning(m); else { bad = true; Errs.Add(m.GetDescriptionText() + " [ids " + string.Join(",", m.GetFailingElementIds().Select(i => i.Value.ToString())) + "]"); } }
    return bad ? FailureProcessingResult.ProceedWithRollBack : FailureProcessingResult.Continue; } }      // қате = диалогсыз RollBack (13.11: диалог Revit-ті іркіп, жартылай күй қалдырды); Errs-ті QCommit логқа жазады
static bool QCommit(Transaction t, StringBuilder sb) {
    QSwallow.Errs.Clear(); var st = t.Commit();
    if (st != TransactionStatus.Committed || QSwallow.Errs.Count > 0) { sb.AppendLine("COMMIT " + st + ": " + string.Join(" | ", QSwallow.Errs.Distinct())); return false; } return true; }
static ElementId QMatId(Document d, string name, Color c) {
    var m = new FilteredElementCollector(d).OfClass(typeof(Material)).Cast<Material>().FirstOrDefault(x => x.Name == name);
    if (m == null) { m = d.GetElement(Material.Create(d, name)) as Material; m.Color = c; m.MaterialClass = "Металл"; }
    m.Color = c; m.Shininess = 0; m.Smoothness = 0; return m.Id; }
// №117 палитрасы (КМ_стандарт §6) + ЖАҢА түрлер (стандарт кестесіне қосу ұсынылады): «рельс», «стойка», «швеллер», «тартпа» — осы түрлердің түсін ереже чатына растату керек
static SolidOptions QSo(Document d, string part) {
    var pal = new Dictionary<string, int[]> { { "плита", new[] { 70, 130, 180 } }, { "ребро", new[] { 60, 160, 90 } }, { "столик", new[] { 230, 150, 30 } },
        { "ребро_столика", new[] { 150, 100, 50 } }, { "накладка", new[] { 210, 100, 230 } }, { "накладка_Б5", new[] { 0, 150, 160 } }, { "уголок", new[] { 130, 90, 170 } }, { "фасонка", new[] { 200, 60, 60 } },
        { "вставка", new[] { 120, 150, 30 } }, { "заглушка", new[] { 150, 150, 150 } }, { "фланец", new[] { 40, 80, 150 } }, { "прокладка", new[] { 210, 180, 60 } },
        { "брус", new[] { 160, 120, 80 } }, { "болт", new[] { 60, 60, 60 } }, { "шов", new[] { 110, 110, 110 } },
        { "рельс", new[] { 95, 100, 115 } }, { "стойка", new[] { 160, 60, 150 } }, { "швеллер", new[] { 210, 120, 160 } }, { "тартпа", new[] { 235, 90, 150 } } };
    var c = pal[part]; return new SolidOptions(QMatId(d, "КМ_уз_" + part, new Color((byte)c[0], (byte)c[1], (byte)c[2])), ElementId.InvalidElementId); }

// ---------------- осьтер / орын атауы
static readonly double[] QAXX = { 150, 6000, 12000, 18000, 24000, 30000, 36000, 42000, 48000, 54000, 59850 };
static int QAxisNo(double x) { for (int i = 0; i < QAXX.Length; i++) if (Math.Abs(QAXX[i] - x) < 60) return i + 1; return 0; }
static string QRowOf(double y) {
    if (Math.Abs(y - 266) < 400) return "A"; if (Math.Abs(y - 6000) < 400) return "B"; if (Math.Abs(y - 12000) < 400) return "C"; if (Math.Abs(y - 18000) < 400) return "D";
    if (Math.Abs(y - 24000) < 400) return "E"; if (Math.Abs(y - 30000) < 400) return "F"; if (Math.Abs(y - 35734) < 400) return "G"; return "?"; }

// ---------------- жергілікті жүйе: Global = O + x·A + y·B (план), z абсолют. A, B — бірлік векторлар (X/Y таңбасымен; айналы жүйе рұқсат)
class QFrm {
    public double Ox, Oy, Ax, Ay, Bx, By;
    public QFrm(double ox, double oy, double ax, double ay, double bx, double by) { Ox = ox; Oy = oy; Ax = ax; Ay = ay; Bx = bx; By = by; }
    public XYZ Mm(double x, double y, double z) { return new XYZ(Ox + x * Ax + y * Bx, Oy + x * Ay + y * By, z); }          // мм, глобал
    public XYZ Pt(double x, double y, double z) { return Mm(x, y, z) * QMM; }                                                  // feet
    public XYZ V(double x, double y, double z) { return new XYZ(x * Ax + y * Bx, x * Ay + y * By, z); }                        // бағыт векторы
    public double Gy(double y) { return Oy + y * By; }      // ТЕК ось-параллель жүйелерде (x ось жергілікті y-ке тәуелсіз): жалпы жағдайда Mm(...).Y қолдан
    public double Gx(double x) { return Ox + x * Ax; }
}
static QFrm QRowFrm(double fx, double oy, double sy) { return new QFrm(fx, oy, 1, 0, 0, sy); }

// ---------------- геометрия (rmc_node_lib.cs-тен көшірілген, Q префиксімен)
static XYZ QNewell(IList<XYZ> p) {
    double nx = 0, ny = 0, nz = 0; int n = p.Count;
    for (int i = 0; i < n; i++) { var a = p[i]; var b = p[(i + 1) % n]; nx += (a.Y - b.Y) * (a.Z + b.Z); ny += (a.Z - b.Z) * (a.X + b.X); nz += (a.X - b.X) * (a.Y + b.Y); }
    return new XYZ(nx, ny, nz); }
static CurveLoop QLoopPts(IList<XYZ> p) { var lp = new CurveLoop(); int n = p.Count; for (int i = 0; i < n; i++) lp.Append(Line.CreateBound(p[i], p[(i + 1) % n])); return lp; }
static void QAxes(XYZ n, out XYZ e1, out XYZ e2) { XYZ r = Math.Abs(n.Z) > 0.9 ? XYZ.BasisX : XYZ.BasisZ; e1 = (r - n * r.DotProduct(n)).Normalize(); e2 = n.CrossProduct(e1).Normalize(); }
static CurveLoop QCircLoop(XYZ c, XYZ n, double dia, bool ccw) {
    XYZ e1, e2; QAxes(n, out e1, out e2); double r = dia / 2 * QMM; var lp = new CurveLoop();
    if (ccw) { lp.Append(Arc.Create(c + e1 * r, c - e1 * r, c + e2 * r)); lp.Append(Arc.Create(c - e1 * r, c + e1 * r, c - e2 * r)); }
    else { lp.Append(Arc.Create(c + e1 * r, c - e1 * r, c - e2 * r)); lp.Append(Arc.Create(c - e1 * r, c + e1 * r, c + e2 * r)); }
    return lp; }
class QHole { public XYZ C; public double D; public QHole(XYZ c, double d) { C = c; D = d; } }
static Solid QExtr(List<CurveLoop> loops, XYZ dir, double lenFeet, SolidOptions so) { return GeometryCreationUtilities.CreateExtrusionGeometry(loops, dir, lenFeet, so); }
// көпбұрыш (feet, бір жазықтықта) + dir бойымен lenMm экструзия; тесіктер (центрі көпбұрыш жазықтығында, осі = dir). Көлем (area·len − тесіктер) тексеріледі.
static Solid QPrism(IList<XYZ> pts, XYZ dir, double lenMm, SolidOptions so, IList<QHole> holes, StringBuilder log, string what) {
    dir = dir.Normalize(); var pl = new List<XYZ>(pts); XYZ nw = QNewell(pl); if (nw.DotProduct(dir) < 0) { pl.Reverse(); nw = nw.Negate(); }
    double len = lenMm * QMM;
    if (holes == null || holes.Count == 0) return QExtr(new List<CurveLoop> { QLoopPts(pl) }, dir, len, so);
    double hv = 0; foreach (var h in holes) hv += Math.PI * Math.Pow(h.D / 2 * QMM, 2);
    double want = (nw.GetLength() / 2 - hv) * len;
    foreach (bool ccw in new[] { false, true }) {
        var loops = new List<CurveLoop> { QLoopPts(pl) }; foreach (var h in holes) loops.Add(QCircLoop(h.C, dir, h.D, ccw));
        Solid s = null; try { s = QExtr(loops, dir, len, so); } catch (Exception ex) { if (log != null) log.AppendLine("  " + what + " extrusion ccw=" + ccw + " failed: " + ex.Message.Split('\n')[0]); continue; }
        if (Math.Abs(s.Volume - want) < 0.002 * want) return s;
        if (log != null) log.AppendLine("  " + what + " ccw=" + ccw + " volume " + QF(s.Volume / QMM / QMM / QMM) + " != " + QF(want / QMM / QMM / QMM)); }
    throw new Exception("hole extrusion failed: " + what); }
static Solid QCylS(XYZ c, XYZ n, double dia, double lenMm, SolidOptions so) { return QExtr(new List<CurveLoop> { QCircLoop(c, n, dia, true) }, n, lenMm * QMM, so); }
static List<XYZ> QHexPts(XYZ c, XYZ n, double S) {
    XYZ e1, e2; QAxes(n, out e1, out e2); double R = S / Math.Sqrt(3) * QMM; var r = new List<XYZ>();
    for (int i = 0; i < 6; i++) r.Add(c + (e1 * Math.Cos(i * Math.PI / 3) + e2 * Math.Sin(i * Math.PI / 3)) * R); return r; }
static Solid QHexS(XYZ c, XYZ n, double S, double lenMm, double holeDia, SolidOptions so, StringBuilder log, string what) {
    return QPrism(QHexPts(c, n, S), n, lenMm, so, holeDia > 0 ? new List<QHole> { new QHole(c, holeDia) } : null, log, what); }
static Solid QRingS(XYZ c, XYZ n, double dout, double din, double lenMm, SolidOptions so, StringBuilder log, string what) {
    double want = Math.PI / 4 * (dout * dout - din * din) * QMM * QMM * lenMm * QMM;
    foreach (bool ccw in new[] { false, true }) {
        var loops = new List<CurveLoop> { QCircLoop(c, n, dout, true), QCircLoop(c, n, din, ccw) };
        Solid s = null; try { s = QExtr(loops, n, lenMm * QMM, so); } catch { continue; }
        if (Math.Abs(s.Volume - want) < 0.002 * want) return s; }
    throw new Exception("ring extrusion failed: " + what); }
// тесік Ø dia (мм) нүкте (мм, глобал) арқылы, ось ax бойымен (±60 мм) — булев айырма (еңіс бетке перпендикуляр тесіктер үшін)
static Solid QDrill(Solid s, XYZ cMm, XYZ ax, double dia) {
    ax = ax.Normalize(); var cyl = QCylS((cMm - ax * 60) * QMM, ax, dia, 120, new SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId));
    var r = BooleanOperationsUtils.ExecuteBooleanOperation(s, cyl, BooleanOperationsType.Difference); if (r == null || r.Volume < 1e-12) throw new Exception("drill failed"); return r; }

// ---------------- жергілікті осьтік экструзия: ax = 'x'|'y'|'z' (жергілікті ось), lvl — бастапқы деңгей, len — +ось бойымен ұзындық (мм), pq — (p,q) жұптары жазықтықта:
// ax='x': (p,q) = (y,z); ax='y': (x,z); ax='z': (x,y). holes: (p, q, диаметр). Тесіктер ось бойымен өтеді.
static XYZ QAxisDir(QFrm f, char ax) { return ax == 'x' ? f.V(1, 0, 0) : ax == 'y' ? f.V(0, 1, 0) : f.V(0, 0, 1); }
static XYZ QPl(QFrm f, char ax, double lvl, double p, double q) { return ax == 'x' ? f.Pt(lvl, p, q) : ax == 'y' ? f.Pt(p, lvl, q) : f.Pt(p, q, lvl); }
static Solid QExtrude(QFrm f, char ax, double lvl, double len, double[] pq, SolidOptions so, double[][] holes, StringBuilder log, string what) {
    if (len < 0) { lvl += len; len = -len; }
    var pts = new List<XYZ>(); for (int i = 0; i + 1 < pq.Length; i += 2) pts.Add(QPl(f, ax, lvl, pq[i], pq[i + 1]));
    List<QHole> hl = null; if (holes != null && holes.Length > 0) { hl = new List<QHole>(); foreach (var h in holes) hl.Add(new QHole(QPl(f, ax, lvl, h[0], h[1]), h[2])); }
    return QPrism(pts, QAxisDir(f, ax), len, so, hl, log, what); }
// тікбұрышты қорап: ось бойымен [lo, hi], қима p0..p1 × q0..q1 (қима координаталары жоғарыдағыдай)
static Solid QBoxA(QFrm f, char ax, double lo, double hi, double p0, double p1, double q0, double q1, SolidOptions so, double[][] holes, StringBuilder log, string what) {
    return QExtrude(f, ax, lo, hi - lo, new[] { p0, q0, p1, q0, p1, q1, p0, q1 }, so, holes, log, what); }
static Solid QBox(QFrm f, double x0, double x1, double y0, double y1, double z0, double z1, SolidOptions so, StringBuilder log, string what) {
    return QBoxA(f, 'z', z0, z1, x0, x1, y0, y1, so, null, log, what); }

// ---------------- шов: үшбұрыш белдік; p0→p1 — тігіс сызығы (жергілікті мм), la/lb — екі катеттің бағыты (жергілікті), kf катет. Катеттер тігіс бағытына ⟂ келтіріледі
static Solid QWeldS(QFrm f, double[] p0, double[] p1, double[] la, double[] lb, double kf, SolidOptions so) {
    XYZ a0 = f.Mm(p0[0], p0[1], p0[2]), a1 = f.Mm(p1[0], p1[1], p1[2]); XYZ dv = a1 - a0; double len = dv.GetLength(); if (len < 0.5 + 2 * QWELD_END) return null; XYZ dir = dv / len;
    XYZ A = f.V(la[0], la[1], la[2]).Normalize(); XYZ B = f.V(lb[0], lb[1], lb[2]).Normalize();
    A = (A - dir * A.DotProduct(dir)).Normalize(); B = (B - dir * B.DotProduct(dir)).Normalize();
    // q20 (13.11): шов ұштары тірек бетінен QWELD_END мм ерте бітеді, катеттер тірек беттерінен QWELD_GAP мм алшақ (жанасу 0…0,3; беттесу жоқ — булев сенімді)
    XYZ c0 = a0 + dir * QWELD_END; XYZ cA = c0 + (A + B) * QWELD_GAP;
    return QPrism(new List<XYZ> { cA * QMM, (c0 + A * kf + B * QWELD_GAP) * QMM, (c0 + A * QWELD_GAP + B * kf) * QMM }, dir, len - 2 * QWELD_END, so, null, null, "шов"); }
const double QWELD_END = 0.3, QWELD_GAP = 0.2;
// шов денесін бір материалға келтіру (булев кесу беттері кесетін дененің материалын алады) — тек жазық түзу қырлы солидтер қайта салынады
static GeometryObject QMonoSolid(Solid s, ElementId mat) {
    try {
        var faces = new List<List<XYZ>>();
        foreach (Face f in s.Faces) { var pf = f as PlanarFace; if (pf == null) return s; var lps = pf.GetEdgesAsCurveLoops(); if (lps.Count != 1) return s;
            var pts = new List<XYZ>(); foreach (Curve c in lps[0]) { if (!(c is Line)) return s; pts.Add(c.GetEndPoint(0)); } faces.Add(pts); }
        foreach (bool rev in new[] { false, true }) {
            var tsb = new TessellatedShapeBuilder(); tsb.OpenConnectedFaceSet(true);
            foreach (var pts in faces) { var q = new List<XYZ>(pts); if (rev) q.Reverse(); tsb.AddFace(new TessellatedFace(q, mat)); }
            tsb.CloseConnectedFaceSet(); tsb.Target = TessellatedShapeBuilderTarget.Solid; tsb.Fallback = TessellatedShapeBuilderFallback.Abort; tsb.Build();
            var res = tsb.GetBuildResult(); if (res.Outcome != TessellatedShapeBuilderOutcome.Solid) continue;
            foreach (var go in res.GetGeometricalObjects()) { var ns = go as Solid; if (ns != null && ns.Volume > 0 && Math.Abs(ns.Volume - s.Volume) < 0.002 * s.Volume + 1e-12) return ns; } }
    } catch { }
    return s; }
static double[] QV3(double x, double y, double z) { return new[] { x, y, z }; }

// ---------------- каркас (кедергілер), булев тазалау, қиылысу
class QSx { public Solid S; public double[] B; }
static double[] QBBox(Solid s) { var b = s.GetBoundingBox(); var tr = b.Transform; var pts = new List<XYZ>();
    foreach (double x in new[] { b.Min.X, b.Max.X }) foreach (double y in new[] { b.Min.Y, b.Max.Y }) foreach (double z in new[] { b.Min.Z, b.Max.Z }) pts.Add(tr.OfPoint(new XYZ(x, y, z)));
    return new[] { pts.Min(p => p.X) / QMM, pts.Min(p => p.Y) / QMM, pts.Min(p => p.Z) / QMM, pts.Max(p => p.X) / QMM, pts.Max(p => p.Y) / QMM, pts.Max(p => p.Z) / QMM }; }
static bool QOvl(double[] a, double[] b, double e) { return !(a[0] > b[3] + e || b[0] > a[3] + e || a[1] > b[4] + e || b[1] > a[4] + e || a[2] > b[5] + e || b[2] > a[5] + e); }
static List<Solid> QSolidsOf(Element e) { var r = new List<Solid>(); var ge = e.get_Geometry(new Options { DetailLevel = ViewDetailLevel.Fine }); if (ge == null) return r;
    foreach (var go in ge) { IEnumerable<GeometryObject> objs = go is GeometryInstance ? ((GeometryInstance)go).GetInstanceGeometry().Cast<GeometryObject>() : new[] { go };
        r.AddRange(objs.OfType<Solid>().Where(x => x.Volume > 1e-9)); } return r; }
// bb (мм, глобал) қиып өтетін колонна/каркас элементтері
static List<QSx> QFrameAround(Document d, double[] bb) {
    var res = new List<QSx>(); var ol = new Outline(QP(bb[0], bb[1], bb[2]), QP(bb[3], bb[4], bb[5]));
    var cats = new List<BuiltInCategory> { BuiltInCategory.OST_StructuralColumns, BuiltInCategory.OST_StructuralFraming };
    var flt = new LogicalAndFilter(new ElementMulticategoryFilter(cats), new BoundingBoxIntersectsFilter(ol));
    foreach (var e in new FilteredElementCollector(d).WherePasses(flt).WhereElementIsNotElementType()) foreach (var s in QSolidsOf(e)) res.Add(new QSx { S = s, B = QBBox(s) });
    return res; }
// тік сызық (gx, gy) бойымен [z0, z1] аралығындағы каркас солидтерімен қиылысу сегменттері (zmin, zmax, мм), біріктірілген, өсу ретімен
static List<double[]> QProbeSegs(List<QSx> fr, double gx, double gy, double z0, double z1) {
    var ln = Line.CreateBound(QP(gx, gy, z0), QP(gx, gy, z1)); var opt = new SolidCurveIntersectionOptions(); var raw = new List<double[]>();
    foreach (var s in fr) { SolidCurveIntersection r = null; try { r = s.S.IntersectWithCurve(ln, opt); } catch { continue; } if (r == null) continue;
        for (int i = 0; i < r.SegmentCount; i++) { var c = r.GetCurveSegment(i); double a = c.GetEndPoint(0).Z / QMM, b = c.GetEndPoint(1).Z / QMM; raw.Add(new[] { Math.Min(a, b), Math.Max(a, b) }); } }
    raw.Sort((p, q) => p[0].CompareTo(q[0])); var res = new List<double[]>();
    foreach (var s in raw) { if (res.Count > 0 && s[0] <= res[res.Count - 1][1] + 0.02) res[res.Count - 1][1] = Math.Max(res[res.Count - 1][1], s[1]); else res.Add(new[] { s[0], s[1] }); }
    return res; }
static string QSegStr(List<double[]> sg) { return sg.Count == 0 ? "жоқ" : string.Join(" ", sg.Select(q => "[" + QF(q[0]) + "…" + QF(q[1]) + "]")); }
static bool QSegHas(List<double[]> sg, double lo, double hi, double tol) { return sg.Any(q => Math.Abs(q[0] - lo) <= tol && Math.Abs(q[1] - hi) <= tol); }
// Comments (ALL_MODEL_INSTANCE_COMMENTS) = марка бойынша FamilyInstance тізімі (К1, К2, К3, КБ1, ПБ1, Б4, Б5, …)
static List<FamilyInstance> QByMark(Document d, string mark) {
    return new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(f => { var p = f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS); return p != null && p.AsString() == mark; }).ToList(); }
// сызықтық элемент ұштары (мм, глобал): p0, p1
static bool QEnds(FamilyInstance fi, out XYZ p0, out XYZ p1) { p0 = null; p1 = null; var lc = fi.Location as LocationCurve; if (lc == null) return false; p0 = lc.Curve.GetEndPoint(0) / QMM; p1 = lc.Curve.GetEndPoint(1) / QMM; return true; }
static double[] QElBB(Element e) { var b = e.get_BoundingBox(null); if (b == null) return null; return new[] { b.Min.X / QMM, b.Min.Y / QMM, b.Min.Z / QMM, b.Max.X / QMM, b.Max.Y / QMM, b.Max.Z / QMM }; }

// ---------------- орынға жинау (QCtx = бір орын)
class QPartDS { public BuiltInCategory Cat; public string Title, Comment; public List<GeometryObject> G = new List<GeometryObject>(); }
class QCtx {
    public Document D; public StringBuilder L; public QFrm F; public string Key, Loc, Mode;
    public List<QSx> FrameObst = new List<QSx>(), Obst = new List<QSx>();
    public Dictionary<string, QPartDS> Parts = new Dictionary<string, QPartDS>(); public List<string> Order = new List<string>();
    public int SkippedParts, CleanFail; public double Removed; }
static QPartDS QPart(QCtx c, string id, BuiltInCategory cat, string title, string comment) {
    QPartDS p; if (c.Parts.TryGetValue(id, out p)) return p; p = new QPartDS { Cat = cat, Title = title, Comment = comment }; c.Parts[id] = p; c.Order.Add(id); return p; }
static double QCu(double ft3) { return ft3 / (QMM * QMM * QMM); }     // feet³ → мм³
static Solid QShiftS(Solid s, XYZ vFeet) { return SolidUtils.CreateTransformed(s, Transform.CreateTranslation(vFeet)); }
// СЕНІМДІ қиылысу көлемі (мм³): тікелей Intersect; беттесетін солидтерде Revit «Failed to perform the Boolean operation» береді — сонда екі кішкентай ығыстырумен V = 2·V(t) − V(2t) экстраполяциясы (медиана). fail = екі жол да құлады.
static double QOvlVol(Solid a, Solid b, out bool viaShift, out bool fail)
{
    viaShift = false; fail = false;
    try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(a, b, BooleanOperationsType.Intersect); return r == null ? 0 : QCu(r.Volume); } catch { }
    viaShift = true; var est = new List<double>();
    foreach (double tmm in new[] { 0.1, 0.25, 0.5 }) foreach (var dv in new[] { new XYZ(1, 0.618, 0.382), new XYZ(-0.7, 0.3, 0.9), new XYZ(0.2, -0.9, 0.4) })
    {
        XYZ sv = dv.Normalize() * (tmm * QMM);
        try {
            var r1 = BooleanOperationsUtils.ExecuteBooleanOperation(QShiftS(a, sv), b, BooleanOperationsType.Intersect); double v1 = r1 == null ? 0 : QCu(r1.Volume);
            var r2 = BooleanOperationsUtils.ExecuteBooleanOperation(QShiftS(a, sv * 2), b, BooleanOperationsType.Intersect); double v2 = r2 == null ? 0 : QCu(r2.Volume);
            est.Add(Math.Max(0, 2 * v1 - v2));
        } catch { }
    }
    if (est.Count == 0) { fail = true; return 0; }
    est.Sort(); return est[est.Count / 2];
}
// s-ты кедергілерден (каркас + бұрын қойылған бөлшектер) тазалайды; нәтиже көлемі жоғалса — null
// Difference: беттесетін бет болса Revit құлайды — сонда s-ті 0,05…0,2 мм ығыстырып қайта (13.11.2026; жалпы нәтижеге әсері ≤ 0,2 мм)
static Solid QDiffRetry(Solid s, Solid o, out bool shifted, out bool fail) {
    shifted = false; fail = false;
    try { return BooleanOperationsUtils.ExecuteBooleanOperation(s, o, BooleanOperationsType.Difference); } catch { }
    shifted = true;
    foreach (double tmm in new[] { 0.05, 0.1, 0.2 }) foreach (var dv in new[] { new XYZ(1, 0.618, 0.382), new XYZ(-0.7, 0.3, 0.9), new XYZ(0.2, -0.9, 0.4), new XYZ(-0.3, -0.5, -0.8) }) {
        try { return BooleanOperationsUtils.ExecuteBooleanOperation(QShiftS(s, dv.Normalize() * (tmm * QMM)), o, BooleanOperationsType.Difference); } catch { } }
    fail = true; return null; }
static Solid QClean(QCtx c, Solid s, out double removed) {
    removed = 0; double v0 = s.Volume; var bx = QBBox(s);
    foreach (var o in c.Obst) {
        if (!QOvl(bx, o.B, 0.5)) continue;
        bool vs0, fl0; double ov0 = QOvlVol(s, o.S, out vs0, out fl0); if (!fl0 && ov0 <= 0.3) continue;      // q20: ≤ 0,3 мм³ қиылысуды кеспейміз (сливер / жарамсыз солид болдырмау)
        bool sh, fl; var r = QDiffRetry(s, o.S, out sh, out fl); if (fl) c.CleanFail++; else if (r != null) s = r;
        if (s.Volume < 1e-12) { removed = QCu(v0); return null; } }
    removed = QCu(v0 - s.Volume); return s; }
// q20: DirectShape жарамдылығы (булев кейде IsValidShape өтпейтін солид береді); уақытша DS жасап тексереді
static bool QVShape(Document d, Solid s) { var t = DirectShape.CreateElement(d, new ElementId(BuiltInCategory.OST_GenericModel)); bool ok = false; try { ok = t.IsValidShape(new List<GeometryObject> { s }); } catch { } d.Delete(t.Id); return ok; }
static Solid QCleanShifted(QCtx c, Solid s) {
    foreach (double tmm in new[] { 0.05, 0.1, 0.2, 0.4 }) foreach (var dv in new[] { new XYZ(1, 0.618, 0.382), new XYZ(-0.7, 0.3, 0.9), new XYZ(0.2, -0.9, 0.4) }) {
        Solid cur = s; bool okAll = true; var bx = QBBox(cur);
        foreach (var o in c.Obst) { if (!QOvl(bx, o.B, 0.5)) continue;
            try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(cur, QShiftS(o.S, dv.Normalize() * (tmm * QMM)), BooleanOperationsType.Difference); if (r != null) cur = r; } catch { okAll = false; break; }
            if (cur.Volume < 1e-12) return null; }
        if (okAll && QVShape(c.D, cur)) return cur; }
    return null; }
// hard = true: бөлшек каркаспен >50 мм³ қиылысса және Mode=="SKIP" болса — салынбайды (false қайтарады); әйтпесе тазаланады (CLEAN)
static bool QPut(QCtx c, QPartDS p, Solid s, bool obstacle, bool hard) {
    if (s == null) return false; var bx = QBBox(s); double ov = 0;
    foreach (var o in c.FrameObst) { if (!QOvl(bx, o.B, 0)) continue; bool vs, fl; ov += QOvlVol(s, o.S, out vs, out fl); if (fl) c.L.AppendLine("  WARN «" + p.Title + "»: каркаспен қиылысуды есептеу мүмкін болмады"); }
    if (hard && ov > 50 && c.Mode != "CLEAN") { c.L.AppendLine("  SKIP «" + p.Title + "»: каркаспен қиылысу " + QF(ov) + " мм3 > 50 (OVERLAP_MODE=SKIP) — СҰРАҚ"); c.SkippedParts++; return false; }
    double rem; var s2 = QClean(c, s, out rem); if (rem > 1) { c.L.AppendLine("  CLEAN «" + p.Title + "»: " + QF(rem) + " мм3 алынды (каркас/бұрынғы бөлшекпен қиылысу)"); c.Removed += rem; }
    if (s2 != null && rem > 1e-4 && !QVShape(c.D, s2)) { c.L.AppendLine("  DBG invalid cut result: vol " + QF(QCu(s2.Volume)) + " (orig " + QF(QCu(s.Volume)) + ") faces " + s2.Faces.Size + " edges " + s2.Edges.Size);
        foreach (Face fc in s2.Faces) { var pf = fc as PlanarFace; var lp = pf == null ? null : pf.GetEdgesAsCurveLoops(); string vs = ""; if (lp != null) foreach (var l0 in lp) foreach (Curve cu in l0) vs += " (" + QF(cu.GetEndPoint(0).X / QMM) + "," + QF(cu.GetEndPoint(0).Y / QMM) + "," + QF(cu.GetEndPoint(0).Z / QMM) + ")"; c.L.AppendLine("     face " + QF(fc.Area / (QMM * QMM)) + (pf == null ? "" : " n=" + QF(pf.FaceNormal.X) + "," + QF(pf.FaceNormal.Y) + "," + QF(pf.FaceNormal.Z)) + vs); }
        foreach (Edge ed in s.Edges) { } c.L.AppendLine("     orig bb " + string.Join(",", QBBox(s).Select(QF)));
        foreach (var o in c.Obst) if (QOvl(QBBox(s), o.B, 0.5)) c.L.AppendLine("     obst bb " + string.Join(",", o.B.Select(QF)) + " ov " + QF(QCu(0))); var s3 = QCleanShifted(c, s); if (s3 != null) { s2 = s3; c.L.AppendLine("  CLEANSHIFT «" + p.Title + "»: булев нәтижесі DS-ке жарамсыз еді — ығыстырылған кескішпен қайталанды"); } else { s2 = s; c.L.AppendLine("  WARN «" + p.Title + "»: булев нәтижесі DS-ке жарамсыз, кесілмеген дене салынды"); } }
    if (s2 == null || s2.Volume < 1e-12) return false;
    p.G.Add(s2); if (obstacle) c.Obst.Add(new QSx { S = s2, B = QBBox(s2) }); return true; }
static DirectShape QMakeDS(Document d, BuiltInCategory want, string key, string loc, string title, string comment, List<GeometryObject> g) {
    var cat = new ElementId(want); if (!DirectShape.IsValidCategoryId(cat, d)) cat = new ElementId(BuiltInCategory.OST_GenericModel);
    var ds = DirectShape.CreateElement(d, cat); ds.ApplicationId = "БК_узел"; ds.ApplicationDataId = key + " | " + loc;
    if (want == BuiltInCategory.OST_StructConnectionWelds) { var wm = QMatId(d, "КМ_уз_шов", new Color(110, 110, 110)); var g2 = new List<GeometryObject>(); foreach (var x in g) { GeometryObject m2 = x is Solid ? QMonoSolid((Solid)x, wm) : x; if (!object.ReferenceEquals(m2, x) && !ds.IsValidShape(new List<GeometryObject> { m2 })) m2 = x; g2.Add(m2); } g = g2; }
    ds.Name = System.Text.RegularExpressions.Regex.Replace(title + " - " + loc, @"[\:{}\[\]|;<>?`~]", " -"); ds.SetShape(g);
    var cm = ds.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS); if (cm != null) cm.Set(title + " — " + comment + " | " + loc); return ds; }
static int QEmit(QCtx c) { int n = 0; foreach (var id in c.Order) { var p = c.Parts[id]; if (p.G.Count == 0) continue; QMakeDS(c.D, p.Cat, c.Key, c.Loc, p.Title, p.Comment, p.G); n++; } return n; }
// нысана орындардағы бұрынғы «узел N» денелерін өшіру (қосарланбау)
static int QRemoveOld(Document d, string key, HashSet<string> locs) {
    var ids = new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел" && (x.ApplicationDataId ?? "").Contains("|")
        && x.ApplicationDataId.Split('|')[0].Trim() == key && locs.Contains(x.ApplicationDataId.Split('|')[1].Trim())).Select(x => x.Id).ToList();
    if (ids.Count > 0) d.Delete(ids); return ids.Count; }
// ---------------- болт жинағы: М16 / М20 өлшемдері v113_lib BoltDims бойынша (S, m, шайба Ø, s, k, шайба тесігі)
static readonly Dictionary<int, double[]> QBD = new Dictionary<int, double[]> { { 16, new double[] { 24, 13, 30, 3, 10, 17 } }, { 20, new double[] { 30, 16, 37, 3, 12.5, 21 } } };
class QBoltSet { public List<GeometryObject> Stems = new List<GeometryObject>(), Heads = new List<GeometryObject>(), Nuts = new List<GeometryObject>(), Washers = new List<GeometryObject>(); }
// cMm — бастиек жағындағы пакет бетінің осьтегі нүктесі (мм, глобал); u — пакет ішіне қарай бірлік вектор; grip — пакет қалыңдығы; L — стержень ұзындығы (бастиек астынан);
// headW/nutW — бастиек/гайка астындағы жалпақ шайба (ГОСТ 11371; s = 3)
static void QBolt(QBoltSet bs, XYZ cMm, XYZ u, double grip, double L, int dia, bool headW, bool nutW, SolidOptions so, StringBuilder log) {
    var b = QBD[dia]; double S = b[0], m = b[1], D = b[2], s = b[3], k = b[4], dh = b[5]; u = u.Normalize();
    Func<double, XYZ> at = t => (cMm + u * t) * QMM; double t0 = headW ? -s : 0;
    if (headW) bs.Washers.Add(QRingS(at(-s), u, D, dh, s, so, log, "шайба 1"));
    bs.Heads.Add(QHexS(at(t0 - k), u, S, k, 0, so, log, "бастиек"));
    bs.Stems.Add(QCylS(at(t0), u, dia, L, so));
    double tn = grip; if (nutW) { bs.Washers.Add(QRingS(at(grip), u, D, dh, s, so, log, "шайба 2")); tn = grip + s; }
    bs.Nuts.Add(QHexS(at(tn), u, S, m, dia, so, log, "гайка")); }
// ВП жинағын (бастиек, гайка, шайба) каркаспен қиылысуға тексеру: стержень пакет арқылы өтеді (каркаста тесік модельденбейді) — есептелмейді
static double QBoltFrameOverlap(QCtx c, QBoltSet bs) {
    double ov = 0; foreach (var g in bs.Heads.Concat(bs.Nuts).Concat(bs.Washers)) { var s = (Solid)g; var bx = QBBox(s);
        foreach (var o in c.FrameObst) { if (!QOvl(bx, o.B, 0)) continue; bool vs, fl; ov += QOvlVol(s, o.S, out vs, out fl); } }
    return ov; }
static void QEmitBolts(QCtx c, QBoltSet bs, string id, string tag, int dia, double L, int n, string grade, string note) {
    var cat = BuiltInCategory.OST_StructConnectionBolts; string dm = "М" + dia, ln = QF(L);
    foreach (var g in bs.Stems) QPart(c, id + "_st", cat, "Узел " + tag + ": болт " + dm + "×" + ln + " стержень", "болт " + dm + " кл. " + grade + " l" + ln + " (" + n + " дана) " + note).G.Add(g);
    foreach (var g in bs.Heads) QPart(c, id + "_hd", cat, "Узел " + tag + ": болт " + dm + "×" + ln + " бастиек", "бастиек (" + n + " дана)").G.Add(g);
    foreach (var g in bs.Nuts) QPart(c, id + "_nt", cat, "Узел " + tag + ": гайка " + dm + "×" + ln, "гайка (" + n + " дана)").G.Add(g);
    foreach (var g in bs.Washers) QPart(c, id + "_ws", cat, "Узел " + tag + ": шайба " + dm + "×" + ln, "шайба ГОСТ 11371 (" + bs.Washers.Count + " дана)").G.Add(g); }
// контур бойынша шов: xy — көпбұрыш (x,y жұптары, жергілікті), z деңгейі; әр қыр бойынша: катет 1 = сыртқа қарай жазықтықта, катет 2 = (0,0,dz) (dz = +1 жоғары / −1 төмен)
static void QWeldRing(QCtx c, QPartDS p, QFrm f, double[] xy, double z, double kf, double dz, SolidOptions so) {
    int n = xy.Length / 2; double area = 0; for (int i = 0; i < n; i++) { int j = (i + 1) % n; area += xy[2 * i] * xy[2 * j + 1] - xy[2 * j] * xy[2 * i + 1]; }
    double sg = area > 0 ? 1 : -1;
    for (int i = 0; i < n; i++) {
        int j = (i + 1) % n; double ax = xy[2 * i], ay = xy[2 * i + 1], bx = xy[2 * j], by = xy[2 * j + 1], dx = bx - ax, dy = by - ay, L = Math.Sqrt(dx * dx + dy * dy); if (L < 0.5) continue;
        QPut(c, p, QWeldS(f, QV3(ax, ay, z), QV3(bx, by, z), QV3(sg * dy / L, -sg * dx / L, 0), QV3(0, 0, dz), kf, so), true, false); } }

// ---------------- void-кесу (БК_срез_плоскостью: референс жазықтық + face-based void қорап, жазықтықтың +нормаль жағын алады; плиндегі қорап ~400×400, +нормаль бойымен ~300 — rmc_03_lambda.cs тәжірибесі)
const string QVOID_LIB = @"D:\Бекасыл КЖ КМ\_Стандарт_КЖ\семейства\БК_срез_плоскостью.rfa";
const double QVOID_HALF = 400;     // void қорабының жазықтықтағы жарты өлшемі (мм): ЗОНДПЕН ӨЛШЕНДІ 13.11.2026 (q_void.cs: Б4 белдеуі, жазықтық z 3886): қорап 800×800 (BB x/y ±400), +нормаль бойымен 3886…4486 (600); белдеу x ±380-де жоқ, ±400-де бар (шешім 14)
static FamilySymbol QVoidSymbol(Document d) {
    var vsym = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).Cast<FamilySymbol>().FirstOrDefault(x => x.FamilyName == "БК_срез_плоскостью");
    if (vsym == null) { Family vf; d.LoadFamily(QVOID_LIB, out vf); if (vf == null) vf = new FilteredElementCollector(d).OfClass(typeof(Family)).Cast<Family>().First(x => x.Name == "БК_срез_плоскостью"); vsym = d.GetElement(vf.GetFamilySymbolIds().First()) as FamilySymbol; }
    if (!vsym.IsActive) vsym.Activate(); d.Regenerate(); return vsym; }
static View3D QView3(Document d) { return new FilteredElementCollector(d).OfClass(typeof(View3D)).Cast<View3D>().First(v => !v.IsTemplate); }
// префикс бойынша бұрынғы void-тар (Comments) мен референс жазықтықтарды (аты «префикс_…») өшіру
static int QRemoveVoids(Document d, string prefix) {
    var ids = new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Symbol.FamilyName == "БК_срез_плоскостью"
        && ((x.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS) != null ? x.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString() : "") ?? "").StartsWith(prefix)).Select(x => x.Id).ToList();
    ids.AddRange(new FilteredElementCollector(d).OfClass(typeof(ReferencePlane)).Cast<ReferencePlane>().Where(r => (r.Name ?? "").StartsWith(prefix + "_")).Select(r => r.Id));
    if (ids.Count > 0) d.Delete(ids); return ids.Count; }
// target элементін жазықтықтан (нүкте pMm, нормаль m) +нормаль жағында кесу. Екі ось ретін де сынайды (face-based instance BasisZ = m болуы тексеріледі).
static bool QPlaneVoidCut(Document d, FamilySymbol vsym, View3D v3, Element target, XYZ pMm, XYZ m, string name, string cmt, StringBuilder log) {
    m = m.Normalize(); XYZ Pp = pMm * QMM; XYZ e1 = Math.Abs(m.Z) < 0.9 ? XYZ.BasisZ : XYZ.BasisX; e1 = (e1 - m * e1.DotProduct(m)).Normalize(); XYZ e2 = m.CrossProduct(e1).Normalize();
    FamilyInstance vi = null; ReferencePlane rpOk = null;
    foreach (bool flip in new[] { false, true }) {
        XYZ a1 = flip ? e2 : e1, a2 = flip ? e1 : e2;
        var rp = d.Create.NewReferencePlane2(Pp, Pp + a1, Pp + a2, v3); rp.Name = name + (flip ? "f" : "");
        FamilyInstance cand = d.Create.NewFamilyInstance(rp.GetReference(), Pp, a1, vsym);
        cand.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.Set(cmt);
        d.Regenerate();
        if (cand.GetTransform().BasisZ.DotProduct(m) > 0.99) { vi = cand; rpOk = rp; break; }
        d.Delete(cand.Id); d.Delete(rp.Id); }
    if (vi == null) { log.AppendLine("  FAIL void жазықтық " + name + " (BasisZ ≠ нормаль)"); return false; }
    try { InstanceVoidCutUtils.AddInstanceVoidCut(d, target, vi); return true; }
    catch (Exception ex) { log.AppendLine("  FAIL void cut " + name + ": " + ex.Message.Split('\n')[0]); return false; } }
// ---------------- сопақ тесік (obround) қиғышы: центрі (xc, yc) жергілікті, x бойы lx, y бойы wy, z бойымен [zLo, zLo+h]; QDiff-пен алынады
static Solid QSlotCutter(QFrm f, double xc, double yc, double zLo, double h, double lx, double wy) {
    double r = wy / 2, a = (lx - wy) / 2, want = ((lx - wy) * wy + Math.PI * r * r) * h * QMM * QMM * QMM; var so = new SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId);
    Func<double, double, XYZ> P = (x, y) => f.Pt(xc + x, yc + y, zLo); XYZ dir = f.V(0, 0, 1);
    foreach (bool ccw in new[] { true, false }) {
        var lp = new CurveLoop();
        if (ccw) { lp.Append(Line.CreateBound(P(-a, -r), P(a, -r))); lp.Append(Arc.Create(P(a, -r), P(a, r), P(a + r, 0))); lp.Append(Line.CreateBound(P(a, r), P(-a, r))); lp.Append(Arc.Create(P(-a, r), P(-a, -r), P(-a - r, 0))); }
        else { lp.Append(Arc.Create(P(-a, -r), P(-a, r), P(-a - r, 0))); lp.Append(Line.CreateBound(P(-a, r), P(a, r))); lp.Append(Arc.Create(P(a, r), P(a, -r), P(a + r, 0))); lp.Append(Line.CreateBound(P(a, -r), P(-a, -r))); }
        Solid s = null; try { s = QExtr(new List<CurveLoop> { lp }, dir, h * QMM, so); } catch { continue; }
        if (s != null && Math.Abs(s.Volume - want) < 0.003 * want) return s; }
    throw new Exception("slot cutter failed"); }
static Solid QDiff(Solid s, Solid cut) { var r = BooleanOperationsUtils.ExecuteBooleanOperation(s, cut, BooleanOperationsType.Difference); if (r == null || r.Volume < 1e-12) throw new Exception("diff failed"); return r; }
static void _libEnd() {
