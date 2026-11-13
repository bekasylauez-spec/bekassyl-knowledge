// ===== rmc_node_lib.cs — РМЦ КМ рама узелдері (1…4) үшін ортақ көмекші. Жазылған 13.11.2026, Revit-те ІСКЕ ҚОСЫЛМАҒАН (тек Roslyn-мен компиляцияланған).
// Қолдану: go.ps1 -Name rmc_u01 -Lib rmc_node_lib.cs   (run.ps1 скриптке осы файлды ТІРКЕЙДІ; соңғы әдіс _libEnd әдейі ашық — runner жабады).
// Негізі: rmc_10_baza_B1.cs (DirectShape, WithHoles көлем тексерісі, Weld, қосарланбау) + v113_lib.cs (So палитрасы, Bolt).
// Ережелер: КМ_стандарт 03 §6 — әр орынға бөлек DirectShape, ApplicationDataId «узел N | <ось>-<қатар>», №117 түстер (So), шов = үшбұрыш белдік,
// қайта іске қосқанда нысана орындардағы «узел N» денелері өшіріледі, белсенді құжат тексеріледі. Элемент аты: «Узел N: <бөлшек> −t×b×l»
// (Revit Name-де «:» тыйым — Name-де « -» болады, толық мәтін «Комментарии»-де, DS-тің ApplicationDataId-інде орын).
const double MM = 1 / 304.8;
static readonly System.Globalization.CultureInfo CI = System.Globalization.CultureInfo.InvariantCulture;
static XYZ P(double x, double y, double z) { return new XYZ(x * MM, y * MM, z * MM); }
static string F(double v) { return Math.Round(v, 2).ToString(CI); }
class Swallow : IFailuresPreprocessor { public FailureProcessingResult PreprocessFailures(FailuresAccessor a) {
    foreach (var m in a.GetFailureMessages()) if (m.GetSeverity() == FailureSeverity.Warning) a.DeleteWarning(m); return FailureProcessingResult.Continue; } }
static ElementId MatId(Document d, string name, Color c) {
    var m = new FilteredElementCollector(d).OfClass(typeof(Material)).Cast<Material>().FirstOrDefault(x => x.Name == name);
    if (m == null) { m = d.GetElement(Material.Create(d, name)) as Material; m.Color = c; m.MaterialClass = "Металл"; }
    m.Shininess = 0; m.Smoothness = 0; return m.Id; }
// №117 палитрасы (КМ_стандарт §6), материал «КМ_уз_<бөлшек>»; шайба/гайка/бастиек = «болт»
static SolidOptions So(Document d, string part) {
    var pal = new Dictionary<string, int[]> { { "плита", new[] { 70, 130, 180 } }, { "ребро", new[] { 60, 160, 90 } }, { "столик", new[] { 230, 150, 30 } },
        { "ребро_столика", new[] { 150, 100, 50 } }, { "накладка", new[] { 0, 150, 160 } }, { "уголок", new[] { 130, 90, 170 } }, { "фасонка", new[] { 200, 60, 60 } },
        { "вставка", new[] { 120, 150, 30 } }, { "заглушка", new[] { 150, 150, 150 } }, { "фланец", new[] { 40, 80, 150 } }, { "прокладка", new[] { 210, 180, 60 } },
        { "брус", new[] { 160, 120, 80 } }, { "болт", new[] { 60, 60, 60 } }, { "шов", new[] { 110, 110, 110 } } };
    var c = pal[part]; return new SolidOptions(MatId(d, "КМ_уз_" + part, new Color((byte)c[0], (byte)c[1], (byte)c[2])), ElementId.InvalidElementId); }

// ---------------- осьтер / орын атауы
static readonly double[] AXX = { 150, 6000, 12000, 18000, 24000, 30000, 36000, 42000, 48000, 54000, 59850 };
static string AxisName(double x, string row) { for (int i = 0; i < AXX.Length; i++) if (Math.Abs(AXX[i] - x) < 60) return (i + 1) + "-" + row; return F(x) + "-" + row; }
static int AxisNo(double x) { for (int i = 0; i < AXX.Length; i++) if (Math.Abs(AXX[i] - x) < 60) return i + 1; return 0; }

