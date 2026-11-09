P = r'D:\Бекасыл КЖ КМ\Завод_В109_КМ\_авто\revit\b109_11_tube_nodes.cs'
s = open(P, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:60], s.count(a)); s = s.replace(a, b)
# insert full tube width (it is outside the tube now)
rep("""new double[] { 8, -bi / 2, outL, -bi / 2, outL, bi / 2, 8, bi / 2 };""", """new double[] { 8, -b / 2, outL, -b / 2, outL, b / 2, 8, b / 2 };""")
rep("""                if (e.TopLap)
                {   // tab ↔ end plate (both faces) + rib −8 under the tab (узел 6, разрез 2-2), clear of the bolt nuts
                    foreach (var w0 in new[] { -b / 2, 4.0 })                            // two runs either side of the rib
                        welds.Add(Weld((e.Pe + e.U * 8 + e.N * (b / 2) + e.W * w0) * MM, e.U, -e.N, e.W, 5, b / 2 - 4, soW));
                    plates.Add(Plate((e.Pe + e.U * 8 + e.W * 4) * MM, e.U, e.N, new double[] { 0, b / 2, 14, b / 2, 0, b / 2 - 40 }, 8, false, soP));
                }
                else
                    foreach (var sn in new[] { 1.0, -1.0 })                               // insert ↔ end plate, both faces
                        welds.Add(Weld((e.Pe + e.U * 8 + e.N * sn * 4 - e.W * (bi / 2)) * MM, e.U, e.N * sn, e.W, 5, bi, soW));""",
"""                // user's узлы 1 (2-2), 6, 7: the insert is a T — flat plate −8 lapped on the gusset + rib −8 along the axis on its free side,
                // welded to the end plate and the flat plate; the 2 bolts go either side of the rib (across the axis)
                {
                    double nf = e.TopLap ? b / 2 : -4, sgn = e.TopLap ? 1 : -1;               // flat plate face away from the gusset, rib towards −N (under it)
                    double aE = Math.Max(30, outL - 5);
                    plates.Add(Plate((e.Pe + e.N * nf + e.W * 4) * MM, e.U, e.N, new double[] { 8, 0, aE, 0, aE, -sgn * 0 - 18, 8, -40 }, 8, false, soP));
                    foreach (var w0 in new[] { -b / 2, 4.0 })                                // flat plate ↔ end plate, either side of the rib
                        welds.Add(Weld((e.Pe + e.U * 8 + e.N * nf + e.W * w0) * MM, e.U, -e.N, e.W, 5, b / 2 - 4, soW));
                    foreach (var sw in new[] { -1.0, 1.0 })                                  // rib ↔ flat plate
                        welds.Add(Weld((e.Pe + e.U * 8 + e.N * nf + e.W * sw * 4) * MM, e.W * sw, -e.N, e.U, 4, aE - 8, soW));
                }""")
rep("""                    double a1 = Math.Max(40, a0 + 30), a2 = a1 + 60;                                            // along the axis: pitch 60 (≥2.5d), edges ≥30
                    if (a2 > outL - 30) { a2 = outL - 30; a1 = a2 - 60; }
                    var bp = a1 >= a0 + 25 && a1 >= 35 ? new[] { new[] { a1, 0 }, new[] { a2, 0 } }
                                                       : new[] { new[] { (a0 + outL) / 2, -(bi / 2 - 25) }, new[] { (a0 + outL) / 2, bi / 2 - 25 } };   // across: edge 25 (≥1.5d), pitch ≥ 40
                    if (bp[0][1] != 0) { shortB++; if (shortB <= 6) sb.AppendLine("across " + e.Key + " a0 " + Math.Round(a0) + " outL " + Math.Round(outL) + " dist " + Math.Round(dist)); }""",
"""                    double aB = Math.Max(a0 + 32, outL - 35); if (aB > outL - 25) { aB = Math.Max(a0 + 25, outL - 25); shortB++; }   // edge 2d along where it fits
                    double wB = Math.Max(25, b / 2 - 30);                                                         // either side of the rib, edge ≥ 25 (1.5d)
                    var bp = new[] { new[] { aB, -wB }, new[] { aB, wB } };""")
open(P, 'w', encoding='utf-8').write(s); print('ok')
