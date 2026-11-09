P = r'D:\Бекасыл КЖ КМ\Завод_В109_КМ\_авто\revit\b109_11_tube_nodes.cs'
s = open(P, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:60], s.count(a)); s = s.replace(a, b)
rep("""            var hp = new List<double[]>(); var land = new List<XYZ>(); double nBase = 0;""",
    """            var hp = new List<double[]>(); var land = new List<XYZ>(); double nBase = 0; var rng = new Dictionary<End, int[]>();""")
rep("""                double b = e.B, bi = b - 2 * e.Tw - 2; List<double[]> insPoly = null;""",
    """                double b = e.B, bi = b - 2 * e.Tw - 2; List<double[]> insPoly = null; int h0 = hp.Count;""")
rep("""                // user's узлы 1 (2-2), 6, 7: the insert is a T""", """                rng[e] = new[] { h0, hp.Count };                                  // this end's own gusset outline points
                // user's узлы 1 (2-2), 6, 7: the insert is a T""")
# clip pipeline as a function, used for the whole hull and for each end's piece
rep("""            var hull = Hull(hp);
            double zmx = L.Where(x => !double.IsNaN(x.Zmax)).Select(x => x.Zmax).DefaultIfEmpty(double.NaN).Min(), zmn = L.Where(x => !double.IsNaN(x.Zmin)).Select(x => x.Zmin).DefaultIfEmpty(double.NaN).Max();
            if (!double.IsNaN(zmx)) hull = Clip(hull, E1.Z, E2.Z, zmx - o3.Z, true);
            foreach (var e in L.Where(x => !x.Apex && !x.P2)) hull = Clip(hull, E1.DotProduct(e.Mn), E2.DotProduct(e.Mn), (e.Q - o3).DotProduct(e.Mn) + 0.3, false);
            if (L.Any(x => x.Colt)) foreach (var e in L) hull = Clip(hull, E1.DotProduct(e.U), E2.DotProduct(e.U), (e.Pe - o3).DotProduct(e.U) + 14, false);   // only where the forced band rectangle could cover an end plate   // gusset clear of every end plate (−8, b + 20) and its insert fillet (leg 5)
            var lo = L.Where(x => !double.IsNaN(x.Ylo)).Select(x => x.Ylo).DefaultIfEmpty(double.NaN).Max(); var hi = L.Where(x => !double.IsNaN(x.Yhi)).Select(x => x.Yhi).DefaultIfEmpty(double.NaN).Min();
            if (!double.IsNaN(lo)) { hull = Clip(hull, E1.Y, E2.Y, lo + 5 - o3.Y, false); hull = Clip(hull, E1.Y, E2.Y, hi - 5 - o3.Y, true); }
            if (!double.IsNaN(zmn)) hull = Clip(hull, E1.Z, E2.Z, zmn - o3.Z, false);
            {   // drop near-duplicate vertices left by the clips
                var hv = new List<double[]>(); for (int i = 0; i < hull.Length; i += 2) { var q = new[] { hull[i], hull[i + 1] }; if (hv.Count == 0 || Math.Abs(hv[hv.Count - 1][0] - q[0]) + Math.Abs(hv[hv.Count - 1][1] - q[1]) > 1) hv.Add(q); }
                if (hv.Count > 1 && Math.Abs(hv[0][0] - hv[hv.Count - 1][0]) + Math.Abs(hv[0][1] - hv[hv.Count - 1][1]) <= 1) hv.RemoveAt(hv.Count - 1);
                hull = hv.SelectMany(q => q).ToArray();
            }
            if (L.Any(x => x.AnxCol)) hull = Clip(hull, E1.X, E2.X, -200 - o3.X, true);     // пристройка: gusset stops 5 off the СФ flange (x −195)""",
"""            double zmx = L.Where(x => !double.IsNaN(x.Zmax)).Select(x => x.Zmax).DefaultIfEmpty(double.NaN).Min(), zmn = L.Where(x => !double.IsNaN(x.Zmin)).Select(x => x.Zmin).DefaultIfEmpty(double.NaN).Max();
            var lo = L.Where(x => !double.IsNaN(x.Ylo)).Select(x => x.Ylo).DefaultIfEmpty(double.NaN).Max(); var hi = L.Where(x => !double.IsNaN(x.Yhi)).Select(x => x.Yhi).DefaultIfEmpty(double.NaN).Min();
            Func<double[], End, double[]> ClipAll = (hh, own) =>
            {
                if (!double.IsNaN(zmx)) hh = Clip(hh, E1.Z, E2.Z, zmx - o3.Z, true);
                foreach (var e in L.Where(x => !x.Apex && !x.P2)) hh = Clip(hh, E1.DotProduct(e.Mn), E2.DotProduct(e.Mn), (e.Q - o3).DotProduct(e.Mn) + 0.3, false);
                foreach (var e in L.Where(x => own == x || (own == null && L.Any(c => c.Colt))))   // gusset clear of the end plate (−8, b + 20) and its insert fillet
                    hh = Clip(hh, E1.DotProduct(e.U), E2.DotProduct(e.U), (e.Pe - o3).DotProduct(e.U) + 14, false);
                if (!double.IsNaN(lo)) { hh = Clip(hh, E1.Y, E2.Y, lo + 5 - o3.Y, false); hh = Clip(hh, E1.Y, E2.Y, hi - 5 - o3.Y, true); }
                if (!double.IsNaN(zmn)) hh = Clip(hh, E1.Z, E2.Z, zmn - o3.Z, false);
                var hv = new List<double[]>(); for (int i = 0; i < hh.Length; i += 2) { var q = new[] { hh[i], hh[i + 1] }; if (hv.Count == 0 || Math.Abs(hv[hv.Count - 1][0] - q[0]) + Math.Abs(hv[hv.Count - 1][1] - q[1]) > 1) hv.Add(q); }
                if (hv.Count > 1 && Math.Abs(hv[0][0] - hv[hv.Count - 1][0]) + Math.Abs(hv[0][1] - hv[hv.Count - 1][1]) <= 1) hv.RemoveAt(hv.Count - 1);
                hh = hv.SelectMany(q => q).ToArray();
                if (L.Any(x => x.AnxCol)) hh = Clip(hh, E1.X, E2.X, -200 - o3.X, true);     // пристройка: gusset stops 5 off the СФ flange (x −195)
                return hh;
            };
            var hull = ClipAll(Hull(hp), null);
            // several ends: the gusset is the union of each end's own outline (lap + landing + shared points), each kept off its own end plate —
            // a convex hull of all of them would run over a neighbour tube (X top tier at +10.340 with Р1)
            List<double[]> pieces = null;
            if (L.Count > 1 && eb == null && !L.Any(x => x.Colt))
            {
                int nAll = hp.Count; var shared = new List<double[]>(); var owned = new HashSet<int>();
                foreach (var kv in rng) for (int i = kv.Value[0]; i < kv.Value[1]; i++) owned.Add(i);
                for (int i = 0; i < nAll; i++) if (!owned.Contains(i)) shared.Add(hp[i]);
                pieces = new List<double[]>();
                foreach (var e in L) { var pts = new List<double[]>(shared); for (int i = rng[e][0]; i < rng[e][1]; i++) pts.Add(hp[i]); if (pts.Count < 3) continue; var hh = ClipAll(Hull(pts), e); if (hh.Length >= 6) pieces.Add(hh); }
            }""")
rep("""            else if (hull.Length >= 6) { try { plates.Add(Plate(o3 * MM + n * gOff * MM, E1, E2, hull, gT, false, soP)); } catch { bad++; } } else bad++;""",
"""            else if (pieces != null && pieces.Count > 0)
            {
                Solid acc = null;
                foreach (var pc in pieces) { try { var sl = Plate(o3 * MM + n * gOff * MM, E1, E2, pc, gT, false, soP); acc = acc == null ? sl : BooleanOperationsUtils.ExecuteBooleanOperation(acc, sl, BooleanOperationsType.Union); } catch { bad++; } }
                if (acc != null) plates.Add(acc); else bad++;
            }
            else if (hull.Length >= 6) { try { plates.Add(Plate(o3 * MM + n * gOff * MM, E1, E2, hull, gT, false, soP)); } catch { bad++; } } else bad++;""")
open(P, 'w', encoding='utf-8').write(s); print('ok')