// ---------------- жергілікті жүйе: Global X = Ox + x ; Global Y = Oy + Sy*y ; Z = z (мм). G қатары: Oy = 36000, Sy = −1
class Frm {
    public double Ox, Oy, Sy;
    public Frm(double ox, double oy, double sy) { Ox = ox; Oy = oy; Sy = sy; }
    public XYZ Pt(double x, double y, double z) { return new XYZ((Ox + x) * MM, (Oy + Sy * y) * MM, z * MM); }     // feet
    public XYZ Mm(double x, double y, double z) { return new XYZ(Ox + x, Oy + Sy * y, z); }                          // мм
    public XYZ V(double x, double y, double z) { return new XYZ(x, Sy * y, z); }                                       // бағыт векторы
    public double Gy(double y) { return Oy + Sy * y; }
}
static List<XYZ> Poly(Frm f, params double[] xyz) { var r = new List<XYZ>(); for (int i = 0; i + 2 < xyz.Length; i += 3) r.Add(f.Pt(xyz[i], xyz[i + 1], xyz[i + 2])); return r; }

// ---------------- геометрия
static XYZ Newell(IList<XYZ> p) {
    double nx = 0, ny = 0, nz = 0; int n = p.Count;
    for (int i = 0; i < n; i++) { var a = p[i]; var b = p[(i + 1) % n]; nx += (a.Y - b.Y) * (a.Z + b.Z); ny += (a.Z - b.Z) * (a.X + b.X); nz += (a.X - b.X) * (a.Y + b.Y); }
    return new XYZ(nx, ny, nz); }
static CurveLoop LoopPts(IList<XYZ> p) { var lp = new CurveLoop(); int n = p.Count; for (int i = 0; i < n; i++) lp.Append(Line.CreateBound(p[i], p[(i + 1) % n])); return lp; }
static void Axes(XYZ n, out XYZ e1, out XYZ e2) { XYZ r = Math.Abs(n.Z) > 0.9 ? XYZ.BasisX : XYZ.BasisZ; e1 = (r - n * r.DotProduct(n)).Normalize(); e2 = n.CrossProduct(e1).Normalize(); }
static CurveLoop CircLoop(XYZ c, XYZ n, double dia, bool ccw) {
    XYZ e1, e2; Axes(n, out e1, out e2); double r = dia / 2 * MM; var lp = new CurveLoop();
    if (ccw) { lp.Append(Arc.Create(c + e1 * r, c - e1 * r, c + e2 * r)); lp.Append(Arc.Create(c - e1 * r, c + e1 * r, c - e2 * r)); }
    else { lp.Append(Arc.Create(c + e1 * r, c - e1 * r, c - e2 * r)); lp.Append(Arc.Create(c - e1 * r, c + e1 * r, c + e2 * r)); }
    return lp; }
class Hole { public XYZ C; public double D; public Hole(XYZ c, double d) { C = c; D = d; } }
static Solid Extr(List<CurveLoop> loops, XYZ dir, double lenFeet, SolidOptions so) { return GeometryCreationUtilities.CreateExtrusionGeometry(loops, dir, lenFeet, so); }
// көпбұрыш (feet, бір жазықтықта) + dir бойымен lenMm экструзия; тесіктер (центрі көпбұрыш жазықтығында, осі = dir). Көлем (area·len − тесіктер) тексеріледі, орын ауыстыру автоматты.
static Solid Prism(IList<XYZ> pts, XYZ dir, double lenMm, SolidOptions so, IList<Hole> holes, StringBuilder log, string what) {
    dir = dir.Normalize(); var pl = new List<XYZ>(pts); XYZ nw = Newell(pl); if (nw.DotProduct(dir) < 0) { pl.Reverse(); nw = nw.Negate(); }
    double len = lenMm * MM;
    if (holes == null || holes.Count == 0) return Extr(new List<CurveLoop> { LoopPts(pl) }, dir, len, so);
    double hv = 0; foreach (var h in holes) hv += Math.PI * Math.Pow(h.D / 2 * MM, 2);
    double want = (nw.GetLength() / 2 - hv) * len;
    foreach (bool ccw in new[] { false, true }) {
        var loops = new List<CurveLoop> { LoopPts(pl) }; foreach (var h in holes) loops.Add(CircLoop(h.C, dir, h.D, ccw));
        Solid s = null; try { s = Extr(loops, dir, len, so); } catch (Exception ex) { if (log != null) log.AppendLine("  " + what + " extrusion ccw=" + ccw + " failed: " + ex.Message.Split('\n')[0]); continue; }
        if (Math.Abs(s.Volume - want) < 0.002 * want) return s;
        if (log != null) log.AppendLine("  " + what + " ccw=" + ccw + " volume " + F(s.Volume / MM / MM / MM) + " != " + F(want / MM / MM / MM)); }
    throw new Exception("hole extrusion failed: " + what); }
