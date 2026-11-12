import io
def patch(p, pairs):
    s = io.open(p, encoding="utf-8-sig").read()
    for o, n in pairs:
        if o not in s: print("MISSING in", p[-20:], ":", o[:90]); continue
        s = s.replace(o, n, 1)
    io.open(p, "w", encoding="utf-8").write(s)
lib = r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\_авто\v113_sec_lib.cs"
patch(lib, [
 # 1. circle number / sheet: the family parameters are «Номер» / «Лист» (пилот 8: empty circles)
 ('fi.LookupParameter("Номер узла")?.Set(((int)c[3]).ToString()); fi.LookupParameter("Лист схемы")?.Set(((int)c[4]).ToString()); }',
  '(fi.LookupParameter("Номер") ?? fi.LookupParameter("Номер узла"))?.Set(((int)c[3]).ToString()); (fi.LookupParameter("Лист") ?? fi.LookupParameter("Лист схемы"))?.Set(((int)c[4]).ToString()); }'),
 # 2. fachwerk is shown on the развертка only (тексеріс №22): hide Ст*, Рф* in every section
 ('|| x.Category.Id.Value == (long)BuiltInCategory.OST_Viewers ||',
  '|| ((x.Category.Id.Value == (long)BuiltInCategory.OST_StructuralFraming || x.Category.Id.Value == (long)BuiltInCategory.OST_StructuralColumns) && (x.Name.StartsWith("Ст") || x.Name.StartsWith("Рф"))) || x.Category.Id.Value == (long)BuiltInCategory.OST_Viewers ||'),
 # 3. level heads: a level 100…600 over the previous one gets its head 1600 further left (no overlap, тексеріс №21); the runway level on the right
 ('      foreach (var l in lv) { try { l.SetDatumExtentType(DatumEnds.End0, v, DatumExtentType.ViewSpecific);',
  '      double prevZ = -1e9; int stag = 0;\n      foreach (var l in lv) { bool right = l.Name.StartsWith("+6.200"); double lz = l.Elevation / M; if (!right) { stag = lz - prevZ < 600 ? (stag + 1) % 2 : 0; prevZ = lz; } try { l.SetDatumExtentType(DatumEnds.End0, v, DatumExtentType.ViewSpecific);'),
 ('var p0 = W(cu0 - 1800, zz); var p1 = W(cu0 + 900, zz);',
  'var p0 = right ? W(cu1 + 1800, zz) : W(cu0 - 1800 - stag * 1600, zz); var p1 = right ? W(cu1 - 900, zz) : W(cu0 + 900, zz);'),
 ('l.ShowBubbleInView(e0left ? DatumEnds.End0 : DatumEnds.End1, v); l.HideBubbleInView(e0left ? DatumEnds.End1 : DatumEnds.End0, v); }',
  'if (right) e0left = !e0left; l.ShowBubbleInView(e0left ? DatumEnds.End0 : DatumEnds.End1, v); l.HideBubbleInView(e0left ? DatumEnds.End1 : DatumEnds.End0, v); }'),
 ('      if (lv.Count >= 2) { var zs = lv.Select(',
  '      lv = lv.Where(l => !l.Name.StartsWith("+6.200")).ToList();   // the runway level stands on the right, outside the chain\n      if (lv.Count >= 2) { var zs = lv.Select('),
 # 4. purlin chain: snap to the real purlin lines (r01) instead of a 1500 grid (5650 / 6350 collapsed into 6000)
 ('foreach (var q0 in pur) { var q = new XYZ(gx0 + Math.Round((q0.X - gx0) / 1500.0) * 1500.0, q0.Y, 0);',
  'var lines = new[] { 0.0, 3000, 5650, 6350, 9000, 12000 }; foreach (var q0 in pur) { double rel = Math.Abs(q0.X - gx0); var sn = lines.OrderBy(z => Math.Abs(z - rel)).First(); var q = new XYZ(gx0 + Math.Sign(q0.X - gx0 + 1e-9) * sn, q0.Y, 0);'),
 # 5. members seen end-on (ПБ1, Пр1): one mark per kind and side (тексеріс №29)
 ('        a = new XYZ(a.X, a.Y, 0); b = new XYZ(b.X, b.Y, 0); var dd = b - a; if (dd.GetLength() < 300) continue;',
  '''        a = new XYZ(a.X, a.Y, 0); b = new XYZ(b.X, b.Y, 0); var dd = b - a;
        if (dd.GetLength() < 300) { string nm0 = el.Name.Split(' ')[0]; if (nm0 != "ПБ1" && nm0 != "Пр1") continue; var bx0 = el.get_BoundingBox(v); if (bx0 == null) continue; var c0 = L((bx0.Min + bx0.Max) / 2);
          if (c0.X < cu0 || c0.X > cu1 || c0.Y < cv0 || c0.Y > cv1) continue; string k0 = nm0 + (c0.X < (cu0 + cu1) / 2 ? "L" : "R") + (nm0 == "Пр1" ? "" : "");
          if (done.Contains(k0)) continue; done.Add(k0); var o0 = new TextNoteOptions(txtT.Id) { HorizontalAlignment = HorizontalTextAlignment.Center, VerticalAlignment = VerticalTextAlignment.Top };
          try { TextNote.Create(d, v.Id, W(c0.X, c0.Y - (nm0 == "ПБ1" ? 250 : 200)), nm0, o0); nt++; } catch { } continue; }'''),
])
secs = r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\_авто\v113_secs.cs"
s = io.open(secs, encoding="utf-8-sig").read()
i = s.index('"Примечания:\\r1.'); j = s.index('",', i)
s = s[:i] + '"Примечания:\\r1. Общие данные — см. листы 1.1, 1.2; спецификацию металла — лист 1.4.\\r2. Опорные усилия — по результатам перерасчета в ПК ЛИРА-САПР по принятой схеме (графа заполняется после перерасчета).\\r3. Заводские швы — полуавтоматическая сварка в среде CO2; монтажные — электроды Э50А по ГОСТ 9467-75.\\r4. Катеты швов — по наименьшей толщине свариваемых элементов, не менее 5 мм.\\r5. Отметки даны от уровня чистого пола ±0,000. Низ путей подвесного крана — отм. +6,200.' + s[j:]
io.open(secs, "w", encoding="utf-8").write(s)
print("ok")
