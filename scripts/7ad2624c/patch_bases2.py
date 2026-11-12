import io
def patch(p, pairs):
    s = io.open(p, encoding="utf-8-sig").read()
    for o, n in pairs:
        if o not in s: print("MISSING in", p[-25:], ":", o[:90]); continue
        s = s.replace(o, n, 1)
    io.open(p, "w", encoding="utf-8").write(s)
A = "D:/Бекасыл КЖ КМ/Завод_В113_КМ/_авто/"
patch(A + "v113_bases_sheets.cs", [
 ('new object[] { vP, new XYZ(cx, cy, 150), XYZ.BasisX, XYZ.BasisY, XYZ.BasisZ, -hx - mg, hx + mg, -hy - mg, hy + mg, 700.0 },',
  'new object[] { vP, new XYZ(cx, cy, 150), XYZ.BasisX, XYZ.BasisY, XYZ.BasisZ, -hx - 480, hx + 480, -hy - mg, hy + mg, 700.0 },   // 12.11: room for the axis binding dims'),
 ('TextNote.Create(d, v.Id, W(be[1] + 160, zF - 20), "Верх фундамента -0,450", o3);',
  'o3.HorizontalAlignment = HorizontalTextAlignment.Right; TextNote.Create(d, v.Id, W(be[0] - 160, zF - 20), "Верх фундамента -0,450", o3); spot(-400, -1, be[0] + 40);'),
 ('leader(new XYZ(be[0] + 60, (zF + zb0) / 2, 0), -10, -6, "Подливка 50", "бетон В25", true); }',
  'leader(new XYZ(be[1] - 60, (zF + zb0) / 2, 0), 16, -16, "Подливка 50", "бетон В25", true); }'),
 ('TextNote.Create(d, v.Id, W(be[1] + 300, axL.Y + 15), "ось " + (cy < 6000 ? "А" : "В"), o4); }',
  'TextNote.Create(d, v.Id, W(be[0] - 470, axL.Y + 15), "ось " + (cy < 6000 ? "А" : "В"), o4); }'),
])
patch(A + "v113_3d.cs", [
 ('          double g = 120 * M; var mn = new XYZ(pts.Min(p => p.X) - g, pts.Min(p => p.Y) - g, pts.Min(p => p.Z) - g); var mx = new XYZ(pts.Max(p => p.X) + g, pts.Max(p => p.Y) + g, pts.Max(p => p.Z) + g);',
  '          double g = (sn <= 15 ? 20 : 120) * M; var mn = new XYZ(pts.Min(p => p.X) - g, pts.Min(p => p.Y) - g, pts.Min(p => p.Z) - g); var mx = new XYZ(pts.Max(p => p.X) + g, pts.Max(p => p.Y) + g, pts.Max(p => p.Z) + g);\n          if (sn <= 15) { mn = new XYZ(mn.X, mn.Y, Math.Max(mn.Z, -480 * M)); mx = new XYZ(mx.X, mx.Y, Math.Min(mx.Z, 350 * M)); }   // 12.11 (№31): the base, not the plan depth — bigger 3D'),
])
print("ok")
