import io
def patch(p, pairs):
    s = io.open(p, encoding="utf-8-sig").read()
    for o, n in pairs:
        if o not in s: print("MISSING", o[:80]); continue
        s = s.replace(o, n, 1)
    io.open(p, "w", encoding="utf-8").write(s)
patch(r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\_авто\v113_secs.cs", [
 ('new[] { 24000.0, 0, 6930, 1, 16, 14, -12 }, new[] { 24000.0, 6000, 7100, 2, 17, 14, -14 }, new[] { 24000.0, 3000, 7270, 8, 24, -2, -16 }, new[] { 24000.0, 1500, 6500, 9, 25, 12, -12 }',
  'new[] { 24000.0, 0, 6930, 1, 16, 10, -45 }, new[] { 24000.0, 6000, 7100, 2, 17, 14, -14 }, new[] { 24000.0, 3000, 7270, 8, 24, 18, -10 }, new[] { 24000.0, 1500, 6500, 9, 25, 14, -25 }')])
patch(r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\_авто\v113_sec_lib.cs", [
 ('var p0 = right ? W(cu1 + 1800, zz) : W(cu0 - 1800 - stag * 1600, zz); var p1 = right ? W(cu1 - 900, zz) : W(cu0 + 900, zz);',
  'var p0 = right ? W(cu1 + 1500, zz) : W(cu0 - 1800 - stag * 1600, zz); var p1 = right ? W(cu1 - 600, zz) : W(cu0 + 900, zz);'),
 ('l.ShowBubbleInView(e0left ? DatumEnds.End0 : DatumEnds.End1, v); l.HideBubbleInView(e0left ? DatumEnds.End1 : DatumEnds.End0, v); }',
  'bool bl = right ? !e0left : e0left; l.ShowBubbleInView(bl ? DatumEnds.End0 : DatumEnds.End1, v); l.HideBubbleInView(bl ? DatumEnds.End1 : DatumEnds.End0, v); }')])
print("ok")
