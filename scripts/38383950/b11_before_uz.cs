// Завод В109 Цех Блок 1: tube-end nodes of СВ1–СВ3 (vertical bracing, узлы 2, 4, 5), ГС1 (horizontal bracing, узел 3) and the ФФ1 lattice.
// Run with -Lib b109_lib.cs. Every tube end: cap ПЛ3 −4 (two halves around the insert slot), insert −8 through the tube end (axis plane),
// one shared gusset −10 per node lapped on the inserts, welded to the face it lands on (column web, Р1 flange, chord web / flange, column flange,
// purlin via a stand plate). СВ / ГС1 (field): 2 bolts М16 per end through insert + gusset (note 8: holes Ø19 for М16). ФФ1 lattice (shop): insert ↔ gusset welds.
// Gusset planes: СВ — the row plane (normal Y), ГС1 — horizontal (normal Z), lattice — the truss plane (normal X). Gussets sit on the +n side of the inserts.
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"D:\Бекасыл КЖ КМ\Завод_В109_КМ\_авто\revit\_b109_11.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder();
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt")); sb.Append(Nodes(nd)); nd.Save(); sb.AppendLine("saved"); }
  catch (Exception ex) { sb.AppendLine("ERR " + ex); }
  System.IO.File.WriteAllText(log, sb.ToString()); };
uiapp.Idling += hnd;
return "queued";
}

static double S = 750.0 / 29705.5;
static double ZTop(double y) { double yy = y <= 30000 ? y : 60000 - y; return 14490 + S * (yy - 294.5); }
static double Zbc(double y) { double dd = y <= 30000 ? y : 60000 - y; return 12337.4 + 0.025 * (dd - 1498.5); }
static double AnxTop(double x) { return 5700.3 + 150.0 * (x + 7100.0) / 7100.0 + 296; }   // пристройка БП1 top (gen.anx_top)
static double PurlinBottom(double y) { if (Math.Abs(y) < 1 || Math.Abs(y - 60000) < 1) return 14490; if (Math.Abs(y - 24000) < 1 || Math.Abs(y - 36000) < 1) return 15097; return ZTop(y); }
class End { public FamilyInstance M; public string Mk; public XYZ Pe, U, N, W; public double B, Tw; public XYZ Q, Mn; public double Clamp0 = double.NaN, Clamp1 = double.NaN; public string Key; public bool Shop, Apex, Base, AnxCol; public double Ypurlin, Xp = double.NaN; public double Zmax = double.NaN, Zmin = double.NaN; public XYZ Hp; public double Ylo = double.NaN, Yhi = double.NaN; }
static double[] Hull(List<double[]> pts) {
    var p = pts.Select(q => new[] { Math.Round(q[0], 3), Math.Round(q[1], 3) }).GroupBy(q => q[0] + "|" + q[1]).Select(g => g.First()).OrderBy(q => q[0]).ThenBy(q => q[1]).ToList();
    Func<double[], double[], double[], double> cr = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
    var lo = new List<double[]>(); foreach (var q in p) { while (lo.Count >= 2 && cr(lo[lo.Count - 2], lo[lo.Count - 1], q) <= 0) lo.RemoveAt(lo.Count - 1); lo.Add(q); }
    var up = new List<double[]>(); foreach (var q in Enumerable.Reverse(p)) { while (up.Count >= 2 && cr(up[up.Count - 2], up[up.Count - 1], q) <= 0) up.RemoveAt(up.Count - 1); up.Add(q); }
    lo.RemoveAt(lo.Count - 1); up.RemoveAt(up.Count - 1); return lo.Concat(up).SelectMany(q => q).ToArray(); }
// distance along u from p to the plane (q, m); +inf if parallel
static double Hit(XYZ p, XYZ u, XYZ q, XYZ m) { double dn = u.DotProduct(m); if (Math.Abs(dn) < 1e-9) return 1e9; return (q - p).DotProduct(m) / dn; }

