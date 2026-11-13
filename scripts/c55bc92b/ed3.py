import io
p=r"D:/Бекасыл КЖ КМ/РМЦ_КМ/_авто/rmc_92_baza_check.cs"
s=io.open(p,encoding='utf-8').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(a[:70],s.count(a)); s=s.replace(a,b)
rep('// РМЦ КМ: База Б1 (D қатары) тексеруі','// РМЦ КМ: База Б1 (A, D, G қатарлары, 25 орын) тексеруі')
rep('(x.ApplicationId == "БК_ЖБ" && (x.ApplicationDataId ?? "").StartsWith("подколонник D"))','(x.ApplicationId == "БК_ЖБ" && (x.ApplicationDataId ?? "").StartsWith("подколонник"))')
rep('var locs = items.Select(i => i.loc).Distinct().OrderBy(l => int.Parse(l.Split(\'-\')[0])).ToList();','var locs = items.Select(i => i.loc).Distinct().OrderBy(l => "ADG".IndexOf(l.Split(\'-\')[1])).ThenBy(l => int.Parse(l.Split(\'-\')[0])).ToList();')
rep('double cx = axX[ai], cy = 18000; var L','double cx = axX[ai], cy = RowY(loc); var L',2)
rep('''var col = colsK1.First(c => { var p = (c.Location as LocationPoint).Point; return Math.Abs(p.X / MM - cx) < 5 && Math.Abs(p.Y / MM - cy) < 5; }); var cb = col.get_BoundingBox(null);''','''var col = colsK1.First(c => { var p = (c.Location as LocationPoint).Point; return Math.Abs(p.X / MM - cx) < 5 && Math.Abs(p.Y / MM - cy) < 5; }); var cb = col.get_BoundingBox(null); var cpt = (col.Location as LocationPoint).Point; cx = cpt.X / MM; cy = cpt.Y / MM;''')
# consistency: skip pod rows
rep('if (rowsBy[loc][i].Replace(loc, "#") != rowsBy[refLoc][i].Replace(refLoc, "#")) {','if (rowsBy[loc][i].StartsWith("подколонник: габарит") || rowsBy[loc][i].StartsWith("подколонник: центр")) continue; if (rowsBy[loc][i].Replace(loc, "#") != rowsBy[refLoc][i].Replace(refLoc, "#")) {')
# capacity section + pod rows kept; add capacity after consistency
rep('sb.AppendLine("--- өзге орындардағы айырма: " + diffs.Count);','''sb.AppendLine("--- өзге орындардағы айырма (подколонник габарит/центр қатарларынан басқа): " + diffs.Count);''')
rep('// ------------------- 2. clash','''// ------------------- 3. подколонник сыйымдылығы (өлшем солидтерден)
sb.AppendLine("=== 3. ПОДКОЛОННИК СЫЙЫМДЫЛЫҒЫ (мм; плита жиегі ↔ подколонник жиегі; анкер осі ↔ подколонник жиегі; ≥150 талап)");
sb.AppendLine("орын\tподк. X×Y\tподк. Y-центр−ось\tплита −X/+X/−Y/+Y\tанкер осі −X/+X/−Y/+Y\tmin анкер\tсыяды");
foreach (var loc in locs)
{
    var L = items.Where(i => i.loc == loc).ToList(); var pd = L.First(i => i.kind == "подколонник"); var pl = L.First(i => i.kind == "плита"); var an = L.Where(i => i.kind == "анкер").ToList();
    double axisY = loc.EndsWith("-A") ? 0 : loc.EndsWith("-G") ? 36000 : 18000; double yc = (pd.bb[1] + pd.bb[4]) / 2; double inward = loc.EndsWith("-G") ? axisY - yc : yc - axisY;
    double[] pg = { pl.bb[0] - pd.bb[0], pd.bb[3] - pl.bb[3], pl.bb[1] - pd.bb[1], pd.bb[4] - pl.bb[4] };
    double ax0 = an.Min(i => (i.bb[0] + i.bb[3]) / 2), ax1 = an.Max(i => (i.bb[0] + i.bb[3]) / 2), ay0 = an.Min(i => (i.bb[1] + i.bb[4]) / 2), ay1 = an.Max(i => (i.bb[1] + i.bb[4]) / 2);
    double[] ag = { ax0 - pd.bb[0], pd.bb[3] - ax1, ay0 - pd.bb[1], pd.bb[4] - ay1 };
    sb.AppendLine(loc + "\t" + F(pd.bb[3] - pd.bb[0]) + "×" + F(pd.bb[4] - pd.bb[1]) + "\t" + F(inward) + (loc.EndsWith("-D") ? " (центр=колонна)" : " ішке") + "\t" + string.Join("/", pg.Select(F)) + "\t" + string.Join("/", ag.Select(F)) + "\t" + F(ag.Min()) + "\t" + (pg.Min() >= 0 && ag.Min() >= 150 ? "иә" : "ЖОҚ"));
}
// ------------------- 2. clash''')
# neighbours: all non-FamilyInstance model elements too
rep('''    var every = L.Concat(nb).ToList();''','''    foreach (var e in otherEls) { var b = e.get_BoundingBox(null); if (b == null) continue; var q = new[] { b.Min.X / MM, b.Min.Y / MM, b.Min.Z / MM, b.Max.X / MM, b.Max.Y / MM, b.Max.Z / MM };
        if (q[0] > gl[3] + 300 || gl[0] > q[3] + 300 || q[1] > gl[4] + 300 || gl[1] > q[4] + 300 || q[2] > gl[5] + 300 || gl[2] > q[5] + 300) continue;
        int k = 0; foreach (var s in SolidsOf(e)) nb.Add(new Item { loc = loc, kind = "каркас:" + e.Category.Name, idx = k++, s = s, bb = BB(s), dsName = e.Category.Name + "#" + e.Id.Value, mat = "" }); }
    var every = L.Concat(nb).ToList();''')
rep('var rowsBy = new Dictionary','''var otherEls = new FilteredElementCollector(d).WhereElementIsNotElementType().Where(e => !(e is FamilyInstance) && !(e is DirectShape) && e.Category != null && e.Category.CategoryType == CategoryType.Model && e.get_BoundingBox(null) != null).ToList();
sb.AppendLine("басқа модель элементтері (FamilyInstance/DirectShape емес): " + otherEls.Count + " " + string.Join(",", otherEls.GroupBy(e => e.Category.Name).Select(g => g.Key + "=" + g.Count())));
var rowsBy = new Dictionary''')
rep('static string F(double v)','static double RowY(string loc) { return loc.EndsWith("-A") ? 266 : loc.EndsWith("-G") ? 35734 : 18000; }\nstatic string F(double v)')
io.open(p,'w',encoding='utf-8',newline='').write(s)