static Solid CylS(XYZ c, XYZ n, double dia, double lenMm, SolidOptions so) { return Extr(new List<CurveLoop> { CircLoop(c, n, dia, true) }, n, lenMm * MM, so); }
static List<XYZ> HexPts(XYZ c, XYZ n, double S) {
    XYZ e1, e2; Axes(n, out e1, out e2); double R = S / Math.Sqrt(3) * MM; var r = new List<XYZ>();
    for (int i = 0; i < 6; i++) r.Add(c + (e1 * Math.Cos(i * Math.PI / 3) + e2 * Math.Sin(i * Math.PI / 3)) * R); return r; }
static Solid HexS(XYZ c, XYZ n, double S, double lenMm, double holeDia, SolidOptions so, StringBuilder log, string what) {
    return Prism(HexPts(c, n, S), n, lenMm, so, holeDia > 0 ? new List<Hole> { new Hole(c, holeDia) } : null, log, what); }
static Solid RingS(XYZ c, XYZ n, double dout, double din, double lenMm, SolidOptions so, StringBuilder log, string what) {
    double want = Math.PI / 4 * (dout * dout - din * din) * MM * MM * lenMm * MM;
    foreach (bool ccw in new[] { false, true }) {
        var loops = new List<CurveLoop> { CircLoop(c, n, dout, true), CircLoop(c, n, din, ccw) };
        Solid s = null; try { s = Extr(loops, n, lenMm * MM, so); } catch { continue; }
        if (Math.Abs(s.Volume - want) < 0.002 * want) return s; }
    throw new Exception("ring extrusion failed: " + what); }
// тесік Ø dia (мм) нүкте (мм, глобал) арқылы, ось ax бойымен (±60 мм) — булев айырма (еңіс бетке перпендикуляр тесіктер үшін)
static Solid Drill(Solid s, XYZ cMm, XYZ ax, double dia) {
    ax = ax.Normalize(); var cyl = CylS((cMm - ax * 60) * MM, ax, dia, 120, new SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId));
    var r = BooleanOperationsUtils.ExecuteBooleanOperation(s, cyl, BooleanOperationsType.Difference); if (r == null || r.Volume < 1e-12) throw new Exception("drill failed"); return r; }

// ---------------- ВП болт М24: стержень + бастиек + гайка + 2 шайба. Өлшемдер v113_lib.cs BoltDims(24) бойынша (S 36, m 19, D 44, s 4, k 15) — СҰРАҚ: ГОСТ 22353/22354/22355 нақты өлшемі (S 41, m 22 …) керек пе
static readonly double[] B24 = { 36, 19, 44, 4, 15, 24, 25 };   // S, m, D, s, k, d, тесік шайбада
class BoltSet { public List<GeometryObject> Stems = new List<GeometryObject>(), Heads = new List<GeometryObject>(), Nuts = new List<GeometryObject>(), Washers = new List<GeometryObject>(); }
// cMm — бастиек жағындағы пакет бетінің осьтегі нүктесі (мм, глобал); u — пакет ішіне қарай бірлік вектор; grip — пакет қалыңдығы; L — стержень ұзындығы (бастиек астынан)
static void BoltVP(BoltSet bs, XYZ cMm, XYZ u, double grip, double L, SolidOptions so, StringBuilder log) {
    double S = B24[0], m = B24[1], D = B24[2], s = B24[3], k = B24[4], dd = B24[5], dh = B24[6]; u = u.Normalize();
    Func<double, XYZ> at = t => (cMm + u * t) * MM;
    bs.Washers.Add(RingS(at(-s), u, D, dh, s, so, log, "шайба 1"));
    bs.Heads.Add(HexS(at(-s - k), u, S, k, 0, so, log, "бастиек"));
    bs.Stems.Add(CylS(at(-s), u, dd, L, so));
    bs.Washers.Add(RingS(at(grip), u, D, dh, s, so, log, "шайба 2"));
    bs.Nuts.Add(HexS(at(grip + s), u, S, m, dd, so, log, "гайка")); }
