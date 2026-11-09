P = r'D:\Бекасыл КЖ КМ\Завод_В109_КМ\_авто\revit\b109_11_tube_nodes.cs'
s = open(P, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:70], s.count(a)); s = s.replace(a, b)
rep("public double Ylo = double.NaN, Yhi = double.NaN; }", "public double Ylo = double.NaN, Yhi = double.NaN; public bool TopLap; public string GK; }")
rep("        var ends = new List<End>();\n",
"""        var ends = new List<End>();
        // gen.py braces.tsv: X = СВ1 crossing (O, through-diagonal unit u, b), T = СВ2 / СВ3 top band at a column (x, y, zmin, zmax, sx)
        var XC = new List<double[]>(); var TB = new List<double[]>();
        foreach (var ln in System.IO.File.ReadAllLines(@"D:\\Бекасыл КЖ КМ\\Завод_В109_КМ\\_авто\\revit\\braces.tsv"))
        { var pp = ln.Split('\\t'); if (pp.Length < 2) continue; var v = pp.Skip(1).Select(q => double.Parse(q, System.Globalization.CultureInfo.InvariantCulture)).ToArray(); if (pp[0] == "X") XC.Add(v); else TB.Add(v); }
""".replace('@"D:\\\\', '@"D:\\').replace('\\\\Завод', '\\Завод').replace('\\\\_авто', '\\_авто').replace('\\\\revit\\\\', '\\revit\\'))
rep("""e.Mn = sx * X; e.Q = new XYZ(xa + sx * (k2 ? 9 : 8), pe.Y, pe.Z); e.Key = "r1 " + xa + " " + pe.Y + " " + sx + " " + Math.Round(pe.Z);
                    e.Zmin = pe.Z - 52; e.Zmax = pe.Z + 52;""",
"""e.Mn = sx * X; e.Q = new XYZ(xa + sx * (k2 ? 9 : 8), pe.Y, pe.Z);
                    double Lv = Math.Abs(pe.Z - 5020) < Math.Abs(pe.Z - 10340) ? 5020 : 10340; e.Key = "col " + xa + " " + pe.Y + " " + sx + " " + Lv; e.GK = e.Key;   // узел 7: one gusset with the СВ1""")
a = s.index('                else if (mk.StartsWith("СВ"))')
b = s.index('                else if (mk == "ГС1")')
s = s[:a] + """                else if (mk.StartsWith("СВ"))
                {
                    e.N = Y;
                    var xc = XC.FirstOrDefault(c => Math.Abs(c[1] - pe.Y) < 1 && Math.Sqrt((c[0] - pe.X) * (c[0] - pe.X) + (c[2] - pe.Z) * (c[2] - pe.Z)) < 700);
                    if (xc != null)
                    {   // узел 8*: half of the split diagonal — gusset −10 butt on the face of the through diagonal
                        var O = new XYZ(xc[0], xc[1], xc[2]); var u1 = new XYZ(xc[3], xc[4], xc[5]); var n1 = new XYZ(-u1.Z, 0, u1.X);
                        double s = Math.Sign((pe - O).DotProduct(n1)); e.Mn = n1 * s; e.Q = O + e.Mn * (xc[6] / 2); e.Key = "xc " + Math.Round(O.X) + " " + O.Y + " " + Math.Round(O.Z) + " " + s;
                    }
                    else if (Math.Abs(pe.X - xa) < 700)
                    {
                        double sx = Math.Sign(pe.X - xa); bool k2 = pe.Y > 59000 && xa >= 72000 - 1 && xa <= 90001; e.Mn = sx * X; e.Q = new XYZ(xa + sx * (k2 ? 9 : 8), pe.Y, pe.Z);
                        if (mk != "СВ1")
                        {   // узел 1, разрез 2-2: top brace on the column web between the rib −8 under the cap and the stiffener under the ФФ1 table
                            var tb = TB.First(c => Math.Abs(c[0] - xa) < 1 && Math.Abs(c[1] - pe.Y) < 1); e.Zmin = tb[2]; e.Zmax = tb[3]; e.Key = "colt " + xa + " " + pe.Y + " " + sx;
                        }
                        else if (pe.Z < 1500) { e.Base = true; e.Key = "col " + xa + " " + pe.Y + " " + sx + " base"; }
                        else { double Lv = Math.Abs(pe.Z - 5020) < Math.Abs(pe.Z - 10340) ? 5020 : 10340; e.Key = "col " + xa + " " + pe.Y + " " + sx + " " + Lv; e.GK = e.Key; }
                    }
                    else { double L = Math.Abs(pe.Z - 5020) < Math.Abs(pe.Z - 10340) ? 5020 : 10340; double sz = Math.Sign(pe.Z - L); e.Mn = sz * Z; e.Q = new XYZ(pe.X, pe.Y, L + sz * 50); e.Key = "p1 " + Math.Round(pe.X / 600) + " " + pe.Y + " " + L + " " + sz; }
                }
""" + s[b:]
rep("""                else if (mk == "ГС1")
                {
                    e.N = Z;""", """                else if (mk == "ГС1")
                {
                    e.TopLap = true;
                    e.N = pe.X < -100 ? new XYZ(-150.0 / 7100.0, 0, 1).Normalize() : new XYZ(0, -(pe.Y < 30000 ? S : -S), 1).Normalize();""")
