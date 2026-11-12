import io
def patch(p, pairs):
    s = io.open(p, encoding="utf-8-sig").read()
    for o, n in pairs:
        if o not in s: print("MISSING in", p[-25:], ":", o[:90]); continue
        s = s.replace(o, n, 1)
    io.open(p, "w", encoding="utf-8").write(s)
A = "D:/Бекасыл КЖ КМ/Завод_В113_КМ/_авто/"
patch(A + "v113_bases_sheets.cs", [
 # section marks in the plan: symbols at the line ends outside the dim tiers (viewers hidden)
 ('var vw = new FilteredElementCollector(d, v.Id).OfCategory(BuiltInCategory.OST_Viewers).ToElements().Where(x => !(i == 0 && keepV.Contains(x.Name))).Select(x => x.Id).ToList();',
  'var vw = new FilteredElementCollector(d, v.Id).OfCategory(BuiltInCategory.OST_Viewers).ToElements().Select(x => x.Id).ToList();   // 12.11: all viewers hidden, the plan gets БК_знак_разреза at the line ends'),
 ('spot(-400, -1, be[0] + 40);', ''),
 ('dim(new List<XYZ> { new XYZ(be[0] - 430, axL.Y, 0), new XYZ(be[0] - 430, ctr0.Y, 0), new XYZ(be[0] - 430, faceL.Y, 0) }, false, be[0] - 430);',
  '''dim(new List<XYZ> { new XYZ(be[0] - 400, axL.Y, 0), new XYZ(be[0] - 400, ctr0.Y, 0), new XYZ(be[0] - 400, faceL.Y, 0) }, false, be[0] - 380);
              dim(new List<XYZ> { new XYZ(be[0] - 450, axL.Y, 0), new XYZ(be[0] - 450, faceL.Y, 0) }, false, be[0] - 450);
              var sSec = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).Cast<FamilySymbol>().Where(x => x.FamilyName == "БК_знак_разреза").ToDictionary(x => x.Name);
              Action<XYZ, string, string> sm = (pt, typ, num) => { if (!sSec.ContainsKey(typ)) return; if (!sSec[typ].IsActive) sSec[typ].Activate(); var fi = d.Create.NewFamilyInstance(W(pt.X, pt.Y), sSec[typ], v);
                foreach (var pn in new[] { "Номер", "Номер разреза", "Текст", "Обозначение" }) { var pp = fi.LookupParameter(pn); if (pp != null && !pp.IsReadOnly && pp.StorageType == StorageType.String) { pp.Set(num); break; } } };
              var c1 = L(new XYZ(cx, cy - 10, 0) * M); sm(new XYZ(be[0] - 330, c1.Y, 0), "гориз., стрелка вниз", "1"); sm(new XYZ(be[1] + 330, c1.Y, 0), "гориз., стрелка вниз", "1");
              var c2 = L(new XYZ(cx + 20, cy, 0) * M); sm(new XYZ(c2.X, be[3] + 330, 0), "верт., стрелка вправо", "2"); sm(new XYZ(c2.X, be[2] - 330, 0), "верт., стрелка вправо", "2");'''),
])
patch(A + "v113_3d.cs", [
 ('if (sn <= 15) { mn = new XYZ(mn.X, mn.Y, Math.Max(mn.Z, -480 * M)); mx = new XYZ(mx.X, mx.Y, Math.Min(mx.Z, 350 * M)); }',
  'if (sn <= 15) { var cc = (mn + mx) / 2; mn = new XYZ(cc.X - 420 * M, cc.Y - 420 * M, Math.Max(mn.Z, -480 * M)); mx = new XYZ(cc.X + 420 * M, cc.Y + 420 * M, Math.Min(mx.Z, 350 * M)); }'),
])
print("ok")