// шов: үшбұрыш белдік; p0→p1 — тігіс сызығы (жергілікті мм), la/lb — екі катеттің бағыты (жергілікті), kf катет. Катеттер тігіс бағытына ⟂ келтіріледі (профиль жазықтығы = экструзия бағытына ⟂)
static Solid WeldS(Frm f, double[] p0, double[] p1, double[] la, double[] lb, double kf, SolidOptions so) {
    XYZ a0 = f.Mm(p0[0], p0[1], p0[2]), a1 = f.Mm(p1[0], p1[1], p1[2]); XYZ dv = a1 - a0; double len = dv.GetLength(); if (len < 0.5) return null; XYZ dir = dv / len;
    XYZ A = f.V(la[0], la[1], la[2]).Normalize(); XYZ B = f.V(lb[0], lb[1], lb[2]).Normalize();
    A = (A - dir * A.DotProduct(dir)).Normalize(); B = (B - dir * B.DotProduct(dir)).Normalize();
    return Prism(new List<XYZ> { a0 * MM, (a0 + A * kf) * MM, (a0 + B * kf) * MM }, dir, len, so, null, null, "шов"); }
static double[] V3(double x, double y, double z) { return new[] { x, y, z }; }

// ---------------- каркас (кедергілер), булев тазалау, қиылысу
class Sx { public Solid S; public double[] B; }
static double[] BBox(Solid s) { var b = s.GetBoundingBox(); var tr = b.Transform; var pts = new List<XYZ>();
    foreach (double x in new[] { b.Min.X, b.Max.X }) foreach (double y in new[] { b.Min.Y, b.Max.Y }) foreach (double z in new[] { b.Min.Z, b.Max.Z }) pts.Add(tr.OfPoint(new XYZ(x, y, z)));
    return new[] { pts.Min(p => p.X) / MM, pts.Min(p => p.Y) / MM, pts.Min(p => p.Z) / MM, pts.Max(p => p.X) / MM, pts.Max(p => p.Y) / MM, pts.Max(p => p.Z) / MM }; }
static bool Ovl(double[] a, double[] b, double e) { return !(a[0] > b[3] + e || b[0] > a[3] + e || a[1] > b[4] + e || b[1] > a[4] + e || a[2] > b[5] + e || b[2] > a[5] + e); }
static List<Solid> SolidsOf(Element e) { var r = new List<Solid>(); var ge = e.get_Geometry(new Options { DetailLevel = ViewDetailLevel.Fine }); if (ge == null) return r;
    foreach (var go in ge) { IEnumerable<GeometryObject> objs = go is GeometryInstance ? ((GeometryInstance)go).GetInstanceGeometry().Cast<GeometryObject>() : new[] { go };
        r.AddRange(objs.OfType<Solid>().Where(x => x.Volume > 1e-9)); } return r; }
// bb (мм, глобал) қиып өтетін колонна/каркас элементтері
static List<Sx> FrameAround(Document d, double[] bb) {
    var res = new List<Sx>(); var ol = new Outline(P(bb[0], bb[1], bb[2]), P(bb[3], bb[4], bb[5]));
    var cats = new List<BuiltInCategory> { BuiltInCategory.OST_StructuralColumns, BuiltInCategory.OST_StructuralFraming };
    var flt = new LogicalAndFilter(new ElementMulticategoryFilter(cats), new BoundingBoxIntersectsFilter(ol));
    foreach (var e in new FilteredElementCollector(d).WherePasses(flt).WhereElementIsNotElementType()) foreach (var s in SolidsOf(e)) res.Add(new Sx { S = s, B = BBox(s) });
    return res; }
