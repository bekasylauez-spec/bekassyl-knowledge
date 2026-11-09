// Завод В109 (227-23-П-УВПиОС-ВП-В109-КМ), Цех Блок 1: project from БК_КМ.rte, grids, levels and the steel frame from members.tsv (gen.py),
// Алатау цех style (al_01): a type per mark («Маркировка типоразмера» = mark), a material colour per mark, the mark in «Комментарии».
// Re-runnable: removes the instances of the (КМ) member families and builds again. Log: _b109_01.txt.
var app = document.Application; var uiapp = new UIApplication(app);
string root = @"D:\Бекасыл КЖ КМ\";
string auto = root + @"Завод_В109_КМ\_авто\revit\";
string log = auto + "_b109_01.txt";
string fam = root + @"_Стандарт_КЖ\семейства\";
string outPath = root + @"Завод_В109_КМ\227-23-П-УВПиОС-ВП-В109-КМ_Цех Блок 1.rvt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder();
  try {
    var nd = app.Documents.Cast<Document>().FirstOrDefault(d => string.Equals(d.PathName, outPath, StringComparison.OrdinalIgnoreCase));
    if (nd == null && System.IO.File.Exists(outPath)) nd = app.OpenDocumentFile(outPath);
    if (nd == null)
    {
        string rteCopy = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "БК_КМ_b109.rte"); System.IO.File.Copy(root + @"_Стандарт_КЖ\шаблоны\БК_КМ.rte", rteCopy, true);
        nd = app.NewProjectDocument(rteCopy); nd.SaveAs(outPath, new SaveAsOptions { OverwriteExistingFile = true }); sb.AppendLine("created " + outPath);
    }
    {   // the library tube family must be cut by unattached voids (lattice end cuts): «Вырезать пустотами при загрузке» on, saved in the library
        var tp = fam + "(КМ)труба_ГОСТ30245_каркас.rfa"; var fdoc = app.OpenDocumentFile(tp);
        var cw = fdoc.OwnerFamily.get_Parameter(BuiltInParameter.FAMILY_ALLOW_CUT_WITH_VOIDS);
        if (cw != null && cw.AsInteger() != 1) { using (var tt = new Transaction(fdoc, "cut with voids")) { tt.Start(); cw.Set(1); tt.Commit(); } fdoc.Save(); sb.AppendLine("tube family: cut with voids on"); }
        fdoc.Close(false);
    }
    sb.Append(Setup(nd)); sb.Append(Frame(nd, fam, auto + "members.tsv"));
    nd.Save(); sb.AppendLine("saved " + nd.PathName);
  } catch (Exception ex) { sb.AppendLine("ERR " + ex); }
  System.IO.File.WriteAllText(log, sb.ToString()); };
uiapp.Idling += hnd;
return "queued";
}

