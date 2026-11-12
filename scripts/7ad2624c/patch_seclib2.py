import io
def patch(p, pairs):
    s = io.open(p, encoding="utf-8-sig").read()
    for o, n in pairs:
        if o not in s: print("MISSING in", p[-20:], ":", o[:90]); continue
        s = s.replace(o, n, 1)
    io.open(p, "w", encoding="utf-8").write(s)
lib = r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\_авто\v113_sec_lib.cs"
patch(lib, [
 ('if (right) e0left = !e0left; l.ShowBubbleInView', 'l.ShowBubbleInView'),
 # total height chain on the right (the left one carried the level heads over its number — тексеріс №21)
 ('dim(new List<Reference> { new Reference(lv.First()), new Reference(lv.Last()) }, false, cu0 - 1400, zs.Min(), zs.Max()); }',
  'dim(new List<Reference> { new Reference(lv.First()), new Reference(lv.Last()) }, false, cu1 + 700, zs.Min(), zs.Max()); }'),
 # Пр1 end-on: mark above the purlin (it stood on the column / beam)
 ('try { TextNote.Create(d, v.Id, W(c0.X, c0.Y - (nm0 == "ПБ1" ? 250 : 200)), nm0, o0); nt++; } catch { } continue; }',
  'if (nm0 == "Пр1") o0.VerticalAlignment = VerticalTextAlignment.Bottom; try { TextNote.Create(d, v.Id, W(c0.X, nm0 == "ПБ1" ? c0.Y - 250 : L(bx0.Max).Y + 150), nm0, o0); nt++; } catch { } continue; }'),
 # node circles: a leader from the circle to the node (тексеріс №20)
 ('(fi.LookupParameter("Номер") ?? fi.LookupParameter("Номер узла"))?.Set(((int)c[3]).ToString());',
  '{ var cc = new XYZ(q.X + ox * v.Scale, q.Y + oy * v.Scale, 0); var dv0 = new XYZ(q.X - cc.X, q.Y - cc.Y, 0); double rr = 7.0 * v.Scale; if (dv0.GetLength() > rr + 50) { var uu = dv0.Normalize(); try { d.Create.NewDetailCurve(v, Line.CreateBound(W(cc.X + uu.X * rr, cc.Y + uu.Y * rr), W(q.X, q.Y))); } catch { } } }\n        (fi.LookupParameter("Номер") ?? fi.LookupParameter("Номер узла"))?.Set(((int)c[3]).ToString());'),
])
secs = r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\_авто\v113_secs.cs"
patch(secs, [
 ('new[] { 24000.0, 0, 6930, 1, 16, -10, 14 }, new[] { 24000.0, 6000, 7600, 2, 17, 0, 16 }, new[] { 24000.0, 3000, 7270, 8, 24, -6, 16 }',
  'new[] { 24000.0, 0, 6930, 1, 16, 14, -12 }, new[] { 24000.0, 6000, 7100, 2, 17, 14, -14 }, new[] { 24000.0, 3000, 7270, 8, 24, -2, -16 }'),
])
print("ok")