// тік сызық (gx, gy) бойымен каркас солидтерімен қиылысудың төменгі/жоғарғы Z (мм); NaN — қиылыспайды
static double ProbeZ(List<Sx> fr, double gx, double gy, double z0, double z1, bool wantMin) {
    var ln = Line.CreateBound(P(gx, gy, z0), P(gx, gy, z1)); double best = double.NaN; var opt = new SolidCurveIntersectionOptions();
    foreach (var s in fr) { SolidCurveIntersection r = null; try { r = s.S.IntersectWithCurve(ln, opt); } catch { continue; } if (r == null) continue;
        for (int i = 0; i < r.SegmentCount; i++) { var c = r.GetCurveSegment(i); double a = c.GetEndPoint(0).Z / MM, b = c.GetEndPoint(1).Z / MM; double z = wantMin ? Math.Min(a, b) : Math.Max(a, b);
            if (double.IsNaN(best) || (wantMin ? z < best : z > best)) best = z; } }
    return best; }
static FamilyInstance FindCol(List<FamilyInstance> cols, double gx, double gy, double tol) {
    return cols.FirstOrDefault(c => { var p = (c.Location as LocationPoint).Point; return Math.Abs(p.X / MM - gx) < tol && Math.Abs(p.Y / MM - gy) < tol; }); }
static List<FamilyInstance> ColsK1(Document d) {
    return new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(f => f.Location is LocationPoint && f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS) != null && f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString() == "К1").ToList(); }

// ---------------- орынға жинау (Ctx = бір орын)
class PartDS { public BuiltInCategory Cat; public string Title, Comment; public List<GeometryObject> G = new List<GeometryObject>(); }
class Ctx {
    public Document D; public StringBuilder L; public Frm F; public string Key, Loc, Mode;
    public List<Sx> FrameObst = new List<Sx>(), Obst = new List<Sx>();
    public Dictionary<string, PartDS> Parts = new Dictionary<string, PartDS>(); public List<string> Order = new List<string>();
    public int SkippedParts; public double Removed; }
static PartDS Part(Ctx c, string id, BuiltInCategory cat, string title, string comment) {
    PartDS p; if (c.Parts.TryGetValue(id, out p)) return p; p = new PartDS { Cat = cat, Title = title, Comment = comment }; c.Parts[id] = p; c.Order.Add(id); return p; }
static double Cu(double ft3) { return ft3 / (MM * MM * MM); }     // feet³ → мм³
// s-ты кедергілерден (каркас + бұрын қойылған бөлшектер) тазалайды; нәтиже көлемі жоғалса — null
static Solid Clean(Ctx c, Solid s, out double removed) {
    removed = 0; double v0 = s.Volume; var bx = BBox(s);
    foreach (var o in c.Obst) {
        if (!Ovl(bx, o.B, 0.5)) continue;
        try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(s, o.S, BooleanOperationsType.Difference); if (r != null) s = r; } catch { }
        if (s.Volume < 1e-12) { removed = Cu(v0); return null; } }
    removed = Cu(v0 - s.Volume); return s; }
// hard = true: бөлшек каркаспен >50 мм³ қиылысса және Mode=="SKIP" болса — салынбайды (қайтарады false); әйтпесе тазаланады (CLEAN)
static bool Put(Ctx c, PartDS p, Solid s, bool obstacle, bool hard) {
    if (s == null) return false; var bx = BBox(s); double ov = 0;
    foreach (var o in c.FrameObst) { if (!Ovl(bx, o.B, 0)) continue; try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(s, o.S, BooleanOperationsType.Intersect); if (r != null) ov += Cu(r.Volume); } catch { } }
    if (hard && ov > 50 && c.Mode != "CLEAN") { c.L.AppendLine("  SKIP «" + p.Title + "»: каркаспен қиылысу " + F(ov) + " мм3 > 50 (OVERLAP_MODE=SKIP) — СҰРАҚ"); c.SkippedParts++; return false; }
    double rem; var s2 = Clean(c, s, out rem); if (rem > 1) { c.L.AppendLine("  CLEAN «" + p.Title + "»: " + F(rem) + " мм3 алынды (каркас/бұрынғы бөлшекпен қиылысу)"); c.Removed += rem; }
    if (s2 == null || s2.Volume < 1e-12) return false;
    p.G.Add(s2); if (obstacle) c.Obst.Add(new Sx { S = s2, B = BBox(s2) }); return true; }
