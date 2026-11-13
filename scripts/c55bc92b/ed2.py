import io
p=r"D:/Бекасыл КЖ КМ/РМЦ_КМ/_авто/rmc_10_baza_B1.cs"
s=io.open(p,encoding='utf-8').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a[:60],s.count(a)); s=s.replace(a,b)
rep('''        string loc0 = Axis(nx, rw.r);
''','''        string loc0 = Axis(nx, rw.r); int axNo = Array.IndexOf(axX, nx) + 1;
        if (rw.r != "D" && (axNo == 4 || axNo == 5 || axNo == 7 || axNo == 8)) { b2locs.Add(loc0); continue; }   // A/G қатарында осьтер 4,5,7,8 = связь аралығы, база Б2 (паспорты жоқ) — САЛЫНБАЙДЫ
''')
rep('var tasks = new List<Tuple','var b2locs = new HashSet<string>(); var tasks = new List<Tuple')
rep('''    var targetLocs = new HashSet<string>(tasks.Select(q => Axis(q.Item1, q.Item2)));''','''    var targetLocs = new HashSet<string>(tasks.Select(q => Axis(q.Item1, q.Item2))); sb.AppendLine("Б2 орындары (салынбайды, бұрын қате салынса өшіріледі): " + string.Join(",", b2locs)); foreach (var q in b2locs) targetLocs.Add(q);''')
io.open(p,'w',encoding='utf-8',newline='').write(s)
