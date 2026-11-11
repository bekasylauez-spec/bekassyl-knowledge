// Завод В113: all frame nodes except the bases (v113_10). Run with -Lib v113_lib.cs. Re-runnable (keys «узел …»). Log: _v113_11.txt.
// Node structure (analog Алатау Блок 1 / В109 user's nodes, КМ_ҚАТЕЛЕР rules 36–55), brought to the В113 sections:
//  Узел 1 (жёсткий, analog Алатау узел 1) К1 top cut on the roof: cap −16, table −16 + rib −12, column ribs −16, fish −12 + L100x7 + М24.
//  Узел 2 Б1/Б2 ridge: shop butt joint (beam = one shop piece 12 m), welds round the section.
//  Узел 3 Р1 ↔ К1 (+3.350): gusset −10 welded to the К1 web, through the Р1 slot (rule 55), Р1 end ≈180 from the axis, cap −8; field welds.
//  Узел 4 СВ1 ends: cap −8 (b+20), tee insert −8 (flat 130×150 + rib 40) on the cap, 2 М16 through insert + gusset −10;
//         gussets: К1 web (top, base — down to the base plate, rule 36), Р1 mid node (one gusset through Р1).
//  Узел 5 ГС1 ends: the same insert in the roof plane, gusset −10 under the beam top flange (welded to flange + web), under the cap of К1,
//         under the purlin (rule 39); crossing — the cut diagonal's cap welded to the through diagonal.
//  Узел 6 Пр1 on Б1/Б2/К1: stand plate −10 behind the purlin web (rule 38), 2 М16 per purlin end.
//  Узел 7 ПБ1 hanger: top plate −10 under the beam, 2 L50x5 (Т1), bottom plate −10 on ПБ1, 4 М16; web splice −8 + 4 М16; end stop −10.
//  Узел 8 К2 top: cap −16 270×270, 4 М16 to the Б2 bottom flange, stiffeners −8 in Б2.
// Every plate is cleaned against the frame and the bases (boolean difference) — clash 0 by construction; bolts pass through packs.
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"D:\Бекасыл КЖ КМ\Завод_В113_КМ\_авто\_v113_11.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder();
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В113-КМ.rvt")); sb.Append(Nodes(nd)); nd.Save(); sb.AppendLine("saved"); }
  catch (Exception ex) { sb.AppendLine("ERR " + ex); }
  System.IO.File.WriteAllText(log, sb.ToString()); };
uiapp.Idling += hnd;
return "queued";
}

const double SLP = 0.11; static double ZT0 = 6450.0 + 492.0 / Math.Cos(Math.Atan(SLP)); const double ZR1 = 2700.0;
static double Roof(double y) { return ZT0 + SLP * (y <= 6000 ? y : 12000 - y); }
static XYZ RoofN(double y) { return (Math.Abs(y - 6000) < 1 ? XYZ.BasisZ : y < 6000 ? new XYZ(0, -SLP, 1) : new XYZ(0, SLP, 1)).Normalize(); }
static XYZ Mm(XYZ p) { return p / MM; }
class Mb { public FamilyInstance F; public string Mk; public XYZ A, B; public List<Solid> S; }
class Sx { public Solid S; public XYZ Mn, Mx; }
static List<Sx> OBST = new List<Sx>();
static Sx BoxOf(Solid s) { var bb = s.GetBoundingBox(); var a = bb.Transform.OfPoint(bb.Min); var b = bb.Transform.OfPoint(bb.Max);
    return new Sx { S = s, Mn = new XYZ(Math.Min(a.X, b.X), Math.Min(a.Y, b.Y), Math.Min(a.Z, b.Z)), Mx = new XYZ(Math.Max(a.X, b.X), Math.Max(a.Y, b.Y), Math.Max(a.Z, b.Z)) }; }
// remove every obstacle (frame, bases, earlier node plates) from s; keep the biggest result
static Solid Clean(Solid s) {
    if (s == null) return null; var bx = BoxOf(s); double e = 0.5 * MM;
    foreach (var o in OBST) {
        if (o.Mx.X < bx.Mn.X - e || o.Mn.X > bx.Mx.X + e || o.Mx.Y < bx.Mn.Y - e || o.Mn.Y > bx.Mx.Y + e || o.Mx.Z < bx.Mn.Z - e || o.Mn.Z > bx.Mx.Z + e) continue;
        try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(s, o.S, BooleanOperationsType.Difference); if (r != null) s = r; } catch { }
        if (s.Volume < 1e-9) return null; }
    return s; }
static void Add(List<GeometryObject> g, Solid s, bool obstacle) { s = Clean(s); if (s == null || s.Volume < 1e-9) return; g.Add(s); if (obstacle) OBST.Add(BoxOf(s)); }
// convex hull (2D)
static double[] Hull(List<double[]> pts) {
    var p = pts.Select(q => new[] { Math.Round(q[0], 2), Math.Round(q[1], 2) }).GroupBy(q => q[0] + "|" + q[1]).Select(g => g.First()).OrderBy(q => q[0]).ThenBy(q => q[1]).ToList();
    Func<double[], double[], double[], double> cr = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
    var lo = new List<double[]>(); foreach (var q in p) { while (lo.Count >= 2 && cr(lo[lo.Count - 2], lo[lo.Count - 1], q) <= 0) lo.RemoveAt(lo.Count - 1); lo.Add(q); }
    var up = new List<double[]>(); foreach (var q in Enumerable.Reverse(p)) { while (up.Count >= 2 && cr(up[up.Count - 2], up[up.Count - 1], q) <= 0) up.RemoveAt(up.Count - 1); up.Add(q); }
    lo.RemoveAt(lo.Count - 1); up.RemoveAt(up.Count - 1); return lo.Concat(up).SelectMany(q => q).ToArray(); }
// plate from world points (mm) projected on the plane (o, eu, ev); thickness along eu×ev
static Solid HullPlate(XYZ o, XYZ eu, XYZ ev, List<XYZ> pts, double t, SolidOptions so) {
    var uv = pts.Select(p => { var d = (p - o); return new[] { d.DotProduct(eu), d.DotProduct(ev) }; }).ToList();
    return Plate(P(o.X, o.Y, o.Z), eu, ev, Hull(uv), t, false, so); }