rep("""if (Math.Abs(pe.Y - yr) < 700) { double sy = Math.Sign(pe.Y - yr); e.Mn = sy * Y; e.Q = new XYZ(pe.X, yr + sy * 2.9, pe.Z);""",
    """if (Math.Abs(pe.Y - yr) < 700) { double sy = Math.Sign(pe.Y - yr); e.Mn = sy * Y; e.Q = new XYZ(pe.X, yr + sy * 70, pe.Z);""")
a = s.index("                        if (onRow)\n")
b = s.index("                    else { e.Apex = true; e.Ypurlin = ya;")
s = s[:a] + """                        double bfh = (pe.Y > 24000 && pe.Y < 36000) ? 82.5 : (Math.Abs(xa) < 1 || Math.Abs(xa - 162000) < 1) ? 70 : 75;   // 40Б1 / 30Б1 / 20Ш1 flange tip
                        e.Mn = sx * X; e.Q = new XYZ(xa + sx * bfh, pe.Y, pe.Z);
                        if (onRow)
                        {   // over a column: the gusset stays off the column, its cap and the member end plate (y beyond the face + 21)
                            double sy = Math.Sign(pe.Y - row); e.Key = "gcol " + xa + " " + row + " " + sy + " " + sx;
                            if (sy > 0) { e.Ylo = row + 316; e.Yhi = 1e9; } else { e.Ylo = -1e9; e.Yhi = row - 316; }
                        }
                        else e.Key = "gch " + xa + " " + ya + " " + sx;
                    }
""" + s[b:]
rep("""        for (int i = 0; i < ends.Count; i++) ends[i].Key = "g" + Fd(i);""",
"""        { var gkFirst = new Dictionary<string, int>(); for (int i = 0; i < ends.Count; i++) { var gk = ends[i].GK; if (gk == null) continue; int j; if (gkFirst.TryGetValue(gk, out j)) par[Fd(i)] = Fd(j); else gkFirst[gk] = i; } }
        for (int i = 0; i < ends.Count; i++) ends[i].Key = "g" + Fd(i);""")
rep("""                caps.Add(Plate((e.Pe + e.N * 4) * MM, e.W, e.N, Rect(-b / 2, 0, b / 2, b / 2 - 4), 4, false, soP));
                caps.Add(Plate((e.Pe - e.N * (b / 2)) * MM, e.W, e.N, Rect(-b / 2, 0, b / 2, b / 2 - 4), 4, false, soP));""",
"""                if (e.TopLap) caps.Add(Plate((e.Pe - e.N * (b / 2)) * MM, e.W, e.N, Rect(-b / 2, 0, b / 2, b), 4, false, soP));
                else {
                caps.Add(Plate((e.Pe + e.N * 4) * MM, e.W, e.N, Rect(-b / 2, 0, b / 2, b / 2 - 4), 4, false, soP));
                caps.Add(Plate((e.Pe - e.N * (b / 2)) * MM, e.W, e.N, Rect(-b / 2, 0, b / 2, b / 2 - 4), 4, false, soP)); }""")