const double MM = 1 / 304.8;
static XYZ P(double x, double y, double z) { return new XYZ(x * MM, y * MM, z * MM); }
static readonly string[] RN = { "A", "B", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M" };
static readonly double[] RY = { 0, 6000, 12000, 18000, 24000, 27000, 33000, 36000, 42000, 48000, 54000, 60000 };

class FL : IFamilyLoadOptions {
    public bool OnFamilyFound(bool inUse, out bool ov) { ov = true; return true; }
    public bool OnSharedFamilyFound(Family f, bool inUse, out FamilySource src, out bool ov) { src = FamilySource.Family; ov = true; return true; } }
class Swallow : IFailuresPreprocessor { public FailureProcessingResult PreprocessFailures(FailuresAccessor a) {
    foreach (var m in a.GetFailureMessages()) if (m.GetSeverity() == FailureSeverity.Warning) a.DeleteWarning(m); return FailureProcessingResult.Continue; } }
static Family Load(Document d, string path) { Family f; d.LoadFamily(path, new FL(), out f);
    return f ?? new FilteredElementCollector(d).OfClass(typeof(Family)).Cast<Family>().First(x => x.Name == System.IO.Path.GetFileNameWithoutExtension(path)); }
// profile type of a family; tubes not in the family are made from the first type (h, b, t + mass by ГОСТ 30245: R = 2t, r = t)
static FamilySymbol Profile(Document d, Family f, string prof, System.Text.StringBuilder sb) {
    var syms = f.GetFamilySymbolIds().Select(i => d.GetElement(i) as FamilySymbol).ToList();
    var s = syms.FirstOrDefault(x => x.Name == prof); if (s != null) return s;
    if (!prof.StartsWith("□")) throw new Exception("no type " + prof + " in " + f.Name);
    var p = prof.Substring(1).Split('x').Select(q => double.Parse(q, System.Globalization.CultureInfo.InvariantCulture)).ToArray();
    double h = p[0], b = p.Length == 3 ? p[1] : p[0], t = p[p.Length - 1];
    s = syms.First(x => x.Name.StartsWith("□")).Duplicate(prof) as FamilySymbol;
    s.LookupParameter("h").Set(h * MM); s.LookupParameter("b").Set(b * MM); s.LookupParameter("t").Set(t * MM);
    double A = 2 * t * (h + b) - 4 * t * t - (4 - Math.PI) * (4 * t * t - t * t);
    var pm = s.LookupParameter("КМ_Масса_1м"); if (pm != null) pm.Set(Math.Round(A * 7.85e-3, 2));
    var ps = s.LookupParameter("КМ_Сечение"); if (ps != null) ps.Set(prof.Replace("x", "×"));
    sb.AppendLine("new tube type " + prof + " in " + f.Name + ", kg/m " + Math.Round(A * 7.85e-3, 2));
    return s; }
static FamilySymbol Mark(Document d, Family f, FamilySymbol prof, string name) {
    var syms = f.GetFamilySymbolIds().Select(i => d.GetElement(i) as FamilySymbol).ToList();
    var s = syms.FirstOrDefault(x => x.Name == name);
    if (s == null) s = prof.Duplicate(name) as FamilySymbol;
    else if (s.Id != prof.Id)
    {   // an existing mark type keeps the profile it was made from: copy every writable type parameter of the current profile (sizes, fillet switches, КМ_*)
        foreach (Parameter pp in prof.Parameters)
        {
            if (pp.IsReadOnly || pp.Definition == null) continue; var q = s.get_Parameter(pp.Definition); if (q == null || q.IsReadOnly) continue;
            if (pp.Id.Value == (long)BuiltInParameter.ALL_MODEL_TYPE_MARK || pp.Id.Value == (long)BuiltInParameter.SYMBOL_NAME_PARAM) continue;
            try { if (pp.StorageType == StorageType.Double) q.Set(pp.AsDouble()); else if (pp.StorageType == StorageType.Integer) q.Set(pp.AsInteger()); else if (pp.StorageType == StorageType.String && pp.AsString() != null) q.Set(pp.AsString()); else if (pp.StorageType == StorageType.ElementId) q.Set(pp.AsElementId()); } catch { }
        }
    }
    s.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_MARK).Set(name.Split(' ')[0]);
    var st = s.LookupParameter("КМ_Сталь"); if (st != null && !st.IsReadOnly) st.Set(name.StartsWith("К") && !name.StartsWith("КН") ? "С345" : name.StartsWith("ФФ1 Н") ? "С345" : "С255");
    if (!s.IsActive) s.Activate(); return s; }
static ElementId MarkMat(Document d, string mark, Color c, string steel) {
    string n = "КМ_" + mark + " (" + steel + ")"; var m = new FilteredElementCollector(d).OfClass(typeof(Material)).Cast<Material>().FirstOrDefault(x => x.Name == n);
    if (m == null) { m = d.GetElement(Material.Create(d, n)) as Material; m.Color = c; m.MaterialClass = "Металл"; }
    m.Shininess = 0; m.Smoothness = 0; return m.Id; }
