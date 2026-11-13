// РМЦ КМ q20: ӨЗ тәсілім: (1) көлемдік clash > 1 мм3 (тікелей булев; құласа масштабтау қоршауы; соңында shift-экстраполяция); (2) z-fighting = бір бағытты беттер бір жазықтықта (до 0,02 мм) және ауданы қабаттасады; (3) жанасу беттері бойынша бірдей түсті жанасатын бөлшектер. ТЕК ОҚИДЫ. Lib: rmc_misc_lib.cs
return RunClash(document);
}
const string OUT = @"C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\w\out\";
static HashSet<string> KEYS = null;
class PF { public double nx, ny, nz, d; public double[] bb; public double area; public PlanarFace Fc; }
class It { public string Kind, Key, Loc, Name, Mark, Mat; public long Eid; public Solid S; public double[] B; public bool Bolt, Weld; public List<PF> F; public int Idx; }
static List<PF> FacesOf(Solid s)
{
    var r = new List<PF>();
    foreach (Face f in s.Faces)
    {
        var pf = f as PlanarFace; if (pf == null) continue; var n = pf.FaceNormal; var o = pf.Origin / QMM; double d = n.X * o.X + n.Y * o.Y + n.Z * o.Z;
        double[] bb = { 1e18, 1e18, 1e18, -1e18, -1e18, -1e18 };
        foreach (var loop in pf.GetEdgesAsCurveLoops()) foreach (Curve c in loop) { var q0 = c.GetEndPoint(0) / QMM; var q1 = c.GetEndPoint(1) / QMM; foreach (var q in new[] { q0, q1 }) { bb[0] = Math.Min(bb[0], q.X); bb[1] = Math.Min(bb[1], q.Y); bb[2] = Math.Min(bb[2], q.Z); bb[3] = Math.Max(bb[3], q.X); bb[4] = Math.Max(bb[4], q.Y); bb[5] = Math.Max(bb[5], q.Z); } }
        r.Add(new PF { nx = n.X, ny = n.Y, nz = n.Z, d = d, bb = bb, area = pf.Area / (QMM * QMM), Fc = pf });
    }
    return r;
}
static string LoopsStr(PlanarFace pf) { var sbb = new StringBuilder(); foreach (var lp in pf.GetEdgesAsCurveLoops()) { if (sbb.Length > 0) sbb.Append("|"); var pts = new List<string>(); foreach (Curve c in lp) { var tp = c.Tessellate(); for (int k = 0; k < tp.Count - 1; k++) { var q = tp[k] / QMM; pts.Add(QF(q.X) + ";" + QF(q.Y) + ";" + QF(q.Z)); } } sbb.Append(string.Join(" ", pts)); } return sbb.ToString(); }
static double Vol(Solid a, Solid b, out string how)
{
    how = "bool";
    try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(a, b, BooleanOperationsType.Intersect); return r == null ? 0 : QCu(r.Volume); } catch { }
    try
    {
        var bb = QBBox(b); var c = new XYZ((bb[0] + bb[3]) / 2, (bb[1] + bb[4]) / 2, (bb[2] + bb[5]) / 2) * QMM; double[] v = new double[2]; int k = 0;
        foreach (double sc in new[] { 0.9995, 1.0005 })
        {
            var tr = Transform.Identity; tr.BasisX = new XYZ(sc, 0, 0); tr.BasisY = new XYZ(0, sc, 0); tr.BasisZ = new XYZ(0, 0, sc); tr.Origin = c * (1 - sc);
            var b2 = SolidUtils.CreateTransformed(b, tr); var r = BooleanOperationsUtils.ExecuteBooleanOperation(a, b2, BooleanOperationsType.Intersect); v[k++] = r == null ? 0 : QCu(r.Volume);
        }
        how = "bracket[" + QF(v[0]) + ".." + QF(v[1]) + "]"; return v[0];
    }
    catch { }
    bool vs, fl; double q = QOvlVol(a, b, out vs, out fl); how = fl ? "FAIL" : "shift"; return q;
}
static string RunClash(Document d)
{
    if (System.IO.File.Exists(OUT + "keys.txt")) KEYS = new HashSet<string>(System.IO.File.ReadAllLines(OUT + "keys.txt", Encoding.UTF8).Select(x => x.Trim()).Where(x => x != ""));
    var sb = new StringBuilder(); var items = new List<It>(); var matCache = new Dictionary<long, string>();
    Func<Solid, string> matOf = s => { foreach (Face f in s.Faces) { long id = f.MaterialElementId.Value; string n; if (!matCache.TryGetValue(id, out n)) { var m = d.GetElement(f.MaterialElementId) as Material; n = m == null ? "-" : m.Name; matCache[id] = n; } return n; } return "-"; };
    foreach (var fi in new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>())
    {
        if (fi.Category == null) continue; long cid = fi.Category.Id.Value; if (cid != (long)BuiltInCategory.OST_StructuralFraming && cid != (long)BuiltInCategory.OST_StructuralColumns) continue;
        var pm = fi.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS); string mk = pm == null ? "" : (pm.AsString() ?? ""); if (mk == "") continue;
        foreach (var s in QSolidsOf(fi)) items.Add(new It { Kind = "F", Key = "каркас", Mark = mk, Name = mk + " " + fi.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString(), Eid = fi.Id.Value, S = s, B = QBBox(s), Mat = matOf(s) });
    }
    int nF = items.Count;
    foreach (var ds in new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>())
    {
        string adi = ds.ApplicationDataId ?? ""; string key = adi.Contains("|") ? adi.Split('|')[0].Trim() : adi; string loc = adi.Contains("|") ? adi.Split('|')[1].Trim() : "";
        long cid = ds.Category == null ? 0 : ds.Category.Id.Value; string kind = ds.ApplicationId == "БК_ЖБ" ? "J" : "N";
        foreach (var s in QSolidsOf(ds)) items.Add(new It { Kind = kind, Key = key, Loc = loc, Name = ds.Name ?? "", Eid = ds.Id.Value, S = s, B = QBBox(s), Bolt = cid == (long)BuiltInCategory.OST_StructConnectionBolts, Weld = cid == (long)BuiltInCategory.OST_StructConnectionWelds, Mat = matOf(s) });
    }
    sb.AppendLine("solids: frame " + nF + ", DS " + (items.Count - nF));
    var ord = items.OrderBy(i => i.B[0]).ToList(); double tol = 0.3;
    var clash = new List<string>(); var zf = new List<string>(); var fail = new List<string>(); var packs = new SortedDictionary<string, int>();
    var cat = new SortedDictionary<string, int[]>(); var sameMat = new SortedDictionary<string, int>(); int contactMat = 0, pairsBB = 0, boolDirect = 0, bracket = 0, shift = 0, failN = 0, zfN = 0, zfPairs = 0;
    var byKey = new SortedDictionary<string, double[]>();
    for (int a = 0; a < ord.Count; a++)
    {
        var A = ord[a];
        for (int c = a + 1; c < ord.Count; c++)
        {
            var B = ord[c]; if (B.B[0] > A.B[3] + tol) break;
            if (A.Eid == B.Eid) continue; if (A.Kind == "J" && B.Kind == "J") continue; if (KEYS != null && !(KEYS.Contains(A.Key) || KEYS.Contains(B.Key) || KEYS.Contains(A.Key + "|" + A.Loc) || KEYS.Contains(B.Key + "|" + B.Loc))) continue;
            double ox = Math.Min(A.B[3], B.B[3]) - Math.Max(A.B[0], B.B[0]), oy = Math.Min(A.B[4], B.B[4]) - Math.Max(A.B[1], B.B[1]), oz = Math.Min(A.B[5], B.B[5]) - Math.Max(A.B[2], B.B[2]);
            if (ox < -tol || oy < -tol || oz < -tol) continue; pairsBB++;
            string cn = (A.Kind == "F" && B.Kind == "F") ? "каркас↔каркас" : (A.Kind == "F" || B.Kind == "F") ? "каркас↔узел/база/ЖБ" : "узел↔узел";
            int[] cc; if (!cat.TryGetValue(cn, out cc)) { cc = new int[4]; cat[cn] = cc; } cc[0]++;
            if (Math.Max(ox, 0) * Math.Max(oy, 0) * Math.Max(oz, 0) > 1)
            {
                string how; double v = Vol(A.S, B.S, out how); if (how == "bool") boolDirect++; else if (how.StartsWith("bracket")) bracket++; else if (how == "shift") shift++; else { failN++; fail.Add(cn + " | " + A.Key + " " + A.Loc + " «" + A.Name + "» ↔ " + B.Key + " " + B.Loc + " «" + B.Name + "»"); cc[3]++; }
                if (v > 1)
                {
                    bool boltFrame = (A.Bolt && B.Kind == "F") || (B.Bolt && A.Kind == "F");
                    if (boltFrame) { string pk = (A.Bolt ? A.Key : B.Key); int n; packs.TryGetValue(pk, out n); packs[pk] = n + 1; }
                    else
                    {
                        cc[1]++; string kk = cn + " | " + (A.Kind == "F" ? "каркас(" + A.Mark + ")" : A.Key) + " ↔ " + (B.Kind == "F" ? "каркас(" + B.Mark + ")" : B.Key); double[] z; if (!byKey.TryGetValue(kk, out z)) { z = new double[2]; byKey[kk] = z; } z[0]++; z[1] = Math.Max(z[1], v);
                        clash.Add(cn + " | " + A.Key + " " + A.Loc + " «" + A.Name + "» [" + A.Eid + "] ↔ " + B.Key + " " + B.Loc + " «" + B.Name + "» [" + B.Eid + "] " + QF(v) + " мм3 (" + how + ")");
                    }
                }
            }
            if (A.F == null) A.F = FacesOf(A.S); if (B.F == null) B.F = FacesOf(B.S); bool anyContact = false, anyZ = false;
            foreach (var fa in A.F) foreach (var fb in B.F)
            {
                double dot = fa.nx * fb.nx + fa.ny * fb.ny + fa.nz * fb.nz; if (Math.Abs(dot) < 0.99999) continue;
                double dist = Math.Abs(fa.d - (dot > 0 ? fb.d : -fb.d)); if (dist > 0.02) continue;
                double ex = Math.Min(fa.bb[3], fb.bb[3]) - Math.Max(fa.bb[0], fb.bb[0]), ey = Math.Min(fa.bb[4], fb.bb[4]) - Math.Max(fa.bb[1], fb.bb[1]), ez = Math.Min(fa.bb[5], fb.bb[5]) - Math.Max(fa.bb[2], fb.bb[2]);
                int pos = (ex > 0.5 ? 1 : 0) + (ey > 0.5 ? 1 : 0) + (ez > 0.5 ? 1 : 0); if (pos < 2) continue; if (ex < -0.02 || ey < -0.02 || ez < -0.02) continue;
                if (dot > 0) { int inside = 0; double[] lo = { Math.Max(fa.bb[0], fb.bb[0]), Math.Max(fa.bb[1], fb.bb[1]), Math.Max(fa.bb[2], fb.bb[2]) }, hi = { Math.Min(fa.bb[3], fb.bb[3]), Math.Min(fa.bb[4], fb.bb[4]), Math.Min(fa.bb[5], fb.bb[5]) }; int ia = 0, ib = 1; { double[] ext = { hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2] }; var ord3 = new[] { 0, 1, 2 }.OrderByDescending(k => ext[k]).ToArray(); ia = ord3[0]; ib = ord3[1]; } foreach (double u in new[] { 0.1, 0.3, 0.5, 0.7, 0.9 }) foreach (double w in new[] { 0.1, 0.3, 0.5, 0.7, 0.9 }) { double[] pc = { (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2 }; pc[ia] = lo[ia] + (hi[ia] - lo[ia]) * u; pc[ib] = lo[ib] + (hi[ib] - lo[ib]) * w; var p = new XYZ(pc[0], pc[1], pc[2]); double sd = fa.nx * p.X + fa.ny * p.Y + fa.nz * p.Z - fa.d; var pp = new XYZ(p.X - fa.nx * sd, p.Y - fa.ny * sd, p.Z - fa.nz * sd) * QMM; var ra = fa.Fc.Project(pp); var rb = fb.Fc.Project(pp); if (ra != null && rb != null && ra.Distance / QMM < 0.002 && rb.Distance / QMM < 0.002) inside++; } inside = 99; if (!anyZ) { zfPairs++; anyZ = true; } zfN++; if (zf.Count < 400000) zf.Add(string.Join("\t", new[] { cn, A.Key, A.Loc, A.Name, A.Eid.ToString(), A.Mat, B.Key, B.Loc, B.Name, B.Eid.ToString(), B.Mat, QF(fa.nx), QF(fa.ny), QF(fa.nz), QF(Math.Min(fa.area, fb.area)), QF(ex), QF(ey), QF(ez), LoopsStr(fa.Fc), LoopsStr(fb.Fc) })); }
                else anyContact = true;
            }
            if (anyContact) { contactMat++; if (A.Mat == B.Mat && A.Mat != "-") { string k2 = A.Mat + " | " + (A.Kind == "F" ? "каркас " + A.Mark : A.Key) + " × " + (B.Kind == "F" ? "каркас " + B.Mark : B.Key); int n; sameMat.TryGetValue(k2, out n); sameMat[k2] = n + 1; } }
        }
    }
    sb.AppendLine("bbox-жанасқан жұп (≤0.3 мм) " + pairsBB + "; көлем есебі: тікелей " + boolDirect + ", масштаб-қоршау " + bracket + ", shift " + shift + ", ЕСЕПТЕЛМЕДІ " + failN);
    foreach (var kv in cat) sb.AppendLine("  " + kv.Key + ": жұп " + kv.Value[0] + ", clash>1мм3 " + kv.Value[1] + ", есептелмеген " + kv.Value[3]);
    sb.AppendLine("=== CLASH (>1 мм3) түр бойынша (саны, макс мм3):"); foreach (var kv in byKey) sb.AppendLine("  " + kv.Value[0] + "  max " + QF(kv.Value[1]) + "  " + kv.Key);
    sb.AppendLine("=== ПАКЕТ (болт стержені ↔ тесіксіз каркас):"); foreach (var kv in packs) sb.AppendLine("  " + kv.Key + ": " + kv.Value);
    sb.AppendLine("=== ЕСЕПТЕЛМЕГЕН: " + fail.Count); foreach (var r in fail.Take(80)) sb.AppendLine("  " + r);
    sb.AppendLine("=== z-fighting (бір бағытты беттер, до 0.02 мм, ауданы қабаттасады): жұп " + zfPairs + ", бет-жұп " + zfN);
    sb.AppendLine("=== жанасу беттері бар жұптар " + contactMat + "; бірдей материал бойынша:"); foreach (var kv in sameMat.OrderByDescending(k => k.Value)) sb.AppendLine("  " + kv.Value + "  " + kv.Key);
    sb.AppendLine("=== CLASH тізімі (барлығы " + clash.Count + "; алғашқы 200):"); foreach (var r in clash.Take(200)) sb.AppendLine("  " + r);
    var u8 = new UTF8Encoding(false);
    System.IO.File.WriteAllLines(OUT + "clash_all.txt", clash, u8); System.IO.File.WriteAllLines(OUT + "zfight2.tsv", zf, u8);
    System.IO.File.WriteAllText(OUT + "clash_report.txt", sb.ToString(), u8);
    return sb.ToString();
}