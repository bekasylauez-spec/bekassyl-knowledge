P = r'D:\Бекасыл КЖ КМ\Завод_В109_КМ\_авто\revit\b109_11_tube_nodes.cs'
s = open(P, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:60], s.count(a)); s = s.replace(a, b)
rep("""                // cap halves on the tube end, outside it (s_e … s_e+4), slot ±4 for the insert
                if (e.TopLap) caps.Add(Plate((e.Pe - e.N * (b / 2)) * MM, e.W, e.N, Rect(-b / 2, 0, b / 2, b), 4, false, soP));
                else {
                caps.Add(Plate((e.Pe + e.N * 4) * MM, e.W, e.N, Rect(-b / 2, 0, b / 2, b / 2 - 4), 4, false, soP));
                caps.Add(Plate((e.Pe - e.N * (b / 2)) * MM, e.W, e.N, Rect(-b / 2, 0, b / 2, b / 2 - 4), 4, false, soP)); }
                foreach (var sw in e.TopLap ? new[] { -1.0 } : new[] { 1.0, -1.0 })
                {   // cap ↔ tube welds on the outer edges (top lap: not under the tab)
                    welds.Add(Weld((e.Pe + e.N * sw * b / 2 - e.W * b / 2) * MM, -e.U, e.N * sw, e.W, 4, b, soW));
                }""",
"""                // user's узлы 6, 7 (09.11): end plate −8 C245 on the tube end, outside it (s_e … s_e+8), 10 wider than the tube each side;
                // the insert −8 (ГС1: tab −8) is welded to its outer face — nothing goes into the tube
                double cw = b / 2 + 10;
                caps.Add(Plate((e.Pe - e.N * cw - e.W * cw) * MM, e.W, e.N, Rect(0, 0, 2 * cw, 2 * cw), 8, false, soP));
                foreach (var sw in new[] { 1.0, -1.0 })
                {   // end plate ↔ tube: fillets round the tube (four sides)
                    welds.Add(Weld((e.Pe + e.N * sw * b / 2 - e.W * b / 2) * MM, -e.U, e.N * sw, e.W, 4, b, soW));
                    welds.Add(Weld((e.Pe + e.W * sw * b / 2 - e.N * b / 2) * MM, -e.U, e.W * sw, e.N, 4, b, soW));
                }""")
rep("""                    var ins = e.TopLap ? new double[] { -80, -b / 2, outL, -b / 2, outL, b / 2, -80, b / 2 } : new double[] { -120, -bi / 2, outL, -bi / 2, outL, bi / 2, -120, bi / 2 };""",
    """                    var ins = e.TopLap ? new double[] { 8, -b / 2, outL, -b / 2, outL, b / 2, 8, b / 2 } : new double[] { 8, -bi / 2, outL, -bi / 2, outL, bi / 2, 8, bi / 2 };""")
# insert ↔ end plate welds and the small rib under the ГС1 tab
rep("""                if (!e.Shop)
                {   // 2 bolts М16 through insert + gusset, head under the insert""",
"""                if (e.TopLap)
                {   // tab ↔ end plate (both faces) + rib −8 under the tab (узел 6, разрез 2-2), clear of the bolt nuts
                    welds.Add(Weld((e.Pe + e.U * 8 + e.N * (b / 2) - e.W * (b / 2)) * MM, e.U, -e.N, e.W, 5, b, soW));
                    plates.Add(Plate((e.Pe + e.U * 8 - e.W * 4) * MM, e.U, e.N, new double[] { 0, b / 2, 14, b / 2, 0, b / 2 - 40 }, 8, false, soP));
                }
                else
                    foreach (var sn in new[] { 1.0, -1.0 })                               // insert ↔ end plate, both faces
                        welds.Add(Weld((e.Pe + e.U * 8 + e.N * sn * 4 - e.W * (bi / 2)) * MM, e.U, e.N * sn, e.W, 5, bi, soW));
                if (!e.Shop)
                {   // 2 bolts М16 through insert + gusset, head under the insert""")
rep('"ПЛ3 заглушка −4 ("', '"ПЛ3 заглушка −8 ("')
open(P, 'w', encoding='utf-8').write(s)
P = r'D:\Бекасыл КЖ КМ\Завод_В109_КМ\_авто\revit\nodes.py'
s = open(P, encoding='utf-8').read()
rep("""    plt(g, [x, y, z], eu, ev, -60, -60, 60, 60, 6)""", """    plt(g, [x, y, z], eu, ev, -70, -70, 70, 70, 8)          # узел 3: end plate −8 10 wider than the tube""")
open(P, 'w', encoding='utf-8').write(s); print('ok')
