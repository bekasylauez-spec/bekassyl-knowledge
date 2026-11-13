def sub(p, pairs):
    s = open(p, encoding='utf-8').read()
    for o, n in pairs:
        assert o in s, o
        s = s.replace(o, n, 1)
    open(p, 'w', encoding='utf-8').write(s)
a = 'D:/Бекасыл КЖ КМ/Завод_В113_КМ/_авто/'
sub(a + 'v113_sec_lib.cs', [
 ('      double prevZ = -1e9; int stag = 0;',
  '      double prevZ = -1e9; int stag = 0;\n'
  '      // 13.11: level heads / height chains are bound to the first axis of the drawing (gA), not to the crop edge (the crop has 2000+ empty mm before axis А — the annotations stood far off and the view had to be shifted into the schedule of sheet 8)\n'
  '      double gA = cu0 + 2600; { var gxs = grids.Select(g => { try { return L(g.Curve.GetEndPoint(0)).X; } catch { return double.NaN; } }).Where(x => !double.IsNaN(x) && x > cu0 - 1 && x < cu1 + 1).ToList(); if (gxs.Count > 0) gA = gxs.Min(); }'),
 ('W(cu0 - 1800 - stag * 1300, zz)', 'W(gA - 2200 - stag * 1300, zz)'),
 ('W(cu0 + 900, zz)', 'W(gA - 400, zz)'),
 ("false, cu0 - 600, zs.Min(), zs.Max());", "false, gA - 1000, zs.Min(), zs.Max());"),
 ("false, cu0 - 1200, zs.Min(), zs.Max()); }", "false, gA - 1600, zs.Min(), zs.Max()); }")])
sub(a + 'v113_secs.cs', [
 ('Cx = 162 /* 13.11: 150 -> 158 (+7,110 head on the frame), +4 for the 800 longer crop on the right */', 'Cx = 148 /* 13.11: heads now from axis А (lib gA), view 14 mm left — axis В was under the schedule */'),
 ('Cx = 155 /* 13.11: 151 -> 159 (+7,307 head on the frame), -4 for the 800 longer crop on the left (PadL) */', 'Cx = 147 /* 13.11: 151, -4 for the 800 longer crop on the left (PadL); heads from the axis (lib gA) */')])
print('ok')
