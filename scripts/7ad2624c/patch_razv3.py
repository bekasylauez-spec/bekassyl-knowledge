import io
def patch(p, pairs):
    s = io.open(p, encoding="utf-8-sig").read()
    for o, n in pairs:
        if o not in s: print("MISSING", p[-18:], o[:70]); continue
        s = s.replace(o, n, 1)
    io.open(p, "w", encoding="utf-8").write(s)
A = "D:/Бекасыл КЖ КМ/Завод_В113_КМ/_авто/"
patch(A + "v113_sec_lib.cs", [
 ('var v = ViewSection.CreateSection(d, vft.Id, bb); v.Name = df.Name; v.Scale = 100;',
  'var v = ViewSection.CreateSection(d, vft.Id, bb); v.Name = df.Name; v.Scale = (df.Name.Contains("Развертка по оси 1")) ? 50 : 100;   // 12.11 (тексеріс №22): gable развертки at 1:50'),
 ('        string nm = el.Name.StartsWith("ФФ1") ? "ФФ1" : el.Name.Split(\' \')[0]; bool isCol = lc == null || Math.Abs(dd.X) < 1;',
  '        string nm = el.Name.StartsWith("ФФ1") ? "ФФ1" : el.Name.Split(\' \')[0]; bool isCol = lc == null || Math.Abs(dd.X) < 1;\n        if (df.Name.Contains("Развертка") && !(nm.StartsWith("Ст") || nm.StartsWith("Рф") || nm.StartsWith("К"))) continue;   // 12.11 (№22): on the развертка only the fachwerk and the columns are marked'),
])
patch(A + "v113_razv.cs", [
 ('Origin = new XYZ(-600, 0, 0),', 'Origin = new XYZ(-600, 0, 0),'),
])
s = io.open(A + "v113_razv.cs", encoding="utf-8-sig").read()
# gable views: smaller range, position for 1:50 on А3
s = s.replace('U0 = -13500, U1 = 1500, V0 = -1200, V1 = 8600, Depth = 1300, Levels = lv, Long = true, Cx = 150, Cy = 195,', 'U0 = -13100, U1 = 1100, V0 = -1100, V1 = 8000, Depth = 1300, Levels = lv, Long = true, Cx = 178, Cy = 190,', 1)
s = s.replace('U0 = -1500, U1 = 13500, V0 = -1200, V1 = 8600, Depth = 1300, Levels = lv, Long = true, Cx = 150, Cy = 195,', 'U0 = -1100, U1 = 13100, V0 = -1100, V1 = 8000, Depth = 1300, Levels = lv, Long = true, Cx = 178, Cy = 190,', 1)
io.open(A + "v113_razv.cs", "w", encoding="utf-8").write(s)
print("ok")
