import io, sys
p = r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\_авто\v113_plans.cs"
s = io.open(p, encoding="utf-8-sig").read()
def rep(o, n):
    global s
    if o not in s:
        print("MISSING:", o[:80]); return
    s = s.replace(o, n, 1)

rep('"Схема расположения подкрановых балок на отм. +6,250", "Схема расположения подкрановых балок на отм. +6,250"',
    '"Схема расположения путей подвесного крана на отм. +6,200", "Схема расположения путей подвесного крана на отм. +6,200"')

vis = '''        {   // 12.11 (ЕРЕЖЕЛЕР №92, тексеріс №24/№27; аналог Блок 1 л.8: ГС1 под прогонами тонким штрихом): own members normal, context halftone, the rest hidden
            var own = new Dictionary<string, string[]> { { "2.1", new string[0] }, { "3", new[] { "К1", "К2", "СВ1" } }, { "4", new[] { "Р1", "СВ1" } }, { "5", new[] { "ПБ1" } }, { "6", new[] { "Б1", "Б2", "ГС1" } }, { "7", new[] { "Пр1" } } };
            var ctx = new Dictionary<string, string[]> { { "2.1", new string[0] }, { "3", new string[0] }, { "4", new[] { "К1", "К2" } }, { "5", new[] { "Б1", "Б2", "К1" } }, { "6", new[] { "К1", "К2" } }, { "7", new[] { "Б1", "Б2", "ГС1" } } };
            var hideM = new List<ElementId>(); var half = new OverrideGraphicSettings(); half.SetHalftone(true);
            var dash = new FilteredElementCollector(d).OfClass(typeof(LinePatternElement)).Cast<LinePatternElement>().FirstOrDefault(x => x.Name.Contains("Штрих") || x.Name.ToLower().Contains("dash"));
            var thin = new OverrideGraphicSettings(); thin.SetHalftone(true); if (dash != null) { thin.SetProjectionLinePatternId(dash.Id); thin.SetCutLinePatternId(dash.Id); } thin.SetProjectionLineWeight(1);
            foreach (var el in new FilteredElementCollector(d, v.Id).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Symbol.Family.Name.StartsWith("(КМ)")))
            { string mk = Cm(el); if (own[snum].Contains(mk)) continue; if (ctx[snum].Contains(mk)) { v.SetElementOverrides(el.Id, mk == "ГС1" ? thin : half); continue; }
              if (snum == "2.1" && (mk == "К1" || mk == "К2")) continue; hideM.Add(el.Id); }
            if (hideM.Count > 0) v.HideElements(hideM);
        }
        // grids'''
rep('        // grids', vis)

rep('            along(c + nrm * off, ang, Cm(m)); }',
    '''            var tagP = c + nrm * off; IndependentTag tg = null;
            if (sTag != null) { try { tg = IndependentTag.Create(d, sTag.Id, v.Id, new Reference(m), false, TagOrientation.AnyModelDirection, P(tagP.X, tagP.Y)); nm++; } catch (Exception ex) { if (nm < 3) sb.AppendLine("  tag ERR " + ex.Message); tg = null; } }
            if (tg == null) along(tagP, ang, Cm(m)); }''')

old_sld = '    var sLd = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).Cast<FamilySymbol>().First(x => x.FamilyName == "БК_типовая_аннотация_текст_с_выноской");'
rep(old_sld, old_sld + '''
    var sTag = new FilteredElementCollector(d).OfCategory(BuiltInCategory.OST_StructuralFramingTags).WhereElementIsElementType().Cast<FamilySymbol>().FirstOrDefault(x => x.FamilyName == "БК_марка_каркаса");   // марка — тег (№92)
    var sKr = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).Cast<FamilySymbol>().FirstOrDefault(x => x.FamilyName == "БК_узел_круг");''')

a2 = '        sb.AppendLine("sheet " + snum + ": dims " + nd + ", marks " + nm);'
extra = '''        // ---- 12.11: binding dims (№92: прогон қадамы, шығыс; ПБ1 осьтен) on invisible reference lines, node marks — circle + leader to the node (тексеріс №20)
        Func<double[], bool, double, double, int> chain = (pos, alongX, at, from) => { var ra = new ReferenceArray();
            foreach (var q in pos.Distinct().OrderBy(z => z)) { var la = alongX ? P(q, from) : P(from, q); var lb = alongX ? P(q, from + (at > from ? 200 : -200)) : P(from + (at > from ? 200 : -200), q);
              var dc = d.Create.NewDetailCurve(v, Line.CreateBound(la, lb)); dc.LineStyle = invis; ra.Append(dc.GeometryCurve.Reference); }
            try { var l0 = alongX ? Line.CreateBound(P(pos.Min() - 100, at), P(pos.Max() + 100, at)) : Line.CreateBound(P(at, pos.Min() - 100), P(at, pos.Max() + 100)); d.Create.NewDimension(v, l0, ra, dimT); nd++; return 1; }
            catch (Exception ex) { sb.AppendLine("  chain ERR " + ex.Message); return 0; } };
        Action<double, double, double, double, string, string> nodeMark = (nx, ny, cx, cy, num, sh) => { if (sKr == null) return;
            var fc = d.Create.NewFamilyInstance(P(cx, cy), sKr, v); (fc.LookupParameter("Номер") ?? fc.LookupParameter("Номер узла"))?.Set(num); (fc.LookupParameter("Лист") ?? fc.LookupParameter("Лист схемы"))?.Set(sh);
            var dvv = new XYZ(nx - cx, ny - cy, 0); double r = 500; if (dvv.GetLength() > r + 50) { var u = dvv.Normalize(); d.Create.NewDetailCurve(v, Line.CreateBound(P(cx + u.X * r, cy + u.Y * r), P(nx, ny))); } nm++; };
        if (snum == "7")
        {   // purlin lines (r01): 0 / 3000 / 5650 / 6350 / 9000 / 12000 — chain on the right; overhang 250 past axes 1 and 10 — at the top
            chain(new[] { 0.0, 3000, 5650, 6350, 9000, 12000 }, false, 55900, 54400);
            chain(new[] { -250.0, 0 }, true, 13600, 12600); chain(new[] { 54000.0, 54250 }, true, 13600, 12600);
            nodeMark(24000, 3000, 25400, 4300, "8", "24"); nodeMark(30000, -16, 31400, -1300, "8а", "24"); nodeMark(36000, 6000, 37400, 7300, "2", "17");
        }
        if (snum == "5") chain(new[] { 0.0, 1500, 10500, 12000 }, false, 55900, 54400);
'''
rep(a2, extra + a2)
rep('var wantC = new XYZ(tbb.Min.X + 395 * M, tbb.Min.Y + 255 * M, 0);', 'var wantC = new XYZ(tbb.Min.X + 395 * M, tbb.Min.Y + 235 * M, 0);   // 12.11 (№39): the plan lower, notes under it')
io.open(p, "w", encoding="utf-8").write(s)
print("ok")
