import io
p=r"D:/Бекасыл КЖ КМ/РМЦ_КМ/_авто/rmc_10_baza_B1.cs"
s=io.open(p,encoding='utf-8').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a[:60],s.count(a)); s=s.replace(a,b)
rep('using (var t = new Transaction(d, "РМЦ: база Б1, D қатары"))','''// қатарлар: (әріп, колонна номинал Y, ось Y, подколонник Y-центрі, подколонник Y-өлшемі, базасы бар орынға тиме)
    var rowsDef = new[] { new { r = "A", ny = 266.0, ay = 0.0, pyc = 250.0, ph = 1100.0, keep = false }, new { r = "D", ny = 18000.0, ay = 18000.0, pyc = 18000.0, ph = 1250.0, keep = true }, new { r = "G", ny = 35734.0, ay = 36000.0, pyc = 36000.0 - 250.0, ph = 1100.0, keep = false } };
    var existing = new HashSet<string>(new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел" && (x.ApplicationDataId ?? "").Split('|')[0].Trim() == "база Б1").Select(x => (x.ApplicationDataId ?? "").Split('|')[1].Trim()));
    var tasks = new List<Tuple<double, string, double, double, double, double>>(); // nx, row, cx, cy, pyc, ph   (cx, cy = колонна нақты орны)
    var colOf = new Dictionary<string, FamilyInstance>();
    foreach (var rw in rowsDef) foreach (double nx in axX)
    {
        string loc0 = Axis(nx, rw.r);
        if (rw.keep && existing.Contains(loc0)) { sb.AppendLine("KEEP " + loc0 + ": база бар, тиілмейді"); continue; }
        var col0 = cols.FirstOrDefault(c => { var p = (c.Location as LocationPoint).Point; return Math.Abs(p.X / MM - nx) < 5 && Math.Abs(p.Y / MM - rw.ny) < 5; });
        if (col0 == null) { var nearc = cols.Where(c => { var p = (c.Location as LocationPoint).Point; return Math.Abs(p.X / MM - nx) < 600 && Math.Abs(p.Y / MM - rw.ny) < 12000; }).Select(c => c.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)?.AsString() + "@" + F((c.Location as LocationPoint).Point.Y / MM)); skipped.Add(loc0); sb.AppendLine("SKIP " + loc0 + ": (" + nx + "; " + rw.ny + ") нүктесінде К1 жоқ (ось маңындағы К1: " + string.Join(",", nearc) + ")"); continue; }
        var cbb = col0.get_BoundingBox(null); double cw = (cbb.Max.X - cbb.Min.X) / MM, ch = (cbb.Max.Y - cbb.Min.Y) / MM;
        if (Math.Abs(cw - KB) > 1 || Math.Abs(ch - KH) > 1) { skipped.Add(loc0); sb.AppendLine("SKIP " + loc0 + ": колонна bbox " + F(cw) + "×" + F(ch) + " ≠ " + KB + "×" + KH + " (бағыты/өлшемі басқа)"); continue; }
        var lp0 = (col0.Location as LocationPoint).Point; double ccx = lp0.X / MM, ccy = lp0.Y / MM;
        // подколонникке сыйымдылық: плита (X ±PX/2, Y ±PY/2) және анкер осьтері (±AX, ±AY) подколонник ішінде; анкер осінен бетон жиегіне ≥ 150
        double pyc = rw.r == "D" ? ccy : rw.pyc, ph = rw.ph; double py0 = pyc - ph / 2, py1 = pyc + ph / 2, px0 = ccx - 475, px1 = ccx + 475;
        double[] gaps = { (ccx - PX / 2) - px0, px1 - (ccx + PX / 2), (ccy - PY / 2) - py0, py1 - (ccy + PY / 2) }; double[] ag = { (ccx - AX) - px0, px1 - (ccx + AX), (ccy - AY) - py0, py1 - (ccy + AY) };
        sb.AppendLine("FIT " + loc0 + ": плита жиегі↔подколонник жиегі (−X,+X,−Y,+Y) " + string.Join(" / ", gaps.Select(F)) + " ; анкер осі↔жиек " + string.Join(" / ", ag.Select(F)));
        if (gaps.Min() < 0 || ag.Min() < 150) { skipped.Add(loc0); sb.AppendLine("SKIP " + loc0 + ": СЫЙМАЙДЫ / анкерден жиекке < 150 — СҰРАҚ"); continue; }
        tasks.Add(Tuple.Create(nx, rw.r, ccx, ccy, pyc, ph)); colOf[loc0] = col0;
    }
    var targetLocs = new HashSet<string>(tasks.Select(q => Axis(q.Item1, q.Item2)));
    using (var t = new Transaction(d, "РМЦ: база Б1, A/D/G қатарлары"))''')
rep('''.Where(x => (x.ApplicationId == "БК_узел" && (x.ApplicationDataId ?? "").Split('|')[0].Trim() == "база Б1") || (x.ApplicationId == "БК_ЖБ" && (x.ApplicationDataId ?? "").Split('|')[0].Trim() == "подколонник D")).Select(x => x.Id).ToList();''',
'''.Where(x => (x.ApplicationDataId ?? "").Contains("|") && targetLocs.Contains(x.ApplicationDataId.Split('|')[1].Trim()) && ((x.ApplicationId == "БК_узел" && x.ApplicationDataId.Split('|')[0].Trim() == "база Б1") || (x.ApplicationId == "БК_ЖБ" && x.ApplicationDataId.Split('|')[0].Trim().StartsWith("подколонник")))).Select(x => x.Id).ToList();''')
i=s.index("        foreach (double nx in axX)\n        {\n            var col = cols")
j=s.index("            var bb0 = col.get_BoundingBox(null);")
s=s[:i]+'''        foreach (var tk in tasks)
        {
            double nx = tk.Item1; string row = tk.Item2; double cx = tk.Item3, cy = tk.Item4, podYc = tk.Item5, podH = tk.Item6; string loc = Axis(nx, row); var col = colOf[loc];
'''+s[j:]
rep('var pod = Box(cx - 475, cy - 625, -1000, cx + 475, cy + 625, PODTOP, soPc);','var pod = Box(cx - 475, podYc - podH / 2, -1000, cx + 475, podYc + podH / 2, PODTOP, soPc);')
rep('"БК_ЖБ", "подколонник D", loc, "подколонник (КЖ, контекст) 950×1250", "подколонник (КЖ, контекст) 950×1250, үсті +0.820 … −1.000; центр = колонна центрі; анкер тесіктері Ø42"','"БК_ЖБ", "подколонник " + row, loc, "подколонник (КЖ, контекст) 950×" + F(podH), "подколонник (КЖ, контекст) 950×" + F(podH) + ", үсті +0.820 … −1.000; X центрі = колонна центрі; Y центрі = " + F(podYc) + (row == "D" ? " (= колонна центрі)" : " (осьтен 250 ішке)") + "; анкер тесіктері Ø42"')
io.open(p,'w',encoding='utf-8',newline='').write(s)
