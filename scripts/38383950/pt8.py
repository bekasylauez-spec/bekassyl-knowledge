D = 'D:\\Бекасыл КЖ КМ\\Завод_В109_КМ\\_авто\\revit\\'
s = ''
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:60], s.count(a)); s = s.replace(a, b)
p = D + 'b109_11_tube_nodes.cs'; s = open(p, encoding='utf-8').read()
rep("public bool TopLap; public string GK; public bool Colt; }", "public bool TopLap; public string GK; public bool Colt, Gcol; }")
rep('double sy = Math.Sign(pe.Y - row); e.Key = "gcol "', 'double sy = Math.Sign(pe.Y - row); e.Gcol = true; e.Key = "gcol "')
rep("""            double gOff = L[0].TopLap ? L[0].B / 2 + 8 : 4;                 // gusset lower face over the axis plane""",
    """            double gOff = L[0].TopLap ? L[0].B / 2 + 8 : 4;                 // gusset lower face over the axis plane
            double gT = L.Any(x => x.Colt || x.Gcol) ? 8 : 10;               // user's узлы 1 / 4 / 8 (разрезы 2-2): gussets at the column −t8; узлы 6 / 7 / 8*: −t10""")
rep("plates.Add(Plate(o3 * MM + n * gOff * MM, E1, E2, hull, 10, false, soP));", "plates.Add(Plate(o3 * MM + n * gOff * MM, E1, E2, hull, gT, false, soP));")
rep("welds.Add(Weld(b0 + n * 10 * MM, e0.Mn, n, dir, 6, len, soW));", "welds.Add(Weld(b0 + n * gT * MM, e0.Mn, n, dir, 6, len, soW));")
rep("var gt = o3 + n * (gOff + 10);", "var gt = o3 + n * (gOff + gT);")
rep('"Узел " + nm + ": фасонка −10, вкладыши −8"', '"Узел " + nm + ": фасонка −" + gT + ", вкладыши −8"')
open(p, 'w', encoding='utf-8').write(s)
p = D + 'gen.py'; s = open(p, encoding='utf-8').read()
rep("zmax = coltop(ic, r) - 8; zmin = ts_top(ic, r)", "zmax = coltop(ic, r); zmin = ts_top(ic, r)      # узел 1 разрез 2-2: gusset −8 welded to the cap underside")
open(p, 'w', encoding='utf-8').write(s)
p = D + 'nodes.py'; s = open(p, encoding='utf-8').read()
rep("""        if b:                                                # СВ2 / СВ3 top (узел 1, разрез 2-2): rib −8 under the cap, both sides of the web
            colstiff(g + ' связь', x, y, top - 4, pr, (-1, 1), 8, False)""",
    """        # СВ2 / СВ3 top (узел 1, разрез 2-2): the gusset −8 is welded straight to the cap −14 — no rib under the cap""")
rep("    if stiff: colstiff(g, x, y, zl - 100 - 7, pr, (-1, 1), 14)", "    if stiff: colstiff(g, x, y, zl - 100 - 4, pr, (-1, 1), 8)              # узел 1 разрез 2-2: −t8 under the table")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
