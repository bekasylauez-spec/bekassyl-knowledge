import io
p = "D:/Бекасыл КЖ КМ/Завод_В113_КМ/_авто/v113_bases_sheets.cs"
s = io.open(p, encoding="utf-8-sig").read()
pairs = [
 ('sm(new XYZ(be[0] - 330, c1.Y, 0), "гориз., стрелка вниз", "1"); sm(new XYZ(be[1] + 330, c1.Y, 0), "гориз., стрелка вниз", "1");',
  'sm(new XYZ(be[0] - 580, c1.Y, 0), "гориз., стрелка вниз", "1"); sm(new XYZ(be[1] + 420, c1.Y, 0), "гориз., стрелка вниз", "1");'),
 ('sm(new XYZ(c2.X, be[3] + 330, 0), "верт., стрелка вправо", "2"); sm(new XYZ(c2.X, be[2] - 330, 0), "верт., стрелка вправо", "2");',
  'sm(new XYZ(c2.X, be[3] + 420, 0), "верт., стрелка вправо", "2"); sm(new XYZ(c2.X, be[2] - 420, 0), "верт., стрелка вправо", "2");'),
 ('TextNote.Create(d, v.Id, W(be[0] - 470, axL.Y + 15), "ось "', 'TextNote.Create(d, v.Id, W(be[1] + 110, axL.Y + 15), "ось "'),
 ('          views.Add(v); }', '          try { v.SetCategoryHidden(new ElementId(BuiltInCategory.OST_StructuralFraming), true); } catch { }   // 12.11: ригели фахверка (Рф1) in the Б3 section\n          views.Add(v); }'),
]
for o, n in pairs:
    if o not in s: print("MISSING", o[:60])
    s = s.replace(o, n, 1)
io.open(p, "w", encoding="utf-8").write(s); print("ok")
