import io
def patch(p, pairs):
    s = io.open(p, encoding="utf-8-sig").read()
    for o, n in pairs:
        if o not in s: print("MISSING", p[-22:], o[:70]); continue
        s = s.replace(o, n, 1)
    io.open(p, "w", encoding="utf-8").write(s)
A = "D:/Бекасыл КЖ КМ/Завод_В113_КМ/_авто/"
patch(A + "v113_bases_sheets.cs", [
 ('var pos = new[] { new XYZ(98, 178, 0),', 'var pos = new[] { new XYZ(113, 178, 0),'),
 ('sm(new XYZ(be[0] - 580, c1.Y, 0), "гориз., стрелка вниз", "1"); sm(new XYZ(be[1] + 420, c1.Y, 0), "гориз., стрелка вниз", "1");',
  'sm(new XYZ(be[0] - 540, c1.Y, 0), "гориз., стрелка вниз", "1"); sm(new XYZ(be[1] + 330, c1.Y, 0), "гориз., стрелка вниз", "1");'),
 ('        TextNote.Create(d, sheet.Id, tbb.Min + new XYZ(25 * M, 52 * M, 0), 200 * M, notes,',
  '        if (mk == "Б2") notes += "\\n7. Крепление вертикальных связей СВ1 к колонне у базы - узел 4 (лист 19). База Б2 отличается от Б1 только фасонкой связи.";\n        if (mk != "Б3") notes += "\\n" + (mk == "Б2" ? "8" : "7") + ". Наружная грань колонны - 210 мм от оси ряда; анкерные болты - по заданию КМ, фундамент КЖ корректируется.";\n        TextNote.Create(d, sheet.Id, tbb.Min + new XYZ(25 * M, 52 * M, 0), 200 * M, notes,'),
])
patch(A + "v113_3d.cs", [('yTop = tbb.Min.Y + 158 * M; yBot = tbb.Min.Y + 66 * M;', 'yTop = tbb.Min.Y + 150 * M; yBot = tbb.Min.Y + 64 * M;')])
print("ok")
