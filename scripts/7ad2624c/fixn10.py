p = 'D:/Бекасыл КЖ КМ/Завод_В113_КМ/_авто/v113_razv.cs'
s = open(p, encoding='utf-8').read()
o = 'Cx = 395, Cy = 275, Lw = 70, Hide = x => { var b = x.get_BoundingBox(null); return b == null || (b.Min.Y + b.Max.Y) / 2 / M > 800; } }),'
assert s.count(o) >= 1
n = ('Cx = 395, Cy = 275, Lw = 70, Hide = x => { var b = x.get_BoundingBox(null); return b == null || (b.Min.Y + b.Max.Y) / 2 / M > 800; },\n'
     '          /* 13.11 (checker): sheet 27 refers to 11/28, 12/28, 12а/28 — the node marks on this elevation (Рф1 ↔ К1 at axis 2, Ст3 foot and head at the gate) */\n'
     '          Circles = new List<double[]> { new[] { 6000.0, -15, 2940, 11, 27, -14, 12 }, new[] { 13940.0, -15, 60, 12, 27, 14, 10 }, new[] { 13940.0, -15, 2120, 12.1, 27, 14, 12 } } }),')
s = s.replace(o, n, 1)
open(p, 'w', encoding='utf-8').write(s); print('ok')
