import io
p = r"D:/_claude_work/RMC/kzh/kz87_slab.cs"
s = io.open(p, encoding="utf-8").read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:90], s.count(a))
    s = s.replace(a, b)


# төменгі тізбектер отмосткадан (−900) тыс
rep("double yAx = y0 - 8 * S, yAll = y0 - 15 * S, yBub = yAll - 8 * S;",
    "double yAx = AY.First() - 900 - 8 * S, yAll = yAx - 7 * S, yBub = yAll - 8 * S;")
rep("double xAx = LEFT - 8 * S, xAll = LEFT - 15 * S, xBub = xAll - 8 * S;",
    "double xAx = LEFT - 8 * S, xAll = xAx - 7 * S, xBub = xAll - 8 * S;")
# жалпы өлшем бағыты — Line.Direction
rep("{ bool hz = Math.Abs(dm.Curve.ComputeDerivatives(0, true).BasisX.Normalize().Y) < 0.5;",
    "{ var dl = dm.Curve as Line; if (dl == null) continue; bool hz = Math.Abs(dl.Direction.Y) < 0.5;")
# маркалар: шов сызықтары мен осьтерді кеспейтін орындар, қысқа мәтін
old = s[s.index("    // Пп-1: B–C/2–3 аралығының ортасында"):s.index("    // ±0,000 мәтіні (плита үсті)")]
new = ("    // Пп-1 және сілтемелер: полкасы бір аралықтың ішінде (шов/ось сызығын кеспейді)\n"
       "    Lbl(\"Пп-1\", \"h=200\", 14600, 9800, new[] { new[] { 13300.0, 8200 } });\n"
       "    Lbl(\"Шов усадочный\", \"см. узел 2, л. 6.1\", 20200, 16300, new[] { new[] { 18000.0, 15600 } });\n"
       "    Lbl(\"Шов 20 мм\", \"см. узел 3, л. 6.1\", 32400, 20600, new[] { new[] { 30450.0, 18600 } });\n"
       "    Lbl(\"Пандус i=5%\", \"см. узел 6, л. 6.1\", 27000, AY.Last() + 4300, new[] { new[] { 29000.0, AY.Last() + 2000 } });\n"
       "    Lbl(\"Пандус i=5% (до -0,150)\", \"см. узел 6, л. 6.1\", 27000, AY.Last() - 4800, new[] { new[] { 26000.0, AY.Last() - 2400 } });\n"
       "    Lbl(\"Крыльцо\", \"см. узел 9, л. 6.1\", AX.Last() + 5500, 18000, new[] { new[] { AX.Last() + 1000, 22900.0 } });\n"
       "    Lbl(\"Отмостка b=600\", \"см. узел 8, л. 6.1\", AX.Last() + 5500, 3000, new[] { new[] { AX.Last() + 600, 2000.0 } });\n"
       "    // санузел −0,150: штрих контур + жазу аймақ ішінде\n"
       "    { double tx0 = 54120, ty0 = 30120, tx1 = AX.Last() + 10, ty1 = AY.Last() + 10;\n"
       "      Poly(new[] { tx0, ty0, tx1, ty0 }, gsDash); Poly(new[] { tx0, ty0, tx0, ty1 }, gsDash);\n"
       "      Lbl(\"Верх плиты -0,150\", \"санузлы, узел 5, л. 6.1\", 57000, 34500, new[] { new[] { 58000.0, 32000 } }); }\n")
s = s[:s.index("    // Пп-1: B–C/2–3 аралығының ортасында")] + new + s[s.index("    // ±0,000 мәтіні (плита үсті)"):]
# примечание штамптың сол жағында, төменде (жоспардың астыңғы оң бұрышымен қабаттаспайды)
rep("var nn = TextNote.Create(d, sh.Id, new XYZ((R - 185) * MM, (B + 55 + 5) * MM, 0), 185 * MM, notes,",
    "var nn = TextNote.Create(d, sh.Id, new XYZ((R - 185 - 8 - 265) * MM, (B + 5) * MM, 0), 265 * MM, notes,")
rep("if (nb.Max.Y / MM > ob.MinimumPoint.Y / MM - 2 && nb.Min.X / MM < ob.MaximumPoint.X / MM) log.Add(\"WARN notes touch plan\");",
    "if (nb.Max.Y / MM > ob.MinimumPoint.Y / MM - 2) log.Add(\"WARN notes touch plan box\"); if (nb.Min.X / MM < b1[2] + 3 && nb.Max.Y / MM > b2[1]) log.Add(\"WARN notes ↔ tables\");")
io.open(p, "w", encoding="utf-8").write(s)
print("ok")