static DirectShape MakeDS(Document d, BuiltInCategory want, string key, string loc, string title, string comment, List<GeometryObject> g) {
    var cat = new ElementId(want); if (!DirectShape.IsValidCategoryId(cat, d)) cat = new ElementId(BuiltInCategory.OST_GenericModel);
    var ds = DirectShape.CreateElement(d, cat); ds.ApplicationId = "БК_узел"; ds.ApplicationDataId = key + " | " + loc;
    ds.Name = System.Text.RegularExpressions.Regex.Replace(title + " - " + loc, @"[\:{}\[\]|;<>?`~]", " -"); ds.SetShape(g);
    var cm = ds.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS); if (cm != null) cm.Set(title + " — " + comment + " | " + loc); return ds; }
static int Emit(Ctx c) { int n = 0; foreach (var id in c.Order) { var p = c.Parts[id]; if (p.G.Count == 0) continue; MakeDS(c.D, p.Cat, c.Key, c.Loc, p.Title, p.Comment, p.G); n++; } return n; }
// нысана орындардағы бұрынғы «узел N» денелерін өшіру (қосарланбау)
static int RemoveOld(Document d, string key, HashSet<string> locs) {
    var ids = new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел" && (x.ApplicationDataId ?? "").Contains("|")
        && x.ApplicationDataId.Split('|')[0].Trim() == key && locs.Contains(x.ApplicationDataId.Split('|')[1].Trim())).Select(x => x.Id).ToList();
    if (ids.Count > 0) d.Delete(ids); return ids.Count; }
// ВП жинағын (бастиек, гайка, шайба) каркаспен қиылысуға тексеру: стержень пакет арқылы өтеді (каркаста тесік модельденбейді) — есептелмейді, шайба/бастиек/гайка — есептеледі
static double BoltFrameOverlap(Ctx c, BoltSet bs) {
    double ov = 0; foreach (var g in bs.Heads.Concat(bs.Nuts).Concat(bs.Washers)) { var s = (Solid)g; var bx = BBox(s);
        foreach (var o in c.FrameObst) { if (!Ovl(bx, o.B, 0)) continue; try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(s, o.S, BooleanOperationsType.Intersect); if (r != null) ov += Cu(r.Volume); } catch { } } }
    return ov; }
static void EmitBolts(Ctx c, BoltSet bs, string tag, string L, int n) {
    var cat = BuiltInCategory.OST_StructConnectionBolts;
    foreach (var g in bs.Stems) Part(c, "b_st", cat, "Узел " + tag + ": болт ВП М24×" + L + " стержень", "ВП М24 40Х «Селект» ГОСТ 22353, стержень Ø24 L" + L + " (" + n + " дана)").G.Add(g);
    foreach (var g in bs.Heads) Part(c, "b_hd", cat, "Узел " + tag + ": болт ВП М24 бастиек", "бастиек (" + n + " дана)").G.Add(g);
    foreach (var g in bs.Nuts) Part(c, "b_nt", cat, "Узел " + tag + ": гайка М24", "гайка ВП (" + n + " дана)").G.Add(g);
    foreach (var g in bs.Washers) Part(c, "b_ws", cat, "Узел " + tag + ": шайба М24", "шайба, әр болтқа 2 (" + (2 * n) + " дана)").G.Add(g); }
static string FrameDiag(List<Sx> fr) { return fr.Count + " солид"; }
static List<double[]> Arcs(Solid s, double zTop) { var r = new List<double[]>(); var seen = new HashSet<string>();
    foreach (Edge e in s.Edges) { var a = e.AsCurve() as Arc; if (a == null) continue; if (Math.Abs(a.Center.Z / MM - zTop) > 0.05) continue; string k = F(a.Center.X / MM) + "|" + F(a.Center.Y / MM) + "|" + F(a.Radius / MM * 2); if (seen.Add(k)) r.Add(new[] { a.Center.X / MM, a.Center.Y / MM, a.Radius / MM * 2 }); } return r; }
static string MatName(Document d, Solid s) { try { var id = s.Faces.get_Item(0).MaterialElementId; var m = d.GetElement(id) as Material; return m == null ? "?" : m.Name; } catch { return "?"; } }
static void _libEnd() {