static string Nodes(Document d)
{
    var sb = new System.Text.StringBuilder(); XYZ X = XYZ.BasisX, Y = XYZ.BasisY, Z = XYZ.BasisZ;
    using (var t = new Transaction(d, "В109: узлы труб"))
    {
        t.Start();
        var fo = t.GetFailureHandlingOptions(); fo.SetFailuresPreprocessor(new Swallow()); t.SetFailureHandlingOptions(fo);
        sb.AppendLine("removed " + RemoveNode(d, "трубы") + " old pieces");
        var soP = SoPlate(d); var soB = SoBolt(d); var soW = SoWeld(d);
        Func<FamilyInstance, string> Cm = f => f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "";
        var tubes = new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>()
            .Where(f => f.Location is LocationCurve && f.Symbol.Family.Name.Contains("труба") && (Cm(f).StartsWith("СВ") || Cm(f) == "ГС1" || Cm(f) == "Р1" || Cm(f) == "ВС1" || Cm(f) == "ВФ1")).ToList();
        var ends = new List<End>();
        foreach (var f in tubes)
        {
            var c = (f.Location as LocationCurve).Curve; string mk = Cm(f);
            double b = f.Symbol.LookupParameter("b").AsDouble() / MM, tw = f.Symbol.LookupParameter("t").AsDouble() / MM;
            for (int k = 0; k < 2; k++)
            {
                var pe = c.GetEndPoint(k) / MM; var pother = c.GetEndPoint(1 - k) / MM; var u = (pe - pother).Normalize();
                var e = new End { M = f, Mk = mk, Pe = pe, U = u, B = b, Tw = tw };
                double xa = Math.Round(pe.X / 6000) * 6000;
                if (mk == "Р1")
                {   // strut tube to the column web, gusset kept to its own band (L ± 52) clear of the brace gussets
                    e.N = Y; double sx = Math.Sign(pe.X - xa); bool k2 = pe.Y > 59000 && xa >= 72000 - 1 && xa <= 90001;
                    e.Mn = sx * X; e.Q = new XYZ(xa + sx * (k2 ? 9 : 8), pe.Y, pe.Z); e.Key = "r1 " + xa + " " + pe.Y + " " + sx + " " + Math.Round(pe.Z);
                    e.Zmin = pe.Z - 52; e.Zmax = pe.Z + 52;
                }
                else if (mk == "ВС1")
                {   // vertical bracing between the trusses: top end on the top chord web (inside the I, under the ГС1 gussets), bottom on the Р2 strut top
                    e.N = Y;
                    if (Math.Abs(pe.X - xa) < 700) { double sx = Math.Sign(pe.X - xa); double tc = ZTop(pe.Y) - 96.5; e.Mn = sx * X; e.Q = new XYZ(xa + sx * 3, pe.Y, pe.Z);
                        e.Zmin = tc - 96.5 + 9 + 13 + 1; e.Zmax = ZTop(pe.Y) - 9 - 13 - 1; e.Key = "vst " + xa + " " + Math.Round(pe.Y) + " " + sx; }
                    else { e.Mn = Z; e.Q = new XYZ(pe.X, pe.Y, ZTop(pe.Y) - 2146.5); e.Key = "vsb " + Math.Round(pe.X / 600) + " " + Math.Round(pe.Y); }
                }
                else if (mk == "ВФ1")
                {   // end-wall girt +6.200: gusset (normal X) on the column face, kept to its own band
                    e.N = X; double[] vy = { 0, 6000, 12000, 18000, 24000, 27000, 33000, 36000, 42000, 48000, 54000, 60000 };
                    double ya2 = vy.OrderBy(v => Math.Abs(v - pe.Y)).First(); double sy = Math.Sign(pe.Y - ya2); bool kc = ya2 == 0 || ya2 == 24000 || ya2 == 36000 || ya2 == 60000;
                    e.Mn = sy * Y; e.Q = new XYZ(pe.X, ya2 + sy * (kc ? 294.5 : 5), pe.Z); e.Zmin = pe.Z - 52; e.Zmax = pe.Z + 52; e.Key = "vf " + Math.Round(pe.X) + " " + ya2 + " " + sy;
                }
                else if (mk.StartsWith("СВ"))
                {
                    e.N = Y;
                    if (mk != "СВ1" && pe.Z > 12000)
                    {   // user 09.11: top end under the longer column cap −14 (plate under the purlin), gusset welded to its underside
                        double capB = (Math.Abs(pe.Y) < 1 || Math.Abs(pe.Y - 60000) < 1 ? 14490 : 15097) - 14;
                        e.Mn = -Z; e.Q = new XYZ(pe.X, pe.Y, capB); e.Key = "cap " + xa + " " + pe.Y;
                    }
                    else if (Math.Abs(pe.X - xa) < 700) { if (mk == "СВ1" && pe.Z < 1500) e.Base = true; double sx = Math.Sign(pe.X - xa); bool k2 = pe.Y > 59000 && xa >= 72000 - 1 && xa <= 90001; e.Mn = sx * X; e.Q = new XYZ(xa + sx * (k2 ? 9 : 8), pe.Y, pe.Z); e.Key = "col " + xa + " " + pe.Y + " " + sx + " " + Math.Round(pe.Z / 300);
                        foreach (var Ls in new[] { 5020.0, 10340.0 }) { if (Math.Abs(pe.Z - (Ls - 50)) < 700 && pe.Z < Ls) e.Zmax = Ls - 54; if (Math.Abs(pe.Z - (Ls + 50)) < 700 && pe.Z > Ls) e.Zmin = Ls + 54; } }
                    else { double L = Math.Abs(pe.Z - 5020) < Math.Abs(pe.Z - 10340) ? 5020 : 10340; double sz = Math.Sign(pe.Z - L); e.Mn = sz * Z; e.Q = new XYZ(pe.X, pe.Y, L + sz * 50); e.Key = "p1 " + Math.Round(pe.X / 600) + " " + pe.Y + " " + L + " " + sz; }
                }
                else if (mk == "ГС1")
                {
                    e.N = Z;
                    double ya = Math.Round(pe.Y / 3000) * 3000;
                    if (pe.X < -100)
                    {   // пристройка: БП1 along X at y = 6000·k (web landing), purlins along Y at x −2333 / −7000 (apex stand)
                        double yr = Math.Round(pe.Y / 6000) * 6000;
                        if (Math.Abs(pe.Y - yr) < 700) { double sy = Math.Sign(pe.Y - yr); e.Mn = sy * Y; e.Q = new XYZ(pe.X, yr + sy * 2.9, pe.Z); e.Key = "agch " + yr + " " + sy + " " + Math.Round(pe.X / 600); e.AnxCol = pe.X > -1000; }
                        else { double xp = Math.Abs(pe.X + 2333) < Math.Abs(pe.X + 7000) ? -2333 : -7000; e.Apex = true; e.Xp = xp; e.Mn = X; e.Q = new XYZ(xp, pe.Y, pe.Z); e.Key = "agap " + xp + " " + Math.Round(pe.Y / 600); }
                    }
                    else if (Math.Abs(pe.X - xa) < 700)
                    {
                        double sx = Math.Sign(pe.X - xa);
                        double[] rows = { 0, 24000, 36000, 60000 }; double row = rows.FirstOrDefault(r => Math.Abs(pe.Y - r) < 700 && Math.Abs(ya - r) < 1); bool onRow = rows.Any(r => Math.Abs(pe.Y - r) < 700 && Math.Abs(ya - r) < 1);
                        if (onRow)
                        {   // over a column: the gusset lands on the column flange outer face (clamped to its width)
                            double sy = Math.Sign(pe.Y - row); bool k2 = row == 60000 && xa >= 72000 - 1 && xa <= 90001; double hf = k2 ? 298.5 : 294.5;
                            // 09.11: the flange (end plate) of the member landing on this face (nodes.py endplate) — the gusset lands on its outer face
                            bool inner = (row == 24000 && sy > 0) || (row == 36000 && sy < 0); bool edge = Math.Abs(xa) < 1 || Math.Abs(xa - 162000) < 1;
                            double st = inner ? 314.5 : edge ? 309.5 : 312, hm = inner ? 392 : edge ? 296 : 193, wpl = (inner || edge) ? 100 : 125;
                            double face = st - (750.0 / 29705.5 * hm / 2 + 0.5); if (face < hf) face = hf;
                            e.Mn = sy * Y; e.Q = new XYZ(xa, row + sy * face, pe.Z); e.Clamp0 = sx > 0 ? xa + 10 : xa - (wpl - 5); e.Clamp1 = sx > 0 ? xa + wpl - 5 : xa - 10; e.Key = "gcol " + xa + " " + row + " " + sy + " " + sx;
                        }
                        else
                        {
                            double s = (pe.Y > 24000 && pe.Y < 36000) ? 7 : (Math.Abs(xa) < 1 || Math.Abs(xa - 162000) < 1) ? 5.8 : 6;
                            double qx = xa + sx * s / 2; if (sx > 0 && Math.Abs(pe.Y - 30000) < 450) qx = xa + 13.5;   // ridge: on the БП2 splice plate (+X side)
                            e.Mn = sx * X; e.Q = new XYZ(qx, pe.Y, pe.Z); e.Key = "gch " + xa + " " + ya + " " + sx;
                        }
                    }
                    else { e.Apex = true; e.Ypurlin = ya; e.Mn = Y; e.Q = new XYZ(pe.X, ya, pe.Z); e.Key = "gap " + Math.Round(pe.X / 600) + " " + ya; }
                }
                else
                {   // truss lattice: top chord underside or bottom chord top face (planes along the slope)
                    e.N = X; e.Shop = true;
                    bool top = pe.Z > (ZTop(pe.Y) - 296 + Zbc(pe.Y)) / 2;
                    Func<double, double> zf = yy => top ? ZTop(yy) - 296 : Zbc(yy);
                    var qa = new XYZ(pe.X, pe.Y, zf(pe.Y)); var qb = new XYZ(pe.X, pe.Y + 100, zf(pe.Y + 100)); var along = (qb - qa).Normalize();
                    var m = X.CrossProduct(along).Normalize(); if (m.Z * (top ? -1 : 1) < 0) m = -m; e.Mn = m; e.Q = qa;
                    double node = top ? Math.Round(pe.Y / 3000) * 3000 : Math.Round((pe.Y - 1500) / 3000) * 3000 + 1500;
                    double side0 = pe.Y < 30000 ? 0 : 60000, sg2 = pe.Y < 30000 ? 1 : -1; double ca = top ? 312 : 1498.5, cb = top ? 23688 : 22498.5;
                    e.Ylo = Math.Min(side0 + sg2 * ca, side0 + sg2 * cb); e.Yhi = Math.Max(side0 + sg2 * ca, side0 + sg2 * cb);
                    e.Key = "ff " + pe.X + " " + (top ? "T" : "B") + " " + Math.Round(pe.Y / 600);
                }
                e.W = e.N.CrossProduct(e.U).Normalize(); ends.Add(e);
            }
        }
        sb.AppendLine("tube ends " + ends.Count + " (" + string.Join(", ", ends.GroupBy(x => x.Mk.Split(' ')[0]).Select(g => g.Key + " " + g.Count())) + ")");
        int nodes = 0, bolts = 0, short_ = 0, bad = 0; int shortB = 0;
        foreach (var e in ends) { double dd = Hit(e.Pe, e.U, e.Q, e.Mn); if (dd > 1e8 || dd < 0) dd = 0; e.Hp = e.Pe + e.U * dd; }
        var par = Enumerable.Range(0, ends.Count).ToArray(); Func<int, int> Fd = null; Fd = i => par[i] == i ? i : (par[i] = Fd(par[i]));
        var srt = Enumerable.Range(0, ends.Count).OrderBy(i => ends[i].Hp.X).ToList();
        for (int a = 0; a < srt.Count; a++) for (int b = a + 1; b < srt.Count && ends[srt[b]].Hp.X - ends[srt[a]].Hp.X < 150; b++)
        { var A = ends[srt[a]]; var Bq = ends[srt[b]]; if (A.Key.Split(' ')[0] != Bq.Key.Split(' ')[0] || A.N.DotProduct(Bq.N) < 0.99 || A.Mn.DotProduct(Bq.Mn) < 0.99) continue;
          if (A.Hp.DistanceTo(Bq.Hp) < 150 && Math.Abs((A.Q - Bq.Q).DotProduct(A.Mn)) < 2) par[Fd(srt[a])] = Fd(srt[b]); }
        for (int i = 0; i < ends.Count; i++) ends[i].Key = "g" + Fd(i);
        foreach (var g in ends.GroupBy(x => x.Key))
        {
            var L = g.ToList(); var e0 = L[0]; var n = e0.N; var E1 = e0.U - n * e0.U.DotProduct(n); E1 = E1.Normalize(); var E2 = n.CrossProduct(E1);
            var plates = new List<GeometryObject>(); var caps = new List<GeometryObject>(); var welds = new List<GeometryObject>(); var bl = new List<GeometryObject>();
            var hp = new List<double[]>(); var land = new List<XYZ>(); double nBase = 0;
            // the axis plane of the node = the axis plane of the first end (all inserts of a node lie in it)
            var o3 = e0.Pe; Func<XYZ, double[]> To2 = p => new[] { (p - o3).DotProduct(E1), (p - o3).DotProduct(E2) };
            foreach (var e in L)
            {
                double b = e.B, bi = b - 2 * e.Tw - 2;
                // cap halves on the tube end, outside it (s_e … s_e+4), slot ±4 for the insert
                caps.Add(Plate((e.Pe + e.N * 4) * MM, e.W, e.N, Rect(-b / 2, 0, b / 2, b / 2 - 4), 4, false, soP));
                caps.Add(Plate((e.Pe - e.N * (b / 2)) * MM, e.W, e.N, Rect(-b / 2, 0, b / 2, b / 2 - 4), 4, false, soP));
                foreach (var sw in new[] { 1.0, -1.0 })
                {   // cap ↔ tube welds on the four outer edges
                    welds.Add(Weld((e.Pe + e.N * sw * b / 2 - e.W * b / 2) * MM, -e.U, e.N * sw, e.W, 4, b, soW));
                }
                double dist = Hit(e.Pe, e.U, e.Q, e.Mn); if (e.Apex) dist = Math.Min(dist, 182);
                if (!double.IsNaN(e.Zmax) && e.U.Z > 1e-6) dist = Math.Min(dist, (e.Zmax - e.Pe.Z) / e.U.Z);
                if (!double.IsNaN(e.Zmin) && e.U.Z < -1e-6) dist = Math.Min(dist, (e.Zmin - e.Pe.Z) / e.U.Z);
                double outL = Math.Min(e.Shop ? 100 : 200, dist - 12);              // 09.11 user: field gussets bigger, insert out up to 170 (2 bolts along the axis)
                {   // both lap corners (±b/2 across) stay 3 mm off the support face
                    double un = e.U.DotProduct(e.Mn), wn = Math.Abs(e.W.DotProduct(e.Mn)) * b / 2, d0 = (e.Pe - e.Q).DotProduct(e.Mn);
                    if (un < -1e-6 && !e.Apex) outL = Math.Min(outL, (d0 - wn - 3) / -un);
                    if (!double.IsNaN(e.Zmax) && e.U.Z > 1e-6) outL = Math.Min(outL, (e.Zmax - e.Pe.Z - Math.Abs(e.W.Z) * b / 2 - 3) / e.U.Z);
                    if (!double.IsNaN(e.Zmin) && e.U.Z < -1e-6) outL = Math.Min(outL, (e.Zmin - e.Pe.Z + Math.Abs(e.W.Z) * b / 2 + 3) / e.U.Z);
                } if (outL < 40) { short_++; outL = Math.Max(outL, 5); }
                // insert −8 in the axis plane: inside the tube 120, outside outL
                {   // insert −8: rectangle (a −120 … outL along U, ±bi/2 across W) clipped 1 mm off the bisector with every other end of the node
                    var ins = new double[] { -120, -bi / 2, outL, -bi / 2, outL, bi / 2, -120, bi / 2 }; var bs = e.Pe - e.N * 4;
                    foreach (var o in L.Where(x => x != e))
                    {
                        var dA = -e.U; var dB = -o.U; var bis = dA + dB; if (bis.GetLength() < 1e-6) continue; bis = bis.Normalize();
                        var sA = dA - bis * dA.DotProduct(bis); if (sA.GetLength() < 1e-6) continue; sA = sA.Normalize();
                        // node point O: closest point of the two axes
                        var w0 = e.Pe - o.Pe; double a1 = e.U.DotProduct(e.U), b1 = e.U.DotProduct(o.U), c1 = o.U.DotProduct(o.U), d1 = e.U.DotProduct(w0), e1 = o.U.DotProduct(w0); double den = a1 * c1 - b1 * b1; if (Math.Abs(den) < 1e-9) continue;
                        double tA = (b1 * e1 - c1 * d1) / den; var O = e.Pe + e.U * tA;
                        ins = Clip(ins, e.U.DotProduct(sA), e.W.DotProduct(sA), 1 - (bs - O).DotProduct(sA) + 4 * e.N.DotProduct(sA), false);
                    }
                    var iv = new List<double[]>(); for (int i = 0; i < ins.Length; i += 2) { var q = new[] { ins[i], ins[i + 1] }; if (iv.Count == 0 || Math.Abs(iv[iv.Count - 1][0] - q[0]) + Math.Abs(iv[iv.Count - 1][1] - q[1]) > 1) iv.Add(q); }
                    if (iv.Count > 1 && Math.Abs(iv[0][0] - iv[iv.Count - 1][0]) + Math.Abs(iv[0][1] - iv[iv.Count - 1][1]) <= 1) iv.RemoveAt(iv.Count - 1);
                    if (iv.Count >= 3) { try { plates.Add(Plate(bs * MM, e.U, e.W, iv.SelectMany(q => q).ToArray(), 8, false, soP)); } catch { } }
                }
                // gusset outline points: the lap on the insert (s_e+10 … s_e+outL, width b) and its landing on the support
                double gw = e.Shop ? b / 2 : b / 2 + 30;                                   // field gusset: 30 wider than the tube each side (edge ≥ 1.5d for М16)
                foreach (var sw in new[] { -b / 2, b / 2 }) hp.Add(To2(e.Pe + e.U * 20.0 + e.W * sw));    // narrow at the tube end (clear of the neighbour caps)
                foreach (var sw in new[] { -gw, gw }) hp.Add(To2(e.Pe + e.U * outL + e.W * sw));
                if (!e.Apex)
                {
                    foreach (var sw in new[] { -gw, gw })
                    {
                        var p = e.Pe + e.U * outL + e.W * sw;                    // lap corner, projected square onto the support face
                        var q = p - e.Mn * ((p - e.Q).DotProduct(e.Mn) - 0.3);
                        if (!double.IsNaN(e.Clamp0)) { double xx = Math.Max(e.Clamp0, Math.Min(e.Clamp1, q.X)); q = new XYZ(xx, q.Y, q.Z); }   // 09.11: q is in mm (was q.X / MM → always one end → landing on the tip)
                        if (e.AnxCol) q = new XYZ(Math.Min(q.X, -200.5), q.Y, q.Z);      // пристройка: landing stops off the СФ flange
                        if (!double.IsNaN(e.Zmax)) q = new XYZ(q.X, q.Y, Math.Min(q.Z, e.Zmax - 1));    // the landing (and its welds) stays in the node band
                        if (!double.IsNaN(e.Zmin)) q = new XYZ(q.X, q.Y, Math.Max(q.Z, e.Zmin + 1));
                        land.Add(q); hp.Add(To2(q));
                    }
                    if (!double.IsNaN(e.Clamp0))
                    {   // over a column: the gusset lands on the whole clamp span of the face (not on its tip)
                        var qa = land[land.Count - 1]; var qb = land[land.Count - 2]; double zq = (qa.Z + qb.Z) / 2, yq = (qa.Y + qb.Y) / 2;
                        foreach (var xx in new[] { e.Clamp0, e.Clamp1 }) { var q2 = new XYZ(xx, yq, zq); land.Add(q2); hp.Add(To2(q2)); }
                    }
                }
                else hp.Add(To2(double.IsNaN(e.Xp) ? new XYZ(e.Pe.X, e.Ypurlin, e.Pe.Z) : new XYZ(e.Xp, e.Pe.Y, e.Pe.Z)));
                if (!e.Shop)
                {   // 2 bolts М16 through insert + gusset, head under the insert
                    // where the gusset starts along the axis (it is clipped under a chord flange etc.): bolts stay ≥ 30 inside it
                    double a0 = 20;
                    if (!double.IsNaN(e.Zmin) && e.U.Z > 1e-6) a0 = Math.Max(a0, (e.Zmin - e.Pe.Z + Math.Abs(e.W.Z) * b / 2) / e.U.Z);
                    if (!double.IsNaN(e.Zmax) && e.U.Z < -1e-6) a0 = Math.Max(a0, (e.Zmax - e.Pe.Z - Math.Abs(e.W.Z) * b / 2) / e.U.Z);
                    double a1 = Math.Max(40, a0 + 30), a2 = a1 + 60;                                            // along the axis: pitch 60 (≥2.5d), edges ≥30
                    if (a2 > outL - 30) { a2 = outL - 30; a1 = a2 - 60; }
                    var bp = a1 >= a0 + 25 && a1 >= 35 ? new[] { new[] { a1, 0 }, new[] { a2, 0 } }
                                                       : new[] { new[] { (a0 + outL) / 2, -(bi / 2 - 25) }, new[] { (a0 + outL) / 2, bi / 2 - 25 } };   // across: edge 25 (≥1.5d), pitch ≥ 40
                    if (bp[0][1] != 0) { shortB++; if (shortB <= 6) sb.AppendLine("across " + e.Key + " a0 " + Math.Round(a0) + " outL " + Math.Round(outL) + " dist " + Math.Round(dist)); }
                    foreach (var q in bp)
                    { var c = (e.Pe + e.U * q[0] + e.W * q[1] - e.N * 4) * MM; bl.AddRange(Bolt(c, e.N, 16, 18, BoltLen(16, 18), soB)); bolts++; }
                }
                else
                {   // insert ↔ gusset welds along both insert edges, under the gusset
                    foreach (var sw in new[] { -1.0, 1.0 })
                        if (outL > 30) welds.Add(Weld((e.Pe + e.U * 20 + e.W * sw * bi / 2 + e.N * 4) * MM, -e.N, e.W * sw, e.U, 4, Math.Min(outL, 50) - 20, soW));
                }
            }
            // gusset −10 on the +n side of the inserts
            var eb = L.FirstOrDefault(x => x.Base); double bxa = 0, bsx = 0;
            if (eb != null)
            {   // user 09.11 (Б2): the СВ1 gusset goes down to the base plate (top −360), slot for the long base rib (u 150…162 from the axis, top −50)
                bxa = Math.Round(eb.Pe.X / 6000) * 6000; bsx = Math.Sign(eb.Pe.X - bxa);
                hp.Add(To2(new XYZ(bxa + bsx * 8.3, o3.Y, -359.7))); hp.Add(To2(new XYZ(bxa + bsx * 300, o3.Y, -359.7)));
                land.Add(new XYZ(bxa + bsx * 8.3, o3.Y, -340));
            }
            var hull = Hull(hp);
            double zmx = L.Where(x => !double.IsNaN(x.Zmax)).Select(x => x.Zmax).DefaultIfEmpty(double.NaN).Min(), zmn = L.Where(x => !double.IsNaN(x.Zmin)).Select(x => x.Zmin).DefaultIfEmpty(double.NaN).Max();
            if (!double.IsNaN(zmx)) hull = Clip(hull, E1.Z, E2.Z, zmx - o3.Z, true);
            foreach (var e in L.Where(x => !x.Apex)) hull = Clip(hull, E1.DotProduct(e.Mn), E2.DotProduct(e.Mn), (e.Q - o3).DotProduct(e.Mn) + 0.3, false);
            var lo = L.Where(x => !double.IsNaN(x.Ylo)).Select(x => x.Ylo).DefaultIfEmpty(double.NaN).Max(); var hi = L.Where(x => !double.IsNaN(x.Yhi)).Select(x => x.Yhi).DefaultIfEmpty(double.NaN).Min();
            if (!double.IsNaN(lo)) { hull = Clip(hull, E1.Y, E2.Y, lo + 5 - o3.Y, false); hull = Clip(hull, E1.Y, E2.Y, hi - 5 - o3.Y, true); }
            if (!double.IsNaN(zmn)) hull = Clip(hull, E1.Z, E2.Z, zmn - o3.Z, false);
            {   // drop near-duplicate vertices left by the clips
                var hv = new List<double[]>(); for (int i = 0; i < hull.Length; i += 2) { var q = new[] { hull[i], hull[i + 1] }; if (hv.Count == 0 || Math.Abs(hv[hv.Count - 1][0] - q[0]) + Math.Abs(hv[hv.Count - 1][1] - q[1]) > 1) hv.Add(q); }
                if (hv.Count > 1 && Math.Abs(hv[0][0] - hv[hv.Count - 1][0]) + Math.Abs(hv[0][1] - hv[hv.Count - 1][1]) <= 1) hv.RemoveAt(hv.Count - 1);
                hull = hv.SelectMany(q => q).ToArray();
            }
            if (L.Any(x => x.AnxCol)) hull = Clip(hull, E1.X, E2.X, -200 - o3.X, true);     // пристройка: gusset stops 5 off the СФ flange (x −195)
            Func<double[], XYZ, double, bool, double[]> ClipW = (poly, nv, val, ge) => Clip(poly, E1.DotProduct(nv), E2.DotProduct(nv), val - o3.DotProduct(nv), !ge);
            if (eb != null && hull.Length >= 6)
            {
                XYZ SX = bsx * X; double sxa = bsx * bxa;
                var pA = ClipW(hull, SX, 149.7 + sxa, false); pA = ClipW(pA, SX + Z, 8.3 + 15 - 359.7 + sxa, true); pA = ClipW(pA, -SX + Z, -149.7 + 12 - 359.7 - sxa, true);
                var pB = ClipW(hull, SX, 162.6 + sxa, true); pB = ClipW(pB, SX + Z, 162.6 + 12 - 359.7 + sxa, true);
                var pC = ClipW(ClipW(ClipW(hull, SX, 149.7 + sxa, true), SX, 162.6 + sxa, false), Z, -49.7, true);
                Solid acc = null;
                foreach (var pc in new[] { pA, pB, pC })
                    if (pc.Length >= 6) { try { var sl = Plate(o3 * MM + n * 4 * MM, E1, E2, pc, 10, false, soP); acc = acc == null ? sl : BooleanOperationsUtils.ExecuteBooleanOperation(acc, sl, BooleanOperationsType.Union); } catch { bad++; } }
                if (acc != null) plates.Add(acc); else bad++;
                double xmaxB = 0; for (int i = 0; i < pB.Length; i += 2) { var w = o3 + E1 * pB[i] + E2 * pB[i + 1]; if (w.Z < -355) xmaxB = Math.Max(xmaxB, bsx * (w.X - bxa)); }
                foreach (var fy in new[] { 4.0, 14.0 })
                {   // gusset ↔ base plate, both faces, either side of the rib slot
                    var lg = fy < 5 ? -Y : Y; double yy = o3.Y + fy;
                    welds.Add(Weld(P(bxa + bsx * 23.3, yy, -360), lg, Z, SX, 6, 149.7 - 12 - 23.3, soW));
                    if (xmaxB - 162.6 - 12 > 10) welds.Add(Weld(P(bxa + bsx * (162.6 + 12), yy, -360), lg, Z, SX, 6, xmaxB - 162.6 - 12 - 3, soW));
                }
            }
            else if (hull.Length >= 6) { try { plates.Add(Plate(o3 * MM + n * 4 * MM, E1, E2, hull, 10, false, soP)); } catch { bad++; } } else bad++;
            if (land.Count >= 2)
            {   // gusset ↔ support: both sides, along the landing line
                var dir = e0.Mn.CrossProduct(n).Normalize(); var l0 = land.OrderBy(p => p.DotProduct(dir)).First(); var l1 = land.OrderBy(p => p.DotProduct(dir)).Last();
                double len = (l1 - l0).DotProduct(dir);
                if (len > 5)
                {
                    var b0 = (l0 - n * l0.DotProduct(n) + (o3 + n * 4).DotProduct(n) * n) * MM;   // on the gusset's lower face plane (ft)
                    welds.Add(Weld(b0, e0.Mn, -n, dir, 6, len, soW)); welds.Add(Weld(b0 + n * 10 * MM, e0.Mn, n, dir, 6, len, soW));
                }
            }
            else if (L.Any(x => x.Apex))
            {   // ГС1 under the purlin middle: stand −10 (along X) from the gusset top to the purlin bottom flange
                var ea = L.First(x => x.Apex); double yp = ea.Ypurlin; double zTopG = o3.Z + 14; double zb = PurlinBottom(yp) - 2;
                var cx = L.Average(x => x.Pe.X);
                if (!double.IsNaN(ea.Xp))
                {   // пристройка: purlin along Y at x = Xp, stand −10 along Y
                    double xp = ea.Xp, zbA = AnxTop(xp) + 1.1 - 2, cy = L.Average(x => x.Pe.Y);
                    if (zbA - zTopG > 2)
                    {
                        plates.Add(Plate(new XYZ((xp - 5) * MM, (cy - 60) * MM, zTopG * MM), Y, Z, Rect(0, 0, 120, zbA - zTopG), 10, false, soP));
                        foreach (var sxx in new[] { -1.0, 1.0 }) { welds.Add(Weld(new XYZ((xp + sxx * 5) * MM, (cy - 60) * MM, zbA * MM), sxx * X, -Z, Y, 5, 120, soW)); welds.Add(Weld(new XYZ((xp + sxx * 5) * MM, (cy - 60) * MM, zTopG * MM), sxx * X, Z, Y, 5, 120, soW)); }
                    }
                }
                else if (zb - zTopG > 2)
                {
                    plates.Add(Plate(new XYZ((cx - 60) * MM, (yp + 5) * MM, zTopG * MM), X, Z, Rect(0, 0, 120, zb - zTopG), 10, false, soP));
                    foreach (var sy in new[] { -1.0, 1.0 }) { welds.Add(Weld(new XYZ((cx - 60) * MM, (yp + sy * 5) * MM, zb * MM), sy * Y, -Z, X, 5, 120, soW)); welds.Add(Weld(new XYZ((cx - 60) * MM, (yp + sy * 5) * MM, zTopG * MM), sy * Y, Z, X, 5, 120, soW)); }
                }
            }
            string nm = L[0].Mk.StartsWith("ФФ1") ? "ФФ1" : L[0].Mk;
            DS(d, BuiltInCategory.OST_StructConnections, "трубы", "Узел " + nm + ": фасонка −10, вкладыши −8" + (L.Any(x => x.Apex) ? ", стойка −10" : ""), plates.Where(x => x != null).ToList());
            DS(d, BuiltInCategory.OST_StructConnections, "трубы", "ПЛ3 заглушка −4 (" + nm + ")", caps);
            if (bl.Count > 0) DS(d, BuiltInCategory.OST_StructConnectionBolts, "трубы", "Болт М16 (" + nm + ")", bl);
            DS(d, BuiltInCategory.OST_StructConnectionWelds, "трубы", "шов узел " + nm, welds);
            nodes++;
        }
        t.Commit();
        sb.AppendLine("nodes " + nodes + ", bolts " + bolts + ", short inserts " + short_ + ", ends with bolts across " + shortB + ", gussets failed " + bad);
    }
    return sb.ToString();
}
// clip a 2D polygon (u, v pairs) by a·u + b·v ≤ c (keepBelow) or ≥ c
static double[] Clip(double[] poly, double a, double b, double c, bool keepBelow) {
    var P = new List<double[]>(); for (int i = 0; i < poly.Length; i += 2) P.Add(new[] { poly[i], poly[i + 1] });
    Func<double[], double> F = q => (a * q[0] + b * q[1] - c) * (keepBelow ? 1 : -1);
    var R = new List<double[]>();
    for (int i = 0; i < P.Count; i++) { var p = P[i]; var q = P[(i + 1) % P.Count]; double fp = F(p), fq = F(q);
        if (fp <= 0) R.Add(p);
        if ((fp < 0 && fq > 0) || (fp > 0 && fq < 0)) { double t = fp / (fp - fq); R.Add(new[] { p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1]) }); } }
    return R.SelectMany(q => q).ToArray(); }
// insert plate: length along u, width across w (centred), thickness along n from o
static Solid PlateN(XYZ o, XYZ u, XYZ w, XYZ n, double len, double wid, double t, SolidOptions so) {
    var o2 = o - w * (wid / 2) * MM; var lp = new CurveLoop();
    var p0 = o2; var p1 = o2 + u * len * MM; var p2 = p1 + w * wid * MM; var p3 = o2 + w * wid * MM;
    lp.Append(Line.CreateBound(p0, p1)); lp.Append(Line.CreateBound(p1, p2)); lp.Append(Line.CreateBound(p2, p3)); lp.Append(Line.CreateBound(p3, p0));
    return GeometryCreationUtilities.CreateExtrusionGeometry(new List<CurveLoop> { lp }, n, t * MM, so); }