rep("""                    var ins = new double[] { -120, -bi / 2, outL, -bi / 2, outL, bi / 2, -120, bi / 2 }; var bs = e.Pe - e.N * 4;""",
"""                    var ins = e.TopLap ? new double[] { -80, -b / 2, outL, -b / 2, outL, b / 2, -80, b / 2 } : new double[] { -120, -bi / 2, outL, -bi / 2, outL, bi / 2, -120, bi / 2 };
                    var bs = e.TopLap ? e.Pe + e.N * (b / 2) : e.Pe - e.N * 4;          // узел 6: tab −8 on the tube top (under the gusset), else insert in the axis plane""")
rep("""                    { var c = (e.Pe + e.U * q[0] + e.W * q[1] - e.N * 4) * MM;""", """                    { var c = (e.Pe + e.U * q[0] + e.W * q[1] + e.N * (e.TopLap ? b / 2 : -4)) * MM;""")
rep("""            var eb = L.FirstOrDefault(x => x.Base); double bxa = 0, bsx = 0;""", """            double gOff = L[0].TopLap ? L[0].B / 2 + 8 : 4;                 // gusset lower face over the axis plane
            var eb = L.FirstOrDefault(x => x.Base); double bxa = 0, bsx = 0;""")
rep("""            else if (hull.Length >= 6) { try { plates.Add(Plate(o3 * MM + n * 4 * MM, E1, E2, hull, 10, false, soP)); } catch { bad++; } } else bad++;""",
"""            else if (hull.Length >= 6) { try { plates.Add(Plate(o3 * MM + n * gOff * MM, E1, E2, hull, 10, false, soP)); } catch { bad++; } } else bad++;
            var gr = L.FirstOrDefault(x => x.GK != null && x.GK.EndsWith(" 5020"));
            if (gr != null && hull.Length >= 6)
            {   // узел 7: ribs −8 over and under the column-web gusset, between the flanges on its side of the web (slot for the gusset)
                double zlo = 1e9, zhi = -1e9; for (int i = 0; i < hull.Length; i += 2) { var w = o3 + E1 * hull[i] + E2 * hull[i + 1]; zlo = Math.Min(zlo, w.Z); zhi = Math.Max(zhi, w.Z); }
                double cxa = Math.Round(gr.Pe.X / 6000) * 6000, csx = Math.Sign(gr.Pe.X - cxa); bool ck2 = gr.Pe.Y > 59000 && cxa >= 72000 - 1 && cxa <= 90001;
                double tw2 = ck2 ? 9 : 8, chf = ck2 ? 298.5 : 294.5, ctf = ck2 ? 25 : 21, yr = gr.Pe.Y;
                double rx0 = Math.Min(cxa + csx * tw2, cxa + csx * 150), rx1 = Math.Max(cxa + csx * tw2, cxa + csx * 150);
                foreach (var zz in new[] { zhi, zlo - 8 })
                    foreach (var yy in new[] { new[] { yr - chf + ctf, yr + 2 }, new[] { yr + 16, yr + chf - ctf } })
                    {
                        plates.Add(Plate(P(rx0, yy[0], zz), X, Y, Rect(0, 0, rx1 - rx0, yy[1] - yy[0]), 8, false, soP));
                        welds.Add(Weld(P(cxa + csx * tw2, yy[0], zz < zhi ? zz : zz + 8), csx * X, zz < zhi ? -Z : Z, Y, 5, yy[1] - yy[0], soW));
                    }
            }""")
rep("""                    var b0 = (l0 - n * l0.DotProduct(n) + (o3 + n * 4).DotProduct(n) * n) * MM;   // on the gusset's lower face plane (ft)""",
    """                    var b0 = (l0 - n * l0.DotProduct(n) + (o3 + n * gOff).DotProduct(n) * n) * MM;   // on the gusset's lower face plane (ft)""")
rep("""                var ea = L.First(x => x.Apex); double yp = ea.Ypurlin; double zTopG = o3.Z + 14; double zb = PurlinBottom(yp) - 2;""",
    """                var ea = L.First(x => x.Apex); double yp = ea.Ypurlin; double zTopG = o3.Z + gOff + 10; double zb = PurlinBottom(yp) - 0.3;""")
open(P, 'w', encoding='utf-8').write(s); print('ok')
