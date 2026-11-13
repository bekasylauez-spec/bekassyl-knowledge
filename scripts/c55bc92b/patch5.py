P = r'D:\Бекасыл КЖ КМ\РМЦ_КМ\_авто\rmc_90_check.cs'
s = open(r'D:\Бекасыл КЖ КМ\РМЦ_КМ\_авто\_v1\rmc_90_check.cs', encoding='utf-8').read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:70])
    s = s.replace(old, new)
rep("// РМЦ КМ каркасы: модельді оқу (model_dump.tsv) + қиылысу (clash.tsv). Тек оқиды, модельді өзгертпейді.",
    "// РМЦ КМ каркасы (v2): модельді оқу (model_dump.tsv, bbox = ГЕОМЕТРИЯ төбелерінен) + қиылысу (clash.tsv): каркас×каркас және каркас×база денелері (DirectShape БК_узел / БК_ЖБ). Тек оқиды, модельді өзгертпейді.")
# geometry-based bbox
rep("""    var bb = fi.get_BoundingBox(null); var sl = SolidsOf(fi); double vol = sl.Sum(s => s.Volume) * Math.Pow(304.8, 3);""",
    """    var sl = SolidsOf(fi); double vol = sl.Sum(s => s.Volume) * Math.Pow(304.8, 3); var gv = Vtx(sl); BoundingBoxXYZ bb = null;
    if (gv.Count > 0) { bb = new BoundingBoxXYZ(); bb.Min = new XYZ(gv.Min(v => v.X), gv.Min(v => v.Y), gv.Min(v => v.Z)); bb.Max = new XYZ(gv.Max(v => v.X), gv.Max(v => v.Y), gv.Max(v => v.Z)); }""")
# base bodies appended before the dump is written
rep("""System.IO.File.WriteAllLines(auto + "model_dump.tsv", lines, new System.Text.UTF8Encoding(false));""",
    """int nFrame = k;
// база денелері (clash үшін ғана, dump-қа кірмейді)
var baseDs = new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел" || x.ApplicationId == "БК_ЖБ").ToList();
foreach (var ds in baseDs) { var sl2 = SolidsOf(ds); var gv2 = Vtx(sl2); if (gv2.Count == 0) continue; int idn2 = k++; solids[idn2] = sl2; info[idn2] = "БАЗА|" + ds.ApplicationDataId + " " + ds.Name;
    bbs[idn2] = new[] { gv2.Min(v => v.X), gv2.Min(v => v.Y), gv2.Min(v => v.Z), gv2.Max(v => v.X), gv2.Max(v => v.Y), gv2.Max(v => v.Z) }; }
sb.AppendLine("base bodies for clash: " + (k - nFrame));
System.IO.File.WriteAllLines(auto + "model_dump.tsv", lines, new System.Text.UTF8Encoding(false));""")
# skip base x base pairs
rep("""        pairs++; double v = 0;""", """        if (ord[a] >= nFrame && ord[c] >= nFrame) continue;
        pairs++; double v = 0;""")
open(P, 'w', encoding='utf-8').write(s)
print('ok')
