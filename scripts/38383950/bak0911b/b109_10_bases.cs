// Завод В109 Цех Блок 1: column bases. Run with -Lib b109_lib.cs.
// 09.11.2026 — by the user's own nodes («КМ Чертеж узелдер.dwg», sheets 13–18 «База колонн Б1…Б6»), the Tekla / album bases are dropped:
//   plate bottom −0.400 on 50 grout (MasterFlow 928) over the foundation −0.450; ribs −12 С245 h310 (top −0.050), straight slope to the plate edge;
//   4 anchors 09Г2С in open slots, washer welded to the plate, 2 nuts on top + a levelling nut under the plate.
//  Б1 К1 (no bracing) / Б2 К1 (braced bays 9-10, 19-20; the СВ1 gusset is in b109_11): plate −40 С345 700×950, М42 at (±260; ±385), slots 60, washer −20×120×120.
//  Б3 К2 60Ш3: plate −40 700×960, М42 at (±260; ±390).        Б5 СФ 40Ш2: plate −40 700×750, М30 at (±260; ±285), slots 40.
//  I-column ribs: two long ribs at the flange tips (u ±150…±162) along the depth over the whole plate, flange-extension ribs in the flange planes to the plate edge.
//  Б4 К3 box: plate −40 800×800, М42 at (±290; ±290), ribs in the wall planes to the plate edges (8 pieces).
//  Б6 СФ1 □200: plate −30 550×550, М24 at (±190; ±190) in round holes, washer −20×100×100, 2 ribs per face at ±75 (8 pieces).
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"D:\Бекасыл КЖ КМ\Завод_В109_КМ\_авто\revit\_b109_10.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder();
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt")); sb.Append(Bases(nd)); nd.Save(); sb.AppendLine("saved"); }
  catch (Exception ex) { sb.AppendLine("ERR " + ex); }
  System.IO.File.WriteAllText(log, sb.ToString()); };
uiapp.Idling += hnd;
return "queued";
}

static Solid PlateW(XYZ o, XYZ a, XYZ b, double[] uv, double t, XYZ want, SolidOptions so) {
    if (a.CrossProduct(b).DotProduct(want) > 0) return Plate(o, a, b, uv, t, false, so);
    var sw = new double[uv.Length]; for (int i = 0; i < uv.Length; i += 2) { sw[i] = uv[i + 1]; sw[i + 1] = uv[i]; } return Plate(o, b, a, sw, t, false, so); }
const double ZP = -400;   // plate bottom
static void Anchor(Func<double, double, double, XYZ> Q, double ax, double ay, double z0, int dia, double w, double tw,
    List<GeometryObject> plates, List<GeometryObject> bolts, List<GeometryObject> welds, SolidOptions soP, SolidOptions soB, SolidOptions soW)
{
    XYZ X = XYZ.BasisX, Y = XYZ.BasisY, Z = XYZ.BasisZ; var bd = BoltDims(dia); double h = w / 2;
    plates.Add(Plate(Q(ax - h, ay - h, z0), X, Y, Rect(0, 0, w, w), tw, false, soP));
    welds.Add(Weld(Q(ax - h, ay - h, z0), -Y, Z, X, 6, w, soW)); welds.Add(Weld(Q(ax - h, ay + h, z0), Y, Z, X, 6, w, soW));
    welds.Add(Weld(Q(ax - h, ay - h, z0), -X, Z, Y, 6, w, soW)); welds.Add(Weld(Q(ax + h, ay - h, z0), X, Z, Y, 6, w, soW));
    bolts.Add(Prism(Q(ax, ay, ZP - 1000), Z, dia, 1000 + (z0 - ZP) + tw + bd[3] + 2 * bd[1] + 0.3 * dia, false, soB));
    bolts.Add(Prism(Q(ax, ay, z0 + tw), Z, bd[2], bd[3], false, soB));
    for (int k = 0; k < 2; k++) bolts.Add(Prism(Q(ax, ay, z0 + tw + bd[3] + k * bd[1]), Z, bd[0], bd[1], true, soB));
    bolts.Add(Prism(Q(ax, ay, ZP - bd[1]), Z, bd[0], bd[1], true, soB));                       // levelling nut in the grout
}
static List<FamilyInstance> ByMark(Document d, string mk) {
    return new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(f => f.Location is LocationPoint && f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS) != null && f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString() == mk).ToList(); }
