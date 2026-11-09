P = r'D:\Бекасыл КЖ КМ\Завод_В109_КМ\_авто\revit\b109_11_tube_nodes.cs'
s = open(P, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:60], s.count(a)); s = s.replace(a, b)
# remember the clipped insert outline; ВС1 / band-clipped ends keep the insert inside the tube width minus walls
rep("""                    var ins = e.TopLap ? new double[] { 8, -b / 2, outL, -b / 2, outL, b / 2, 8, b / 2 } : new double[] { 8, -b / 2, outL, -b / 2,""",
    """                    double hw = (double.IsNaN(e.Zmax) && double.IsNaN(e.Zmin)) || e.Colt ? b / 2 : bi / 2;   // ВС1 top (band under the chord flange): narrower
                    var ins = e.TopLap ? new double[] { 8, -b / 2, outL, -b / 2, outL, b / 2, 8, b / 2 } : new double[] { 8, -hw, outL, -hw,""")
i = s.index("var ins = e.TopLap ? new double[] { 8, -b / 2, outL, -b / 2, outL, b / 2, 8, b / 2 } : new double[] { 8, -hw, outL, -hw,")
j = s.index("\n", i)
line = s[i:j]
line2 = line.replace("outL, b / 2, 8, b / 2 };", "XX").replace("outL, bi / 2, 8, bi / 2 };", "outL, hw, 8, hw };").replace("XX", "outL, b / 2, 8, b / 2 };")
s = s[:i] + line2 + s[j:]
rep("""                    if (iv.Count >= 3) { try { plates.Add(Plate(bs * MM, e.U, e.W, iv.SelectMany(q => q).ToArray(), 8, false, soP)); } catch { } }""",
    """                    if (iv.Count >= 3) { try { plates.Add(Plate(bs * MM, e.U, e.W, iv.SelectMany(q => q).ToArray(), 8, false, soP)); } catch { } }
                    insPoly = iv;""")
rep("""            foreach (var e in L)
            {
                double b = e.B, bi = b - 2 * e.Tw - 2;""", """            foreach (var e in L)
            {
                double b = e.B, bi = b - 2 * e.Tw - 2; List<double[]> insPoly = null;""")
rep("""                    var bp = new[] { new[] { aB, -wB }, new[] { aB, wB } };""",
"""                    if (insPoly != null && insPoly.Count >= 3)
                    {   // bolts ≥ 25 (1.5d) inside the clipped insert outline: slide towards the tube, then closer to the rib
                        Func<double, double, double> Ed = (u, w) => { double dm = 1e9; for (int k = 0; k < insPoly.Count; k++) { var p1 = insPoly[k]; var p2 = insPoly[(k + 1) % insPoly.Count];
                            double ex = p2[0] - p1[0], ey = p2[1] - p1[1], l2 = ex * ex + ey * ey; double t = l2 < 1e-9 ? 0 : Math.Max(0, Math.Min(1, ((u - p1[0]) * ex + (w - p1[1]) * ey) / l2));
                            dm = Math.Min(dm, Math.Sqrt(Math.Pow(u - p1[0] - t * ex, 2) + Math.Pow(w - p1[1] - t * ey, 2))); } return dm; };
                        bool ok = false;
                        foreach (var ww in new[] { wB, Math.Max(21, wB - 10), 21.0 })
                        {
                            for (double aa = aB; aa >= a0 + 25 - 1e-6; aa -= 5) if (Ed(aa, -ww) >= 25 && Ed(aa, ww) >= 25) { aB = aa; wB = ww; ok = true; break; }
                            if (ok) break;
                        }
                        if (!ok) { shortB++; if (shortB <= 6) sb.AppendLine("bolt edge < 25 " + e.Key + " outL " + Math.Round(outL)); }
                    }
                    var bp = new[] { new[] { aB, -wB }, new[] { aB, wB } };""")
open(P, 'w', encoding='utf-8').write(s); print('ok')
