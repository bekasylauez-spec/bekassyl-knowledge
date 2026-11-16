import io
BS = chr(92)
NL = BS + "n"
p = r"D:/_claude_work/RMC/kzh/kz97_static_tables.cs"
s = io.open(p, encoding="utf-8").read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:90], s.count(a))
    s = s.replace(a, b)


# (1) «Масса ед.кг» — шаблондағыдай екі жол (7.1-де бір жолда ұяшыққа тиіп тұрды)
rep('string[] H6 = { "Поз.", "Обозначение", "Наименование", "Кол.", "Масса ед.кг", "Примечание" };',
    'string[] H6 = { "Поз.", "Обозначение", "Наименование", "Кол.", "Масса' + NL + 'ед.кг", "Примечание" };')
# (2) масса = Кол. × Масса ед. (пог.м. жолдарында бүтінге дөңгелектелген еді: 22605 × 0.617 = 13947.29)
rep('Func<double, string> FV = x => x < 0.1 ? x.ToString("0.000", INV) : x.ToString("0.00", INV);   // бетон көлемі',
    'Func<double, string> FV = x => x < 0.1 ? x.ToString("0.000", INV) : x.ToString("0.00", INV);   // бетон көлемі\n'
    'Func<string[], double> Pm = r => { double q, m; q = Num(r[4]); m = Num(r[5]); return q > 0 && m > 0 ? Math.Round(q * m, 2) : Num(r[6]); };   // позиция массасы = Кол. × Масса ед.')
rep('var p1 = sp.First(r => r[1] == "1"); double mass = Num(p1[6]);',
    'var p1 = sp.First(r => r[1] == "1"); double mass = Pm(p1);')
rep('double tot = g.Sum(r => Num(r[6])); rows.Add(new[] { "", "", el, "", "", F2(tot) });\n        foreach (var r in g) rows.Add(new[] { r[1], r[2], r[3], r[4], Dt(r[5]), F2(Num(r[6])) });',
    'double tot = g.Sum(r => Pm(r)); rows.Add(new[] { "", "", el, "", "", F2(tot) });\n        foreach (var r in g) rows.Add(new[] { r[1], r[2], r[3], r[4], Dt(r[5]), F2(Pm(r)) });')
rep('double a6 = g.Where(r => r[3].Contains("Ø6 А240")).Sum(r => Num(r[6])), b10 = g.Where(r => r[3].Contains("Ø10 А500С")).Sum(r => Num(r[6]));',
    'double a6 = g.Where(r => r[3].Contains("Ø6 А240")).Sum(r => Pm(r)), b10 = g.Where(r => r[3].Contains("Ø10 А500С")).Sum(r => Pm(r));')
# (3) 7.1: Пп-1 мен Пандусы — 5.1 / 6.2 кестелеріндегі нақты масса; ВРС «Всего» жолы қайта қосылады
rep('      var rows = new List<string[]> { H6 };\n      foreach (var g in sp.GroupBy(r => r[0]))\n      { string gn = ',
    '      double m51 = 0, m62 = 0; { var s51 = Carr("КЖ-5.1/спец").FirstOrDefault(r => r[1] == "1"); if (s51 != null) m51 = Pm(s51); var s62 = Carr("КЖ-6.2/спец").Where(r => r[0].Contains("Пандус") && r[3].Contains("Ø10 А500С")).ToList(); m62 = s62.Sum(r => Pm(r)); }\n'
    '      var rows = new List<string[]> { H6 };\n      foreach (var g in sp.GroupBy(r => r[0]))\n      { string gn = ')
rep('foreach (var r in g) { double n0 = Num(r[4]), m0 = Num(r[5]); rows.Add(',
    'foreach (var r in g) { double n0 = Num(r[4]), m0 = Num(r[5]); if (r[1] == "Пп-1" && m51 > 0) m0 = m51; rows.Add(')
rep('rows.Add(new[] { r[1] == "-" ? "" : r[1], r[2], r[3], r[4], Dt(r[5]), n0 > 0 && m0 > 0 ? F2(n0 * m0) : "" }); } }',
    'rows.Add(new[] { r[1] == "-" ? "" : r[1], r[2], r[3], r[4], r[1] == "Пп-1" && m51 > 0 ? F2(m51) : Dt(r[5]), n0 > 0 && m0 > 0 ? F2(n0 * m0) : "" }); } }')
rep('      var data = vr.Select(r => new[] { r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11] }.Select(q => q == "-" ? "---" : Dt(q)).ToArray()).ToList();',
    '      var data = vr.Select(r => new[] { r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11] }.Select(q => q == "-" ? "---" : Dt(q)).ToArray()).ToList();\n'
    '      foreach (var row in data) { double mm0 = row[0] == "Пп-1" ? m51 : row[0] == "Пандусы" ? m62 : 0; if (mm0 > 0) { row[4] = F2(mm0); row[9] = F2(mm0); row[10] = F2(mm0); } }\n'
    '      { var tr = data.FirstOrDefault(r => r[0] == "Всего"); if (tr != null) for (int c = 1; c < tr.Length; c++) { double sum = data.Where(r => r[0] != "Всего").Sum(r => r[c] == "---" ? 0 : Num(r[c].Replace(".", ","))); tr[c] = sum > 0.004 ? F2(sum) : "---"; } }')
io.open(p, "w", encoding="utf-8").write(s)
print("ok")
