import io
p = r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\_авто\v113_plans.cs"
s = io.open(p, encoding="utf-8-sig").read()
def rep(o, n):
    global s
    if o not in s: print("MISSING:", o[:90]); return
    s = s.replace(o, n, 1)
# 2.1: top of the view range 400 (fachwerk posts from +0.900 no longer cut into the base scheme)
rep('new object[] { "2.1", "Схема расположения баз колонн", "Схема расположения баз колонн", 1000.0, 300.0, -700.0', 'new object[] { "2.1", "Схема расположения баз колонн", "Схема расположения баз колонн", 400.0, 300.0, -700.0')
# viewers: hide on every scheme (section marks are drawn as БК_знак_разреза at the line ends, outside the dim chains — тексеріс №23)
rep('        if (snum != "3" && snum != "6") { var hv', '        if (true) { var hv')
rep('        if (snum == "3" || snum == "6") { var keepS', '        if (false) { var keepS')
# braced-bay labels off the Р1 tags
rep('along(new XYZ(xy[0] + 3000, xy[1], 0), 0, "СВ1");', 'along(new XYZ(xy[0] + 1200, xy[1], 0), 0, "СВ1");')
# remove the old floating node circles on sheet 6
rep('        if (snum == "6") { var sK = new FilteredElementCollector', '        if (false) { var sK = new FilteredElementCollector')
extra = '''        {   // 12.11: section marks at the ends of the cut lines (outside the dim chains), column binding 210 (№103), node marks on the roof scheme
            var sSec = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).Cast<FamilySymbol>().Where(x => x.FamilyName == "БК_знак_разреза").ToDictionary(x => x.Name);
            Action<double, double, string, string> secMark = (x, y, typ, num) => { if (!sSec.ContainsKey(typ)) return; if (!sSec[typ].IsActive) sSec[typ].Activate();
                var fi = d.Create.NewFamilyInstance(P(x, y), sSec[typ], v); bool ok = false;
                foreach (var pn in new[] { "Номер", "Номер разреза", "Текст", "Обозначение" }) { var pp = fi.LookupParameter(pn); if (pp != null && !pp.IsReadOnly && pp.StorageType == StorageType.String) { pp.Set(num); ok = true; break; } }
                if (!ok) sb.AppendLine("  sec mark: no number parameter"); nm++; };
            if (snum == "3") { foreach (var q in new[] { Tuple.Create(24300.0, "1"), Tuple.Create(600.0, "2") }) { secMark(q.Item1, 12800, "верт., стрелка вправо", q.Item2); secMark(q.Item1, -800, "верт., стрелка вправо", q.Item2); }
                secMark(53400, 12800, "верт., стрелка влево", "3"); secMark(53400, -800, "верт., стрелка влево", "3");
                foreach (var q in new[] { Tuple.Create(-600.0, "4"), Tuple.Create(11400.0, "5") }) { secMark(-700, q.Item1, "гориз., стрелка вниз", q.Item2); secMark(54800, q.Item1, "гориз., стрелка вниз", q.Item2); } }
            if (snum == "6") { secMark(24300, 12800, "верт., стрелка вправо", "1"); secMark(24300, -800, "верт., стрелка вправо", "1"); }
            if (snum == "2.1" || snum == "3") { chain(new[] { -210.0, 0 }, false, -800, -350); chain(new[] { 12000.0, 12210 }, false, -800, -350); }
            if (snum == "6") { nodeMark(0, 0, 1300, 1700, "7а", "22"); nodeMark(6000, 9000, 4500, 10300, "7", "22"); nodeMark(6000, 6000, 4400, 7300, "7б", "22");
                nodeMark(3000, 3000, 1600, 4300, "7г", "23"); nodeMark(9000, 12000, 10400, 10700, "7в", "23"); nodeMark(24000, 6000, 25500, 7300, "2", "17"); nodeMark(24000, 0, 25500, 1400, "1", "16"); }
        }
'''
a2 = '        sb.AppendLine("sheet " + snum + ": dims " + nd + ", marks " + nm);'
rep(a2, extra + a2)
io.open(p, "w", encoding="utf-8").write(s)
print("ok")
