D = 'D:\\Бекасыл КЖ КМ\\Завод_В109_КМ\\_авто\\revit\\'
s = ''
def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:60], s.count(a)); s = s.replace(a, b)
p = D + 'b109_11_tube_nodes.cs'; s = open(p, encoding='utf-8').read()
# узел 12: the plate under the chord spans both Р2 laps (no clip at the far chord face)
rep("""            foreach (var e in L.Where(x => !x.Apex)) hull = Clip(hull, E1.DotProduct(e.Mn), E2.DotProduct(e.Mn), (e.Q - o3).DotProduct(e.Mn) + 0.3, false);""",
    """            foreach (var e in L.Where(x => !x.Apex && !x.P2)) hull = Clip(hull, E1.DotProduct(e.Mn), E2.DotProduct(e.Mn), (e.Q - o3).DotProduct(e.Mn) + 0.3, false);""")
rep("""            var ct = L.FirstOrDefault(x => x.Colt);""", """            if (L.Any(x => x.P2))
            {   // узел 12: the plate covers the chord bottom between the Р2 laps
                var e2 = L.First(x => x.P2); double cxa = Math.Round(e2.Pe.X / 6000) * 6000; double hy = e2.B / 2 + 30;
                foreach (var xx in new[] { cxa - 60, cxa + 60 }) foreach (var yy in new[] { e2.Pe.Y - hy, e2.Pe.Y + hy }) hp.Add(To2(new XYZ(xx, yy, e2.Pe.Z)));
            }
            var ct = L.FirstOrDefault(x => x.Colt);""")
# М24 (узел 14): insert 20 wider each side (edge ≥ 1.5d), gusset lap wider too
rep("double hw = e.Dia == 24 ? b / 2 + 10 : b / 2;                 // М24 (узел 14): insert 10 wider each side",
    "double hw = e.Dia == 24 ? b / 2 + 20 : b / 2;                 // М24 (узел 14): insert 20 wider each side (edge ≥ 1.5d)")
rep("double gw = e.Shop ? b / 2 : b / 2 + 30;", "double gw = e.Shop ? b / 2 : b / 2 + (e.Dia == 24 ? 45 : 30);")
rep("double wB = Math.Max(e.Dia == 24 ? 30 : 25, b / 2 - 30);", "double wB = Math.Max(e.Dia == 24 ? 32 : 25, b / 2 - 30);")
rep("""                            for (double aa = aB; aa >= a0 + 25 - 1e-6; aa -= 5) if (Ed(aa, -ww) >= 25 && Ed(aa, ww) >= 25)""",
    """                            double emin = e.Dia == 24 ? 36 : 25;
                            for (double aa = aB; aa >= a0 + 25 - 1e-6; aa -= 5) if (Ed(aa, -ww) >= emin && Ed(aa, ww) >= emin)""")
# узел 13: ВС1 gussets −t8
rep("""            double gT = L.Any(x => x.Colt || x.Gcol || x.Apex || x.P2) ? 8 : 10;""",
    """            double gT = L.Any(x => x.Colt || x.Gcol || x.Apex || x.P2 || x.Mk == "ВС1") ? 8 : 10;     // + узел 13 (ВФ1 = ВС1) −t8""")
open(p, 'w', encoding='utf-8').write(s)
p = D + 'nodes.py'; s = open(p, encoding='utf-8').read()
# узел 9: tie bolts М24
rep("""            bolt(g, [x - ta * 7, yc + sy * 104, zz], [ta, 0, 0], 16, 14 + 9)
            if 0 < i < 27: bolt(g, [x - 28, yb - sy * 55, zz], [1, 0, 0], 16, 20 + 14 + 20 + 2)
            else: bolt(g, [x - ta * 7, yb - sy * 55, zz], [ta, 0, 0], 16, 14 + 1 + 20)""",
"""            bolt(g, [x - ta * 7, yc + sy * 104, zz], [ta, 0, 0], 24, 14 + 9)                 # узел 9: болты М24
            if 0 < i < 27: bolt(g, [x - 28, yb - sy * 55, zz], [1, 0, 0], 24, 20 + 14 + 20 + 2)
            else: bolt(g, [x - ta * 7, yb - sy * 55, zz], [ta, 0, 0], 24, 14 + 1 + 20)""")
# узел 9: triangular rib −t10 under the console at the column face (190 × 240), in the console web plane
rep("""        for z in (zt, zbm): weld(g, [x - 150, yf, z], [0, sy, 0], [0, 0, 1 if z == zt else -1], [1, 0, 0], 8, 300)""",
    """        for z in (zt, zbm): weld(g, [x - 150, yf, z], [0, sy, 0], [0, 0, 1 if z == zt else -1], [1, 0, 0], 8, 300)
        ply(g, [x, y + sy * hf, zbm], [0, sy, 0], [0, 0, -1], [(0, 0), (190, 0), (20, 240), (0, 240)], 10, True)      # узел 9: −t10 C245 under the КН""")
open(p, 'w', encoding='utf-8').write(s); print('ok')
