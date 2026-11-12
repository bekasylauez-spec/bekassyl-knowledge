import io
def patch(p, pairs):
    s = io.open(p, encoding="utf-8-sig").read()
    for o, n in pairs:
        if o not in s: print("MISSING", p[-18:], o[:70]); continue
        s = s.replace(o, n, 1)
    io.open(p, "w", encoding="utf-8").write(s)
A = "D:/Бекасыл КЖ КМ/Завод_В113_КМ/_авто/"
patch(A + "v113_sec_lib.cs", [
 ('&& (x.Name.StartsWith("Ст") || x.Name.StartsWith("Рф"))) || x.Category.Id.Value == (long)BuiltInCategory.OST_Viewers ||',
  '&& (x.Name.StartsWith("Ст") || x.Name.StartsWith("Рф")) && !df.Name.Contains("Развертка")) || x.Category.Id.Value == (long)BuiltInCategory.OST_Viewers ||'),
])
patch(A + "v113_razv.cs", [
 ('if (zs.Count >= 2) { try { d.Create.NewDimension(v, Line.CreateBound(Wp(ua, zs.First()), Wp(ua, zs.Last())), raz, dimT); nd++; } catch (Exception ex) { sb.AppendLine("  z chain " + ex.Message); } }',
  '''if (zs.Count >= 2) { try { var dmz = d.Create.NewDimension(v, Line.CreateBound(Wp(ua, zs.First()), Wp(ua, zs.Last())), raz, dimT); nd++; d.Regenerate(); int alt = 0;
                foreach (DimensionSegment sg in dmz.Segments) { if ((sg.Value ?? 0) / M < 700) { var outw = v.RightDirection * ((fac == "А" || fac == "10") ? -1 : 1); sg.TextPosition = sg.TextPosition + outw * ((alt++ % 2 == 0 ? 4.0 : 8.0) * 100 * M); } } }   // short segments: numbers outward, staggered
              catch (Exception ex) { sb.AppendLine("  z chain " + ex.Message); } }'''),
])
print("ok")
