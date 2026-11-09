P = r'D:\Бекасыл КЖ КМ\Завод_В109_КМ\_авто\revit\b109_11_tube_nodes.cs'
s = open(P, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:60], s.count(a)); s = s.replace(a, b)
rep('|| Cm(f) == "ВС1" || Cm(f) == "ВФ1")).ToList();', '|| Cm(f) == "ВС1" || Cm(f) == "ВФ1" || Cm(f) == "Р2")).ToList();')
rep("public bool TopLap; public string GK; public bool Colt, Gcol; }", "public bool TopLap; public string GK; public bool Colt, Gcol, P2; public int Dia = 16; }")
rep("""        var XC = new List<double[]>(); var TB = new List<double[]>();""", """        var XC = new List<double[]>(); var TB = new List<double[]>(); var P2L = new List<double[]>();""")
rep("""if (pp[0] == "X") XC.Add(v); else TB.Add(v); }""", """if (pp[0] == "X") XC.Add(v); else if (pp[0] == "P") P2L.Add(v); else TB.Add(v); }""")
rep("""                if (mk == "Р1")
                {""", """                if (mk == "Р2")
                {   // user's узел 12: Р2 under the bottom chord — plate −8 welded to the chord bottom, tab −8 on the Р2 top + rib, 2 bolts М16 beside the chord
                    e.N = Z; e.TopLap = true; e.P2 = true; double sx = Math.Sign(pe.X - xa);
                    e.Mn = sx * X; e.Q = new XYZ(xa - sx * 60, pe.Y, pe.Z); e.Key = "p2 " + xa + " " + Math.Round(pe.Y); e.GK = e.Key;
                }
                else if (mk == "Р1")
                {""")
rep("""double Lv = Math.Abs(pe.Z - 5020) < Math.Abs(pe.Z - 10340) ? 5020 : 10340; e.Key = "col " + xa + " " + pe.Y + " " + sx + " " + Lv; e.GK = e.Key;   // узел 7: one gusset with the СВ1""",
    """double Lv = Math.Abs(pe.Z - 5020) < Math.Abs(pe.Z - 10340) ? 5020 : 10340; e.Key = "col " + xa + " " + pe.Y + " " + sx + " " + Lv; e.GK = e.Key;   // узел 7: one gusset with the СВ1
                    if (Lv > 10000) e.Dia = 24;                                                       // узел 14: Р1 +10.340 bolts М24""")
rep("""                        if (mk != "СВ1")
                        {   // узел 1, разрез 2-2""", """                        if (mk != "СВ1" && pe.Z > 12000)
                        {   // узел 1, разрез 2-2""")
rep("""else { e.Mn = Z; e.Q = new XYZ(pe.X, pe.Y, ZTop(pe.Y) - 2146.5); e.Key = "vsb " + """,
    """else { var pl = P2L.OrderBy(c => Math.Abs(c[0] - pe.Y)).First(); e.Mn = Z; e.Q = new XYZ(pe.X, pe.Y, pl[1]); e.Key = "vsb " + """)
# P2: tab only to under the chord edge, bolts outside the chord
rep("""                } if (outL < 40) { short_++; outL = Math.Max(outL, 5); }""", """                    if (e.P2) outL = Math.Min(outL, Math.Abs(e.Pe.X - Math.Round(e.Pe.X / 6000) * 6000) - 60 + 40);   // узел 12: to 40 under the chord
                } if (outL < 40) { short_++; outL = Math.Max(outL, 5); }""")
rep("""                    double aB = Math.Min(Math.Max(a0 + 32, 0.65 * outL), outL - 35);""",
    """                    double aB = Math.Min(Math.Max(a0 + 32, 0.65 * outL), outL - 35);
                    if (e.P2) aB = Math.Min(aB, Math.Abs(e.Pe.X - Math.Round(e.Pe.X / 6000) * 6000) - 60 - 22);      // узел 12: bolts outside the chord""")
rep("""bl.AddRange(Bolt(c, e.N, 16, 18, BoltLen(16, 18), soB)); bolts++; }""", """bl.AddRange(Bolt(c, e.N, e.Dia, 16, BoltLen(e.Dia, 16), soB)); bolts++; }""")
rep("""            double gT = L.Any(x => x.Colt || x.Gcol) ? 8 : 10;""", """            double gT = L.Any(x => x.Colt || x.Gcol || x.Apex || x.P2) ? 8 : 10;     // + узел 11 (under the purlin middle) and узел 12 (Р2) −t8""")
rep("""            if (land.Count >= 2)
            {   // gusset ↔ support: both sides, along the landing line""", """            if (L.Any(x => x.P2) && hull.Length >= 6)
            {   // узел 12: plate under the chord — fillets along the chord bottom edges (x = axis ± 60), over the plate's y span
                double cxa = Math.Round(L[0].Pe.X / 6000) * 6000, ylo = 1e9, yhi = -1e9; for (int i = 0; i < hull.Length; i += 2) { var w = o3 + E1 * hull[i] + E2 * hull[i + 1]; ylo = Math.Min(ylo, w.Y); yhi = Math.Max(yhi, w.Y); }
                double zt = (o3 + n * (gOff + gT)).Z;
                foreach (var sx in new[] { -1.0, 1.0 }) welds.Add(Weld(P(cxa + sx * 60, ylo + 3, zt), sx * X, Z, Y, 5, yhi - ylo - 6, soW));
            }
            else if (land.Count >= 2)
            {   // gusset ↔ support: both sides, along the landing line""")
open(P, 'w', encoding='utf-8').write(s); print('ok')
