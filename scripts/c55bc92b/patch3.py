P = r'D:\Бекасыл КЖ КМ\РМЦ_КМ\_авто\rmc_01b_fams.cs'
s = open(P, encoding='utf-8').read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:60])
    s = s.replace(old, new)
# header note
rep("// Қайта іске қосуға болады (семейство файлдары қайта жазылады). Лог: go.ps1 -Name rmc_01b_fams",
    "// БАЛКА СЕМЕЙСТВОСЫНЫҢ СОЗЫЛУ ҚАСИЕТІ (13.11 тәжірибе): Revit «Слева/Справа/Элемент/Стикер» жазықтықтарын дана ұзындығына қарай жылжытады, ұшына жақын емес (ішкі) төбелерді ±250 мм ығыстырады.\n"
    "// Сондықтан жазықтықтар номинал ұзындыққа орналастырылады (MovePlanes: Элемент жазықтығы = ±S/2), ал ішкі төбелер (сынық, ойық баспалдағы) 250 мм ішке алдын ала түзетіледі (Comp). Нәтиже сандық тексеріледі (rmc_01b_test).\n"
    "// Қайта іске қосуға болады (семейство файлдары қайта жазылады). Лог: go.ps1 -Name rmc_01b_fams")
# helpers
rep("static Extrusion Body(", """static string MovePlanes(Document fd, double S)
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
static Extrusion Body(""")
# MakeRaf: move planes + comp
rep("""        int n = bot.Length / 2 - 1;""", """        sb.Append(MovePlanes(fd, S));
        int n = bot.Length / 2 - 1;""")
rep("""            bodies.Add(Body(fd, plane, top, bt)); bodies.Add(Body(fd, plane, web, tw)); bodies.Add(Body(fd, plane, lo, bb)); t.Commit(); }""",
    """            bodies.Add(Body(fd, plane, Comp(top, S / 2), bt)); bodies.Add(Body(fd, plane, Comp(web, S / 2), tw)); bodies.Add(Body(fd, plane, Comp(lo, S / 2), bb)); t.Commit(); }""")
# MakeB5
rep("""        Prep(fd);
        double h = 324, tf = 12, bw = 200, tw = 6, nn = 117, hl = Lb / 2;""", """        Prep(fd); sb.Append(MovePlanes(fd, Lb));
        double h = 324, tf = 12, bw = 200, tw = 6, nn = 117, hl = Lb / 2;""")
rep("""            bodies.Add(Body(fd, plane, top, bw)); bodies.Add(Body(fd, plane, web, tw)); bodies.Add(Body(fd, plane, bot, bw)); t.Commit(); }""",
    """            bodies.Add(Body(fd, plane, Comp(top, hl), bw)); bodies.Add(Body(fd, plane, Comp(web, hl), tw)); bodies.Add(Body(fd, plane, Comp(bot, hl), bw)); t.Commit(); }""")
open(P, 'w', encoding='utf-8').write(s)
print('ok')
