// РМЦ КМ (v2, 13.11.2026): ригель Б1, Б2, Б3 және Б5 семействолары (жұмыс папкасы D:\_claude_work\RMC\revit\fam\). Түпнұсқа кітапхана мен шаблон өзгермейді.
// Геометрия — НОМИНАЛ ҰЗЫНДЫҚҚА тұрақты (семейство созылмайды): профиль экструзиясы балка осінің ортасынан есептелген (X = s − S/2), ұштары ГЛОБАЛ ТІК (жақ жазықтығы қиғаш),
// төменгі белдеу сынық сызық (Б1: горизонталь 0…600, вут 600…6000, 6000…6600 h 450). Б5: ұшында белдеу 117 мм-ге ойылған, стенка 30 + 30 ойықты.
// БАЛКА СЕМЕЙСТВОСЫНЫҢ СОЗЫЛУ ҚАСИЕТІ (13.11 тәжірибе): Revit «Слева/Справа/Элемент/Стикер» жазықтықтарын дана ұзындығына қарай жылжытады, ұшына жақын емес (ішкі) төбелерді ±250 мм ығыстырады.
// Сондықтан жазықтықтар номинал ұзындыққа орналастырылады (MovePlanes: Элемент жазықтығы = ±S/2), ал ішкі төбелер (сынық, ойық баспалдағы) 250 мм ішке алдын ала түзетіледі (Comp). Нәтиже сандық тексеріледі (rmc_01b_test).
// Қайта іске қосуға болады (семейство файлдары қайта жазылады). Лог: go.ps1 -Name rmc_01b_fams
var app = document.Application; var sb = new System.Text.StringBuilder();
string outDir = @"D:\_claude_work\RMC\revit\fam\";
string tpl = @"C:\ProgramData\Autodesk\RVT 2025\Family Templates\Russian\Метрическая система, несущий каркас - Балки и раскосы.rft";
foreach (Document dd in app.Documents.Cast<Document>().ToList()) if (dd.IsFamilyDocument) dd.Close(false);
try {
  // (файл, тип, bt, tf, bb, tb, tw, yS, yE, төменгі белдеу төмен беті: (y, z) жұптары) — A жартысы, top z = 8968 + 0,05 y
  sb.Append(MakeRaf(app, tpl, outDir + "РМЦ_Б1_двутавр_сварной.rfa", "Б1", 250, 12, 250, 12, 6, 0, 6600, new double[] { 0, 8311, 600, 8311, 6000, 8818, 6600, 8848 }));
  sb.Append(MakeRaf(app, tpl, outDir + "РМЦ_Б2_двутавр_сварной.rfa", "Б2", 280, 14, 280, 14, 6, 6600, 12500, new double[] { 6600, 8848, 12500, 9143 }));
  sb.Append(MakeRaf(app, tpl, outDir + "РМЦ_Б3_двутавр_сварной.rfa", "Б3", 350, 18, 350, 18, 8, 12500, 17990, new double[] { 12500, 9143, 17990, 9143 + 175.0 * 5490.0 / 5500.0 }));
  sb.Append(MakeB5(app, tpl, outDir + "РМЦ_Б5L5954_двутавр_сварной.rfa", 5954));
  sb.Append(MakeB5(app, tpl, outDir + "РМЦ_Б5L5804_двутавр_сварной.rfa", 5804));
} catch (Exception ex) { sb.AppendLine("ERR " + ex); }
return sb.ToString();
}
const double MM = 1 / 304.8;
static void Prep(Document fd)
{
    using (var t = new Transaction(fd, "reset")) { t.Start();
        var ex0 = new FilteredElementCollector(fd).OfClass(typeof(Extrusion)).ToElementIds(); if (ex0.Count > 0) fd.Delete(ex0);
        var old = new FilteredElementCollector(fd).OfClass(typeof(ReferencePlane)).Cast<ReferencePlane>().Where(r => r.Name == "Опорная плоскость").Select(r => r.Id).ToList(); if (old.Count > 0) fd.Delete(old);
        t.Commit(); }
}
static CurveArrArray Poly(List<double[]> pts)
{   // pts: (X, Z) мм, профиль XZ жазықтығында
    var ca = new CurveArray(); int n = pts.Count;
    for (int i = 0; i < n; i++) { var a = pts[i]; var b = pts[(i + 1) % n]; ca.Append(Line.CreateBound(new XYZ(a[0] * MM, 0, a[1] * MM), new XYZ(b[0] * MM, 0, b[1] * MM))); }
    var aa = new CurveArrArray(); aa.Append(ca); return aa;
}
static string MovePlanes(Document fd, double S)
{
    var sb = new System.Text.StringBuilder(); double d0 = S / 2 - 1250;
    using (var t = new Transaction(fd, "planes")) { t.Start();
        foreach (var nm in new[] { "Слева", "Элемент слева", "Стикер слева", "Справа", "Элемент справа", "Стикер справа" })
        { var rp = new FilteredElementCollector(fd).OfClass(typeof(ReferencePlane)).Cast<ReferencePlane>().FirstOrDefault(r => r.Name == nm); if (rp == null) { sb.AppendLine("  no plane " + nm); continue; }
          double dx = (nm.Contains("лева") ? -d0 : d0) * MM; try { ElementTransformUtils.MoveElement(fd, rp.Id, new XYZ(dx, 0, 0)); } catch (Exception ex) { sb.AppendLine("  MOVE FAIL " + nm + ": " + ex.Message.Split((char)10)[0]); } }
        t.Commit(); }
    return sb.ToString();
}
// ішкі төбені (ұштан 60 мм-ден артық ішкі) ±250 мм ішке алдын ала түзету
static List<double[]> Comp(List<double[]> pts, double halfLen)
{
    var r = new List<double[]>(); foreach (var p in pts) { double x = p[0]; if (Math.Abs(x) < halfLen - 60) x -= Math.Sign(x) * 250.0; r.Add(new[] { x, p[1] }); } return r;
}
static Extrusion Body(Document fd, SketchPlane plane, List<double[]> pts, double width)
{
    var ex = fd.FamilyCreate.NewExtrusion(true, Poly(pts), plane, 1); ex.StartOffset = -width / 2 * MM; ex.EndOffset = width / 2 * MM; return ex;
}
static void Finish2(Document fd, List<Extrusion> bodies, string tname, System.Text.StringBuilder sb)
{
    var fm = fd.FamilyManager;
    using (var t = new Transaction(fd, "mat+type")) { t.Start(); fd.Regenerate();
        var pMat = fm.get_Parameter(BuiltInParameter.STRUCTURAL_MATERIAL_PARAM);
        var mat = new FilteredElementCollector(fd).OfClass(typeof(Material)).Cast<Material>().FirstOrDefault(m => m.Name == "КМ_сталь") ?? fd.GetElement(Material.Create(fd, "КМ_сталь")) as Material;
        fm.Set(pMat, mat.Id); fd.Regenerate();
        foreach (var x in bodies) { var mp = x.get_Parameter(BuiltInParameter.MATERIAL_ID_PARAM); if (mp != null) try { fm.AssociateElementParameterToFamilyParameter(mp, pMat); } catch (Exception ex) { sb.AppendLine("  material FAIL " + ex.Message); } }
        if (fm.CurrentType == null) fm.NewType(tname); else { try { fm.RenameCurrentType(tname); } catch { } }
        t.Commit(); }
}
static string MakeRaf(Autodesk.Revit.ApplicationServices.Application app, string tpl, string path, string tname, double bt, double tf, double bb, double tb, double tw, double yS, double yE, double[] bot)
{
    var sb = new System.Text.StringBuilder(); var fd = app.NewFamilyDocument(tpl);
    try {
        Prep(fd);
        double th = Math.Atan(0.05), cs = Math.Cos(th), sn = Math.Sin(th);
        Func<double, double> zt = y => 8968.0 + 0.05 * y; double zs = zt(yS); double S = (yE - yS) / cs;
        Func<double, double, double[]> L = (y, z) => { double dy = y - yS, dz = z - zs; double s = dy * cs + dz * sn, w = dy * sn - dz * cs; return new[] { s - S / 2, -w }; };
        sb.Append(MovePlanes(fd, S));
        int n = bot.Length / 2 - 1; double[] by = new double[n + 1], bz = new double[n + 1]; for (int i = 0; i <= n; i++) { by[i] = bot[2 * i]; bz[i] = bot[2 * i + 1]; }
        var top = new List<double[]> { L(yS, zt(yS)), L(yE, zt(yE)), L(yE, zt(yE) - tf / cs), L(yS, zt(yS) - tf / cs) };
        var web = new List<double[]> { L(yS, zt(yS) - tf / cs), L(yE, zt(yE) - tf / cs), L(yE, bz[n] + tb) }; for (int i = n - 1; i >= 0; i--) web.Add(L(by[i], bz[i] + tb));
        var lo = new List<double[]>(); for (int i = 0; i <= n; i++) lo.Add(L(by[i], bz[i])); lo.Add(L(yE, bz[n] + tb)); for (int i = n - 1; i >= 0; i--) lo.Add(L(by[i], bz[i] + tb));
        var bodies = new List<Extrusion>();
        using (var t = new Transaction(fd, "body")) { t.Start();
            var plane = SketchPlane.Create(fd, Plane.CreateByNormalAndOrigin(XYZ.BasisY, XYZ.Zero));
            bodies.Add(Body(fd, plane, Comp(top, S / 2), bt)); bodies.Add(Body(fd, plane, Comp(web, S / 2), tw)); bodies.Add(Body(fd, plane, Comp(lo, S / 2), bb)); t.Commit(); }
        Finish2(fd, bodies, tname, sb);
        fd.SaveAs(path, new SaveAsOptions { OverwriteExistingFile = true }); sb.AppendLine("saved " + path + " (S = " + Math.Round(S, 2) + ")");
    } finally { fd.Close(false); }
    return sb.ToString();
}
static string MakeB5(Autodesk.Revit.ApplicationServices.Application app, string tpl, string path, double Lb)
{
    var sb = new System.Text.StringBuilder(); var fd = app.NewFamilyDocument(tpl);
    try {
        Prep(fd); sb.Append(MovePlanes(fd, Lb));
        double h = 324, tf = 12, bw = 200, tw = 6, nn = 117, hl = Lb / 2;   // белдеу Б4 осінен 140-тан басталады: ұштан 140 − 23 = 117
        var top = new List<double[]> { new[] { -hl + nn, 0.0 }, new[] { hl - nn, 0.0 }, new[] { hl - nn, -tf }, new[] { -hl + nn, -tf } };
        var bot = new List<double[]> { new[] { -hl + nn, -(h - tf) }, new[] { hl - nn, -(h - tf) }, new[] { hl - nn, -h }, new[] { -hl + nn, -h } };
        var web = new List<double[]> { new[] { -hl, -30.0 }, new[] { -hl + nn, -30.0 }, new[] { -hl + nn, -tf }, new[] { hl - nn, -tf }, new[] { hl - nn, -30.0 }, new[] { hl, -30.0 },
            new[] { hl, -(h - 30) }, new[] { hl - nn, -(h - 30) }, new[] { hl - nn, -(h - tf) }, new[] { -hl + nn, -(h - tf) }, new[] { -hl + nn, -(h - 30) }, new[] { -hl, -(h - 30) } };
        var bodies = new List<Extrusion>();
        using (var t = new Transaction(fd, "body")) { t.Start();
            var plane = SketchPlane.Create(fd, Plane.CreateByNormalAndOrigin(XYZ.BasisY, XYZ.Zero));
            bodies.Add(Body(fd, plane, Comp(top, hl), bw)); bodies.Add(Body(fd, plane, Comp(web, hl), tw)); bodies.Add(Body(fd, plane, Comp(bot, hl), bw)); t.Commit(); }
        Finish2(fd, bodies, "Б5", sb);
        fd.SaveAs(path, new SaveAsOptions { OverwriteExistingFile = true }); sb.AppendLine("saved " + path);
    } finally { fd.Close(false); }
    return sb.ToString();