// rib −t from the column face (h) sloping straight to 20 at the free end; org = foot of the rib centre plane at the column end, along dir, plate normal nrm
static Solid Rib(XYZ org, XYZ dir, XYZ nrm, double len, double t, double h, SolidOptions so) {
    var uv = new double[] { 0, 0, len, 0, len, 20, 0, h };
    return PlateW(org - nrm * (t / 2) * MM, dir, XYZ.BasisZ, uv, t, nrm, so); }
// base plate outline (local u/v, CCW) with open slots from the ±v edges at u = ±bu, ending in a half circle round the anchor at v = ±bv
static double[] SlotPlate(double Au, double Av, double bu, double bv, double sw)
{
    var pts = new List<double>(); double r = sw / 2; int n = 8;
    Action<double, double> A = (u, v) => { pts.Add(u); pts.Add(v); };
    A(-Au, -Av);
    if (sw > 0) foreach (var uc in new[] { -bu, bu }) {          // bottom edge, u increasing
        A(uc - r, -Av); A(uc - r, -bv);
        for (int i = 1; i < n; i++) { double a = Math.PI - Math.PI * i / n; A(uc + r * Math.Cos(a), -bv + r * Math.Sin(a)); }
        A(uc + r, -bv); A(uc + r, -Av); }
    A(Au, -Av); A(Au, Av);
    if (sw > 0) foreach (var uc in new[] { bu, -bu }) {          // top edge, u decreasing
        A(uc + r, Av); A(uc + r, bv);
        for (int i = 1; i < n; i++) { double a = -Math.PI * i / n; A(uc + r * Math.Cos(a), bv + r * Math.Sin(a)); }
        A(uc - r, bv); A(uc - r, Av); }
    A(-Au, Av);
    return pts.ToArray();
}