static void SetMat(FamilyInstance fi, ElementId mid) {
    var p = fi.get_Parameter(BuiltInParameter.STRUCTURAL_MATERIAL_PARAM); if (p != null && !p.IsReadOnly) { p.Set(mid); return; }
    p = fi.Symbol.get_Parameter(BuiltInParameter.STRUCTURAL_MATERIAL_PARAM); if (p != null && !p.IsReadOnly) p.Set(mid); }
static double Num(string s) { return double.Parse(s, System.Globalization.CultureInfo.InvariantCulture); }

static string Setup(Document d)
{
    var sb = new System.Text.StringBuilder();
    using (var t = new Transaction(d, "В109: оси, уровни"))
    {
        t.Start();
        var pi = d.ProjectInformation; pi.Number = "227-23-П-УВПиОС-ВП-В109-КМ"; pi.Name = "Алматинский завод гигиенических изделий. Водоподготовка ВП-В109";
        try { pi.BuildingName = "Цех Блок 1"; } catch { }
        var grids = new FilteredElementCollector(d).OfClass(typeof(Grid)).Cast<Grid>().ToDictionary(g => g.Name);
        for (int i = 0; i < 28; i++) { string n = (i + 1).ToString(); if (!grids.ContainsKey(n)) { var g = Grid.Create(d, Line.CreateBound(P(6000.0 * i, -6000, 0), P(6000.0 * i, 66000, 0))); g.Name = n; } }
        for (int r = 0; r < RN.Length; r++) { if (!grids.ContainsKey(RN[r])) { var g = Grid.Create(d, Line.CreateBound(P(-12000, RY[r], 0), P(168000, RY[r], 0))); g.Name = RN[r]; } }
        var levels = new FilteredElementCollector(d).OfClass(typeof(Level)).Cast<Level>().ToList();
        foreach (var lv in new[] { Tuple.Create("-0.300 Верх фундамента", -300.0), Tuple.Create("+4.000 Площадка", 4000.0), Tuple.Create("+5.020", 5020.0), Tuple.Create("+7.600 Площадка", 7600.0),
                                   Tuple.Create("+10.340 Консоль", 10340.0), Tuple.Create("+14.490 Верх колонн A, M", 14490.0), Tuple.Create("+15.240 Конёк", 15240.0) })
            if (!levels.Any(l => Math.Abs(l.Elevation / MM - lv.Item2) < 0.5)) { var L = Level.Create(d, lv.Item2 * MM); L.Name = lv.Item1; }
        t.Commit();
    }
    sb.AppendLine("grids " + new FilteredElementCollector(d).OfClass(typeof(Grid)).GetElementCount() + ", levels " + string.Join(", ", new FilteredElementCollector(d).OfClass(typeof(Level)).Cast<Level>().OrderBy(l => l.Elevation).Select(l => l.Name)));
    return sb.ToString();
}

