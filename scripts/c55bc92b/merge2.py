sp = r'C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad'
p = r'D:\Бекасыл КЖ КМ\РМЦ_КМ\_авто\rmc_brace_lib.cs'
s = open(p, encoding='utf-8').read()
add = open(sp + r'\xadd2.txt', encoding='utf-8').read()
marker = '    // ---------------- 2D көпбұрышта нүкте'
if 'HorizF' not in s:
    s = s.replace(marker, add + marker, 1)
if 'class BKnot' not in s:
    s = s.replace('class BSx {', 'class BKnot { public int Ax, Sg; public double Xf, Yw, Z, EndX; public string Row; public bool HasGs; }\nclass BSx {', 1)
# болт ұзындығы жоқ (Lbolt <= 0) — болттар салынбайды (TODO_SURAQ), тесіктер қалады
old = '        foreach (double pb in new[] { -sp.Ebolt, sp.Ebolt }) { BoltM(r.Bolts, X(sB, pb, -sp.Ti / 2), n, sp.Ti + sp.Tg, sp.Lbolt, bd, soB, log); r.BoltC.Add(X(sB, pb, 0)); }'
new = ('        foreach (double pb in new[] { -sp.Ebolt, sp.Ebolt }) { if (sp.Lbolt > 0) BoltM(r.Bolts, X(sB, pb, -sp.Ti / 2), n, sp.Ti + sp.Tg, sp.Lbolt, bd, soB, log); r.BoltC.Add(X(sB, pb, 0)); }\n'
       '        if (sp.Lbolt <= 0) log.AppendLine("  TODO_SURAQ «" + sp.Tag + "»: болт ұзындығы паспортта жоқ — болттар салынбады (тесіктер Ø" + F(bd.hole) + " бар)");')
assert old in s
s = s.replace(old, new, 1)
# PutEnd: болт DS-тері тек болт бар болса (Part тек G қосылғанда пайда болады — бос Part Emit-те өткізіледі)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
