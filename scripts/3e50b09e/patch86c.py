import io
p = r"D:/_claude_work/RMC/kzh/kz86_rb.cs"
s = io.open(p, encoding="utf-8-sig").read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:90], s.count(a))
    s = s.replace(a, b)


# атау мәтіні белгі қорабының жоғарғы жағынан ~2…8 мм төмен → қорап үсті = сызба қорабы + 10 мм; фасад рамкадан 13 мм төмен
rep("titleT[vp.Id.Value] = new XYZ((ob.MinimumPoint.X + ob.MaximumPoint.X) / 2, ob.MaximumPoint.Y + 7 * MM, 0); }",
    "titleT[vp.Id.Value] = new XYZ((ob.MinimumPoint.X + ob.MaximumPoint.X) / 2, ob.MaximumPoint.Y + 10 * MM, 0); }")
rep("PlaceTL(VP(views[0]), L + 4, T - 10);", "PlaceTL(VP(views[0]), L + 4, T - 13);")
# 1-1 төменгі маркалар арасы 4,5 мм (мәтін үстіңгі полкаға тимесін)
rep("-1400 - Sc(4) - gi * Sc(4)", "-1400 - Sc(3.5) - gi * Sc(4.5)")
# қорғаныс қабаты: жоғарғы және төменгі бөлек (модельден)
rep("double coverTop = 0;", "double coverTop = 0, coverBot = 0;")
rep("coverTop = Math.Round(-600 - tz - 11); }",
    "coverTop = Math.Round(-600 - tz - 11);\n"
    "      var bz = ri.rebars.Where(q => Cm(q).EndsWith(\"rb:bot\")).Select(Leg).Where(l0 => l0 != null).Select(l0 => l0.GetEndPoint(0).Z / MM).DefaultIfEmpty(-1349).Min(); coverBot = Math.Round(bz + 1400 - 11); }")
rep('lines.Add("Защитный слой бетона до продольной арматуры - " + coverTop + " мм.");',
    'lines.Add(coverTop == coverBot ? "Защитный слой бетона до продольной арматуры - " + coverTop + " мм." : "Защитный слой бетона до продольной арматуры: верхней - " + coverTop + " мм, нижней - " + coverBot + " мм.");')
io.open(p, "w", encoding="utf-8-sig").write(s)
print("ok")