static string Frame(Document d, string fam, string tsv)
{
    var sb = new System.Text.StringBuilder(); var cnt = new Dictionary<string, int>();
    var lines = System.IO.File.ReadAllLines(tsv, System.Text.Encoding.UTF8).Where(l => l.Trim().Length > 0).Select(l => l.Split('\t')).ToList();
    using (var t = new Transaction(d, "В109: каркас"))
    {
        t.Start();
        var fo = t.GetFailureHandlingOptions(); fo.SetFailuresPreprocessor(new Swallow()); t.SetFailureHandlingOptions(fo);
        var F = new Dictionary<string, Family> {
            { "Ic", Load(d, fam + "(КМ)двутавр_ГОСТ57837_колонна.rfa") }, { "Ib", Load(d, fam + "(КМ)двутавр_ГОСТ57837_каркас.rfa") },
            { "Tc", Load(d, fam + "(КМ)труба_ГОСТ30245_колонна.rfa") }, { "Tb", Load(d, fam + "(КМ)труба_ГОСТ30245_каркас.rfa") },
            { "W", Load(d, fam + "(КМ)двутавр_сварной_несимметричный.rfa") }, { "Cb", Load(d, fam + "(КМ)швеллер_ГОСТ8240_каркас.rfa") } };
        var mine = F.Values.Select(f => f.Id).ToList();
        var old = new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => mine.Contains(x.Symbol.Family.Id)).Select(x => x.Id).ToList();
        if (old.Count > 0) { d.Delete(old); sb.AppendLine("removed " + old.Count + " members of the previous run"); }
        var lvl = new FilteredElementCollector(d).OfClass(typeof(Level)).Cast<Level>().OrderBy(l => Math.Abs(l.Elevation)).First();
        sb.AppendLine("reference level " + lvl.Name + " " + Math.Round(lvl.Elevation / MM));
        // colours per mark
        var col = new Dictionary<string, Color> {
            { "К1", new Color(255, 0, 0) }, { "К2", new Color(200, 0, 60) }, { "К3", new Color(160, 40, 40) }, { "СФ", new Color(0, 150, 90) }, { "СФ1", new Color(0, 110, 60) },
            { "СВ1", new Color(0, 0, 255) }, { "СВ2", new Color(70, 100, 255) }, { "СВ3", new Color(0, 0, 150) }, { "Р1", new Color(0, 190, 255) }, { "Р2", new Color(0, 150, 200) },
            { "БМ1", new Color(120, 60, 200) }, { "КН", new Color(180, 90, 230) }, { "ФФ1", new Color(230, 110, 0) }, { "БП1", new Color(255, 0, 255) }, { "БП2", new Color(200, 0, 200) },
            { "Пр1", new Color(170, 130, 0) }, { "ГС1", new Color(0, 170, 0) },
            { "Б1", new Color(255, 120, 120) }, { "Б2", new Color(255, 160, 60) }, { "Б3", new Color(140, 70, 20) }, { "Б4", new Color(90, 200, 200) }, { "Б5", new Color(200, 200, 0) },
            { "Б6", new Color(150, 150, 0) }, { "Б7", new Color(120, 120, 200) } };
        var syms = new Dictionary<string, FamilySymbol>(); var mats = new Dictionary<string, ElementId>();
        foreach (var l in lines)
        {
            string key = l[1] + "|" + l[2]; if (syms.ContainsKey(key)) continue;
            var f = F[l[2]]; var prof = Profile(d, f, l[3], sb); var s = Mark(d, f, prof, l[1]); syms[key] = s;
            string mk = l[1].Split(' ')[0]; if (!mats.ContainsKey(mk)) mats[mk] = MarkMat(d, mk, col.ContainsKey(mk) ? col[mk] : new Color(128, 128, 128), mk.StartsWith("К") && mk != "КН" ? "С345" : "С255");
        }
        d.Regenerate();
        var colInst = new List<Tuple<FamilyInstance, string, double>>(); var beams = new List<Tuple<FamilyInstance, string[]>>(); var byRow = new List<FamilyInstance>();
        foreach (var l in lines)
        {
            var sym = syms[l[1] + "|" + l[2]]; string mk = l[1].Split(' ')[0]; FamilyInstance fi;
            if (l[0] == "C")
            {
                fi = d.Create.NewFamilyInstance(P(Num(l[4]), Num(l[5]), 0), sym, lvl, Autodesk.Revit.DB.Structure.StructuralType.Column);
                fi.get_Parameter(BuiltInParameter.FAMILY_BASE_LEVEL_PARAM).Set(lvl.Id); fi.get_Parameter(BuiltInParameter.FAMILY_BASE_LEVEL_OFFSET_PARAM).Set(Num(l[6]) * MM);
                fi.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_PARAM).Set(lvl.Id); fi.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_OFFSET_PARAM).Set(Num(l[9]) * MM);
                colInst.Add(Tuple.Create(fi, l[10], Num(l[3].StartsWith("□") ? "0" : "0")));
            }
            else
            {
                var a = P(Num(l[4]), Num(l[5]), Num(l[6])); var b = P(Num(l[7]), Num(l[8]), Num(l[9]));
                fi = d.Create.NewFamilyInstance(Line.CreateBound(a, b), sym, lvl, Autodesk.Revit.DB.Structure.StructuralType.Beam);
                fi.get_Parameter(BuiltInParameter.Z_JUSTIFICATION).Set((int)Autodesk.Revit.DB.Structure.ZJustification.Origin);
                fi.get_Parameter(BuiltInParameter.Y_JUSTIFICATION).Set((int)Autodesk.Revit.DB.Structure.YJustification.Origin);
                Autodesk.Revit.DB.Structure.StructuralFramingUtils.DisallowJoinAtEnd(fi, 0); Autodesk.Revit.DB.Structure.StructuralFramingUtils.DisallowJoinAtEnd(fi, 1);
                double roll = Num(l[10]); if (Math.Abs(roll) > 1e-6) fi.get_Parameter(BuiltInParameter.STRUCTURAL_BEND_DIR_ANGLE).Set(roll * Math.PI / 180);
                beams.Add(Tuple.Create(fi, l));
            }
            fi.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set(l[1]); SetMat(fi, mats[mk]); byRow.Add(fi);
            cnt[l[1]] = (cnt.ContainsKey(l[1]) ? cnt[l[1]] : 0) + 1;
        }
        d.Regenerate();
        // column orientation: depth h along the asked axis (bounding box), else rotate 90°
        int rot = 0;
        foreach (var c in colInst)
        {
            var bb = c.Item1.get_BoundingBox(null); double dx = bb.Max.X - bb.Min.X, dy = bb.Max.Y - bb.Min.Y;
            bool wantY = c.Item2 == "Y"; if ((wantY && dx > dy + 1e-6) || (!wantY && dy > dx + 1e-6))
            { var lp = (c.Item1.Location as LocationPoint).Point; ElementTransformUtils.RotateElement(d, c.Item1.Id, Line.CreateBound(lp, lp + XYZ.BasisZ), Math.PI / 2); rot++; }
        }
        sb.AppendLine("columns rotated 90°: " + rot + " of " + colInst.Count);
        d.Regenerate();
        // purlin roll check: the bottom flange must lie on the roof (a face with normal = −roof normal)
        int flip = 0;
        foreach (var bm in beams.Where(q => q.Item2[1] == "Пр1" && Math.Abs(Num(q.Item2[10])) > 1e-6).Take(2))
        {
            double roll = Num(bm.Item2[10]) * Math.PI / 180; var nrm = new XYZ(0, -Math.Sin(roll), Math.Cos(roll));
            var faces = bm.Item1.get_Geometry(new Options()).OfType<GeometryInstance>().SelectMany(g => g.GetInstanceGeometry().OfType<Solid>()).SelectMany(so => so.Faces.Cast<Face>()).OfType<PlanarFace>();
            if (!faces.Any(f => f.FaceNormal.DotProduct(-nrm) > 0.99999)) flip++;
        }
        if (flip > 0) { foreach (var bm in beams.Where(q => q.Item2[1] == "Пр1")) { var p = bm.Item1.get_Parameter(BuiltInParameter.STRUCTURAL_BEND_DIR_ANGLE); p.Set(-p.AsDouble()); } sb.AppendLine("purlin roll sign flipped"); }
        // ---- lattice ends cut on the chord faces: a reference plane through the cut point, a «БК_срез» void (400×400×300 on its +normal side) into the chord
        var oldV = new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Symbol.FamilyName == "БК_срез" && (x.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "").StartsWith("БК_срез ферма")).Select(x => x.Id).ToList();
        oldV.AddRange(new FilteredElementCollector(d).OfClass(typeof(ReferencePlane)).Cast<ReferencePlane>().Where(r => (r.Name ?? "").StartsWith("БК_ферма_")).Select(r => r.Id));
        if (oldV.Count > 0) d.Delete(oldV);
        var vsym = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).Cast<FamilySymbol>().FirstOrDefault(x => x.FamilyName == "БК_срез");
        if (vsym == null) { Family vf = Load(d, fam + "БК_срез.rfa"); vsym = d.GetElement(vf.GetFamilySymbolIds().First()) as FamilySymbol; }
        if (!vsym.IsActive) vsym.Activate();
        var view3 = new FilteredElementCollector(d).OfClass(typeof(View3D)).Cast<View3D>().First(v => !v.IsTemplate);
        var ctsv = System.IO.Path.Combine(System.IO.Path.GetDirectoryName(tsv), "cuts.tsv"); int nCut = 0, nBad = 0; var vflip = new Dictionary<int, bool>();
        foreach (var c in System.IO.File.ReadAllLines(ctsv).Where(q => q.Trim().Length > 0).Select(q => q.Split('	')))
        {
            var mem = byRow[int.Parse(c[0])]; var Pp = P(Num(c[2]), Num(c[3]), Num(c[4])); var m = new XYZ(Num(c[5]), Num(c[6]), Num(c[7])).Normalize();
            var e1 = XYZ.BasisX; var e2 = m.CrossProduct(e1).Normalize(); int key = m.Z > 0 ? 1 : -1;
            FamilyInstance vi = null;
            foreach (var f in (vflip.ContainsKey(key) ? new[] { vflip[key] } : new[] { false, true }))
            {
                var a1 = f ? e2 : e1; var a2 = f ? e1 : e2;
                var rp = d.Create.NewReferencePlane2(Pp, Pp + a1, Pp + a2, view3); rp.Name = "БК_ферма_" + mem.Id.Value + "_" + c[1];
                vi = d.Create.NewFamilyInstance(rp.GetReference(), Pp, a1, vsym);
                vi.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.Set("БК_срез ферма " + mem.Id.Value);
                if (vflip.ContainsKey(key)) break;
                d.Regenerate();
                if (vi.GetTransform().BasisZ.DotProduct(m) > 0.99) { vflip[key] = f; break; }
                d.Delete(vi.Id); d.Delete(rp.Id); vi = null;
            }
            if (vi == null) { nBad++; continue; }
            try { InstanceVoidCutUtils.AddInstanceVoidCut(d, mem, vi); nCut++; } catch { nBad++; }
        }
        sb.AppendLine("lattice cuts " + nCut + ", failed " + nBad + ", flip rule " + string.Join(",", vflip.Select(k => k.Key + ":" + k.Value)));
        t.Commit();
        // placement checks: bbox of a sample per kind against the intended section
        foreach (var k in new[] { "Р1", "ФФ1 Р2", "БМ1", "Б3", "Пр1", "ГС1" })
        {
            var q = beams.FirstOrDefault(x => x.Item2[1] == k); if (q == null) continue; var bb = q.Item1.get_BoundingBox(null);
            sb.AppendLine("check " + k + ": line z " + q.Item2[6] + "…" + q.Item2[9] + ", bbox z " + Math.Round(bb.Min.Z / MM, 1) + "…" + Math.Round(bb.Max.Z / MM, 1) + ", y " + Math.Round(bb.Min.Y / MM, 1) + "…" + Math.Round(bb.Max.Y / MM, 1));
        }
        foreach (var k in new[] { "К1", "СФ", "К3" })
        {
            var q = colInst.FirstOrDefault(x => x.Item1.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString() == k); if (q == null) continue; var bb = q.Item1.get_BoundingBox(null);
            sb.AppendLine("check " + k + ": bbox x " + Math.Round(bb.Min.X / MM, 1) + "…" + Math.Round(bb.Max.X / MM, 1) + ", y " + Math.Round(bb.Min.Y / MM, 1) + "…" + Math.Round(bb.Max.Y / MM, 1) + ", z " + Math.Round(bb.Min.Z / MM, 1) + "…" + Math.Round(bb.Max.Z / MM, 1));
        }
    }
    sb.AppendLine("members " + cnt.Values.Sum() + ": " + string.Join(", ", cnt.Select(k => k.Key + " " + k.Value)));
    return sb.ToString();