static string Bases(Document d)
{
    var sb = new System.Text.StringBuilder(); var cnt = new Dictionary<string, int>();
    using (var t = new Transaction(d, "В109: базы колонн (узлы пользователя Б1–Б6)"))
    {
        t.Start();
        var fo = t.GetFailureHandlingOptions(); fo.SetFailuresPreprocessor(new Swallow()); t.SetFailureHandlingOptions(fo);
        sb.AppendLine("removed " + RemoveNode(d, "база") + " old pieces");
        var soP = SoPlate(d); var soB = SoBolt(d); var soW = SoWeld(d);
        XYZ X = XYZ.BasisX, Y = XYZ.BasisY, Z = XYZ.BasisZ; const double g = 0.3, TR = 12, HR = 310, BF = 150;
        var braced = new[] { 48000.0, 54000, 108000, 114000 };
        // ---- I-columns: К1 (Б1/Б2), К2 (Б3), СФ (Б5); local u = flange width W, v = depth D (W×D = +Z)
        foreach (var mk in new[] { "К1", "К2", "СФ" })
            foreach (var c in ByMark(d, mk))
            {
                var o = (c.Location as LocationPoint).Point; double cx = o.X / MM, cy = o.Y / MM;
                XYZ D = mk == "СФ" ? X : Y, W = D.CrossProduct(Z);
                double hf, tf, tw, r, Av, bv, bu = 260, sw; int dia; string nm;
                if (mk == "К1") { hf = 294.5; tf = 21; tw = 16; r = 28; Av = 475; bv = 385; dia = 42; sw = 60; nm = braced.Any(x => Math.Abs(x - cx) < 1) ? "Б2" : "Б1"; }
                else if (mk == "К2") { hf = 298.5; tf = 25; tw = 18; r = 28; Av = 480; bv = 390; dia = 42; sw = 60; nm = "Б3"; }
                else { hf = 195; tf = 16; tw = 10; r = 22; Av = 375; bv = 285; dia = 30; sw = 40; nm = "Б5"; }
                double Au = 350, tp = 40, z0 = ZP + tp;
                Func<double, double, double, XYZ> Q = (u, v, z) => P(cx, cy, z) + (W * u + D * v) * MM;
                var plates = new List<GeometryObject>(); var welds = new List<GeometryObject>(); var bolts = new List<GeometryObject>();
                plates.Add(Plate(Q(0, 0, ZP), W, D, SlotPlate(Au, Av, bu, bv, sw), tp, false, soP));
                double u0 = BF + g, u1 = u0 + TR, ue = u1 + g;                           // long rib faces, flange-rib start
                foreach (var s in new[] { 1.0, -1.0 })
                {
                    // long rib at the flange tips over the whole plate length
                    plates.Add(PlateW(Q(s * u0, 0, z0), D, Z, new double[] { -Av, 0, Av, 0, Av, 20, hf, HR, -hf, HR, -Av, 20 }, TR, s * W, soP));
                    foreach (var pr in new[] { new[] { -Av + 5, -hf - 10 }, new[] { -(hf - tf) + 10, hf - tf - 10 }, new[] { hf + 10, Av - 5 } })
                        welds.Add(Weld(Q(s * u0, pr[0], z0), -s * W, Z, D, 6, pr[1] - pr[0], soW));
                    foreach (var pr in new[] { new[] { -Av + 5, -hf - 10 }, new[] { -(hf - TR) + 10, hf - TR - 10 }, new[] { hf + 10, Av - 5 } })
                        welds.Add(Weld(Q(s * u1, pr[0], z0), s * W, Z, D, 6, pr[1] - pr[0], soW));
                    foreach (var sv in new[] { 1.0, -1.0 })
                    {
                        // flange-extension rib in the flange plane to the plate edge
                        plates.Add(Rib(Q(s * ue, sv * (hf - TR / 2), z0), s * W, sv * D, Au - ue, TR, HR, soP));
                        welds.Add(Weld(Q(s * (ue + 10), sv * hf, z0), sv * D, Z, s * W, 6, Au - ue - 15, soW));
                        welds.Add(Weld(Q(s * (ue + 10), sv * (hf - TR), z0), -sv * D, Z, s * W, 6, Au - ue - 15, soW));
                        // long rib ↔ flange tip (both flange faces)
                        welds.Add(Weld(Q(s * u0, sv * hf, z0 + 10), -s * W, sv * D, Z, 6, HR - 20, soW));
                        welds.Add(Weld(Q(s * u0, sv * (hf - tf), z0 + 10), -s * W, -sv * D, Z, 6, HR - 20, soW));
                        // column ↔ plate: inner flange faces
                        welds.Add(Weld(Q(s * (tw / 2 + r), sv * (hf - tf), z0), -sv * D, Z, s * W, 8, BF - tw / 2 - r, soW));
                    }
                    welds.Add(Weld(Q(-BF, s * hf, z0), s * D, Z, W, 8, 2 * BF, soW));                       // outer flange faces
                    welds.Add(Weld(Q(s * tw / 2, -(hf - tf - r), z0), s * W, Z, D, 8, 2 * (hf - tf - r), soW)); // web
                }
                foreach (var su in new[] { 1.0, -1.0 }) foreach (var sv in new[] { 1.0, -1.0 })
                {   // anchors are built in world X/Y: pass the world offset of the local (u, v) point
                    var off = W * (su * bu) + D * (sv * bv);
                    Anchor((x, y, z) => P(cx + x, cy + y, z), off.X, off.Y, z0, dia, 120, 20, plates, bolts, welds, soP, soB, soW);
                }
                string pl = "−40×700×" + (2 * Av);
                DS(d, BuiltInCategory.OST_StructConnections, "база", "База " + nm + " (" + mk + "): плита " + pl + " С345, рёбра −12 h310 С245, шайбы −20×120×120 С345", plates);
                DS(d, BuiltInCategory.OST_StructConnectionBolts, "база", "Фундаментный болт М" + dia + " 09Г2С ×4 (2 гайки + установочная)", bolts);
                DS(d, BuiltInCategory.OST_StructConnectionWelds, "база", "шов база " + nm, welds);
                cnt[nm] = (cnt.ContainsKey(nm) ? cnt[nm] : 0) + 1;
            }
        // ---- К3 □374x362x12 (Б4) and СФ1 □200x6 (Б6)
        foreach (var mk in new[] { "К3", "СФ1" })
        {
            bool k3 = mk == "К3"; double hx = k3 ? 187 : 100, hy = k3 ? 181 : 100, a = k3 ? 400 : 275, tp = k3 ? 40 : 30, z0 = ZP + tp, bb = k3 ? 290 : 190, ww = k3 ? 120 : 100;
            int dia = k3 ? 42 : 24; string nm = k3 ? "Б4" : "Б6";
            foreach (var c in ByMark(d, mk))
            {
                var o = (c.Location as LocationPoint).Point; double cx = o.X / MM, cy = o.Y / MM;
                Func<double, double, double, XYZ> Q = (x, y, z) => P(cx + x, cy + y, z);
                var plates = new List<GeometryObject>(); var welds = new List<GeometryObject>(); var bolts = new List<GeometryObject>();
                plates.Add(Plate(Q(0, 0, ZP), X, Y, k3 ? SlotPlate(a, a, bb, bb, 60) : Rect(-a, -a, a, a), tp, false, soP));
                foreach (var s1 in new[] { 1.0, -1.0 })
                {
                    if (k3)
                    {   // ribs −12 in the box wall planes to the plate edges (8 ribs)
                        foreach (var s2 in new[] { 1.0, -1.0 })
                        {
                            plates.Add(Rib(Q(s1 * hx, s2 * (hy - 6), z0), s1 * X, Y, a - hx, 12, HR, soP));
                            plates.Add(Rib(Q(s2 * (hx - 6), s1 * hy, z0), s1 * Y, X, a - hy, 12, HR, soP));
                            welds.Add(Weld(Q(s1 * (hx + 8), s2 * hy, z0), s2 * Y, Z, s1 * X, 6, a - hx - 13, soW)); welds.Add(Weld(Q(s1 * (hx + 8), s2 * (hy - 12), z0), -s2 * Y, Z, s1 * X, 6, a - hx - 13, soW));
                            welds.Add(Weld(Q(s2 * hx, s1 * (hy + 8), z0), s2 * X, Z, s1 * Y, 6, a - hy - 13, soW)); welds.Add(Weld(Q(s2 * (hx - 12), s1 * (hy + 8), z0), -s2 * X, Z, s1 * Y, 6, a - hy - 13, soW));
                        }
                        welds.Add(Weld(Q(s1 * hx, -hy + 12, z0), Z, s1 * X, Y, 6, 2 * hy - 24, soW)); welds.Add(Weld(Q(-hx + 12, s1 * hy, z0), Z, s1 * Y, X, 6, 2 * hx - 24, soW));
                    }
                    else
                    {   // 2 ribs per face at ±75, from the box face to the plate edge
                        foreach (var s2 in new[] { 1.0, -1.0 })
                        {
                            plates.Add(Rib(Q(s1 * hx, s2 * 75, z0), s1 * X, Y, a - hx, 12, HR, soP));
                            plates.Add(Rib(Q(s2 * 75, s1 * hy, z0), s1 * Y, X, a - hy, 12, HR, soP));
                            foreach (var s3 in new[] { 1.0, -1.0 })
                            {
                                double f = s2 * 75 + s3 * 6;
                                welds.Add(Weld(Q(s1 * (hx + 8), f, z0), s3 * Y, Z, s1 * X, 6, a - hx - 13, soW));
                                welds.Add(Weld(Q(f, s1 * (hy + 8), z0), s3 * X, Z, s1 * Y, 6, a - hy - 13, soW));
                                welds.Add(Weld(Q(s1 * hx, f, z0 + 8), s1 * X, s3 * Y, Z, 6, HR - 18, soW));
                                welds.Add(Weld(Q(f, s1 * hy, z0 + 8), s1 * Y, s3 * X, Z, 6, HR - 18, soW));
                            }
                        }
                        foreach (var pr in new[] { new[] { -hy, -84.0 }, new[] { -66.0, 66 }, new[] { 84.0, hy } })
                        {
                            welds.Add(Weld(Q(s1 * hx, pr[0], z0), Z, s1 * X, Y, 6, pr[1] - pr[0], soW));
                            welds.Add(Weld(Q(pr[0], s1 * hy, z0), Z, s1 * Y, X, 6, pr[1] - pr[0], soW));
                        }
                    }
                    foreach (var s2 in new[] { 1.0, -1.0 }) Anchor(Q, s1 * bb, s2 * bb, z0, dia, ww, 20, plates, bolts, welds, soP, soB, soW);
                }
                DS(d, BuiltInCategory.OST_StructConnections, "база", "База " + nm + " (" + mk + "): плита −" + tp + "×" + 2 * a + "×" + 2 * a + " С345, рёбра −12 h310 С245, шайбы −20×" + ww + "×" + ww + " С345", plates);
                DS(d, BuiltInCategory.OST_StructConnectionBolts, "база", "Фундаментный болт М" + dia + " 09Г2С ×4 (2 гайки + установочная)", bolts);
                DS(d, BuiltInCategory.OST_StructConnectionWelds, "база", "шов база " + nm, welds);
                cnt[nm] = (cnt.ContainsKey(nm) ? cnt[nm] : 0) + 1;
            }
        }
        t.Commit();
    }
    sb.AppendLine("bases: " + string.Join(", ", cnt.Select(k => k.Key + " " + k.Value)));
    return sb.ToString();
}
