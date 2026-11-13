p = 'D:/Бекасыл КЖ КМ/Завод_В113_КМ/_авто/v113_sec_lib.cs'
s = open(p, encoding='utf-8').read()
o = 'var gxs = grids.Select(g => { try { return L(g.Curve.GetEndPoint(0)).X; } catch { return double.NaN; } })'
n = 'var gxs = grids.Select(g => { try { double xa = L(g.Curve.GetEndPoint(0)).X, xb = L(g.Curve.GetEndPoint(1)).X; return Math.Abs(xa - xb) < 1 ? xa : double.NaN; } catch { return double.NaN; } })   /* only the grids seen end-on (parallel ones gave a wrong gA) */'
assert o in s; s = s.replace(o, n, 1); open(p, 'w', encoding='utf-8').write(s); print('ok')