// box from a centre (mm), three unit axes and the full sizes
static Solid Box(XYZ c, XYZ a, XYZ b, double la, double lb, double lc, SolidOptions so) {
    var n = a.CrossProduct(b).Normalize(); var o = c - a * la / 2 - b * lb / 2 - n * lc / 2;
    return Plate(P(o.X, o.Y, o.Z), a, b, Rect(0, 0, la, lb), lc, false, so); }
static XYZ W(XYZ p) { return P(p.X, p.Y, p.Z); }   // mm → feet

class TEnd { public Mb M; public XYZ Pe, U, N, S; public double B; public string Kind, Key; }

static string Nodes(Document d)
{
    var sb = new System.Text.StringBuilder(); XYZ X = XYZ.BasisX, Y = XYZ.BasisY, Z = XYZ.BasisZ; var cnt = new Dictionary<string, int>();
    Action<string> C = k => cnt[k] = (cnt.ContainsKey(k) ? cnt[k] : 0) + 1;
    using (var t = new Transaction(d, "В113: узлы"))
    {
        t.Start();
        var fo = t.GetFailureHandlingOptions(); fo.SetFailuresPreprocessor(new Swallow()); t.SetFailureHandlingOptions(fo);
        var PW = new List<Tuple<string, string, List<GeometryObject>>>();
        int rem = 0; foreach (var k in new[] { "узел 1", "узел 2", "узел 3", "узел 4", "узел 5", "узел 6", "узел 7", "узел 8", "узел 9", "заглушки" }) rem += RemoveNode(d, k);
        sb.AppendLine("removed " + rem + " old pieces");
        var soP = SoPlate(d); var soB = SoBolt(d); var soW = SoWeld(d);
        Func<FamilyInstance, string> Cm = f => f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "";
        var mem = new List<Mb>();
        foreach (var f in new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Symbol.Family.Name.StartsWith("(КМ)")))
        {
            var m = new Mb { F = f, Mk = Cm(f), S = Solids(f) };
            if (f.Location is LocationCurve lc) { m.A = Mm(lc.Curve.GetEndPoint(0)); m.B = Mm(lc.Curve.GetEndPoint(1)); }
            else { var bb = f.get_BoundingBox(null); var lp = Mm((f.Location as LocationPoint).Point); m.A = new XYZ(lp.X, lp.Y, bb.Min.Z / MM); m.B = new XYZ(lp.X, lp.Y, bb.Max.Z / MM); }
            mem.Add(m);
        }
        OBST.Clear();
        foreach (var m in mem) foreach (var s in m.S) OBST.Add(BoxOf(s));
        foreach (var ds in new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел" && x.ApplicationDataId == "база" && x.Category.Id.Value != (long)BuiltInCategory.OST_StructConnectionBolts))
            foreach (var s in Solids(ds)) OBST.Add(BoxOf(s));
        var K1 = mem.Where(m => m.Mk == "К1").ToList(); var K2 = mem.Where(m => m.Mk == "К2").ToList();
        var BB = mem.Where(m => m.Mk == "Б1" || m.Mk == "Б2").ToList(); var PR = mem.Where(m => m.Mk == "Пр1").ToList();
        double colTop = K1[0].B.Z;
        // ================= Узел 1 (жёсткий, analog Алатау Блок 1 узел 1): cap −16, table −16 + rib −12, column ribs −16, fish −12 + L100x7 + М24
        {
            var pl = new List<GeometryObject>(); var bo = new List<GeometryObject>(); var we = new List<GeometryObject>();
            double cth = Math.Cos(Math.Atan(SLP));
            foreach (var c in K1)
            {
                double cx = c.A.X, cy = c.A.Y; double sy = cy < 6000 ? 1 : -1;     // the beam goes from the column to +sy
                var b = BB.FirstOrDefault(q => Math.Abs(q.A.X - cx) < 1 && (Math.Abs(q.A.Y - cy) < 400 || Math.Abs(q.B.Y - cy) < 400)); if (b == null) continue;
                bool b1 = b.Mk == "Б1"; double h = b1 ? 492 : 296, bf = b1 ? 199 : 140, tf = b1 ? 12 : 8.5, tw = b1 ? 8.8 : 5.8;
                var tv = new XYZ(0, sy, SLP).Normalize(); var eu = X * sy; var nUp = eu.CrossProduct(tv).Normalize();   // in the roof plane / its up normal
                Func<double, double, XYZ> RP = (xx, yy) => new XYZ(xx, yy, Roof(yy));                            // beam-top plane (mm)
                double yf = cy + sy * 194.0;                                                                       // column inner face
                // cap −16 on the roof plane: 300 wide to the face, 230 over the beam (280 past the beam end 214)
                var oC = RP(cx, cy); double vO = -214.0 / cth, vF = 194.0 / cth, vE = 494.0 / cth;
                pl.Add(Plate(W(oC + nUp * 0.0), eu, tv, new double[] { -150, vO, 150, vO, 150, vF, 115, vF, 115, vE, -115, vE, -115, vF, -150, vF }, 16, false, soP));
                // table −16 under the bottom flange: top = beam bottom plane, from the face 300 along, 300 wide
                double hb = h / cth;                                                                              // vertical depth of the beam
                var oT = RP(cx, yf + sy * 0.3) - Z * (hb + 0.3);
                pl.Add(Plate(W(oT), -eu, tv, Rect(-150, 0, 150, 300 / cth), 16, false, soP));
                // rib −12 under the table in the web plane: 150 high at the face, 150 long
                var oR = oT - Z * (16 / cth);
                pl.Add(Plate(W(oR), Y * sy, Z, new double[] { 0, 0, 150, 150 * SLP, 150, 150 * SLP - 18, 20, -150, 0, -150 }, 12, true, soP));
                // column ribs −16 between the flanges, in the table plane (both sides of the web)
                var oCR = RP(cx, yf) - Z * (hb + 0.3);
                foreach (var sx in new[] { 1.0, -1.0 }) pl.Add(Plate(W(oCR), -eu, tv, Rect(sx > 0 ? 5.1 : -150, -374.0 / cth, sx > 0 ? 150 : -5.1, -14.3 / cth), 16, false, soP));
                // fish plate −12 (−X side of the web) and L100x7 (+X side): 150 / 100 from the column face, 0.8 h high, from 40 under the beam top
                double zTop = Roof(yf + sy * 75) - tf - 30, hh = Math.Round(0.8 * h / 10) * 10 - 60;
                pl.Add(Box(new XYZ(cx - tw / 2 - 0.3 - 6, yf + sy * (0.3 + 75), zTop - hh / 2), Y, Z, 150, hh, 12, soP));
                pl.Add(Box(new XYZ(cx + tw / 2 + 0.3 + 3.5, yf + sy * (0.3 + 50), zTop - hh / 2), Y, Z, 100, hh, 7, soP));
                pl.Add(Box(new XYZ(cx + tw / 2 + 0.3 + 50, yf + sy * (0.3 + 3.5), zTop - hh / 2), X, Z, 100, hh, 7, soP));
                int nb = b1 ? 4 : 2; for (int k = 0; k < nb; k++)
                { double zb = zTop - 40 - k * (hh - 80) / Math.Max(nb - 1, 1); double grip = 12 + tw + 7;
                  bo.AddRange(Bolt(W(new XYZ(cx - tw / 2 - 12.3, yf + sy * 75.3, zb)), X, 24, grip, BoltLen(24, grip), soB)); }
                // welds: cap ↔ column (shop, the column contour), cap ↔ beam top flange (field, both edges), table ↔ column (shop), bottom flange ↔ table (field)
                foreach (var sx in new[] { 1.0, -1.0 })
                { we.Add(Weld(W(RP(cx + sx * bf / 2, yf + sy * 20.3)), X * sx, -Z, tv, 6, 280, soW));
                  we.Add(Weld(W(RP(cx + sx * bf / 2, yf + sy * 20.3) - Z * (hb + 0.3)), X * sx, Z, tv, 6, 280, soW)); }
                foreach (var sv in new[] { 1.0, -1.0 }) we.Add(Weld(W(RP(cx - 150, cy + sv * 194.0) - Z * 0.3), Y * sv, -Z, X, 6, 300, soW));
                // shop welds to the column flange (expert 11.11): table (under its edge), rib, fish plate −12, L100x7; column ribs to the web
                { var tb0 = RP(cx - 150, yf) - Z * (hb + 0.3 + 16 / cth); we.Add(Weld(W(tb0 + Y * sy * 0.3), Y * sy, -Z, X, 6, 300, soW));
                  we.Add(Weld(W(new XYZ(cx - tw / 2 - 12.3, yf + sy * 0.3, zTop - hh)), -X, Y * sy, Z, 6, hh, soW));
                  we.Add(Weld(W(new XYZ(cx + tw / 2 + 100.3, yf + sy * 7.3, zTop - hh)), X, Y * sy, Z, 6, hh, soW));
                  we.Add(Weld(W(new XYZ(cx + tw / 2 + 0.3, yf + sy * 100.3, zTop - hh)), X, Y * sy, Z, 6, hh, soW));
                  foreach (var sx in new[] { 1.0, -1.0 }) we.Add(Weld(W(RP(cx + sx * 4.75, cy - 180) - Z * (hb + 0.3)), X * sx, -Z, Y, 6, 360, soW)); }
                C("узел 1 " + b.Mk);
            }
            var cl = new List<GeometryObject>(); foreach (var s in pl.OfType<Solid>()) Add(cl, s, true);
            DS(d, BuiltInCategory.OST_StructConnections, "узел 1", "Узел 1 (жёсткий): оголовок −16 С345, столик −16, рёбра колонны −16, ребро столика −12, рыбка −12, L100x7 С255", cl);
            DS(d, BuiltInCategory.OST_StructConnectionBolts, "узел 1", "Узел 1: болты М24 кл. 8.8 (Б1 ×4, Б2 ×2)", bo);
            PW.Add(Tuple.Create("узел 1", "шов узел 1", we));
        }
        // ================= Узел 2: ridge butt joint (shop)
        {
            var we = new List<GeometryObject>();
            foreach (var b in BB.Where(q => q.A.Y < 5000 || q.B.Y < 5000))
            {
                double x = b.A.X, h = b.Mk == "Б1" ? 492 : 296, bf = b.Mk == "Б1" ? 199 : 140;
                double zr = Roof(6000); we.Add(Weld(W(new XYZ(x - bf / 2, 6000, zr)), Y, Z, X, 4, bf, soW)); we.Add(Weld(W(new XYZ(x - bf / 2, 6000, zr)), -Y, Z, X, 4, bf, soW));
                double zbr = zr - h / Math.Cos(Math.Atan(SLP)) - 0.5; we.Add(Weld(W(new XYZ(x - bf / 2, 6000, zbr)), Y, -Z, X, 4, bf, soW)); we.Add(Weld(W(new XYZ(x - bf / 2, 6000, zbr)), -Y, -Z, X, 4, bf, soW));
                C("ridge " + b.Mk);
            }
            PW.Add(Tuple.Create("узел 2", "Узел 2: стыковой заводской шов балки в коньке (Б1/Б2 — одна отправочная марка)", we));
        }
        // ================= Узел 8: К2 top
        {
            var pl = new List<GeometryObject>(); var bo = new List<GeometryObject>(); var we = new List<GeometryObject>();
            foreach (var c in K2)
            {
                double zt = c.B.Z; var o = new XYZ(c.A.X, c.A.Y, zt);
                {   // cap −16 under the Б2 ridge: flat on the post, its top follows the Λ of the beam bottom (expert 11.11: no gap at the edges)
                    double hb2 = 296 / Math.Cos(Math.Atan(SLP)); Func<double, double> tt = yy => (Roof(c.A.Y + yy) - hb2 - 0.3) - zt;
                    pl.Add(Plate(P(c.A.X, c.A.Y, zt), Y, Z, new double[] { -135, 0, 135, 0, 135, tt(135), 0, tt(0), -135, tt(-135) }, 270, true, soP)); }
                foreach (var sx in new[] { 1.0, -1.0 }) { we.Add(Weld(W(o + new XYZ(sx * 125, -125, 0)), X * sx, -Z, Y, 6, 250, soW)); we.Add(Weld(W(o + new XYZ(-125, sx * 125, 0)), Y * sx, -Z, X, 6, 250, soW)); }
                foreach (var sx in new[] { -45.0, 45 }) foreach (var syy in new[] { -90.0, 90 })
                { double grip = 16 + 8.5 + 1.3; bo.AddRange(Bolt(W(new XYZ(c.A.X + sx, c.A.Y + syy, zt)), Z, 16, grip, BoltLen(16, grip), soB)); }
                // Б2 stiffeners −8 over the support, both sides of the web, y = 6000 ± 90 (plates cleaned against the beam)
                foreach (var syy in new[] { -110.0, 110 }) foreach (var sx in new[] { 1.0, -1.0 })
                {
                    double y = 6000 + syy, zt2 = Roof(y) - 8.5 - 0.3, zb = Roof(y) - 296 + 8.5 + 0.3;
                    pl.Add(Plate(P(c.A.X + sx * 3.2, y - 4, zb), X * sx, Z, Rect(0, 0, 62, zt2 - zb), 8, false, soP));
                }
                C("К2 top");
            }
            var cl = new List<GeometryObject>(); foreach (var s in pl.OfType<Solid>()) Add(cl, s, true);
            DS(d, BuiltInCategory.OST_StructConnections, "узел 8", "Узел 8 (шарнир): оголовок К2 −16×270×270 С345, рёбра Б2 −8 С245", cl);
            DS(d, BuiltInCategory.OST_StructConnectionBolts, "узел 8", "Узел 8: болты М16 кл. 8.8 ×4", bo);
            PW.Add(Tuple.Create("узел 8", "шов узел 8", we));
        }
        // ================= Узел 6: purlin stand plates
        {
            var pl = new List<GeometryObject>(); var bo = new List<GeometryObject>(); var we = new List<GeometryObject>();
            var xs = Enumerable.Range(0, 10).Select(i => 6000.0 * i);
            foreach (var y in new[] { 0.0, 3000, 6000, 9000, 12000 })
                foreach (var x in xs)
                {
                    var n = RoofN(y); var f = Math.Abs(y - 6000) < 1 || y < 6000 ? Y : -Y;   // flanges towards the ridge (ridge line: +Y)
                    var fr = n.CrossProduct(X).Normalize(); if (fr.DotProduct(f) < 0) fr = -fr;  // in the roof plane, ⟂ X, towards the flanges
                    var basePt = new XYZ(x, y, Roof(y) + 0.3 + ((Math.Abs(y) < 1 || Math.Abs(y - 12000) < 1) ? 16 : 0));
                    var webFace = basePt - fr * 40.3;                                          // outside face of the purlin web
                    var o = webFace - X * 110;
                    if (X.CrossProduct(n).DotProduct(fr) < 0) pl.Add(Plate(W(o), X, n, Rect(0, 0, 220, 200), 10, false, soP)); else pl.Add(Plate(W(o), n, X, Rect(0, 0, 200, 220), 10, false, soP));
                    we.Add(Weld(W(o - fr * 10), -fr, -n * -1, X, 5, 220, soW));
                    foreach (var sx in new[] { -1.0, 1.0 })
                    {
                        bool has = (sx < 0 && x > 1) || (sx > 0 && x < 53999) || x < 1 || x > 53999;
                        if (!has) continue;
                        foreach (var hz in new[] { 70.0, 160 })
                        { var hp = webFace + X * (sx * 50) + n * hz - fr * 10; double grip = 10 + 5; bo.AddRange(Bolt(W(hp), fr, 16, grip, BoltLen(16, grip), soB)); }
                    }
                    C("purlin support");
                }
            var cl = new List<GeometryObject>(); foreach (var s in pl.OfType<Solid>()) Add(cl, s, true);
            DS(d, BuiltInCategory.OST_StructConnections, "узел 6", "Узел 6 (шарнир): опорный столик прогона −10×220×200 С255", cl);
            DS(d, BuiltInCategory.OST_StructConnectionBolts, "узел 6", "Узел 6: болты М16 кл. 8.8, 2 на конец прогона", bo);
            PW.Add(Tuple.Create("узел 6", "шов узел 6", we));
        }
        // ================= tube ends: СВ1, Р1, ГС1
        var ends = new List<TEnd>();
        foreach (var m in mem.Where(q => q.Mk == "СВ1" || q.Mk == "Р1" || q.Mk == "ГС1"))
            for (int k = 0; k < 2; k++)
            {
                var pe = k == 0 ? m.A : m.B; var po = k == 0 ? m.B : m.A; var u = (pe - po).Normalize();
                var te = new TEnd { M = m, Pe = pe, U = u, B = 100 };
                if (m.Mk == "ГС1") { te.N = RoofN((m.A.Y + m.B.Y) / 2); }
                else te.N = Y;
                te.S = te.N.CrossProduct(u).Normalize();
                // node kind
                double nx = Math.Round(pe.X / 3000.0) * 3000, ny = Math.Round(pe.Y / 3000.0) * 3000;
                bool onAx = Math.Abs(nx / 6000.0 - Math.Round(nx / 6000.0)) < 1e-6;
                if (m.Mk == "Р1") te.Kind = "р1";
                else if (m.Mk == "СВ1") te.Kind = Math.Abs(pe.X - Math.Round(pe.X / 6000.0) * 6000) < 600 ? (pe.Z < 1500 ? "св-база" : "св-верх") : "св-р1";
                else
                {
                    // ГС1: node point = the nearest 3 m grid node in plan
                    var others = mem.Where(q => q.Mk == "ГС1" && q != m).ToList();
                    bool through = others.Any(q => { var a = q.A; var b = q.B; var v = b - a; double L = v.GetLength(); var w = new XYZ(nx, ny, 0) - new XYZ(a.X, a.Y, 0); var vv = new XYZ(v.X, v.Y, 0);
                        double tt = w.DotProduct(vv) / vv.DotProduct(vv); if (tt < 0.1 || tt > 0.9) return false; var pp = new XYZ(a.X, a.Y, 0) + vv * tt; return (pp - new XYZ(nx, ny, 0)).GetLength() < 5; });
                    if (through) te.Kind = "гс-крест";
                    else if (onAx && (Math.Abs(ny) < 1 || Math.Abs(ny - 12000) < 1)) te.Kind = "гс-кол";
                    else if (onAx) te.Kind = "гс-балка";
                    else te.Kind = "гс-прогон";
                }
                te.Key = Math.Round(Math.Round(pe.X / 3000.0) * 3000) + "|" + Math.Round(Math.Round(pe.Y / 3000.0) * 3000) + "|" + (m.Mk == "ГС1" ? "r" : Math.Round(pe.Z / 100.0).ToString()) + "|" + te.Kind;
                ends.Add(te);
            }
        sb.AppendLine("tube ends " + ends.Count + ": " + string.Join(", ", ends.GroupBy(q => q.Kind).Select(g => g.Key + " " + g.Count())));
        var plC = new List<GeometryObject>(); var weC = new List<GeometryObject>();   // caps (all tube ends)
        var pl3 = new List<GeometryObject>(); var bo3 = new List<GeometryObject>(); var we3 = new List<GeometryObject>();  // Р1
        var pl4 = new List<GeometryObject>(); var bo4 = new List<GeometryObject>(); var we4 = new List<GeometryObject>();  // СВ1
        var gus4 = new List<GeometryObject>(); var gus5 = new List<GeometryObject>();
        var pl5 = new List<GeometryObject>(); var bo5 = new List<GeometryObject>(); var we5 = new List<GeometryObject>();  // ГС1
        // ---- Р1 ↔ К1: gusset −10 centred in the row plane, through the Р1 slot
        foreach (var te in ends.Where(q => q.Kind == "р1"))
        {
            var pe = te.Pe; double cx = Math.Round(pe.X / 6000.0) * 6000; double sx = pe.X > cx ? 1 : -1; double yr = pe.Y;
            var g = Plate(P(cx + sx * 5.05, yr + 5 * sx, ZR1 - 100), X * sx, Z, Rect(0, 0, 380, 200), 10, false, soP);
            // Р1 is an obstacle already (frame) → the gusset gets the slot automatically
            Add(pl3, g, true);
            foreach (var sz in new[] { 1.0, -1.0 }) foreach (var syy in new[] { 1.0, -1.0 })
                we3.Add(Weld(P(cx + sx * 180, yr + syy * 5, ZR1 + sz * 50), Y * syy, Z * sz, X * sx, 6, 200, soW));
            we3.Add(Weld(P(cx + sx * 5.05, yr - 5, ZR1 - 100), X * sx, Y * -1, Z, 6, 200, soW)); we3.Add(Weld(P(cx + sx * 5.05, yr + 5, ZR1 - 100), X * sx, Y, Z, 6, 200, soW));
            C("Р1 end");
        }
        // ---- generic insert (tee) for СВ1 / ГС1 ends; returns the insert outline points (world mm) for the gusset hull
        Func<TEnd, double, List<XYZ>> Insert = (te, off) => {
            // off: offset of the flat plate centre from the tube axis along N (ГС1 — under the gusset)
            var c0 = te.Pe + te.U * 8.0 + te.N * off; double L = 150, w = 130;
            var o = c0 - te.S * (w / 2) - te.N * 4;
            var plates = te.M.Mk == "СВ1" ? pl4 : pl5; var bolts = te.M.Mk == "СВ1" ? bo4 : bo5; var welds = te.M.Mk == "СВ1" ? we4 : we5;
            // u × s = −n → the flat thickness goes −N: start the plate at +4 so it is centred
            plates.Add(Plate(W(c0 - te.S * (w / 2) + te.N * 4), te.S, te.U, Rect(0, 0, w, L), 8, false, soP));
            // rib −8 on the free side (−N), along the axis, 40 high, welded to the cap and the flat
            plates.Add(Plate(W(c0 - te.N * 4 - te.S * 4), te.U, -te.N, Rect(0, 0, L - 20, 40), 8, false, soP));
            welds.Add(Weld(W(c0 + te.N * 4 - te.S * (w / 2)), te.N, -te.U, te.S, 5, w, soW));
            // 2 М16 side by side at 0.65 L, ±40 from the axis
            foreach (var ss in new[] { -40.0, 40 }) { var hp = c0 + te.U * (0.65 * L) + te.S * ss + te.N * 4; double grip = 8 + 10; bolts.AddRange(Bolt(W(hp + te.N * 10), -te.N, 16, grip, BoltLen(16, grip), soB)); }
            return new List<XYZ> { c0 - te.S * (w / 2), c0 + te.S * (w / 2), c0 + te.U * L - te.S * (w / 2), c0 + te.U * L + te.S * (w / 2) }; };
        // ---- caps on every tube end (−8, b + 20) + welds round the tube
        foreach (var te in ends)
        {
            var c0 = te.Pe + te.U * 4.0; var s2 = te.N.CrossProduct(te.U).Normalize(); var n2 = te.U.CrossProduct(s2).Normalize();
            var cap = Box(c0, s2, n2, te.B + 20, te.B + 20, 8, soP);
            plC.Add(cap);
            foreach (var a in new[] { s2, -s2, n2, -n2 }) { var b2 = a.CrossProduct(te.U).Normalize(); weC.Add(Weld(W(te.Pe + a * 50 - b2 * 50), a, -te.U, b2, 4, 100, soW)); }
        }
        // ---- СВ1: gussets on the +N side of the inserts (t 10), one per node
        foreach (var grp in ends.Where(q => q.M.Mk == "СВ1").GroupBy(q => q.Key))
        {
            var pts = new List<XYZ>(); foreach (var te in grp) pts.AddRange(Insert(te, 0));
            var f = grp.First(); double yr = f.Pe.Y; var o = new XYZ(0, yr + 4.3, 0);
            if (f.Kind != "св-р1")
            {
                double cx = Math.Round(f.Pe.X / 6000.0) * 6000; double sx = f.Pe.X > cx ? 1 : -1; double zmin = pts.Min(p => p.Z), zmax = pts.Max(p => p.Z);
                pts.Add(new XYZ(cx + sx * 5.05, yr, zmin - 40)); pts.Add(new XYZ(cx + sx * 5.05, yr, zmax + 40));
                if (f.Kind == "св-база") { pts.Add(new XYZ(cx + sx * 5.05, yr, -369.7)); pts.Add(new XYZ(pts.Max(p => sx * p.X) * sx, yr, -369.7)); }
                we4.Add(Weld(P(cx + sx * 4.75, yr + 4, zmin - 40), X * sx, Y, Z, 6, zmax - zmin + 80, soW)); we4.Add(Weld(P(cx + sx * 4.75, yr + 14, zmin - 40), X * sx, -Y, Z, 6, zmax - zmin + 80, soW));
            }
            else
            {   // узел 9: the gusset runs to and through Р1 (slot), welded to its top and bottom faces
                double nx = Math.Round(f.Pe.X / 3000.0) * 3000;
                foreach (var dx in new[] { -260.0, 260 }) foreach (var dz in new[] { -60.0, 60 }) pts.Add(new XYZ(nx + dx, yr, ZR1 + dz));
                foreach (var sz in new[] { 1.0, -1.0 }) foreach (var syy in new[] { 4.3, 14.3 }) we4.Add(Weld(P(nx - 260, yr + syy, ZR1 + sz * 50), Y * (syy < 10 ? -1 : 1), Z * sz, X, 6, 520, soW));
            }
            // plane y = yr + 4 … +14: eu = Z, ev = X → eu × ev = Y
            var g = HullPlate(o, Z, X, pts, 10, soP);
            Add(gus4, g, true); C("СВ1 node " + f.Kind);
        }
        // ---- ГС1: gusset plane under the support; inserts just under the gusset
        foreach (var grp in ends.Where(q => q.M.Mk == "ГС1" && q.Kind != "гс-крест").GroupBy(q => q.Key + (q.Kind == "гс-балка" ? "|" + Math.Sign(q.Pe.X - Math.Round(q.Pe.X / 6000.0) * 6000) : "")))
        {
            var f = grp.First(); var n = f.N; double ny = Math.Round(f.Pe.Y / 3000.0) * 3000, nx = Math.Round(f.Pe.X / 3000.0) * 3000;
            // depth of the gusset top under the roof plane
            double top;
            if (f.Kind == "гс-прогон") top = 0.3;
            else top = ((Math.Abs(nx) < 1 || Math.Abs(nx - 54000) < 1) ? 8.5 : 12.0) + 0.3;
            var pts = new List<XYZ>();
            foreach (var te in grp)
            {
                // axis of the tube is 52 under the roof; flat top = gusset bottom → offset along N from the axis
                double off = 56.0 - (top + 10) - 4.3;
                pts.AddRange(Insert(te, off));
            }
            var rp = new XYZ(nx, ny, Roof(ny)) - n * top;                     // a point of the gusset top plane
            if (f.Kind == "гс-балка" || f.Kind == "гс-кол")
            {   // weld edge along the beam web (x = nx ± tw/2) / column flange
                double sx = Math.Sign(f.Pe.X - nx); if (sx == 0) sx = 1; double tw = (Math.Abs(nx) < 1 || Math.Abs(nx - 54000) < 1) ? 5.8 : 8.8;
                double ymn = pts.Min(p => p.Y), ymx = pts.Max(p => p.Y);
                pts.Add(new XYZ(nx + sx * (tw / 2 + 0.3), ymn, 0)); pts.Add(new XYZ(nx + sx * (tw / 2 + 0.3), ymx, 0));
                if (f.Kind == "гс-кол") { double yf = ny < 6000 ? ny + 194.3 : ny - 194.3; pts.Add(new XYZ(nx + sx * 140, yf, 0)); pts.Add(new XYZ(nx - sx * 140, yf, 0)); }
                we5.Add(Weld(W(new XYZ(nx + sx * tw / 2, ymn, Roof(ny) - top - 10)), X * sx, -Z, Y, 5, ymx - ymn, soW));
            }
            // project the hull onto the gusset plane: plane through rp with normal n; eu = X, ev = n × X (in plane)
            var ev = n.CrossProduct(X).Normalize(); var eu = X;
            var prj = pts.Select(p => { var q = new XYZ(p.X, p.Y, Roof(p.Y)) - n * top; return q; }).ToList();
            // thickness must go −n: eu × ev = X × (n × X) = n → build on the plane shifted by −10
            var g = HullPlate(rp - n * 10, eu, ev, prj.Select(p => p - n * 10).ToList(), 10, soP);
            Add(gus5, g, true); C("ГС1 node " + f.Kind);
            if (f.Kind == "гс-прогон" && (Math.Abs(ny) < 1 || Math.Abs(ny - 12000) < 1)) { var g2 = HullPlate(rp, eu, ev, prj.Select(p => p).ToList(), 16, soP); Add(gus5, g2, true); C("ГС1 filler −16"); }
        }
        // ---- ГС1 crossing: the cut diagonal's cap welded to the through diagonal (only the cap — done above) + a weld bead
        foreach (var te in ends.Where(q => q.Kind == "гс-крест")) { we5.Add(Weld(W(te.Pe + te.U * 8 - te.S * 60), te.U, te.N, te.S, 5, 120, soW)); C("ГС1 crossing end"); }
        var capsClean = new List<GeometryObject>(); foreach (var s in plC.OfType<Solid>()) Add(capsClean, s, true);
        DS(d, BuiltInCategory.OST_StructConnections, "заглушки", "Заглушки труб ПЛ −8×120×120 С255", capsClean);
        PW.Add(Tuple.Create("заглушки", "шов заглушки", weC));
        var c3 = new List<GeometryObject>(); foreach (var s in pl3.OfType<Solid>()) c3.Add(s);
        DS(d, BuiltInCategory.OST_StructConnections, "узел 3", "Узел 3 (шарнир): фасонка Р1 −10×380×200 С255 через паз Р1", c3);
        PW.Add(Tuple.Create("узел 3", "шов узел 3 (монтажный)", we3));
        var c4 = new List<GeometryObject>(gus4); foreach (var s in pl4.Where(q => q != null).OfType<Solid>()) { double v0 = s.Volume / (MM * MM * MM); int n0 = c4.Count; Add(c4, s, true); if (Math.Abs(v0 - 41600) < 500) { double v1 = c4.Count > n0 ? ((Solid)c4[c4.Count - 1]).Volume / (MM * MM * MM) : 0; if (v1 < 0.95 * v0) { var cc = s.ComputeCentroid() / MM; sb.AppendLine("  rib СВ1 clipped @" + Math.Round(cc.X) + "," + Math.Round(cc.Y) + "," + Math.Round(cc.Z) + " " + Math.Round(v1)); } } }
        DS(d, BuiltInCategory.OST_StructConnections, "узел 4", "Узел 4 (шарнир): фасонки СВ1 −10 С255, вкладыши −8 (тавр) С255", c4);
        DS(d, BuiltInCategory.OST_StructConnectionBolts, "узел 4", "Узел 4: болты М16 кл. 8.8, 2 на конец связи", bo4);
        PW.Add(Tuple.Create("узел 4", "шов узел 4", we4));
        var c5 = new List<GeometryObject>(gus5); foreach (var s in pl5.Where(q => q != null).OfType<Solid>()) { double v0 = s.Volume / (MM * MM * MM); int n0 = c5.Count; Add(c5, s, true); if (Math.Abs(v0 - 41600) < 500) { double v1 = c5.Count > n0 ? ((Solid)c5[c5.Count - 1]).Volume / (MM * MM * MM) : 0; if (v1 < 0.95 * v0) { var cc = s.ComputeCentroid() / MM; sb.AppendLine("  rib ГС1 clipped @" + Math.Round(cc.X) + "," + Math.Round(cc.Y) + "," + Math.Round(cc.Z) + " " + Math.Round(v1)); } } }
        DS(d, BuiltInCategory.OST_StructConnections, "узел 5", "Узел 5 (шарнир): фасонки ГС1 −10 С255, вкладыши −8 (тавр) С255", c5);
        DS(d, BuiltInCategory.OST_StructConnectionBolts, "узел 5", "Узел 5: болты М16 кл. 8.8, 2 на конец связи", bo5);
        PW.Add(Tuple.Create("узел 5", "шов узел 5", we5));
        // ================= Узел 7: ПБ1 hangers, splices, stops
        {
            var pl = new List<GeometryObject>(); var bo = new List<GeometryObject>(); var we = new List<GeometryObject>();
            foreach (var y in new[] { 1500.0, 10500 })
                for (int i = 0; i <= 8; i++)
                {
                    double x = 6000.0 * i; double h = (i == 0) ? 296 : 492, bfw = (i == 0) ? 140 : 199;
                    double zb = Math.Min(Roof(y - 100), Roof(y + 100)) - h / Math.Cos(Math.Atan(0.025)) - 0.3;  // under the beam bottom
                    double ztopPB = 6550.3;
                    bool pack = zb - ztopPB < 150;   // Б1 low over the crane path: packing plates −t20 bolted through (АР geometry)
                    if (pack) { double hbB = h / Math.Cos(Math.Atan(SLP)); double z1 = Roof(y - 100) - hbB - 0.3, z2 = Roof(y + 100) - hbB - 0.3;   // wedge packing: flat on ПБ1, top on the 11 % Б1 bottom
                      pl.Add(Plate(P(x, y, ztopPB), Y, Z, new double[] { -100, 0, 100, 0, 100, z2 - ztopPB, -100, z1 - ztopPB }, 200, true, soP));
                      foreach (var sx2 in new[] { -60.0, 60 }) foreach (var sy3 in new[] { -40.0, 40 }) { double grip = 15 + (zb - ztopPB) + 12; bo.AddRange(Bolt(P(x + sx2, y + sy3, ztopPB - 15), Z, 20, grip, BoltLen(20, grip), soB)); } }
                    else {
                    pl.Add(Box(new XYZ(x, y, zb - 5), X, Y, 200, 200, 10, soP));
                    pl.Add(Box(new XYZ(x, y, ztopPB + 5), X, Y, 200, 200, 10, soP)); }
                    double zl0 = ztopPB + 10, zl1 = zb - 10;
                    if (!pack) foreach (var sy2 in new[] { 1.0, -1.0 })
                    {   // L50x5 legs: one leg in the X Z plane at y ± 45, the other along Y
                        pl.Add(Box(new XYZ(x, y + sy2 * 47.5, (zl0 + zl1) / 2), X, Z, 50, zl1 - zl0, 5, soP));
                        pl.Add(Box(new XYZ(x - 22.5, y + sy2 * 25, (zl0 + zl1) / 2), Y, Z, 40, zl1 - zl0, 5, soP));
                    }
                    if (!pack) foreach (var sx in new[] { -60.0, 60 }) foreach (var syy in new[] { -40.0, 40 })
                    { double grip = 10 + 15; bo.AddRange(Bolt(P(x + sx, y + syy, ztopPB + 10), -Z, 16, grip, BoltLen(16, grip), soB)); }
                    we.Add(Weld(P(x - 100, y - 100, zb), -Y, Z * -1, X, 5, 200, soW));
                    // web splice −8 both sides at the joint of two ПБ1 pieces
                    if (i > 0 && i < 8)
                        foreach (var syy in new[] { 1.0, -1.0 })
                        {
                            pl.Add(Box(new XYZ(x, y + syy * (4.5 + 4.3), 6400), X, Z, 200, 180, 8, soP));
                            foreach (var sx in new[] { -50.0, 50 }) foreach (var dz in new[] { -50.0, 50 }) if (syy > 0) { double grip = 9 + 16.6; bo.AddRange(Bolt(P(x + sx, y + 12.8, 6400 + dz), -Y, 16, grip, BoltLen(16, grip), soB)); }
                        }
                    if (i == 0 || i == 8) { double xe = i == 0 ? 0.0 : 48000.0; pl.Add(Box(new XYZ(xe + (i == 0 ? 5 : -5) * 1.0, y, 6250 - 50), Y, Z, 130, 100, 10, soP)); }
                    C("ПБ1 hanger");
                }
            var cl = new List<GeometryObject>(); foreach (var s in pl.Where(q => q != null).OfType<Solid>()) Add(cl, s, true);
            DS(d, BuiltInCategory.OST_StructConnections, "узел 7", "Узел 7 (шарнир): подвеска ПБ1 к Б1 — прокладки −t20 200×200 + 4 М20 (у торцов Б2 — пластины −10 и Т1 2L50x5), накладки стенки −8×200×180, упор −10 С255", cl);
            DS(d, BuiltInCategory.OST_StructConnectionBolts, "узел 7", "Узел 7: болты М20 кл. 8.8 (прокладки), М16 (накладки стенки)", bo);
            PW.Add(Tuple.Create("узел 7", "шов узел 7", we));
        }
        // ================= Узел 10: фахверк — Рф1 ↔ column: plate −8 welded to the column + 2 М16 through the channel web; Рф1 ↔ post (segment end at a
        // post): weld; posts Ст2 / Ст3: end plates −8 under / over the ригели, door posts on a plate −10 + 2 анкера М12 (rule 9)
        {
            var pl = new List<GeometryObject>(); var bo = new List<GeometryObject>(); var we = new List<GeometryObject>(); var caps9 = new List<GeometryObject>();
            foreach (var m in mem.Where(q => q.Mk == "Рф1"))
            {
                var u = (m.B - m.A).Normalize(); bool row = Math.Abs(u.X) > 0.9;
                var nF = row ? Y * Math.Sign(m.A.Y - 6000) : X * Math.Sign(m.A.X - 27000);   // outward
                foreach (var pr in new[] { Tuple.Create(m.A, -u), Tuple.Create(m.B, u) })
                {
                    var pe = pr.Item1; var uo = pr.Item2;
                    double uu = row ? pe.X : pe.Y; double axn = Math.Round(uu / 6000.0) * 6000; bool atCol = Math.Abs(uu - axn) < 215;
                    if (!atCol) { foreach (var zz in new[] { 80.0, -80.0 }) we.Add(Weld(W(pe + Z * zz - nF * 40), uo, -nF, Z * Math.Sign(zz) * -1, 4, 40, soW)); continue; }
                    // plate −8 in the web plane (behind the web, toward the inside), from the column face across the 10 mm gap, 140 high
                    var webFace = pe - nF * 40;                                   // channel web: the outer face of the box
                    var c0 = webFace + uo * (10 - 60) - nF * 4.3;
                    pl.Add(Box(c0, uo, Z, 120, 140, 8, soP));
                    foreach (var zz in new[] { -35.0, 35 }) { var hp = webFace + uo * (-25) + Z * zz - nF * 8.3; double grip = 8 + 5; bo.AddRange(Bolt(W(hp), nF, 16, grip, BoltLen(16, grip), soB)); }
                    we.Add(Weld(W(webFace + uo * 10 - nF * 8.3 - Z * 70), uo, -nF, Z, 5, 140, soW));
                }
                C("Рф1");
            }
            foreach (var m in mem.Where(q => q.Mk == "Ст2" || q.Mk == "Ст3"))
            {
                var bot = m.A.Z < m.B.Z ? m.A : m.B; var top = m.A.Z < m.B.Z ? m.B : m.A; double w = m.Mk == "Ст3" ? 120 : 80;
                foreach (var e0 in new[] { bot, top }) { bool up = e0 == top;
                    if (!(e0 == bot && bot.Z < 20)) caps9.Add(Box(e0 + Z * (up ? -4.3 : 4.3), X, Y, w, w, 8, soP));          // end plate inside the tube end, welded to the ригель
                    foreach (var a in new[] { X, -X, Y, -Y }) { var b2 = a.CrossProduct(Z).Normalize(); we.Add(Weld(W(e0 + a * (w / 2) - b2 * (w / 2)), a, up ? -Z : Z, b2, 4, w, soW)); } }
                if (bot.Z < 20)
                {   // door / gate post on the floor slab: plate −10 220×220, 2 анкера М12
                    pl.Add(Box(new XYZ(bot.X, bot.Y, 5), X, Y, 220, 220, 10, soP));
                    bool row = Math.Abs(bot.Y) < 500 || Math.Abs(bot.Y - 12000) < 500; var along = row ? X : Y;
                    foreach (var sgn in new[] { -1.0, 1.0 }) { var c = new XYZ(bot.X, bot.Y, 10) + along * (sgn * 85); bo.Add(Prism(W(c - Z * 160), Z, 12, 175, false, soB)); bo.Add(Prism(W(c), Z, 18, 10, true, soB)); }
                }
                C(m.Mk);
            }
            var cl = new List<GeometryObject>(); foreach (var s in pl.OfType<Solid>()) Add(cl, s, true);
            foreach (var s in caps9.OfType<Solid>()) Add(cl, s, true);
            DS(d, BuiltInCategory.OST_StructConnections, "узел 9", "Узел 10 (шарнир): фахверк — пластины Рф1 −8×120×140 + 2 М16, торцевые пластины стоек −8, опорные пластины стоек −10×220×220 С255", cl);
            DS(d, BuiltInCategory.OST_StructConnectionBolts, "узел 9", "Узел 10: болты М16 кл. 8.8 (Рф1), анкеры М12 (стойки Ст3)", bo);
            PW.Add(Tuple.Create("узел 9", "шов узел 10", we));
        }
        // welds last: cleaned against the frame, the bases, every plate and the welds made before them
        int wn = 0; foreach (var pw in PW) { var cl = new List<GeometryObject>(); foreach (var s in pw.Item3.OfType<Solid>()) Add(cl, s, true); wn += cl.Count; DS(d, BuiltInCategory.OST_StructConnectionWelds, pw.Item1, pw.Item2, cl); }
        sb.AppendLine("welds kept " + wn);
        t.Commit();
    }
    sb.AppendLine(string.Join("\n", cnt.OrderBy(k => k.Key).Select(k => k.Key + ": " + k.Value)));
    return sb.ToString();
}
