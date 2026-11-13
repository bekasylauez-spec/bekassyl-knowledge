// РМЦ КМ: узелдер 1…4 суреттері -> _тексеру\ (PNG ≥ 2000 px). Тек көріністер жасайды (модель геометриясына тимейді), Revit ашық қалады. ЖАЗЫЛҒАН 13.11.2026.
// Іске қосу: go.ps1 -Name rmc_u_shots -Lib rmc_node_lib.cs ; тапсырма: C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\shots1.txt — әр жолда «<узел N> <орын>» (мысалы «1 6-A», «2 5-D», «3 6-A», «4 6-A»).
// Әр орынға: 3D екі қарама-қарсы жақтан (section box), разрез рама жазықтығында (x = рама, −X жақтан +X-ке қарау), көлденең разрез(тер) (план, кесу z-тері төменде), узел 2-ге қосымша: Λ-кесу (узел денелері мен ригельсіз колонна басы).
var d = document; var sb = new StringBuilder(); string outDir = @"D:\Бекасыл КЖ КМ\РМЦ_КМ\_тексеру\"; System.IO.Directory.CreateDirectory(outDir);
var req = System.IO.File.ReadAllLines(@"C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\shots1.txt").Select(l => l.Trim()).Where(l => l.Length > 0).ToList();
var jobs = new List<string[]>();   // view name, file
Dictionary<int, double[]> CUTZ = new Dictionary<int, double[]> { { 1, new[] { 8332.0 } }, { 2, new[] { 9300.0 } }, { 3, new[] { 9033.0, 8800.0 } }, { 4, new[] { 9328.0, 9090.0 } } };
using (var t = new Transaction(d, "РМЦ: узел суреттері"))
{
    t.Start(); var fo = t.GetFailureHandlingOptions(); fo.SetFailuresPreprocessor(new Swallow()); t.SetFailureHandlingOptions(fo);
    var vft3 = new FilteredElementCollector(d).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().First(x => x.ViewFamily == ViewFamily.ThreeDimensional);
    var vftS = new FilteredElementCollector(d).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().First(x => x.ViewFamily == ViewFamily.Section);
    var vftP = new FilteredElementCollector(d).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().First(x => x.ViewFamily == ViewFamily.FloorPlan);
    var levels = new FilteredElementCollector(d).OfClass(typeof(Level)).Cast<Level>().OrderBy(l => l.Elevation).ToList();
    Action<View> style = v => { v.DetailLevel = ViewDetailLevel.Fine; try { v.DisplayStyle = DisplayStyle.ShadingWithEdges; } catch { }
        foreach (var bc in new[] { BuiltInCategory.OST_Grids, BuiltInCategory.OST_Levels, BuiltInCategory.OST_SectionBox, BuiltInCategory.OST_Viewers, BuiltInCategory.OST_Cameras }) { try { v.SetCategoryHidden(new ElementId(bc), true); } catch { } } };
    Func<string, XYZ, XYZ, double[], View3D> mk3 = (nm, fwd, ctr, bb) => {
        var v = View3D.CreateIsometric(d, vft3.Id); v.Name = nm; var f = fwd.Normalize(); var up = (XYZ.BasisZ - f * f.DotProduct(XYZ.BasisZ)).Normalize(); var eye = ctr - f * (50000 * MM);
        v.SetOrientation(new ViewOrientation3D(eye, up, f)); style(v); var bx = new BoundingBoxXYZ(); bx.Min = P(bb[0], bb[1], bb[2]); bx.Max = P(bb[3], bb[4], bb[5]); v.SetSectionBox(bx); v.IsSectionBoxActive = true; return v; };
    var dsAll = new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел").ToList();
    foreach (var line in req)
    {
        var pr = line.Split(' '); int node = int.Parse(pr[0]); string loc = pr[1]; string row = loc.Split('-')[1]; int ax = AxisNo(0); ax = int.Parse(loc.Split('-')[0]); double fx = AXX[ax - 1];
        string key = "узел " + node; var mine = dsAll.Where(x => x.ApplicationDataId == key + " | " + loc).ToList();
        bool lam = pr.Length > 2 && pr[2] == "lambda"; string nmBase = lam ? "РМЦ_Λ-кесу " + node + " " + loc + " " : "РМЦ_узел " + node + " " + loc + " "; string fb = "Узел_" + node + "_" + loc + "_";
        var olds = new FilteredElementCollector(d).OfClass(typeof(View)).Cast<View>().Where(v => !v.IsTemplate && v.Name.StartsWith(nmBase)).Select(v => v.Id).ToList(); if (olds.Count > 0) d.Delete(olds);
        double[] g;
        if (mine.Count == 0 && !lam) { sb.AppendLine("SKIP " + line + ": DS жоқ"); continue; }
        if (mine.Count > 0) { var gb = mine.Select(x => x.get_BoundingBox(null)).Where(b => b != null).ToList(); g = new[] { gb.Min(b => b.Min.X) / MM, gb.Min(b => b.Min.Y) / MM, gb.Min(b => b.Min.Z) / MM, gb.Max(b => b.Max.X) / MM, gb.Max(b => b.Max.Y) / MM, gb.Max(b => b.Max.Z) / MM }; }
        else g = new[] { fx - 200, 17500.0, 8900, fx + 200, 18500, 9500 };
        double cx = (g[0] + g[3]) / 2, cy = (g[1] + g[4]) / 2, cz = (g[2] + g[5]) / 2; double s = row == "G" ? -1 : 1;
        double MXm = 330, MYm = 230, MZm = 230; var box = new[] { g[0] - MXm, g[1] - MYm, g[2] - MZm, g[3] + MXm, g[4] + MYm, g[5] + MZm };
        if (lam)
        {   // Λ-кесу: колонна басы; ригель мен узел денелері көрініссіз; 3D екі жақтан
            var col = new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().First(x => (x.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "") == "К1" && Math.Abs((x.Location as LocationPoint).Point.X / MM - fx) < 5 && Math.Abs((x.Location as LocationPoint).Point.Y / MM - 18000) < 5);
            var hide = new List<ElementId>(); var lbx = new[] { fx - 500, 17400.0, 9000, fx + 500, 18600, 9800 };
            var ol = new Outline(P(lbx[0], lbx[1], lbx[2]), P(lbx[3], lbx[4], lbx[5]));
            foreach (var e in new FilteredElementCollector(d).WherePasses(new BoundingBoxIntersectsFilter(ol)).WhereElementIsNotElementType()) { if (e.Id == col.Id) continue; if (e is DirectShape || (e is FamilyInstance fi && fi.Symbol.FamilyName != "БК_срез_плоскостью" && e.Category != null && e.Category.Id.Value == (long)BuiltInCategory.OST_StructuralFraming)) hide.Add(e.Id); }
            foreach (var sg in new[] { 1, -1 })
            {
                var v = mk3(nmBase + "Λ 3D " + (sg > 0 ? "1" : "2"), new XYZ(0.8 * sg, 0.55 * sg, -0.45), P(fx, 18000, 9250), new[] { fx - 260, 17650.0, 9000, fx + 260, 18350, 9400 });
                var hh = hide.Where(i => d.GetElement(i).CanBeHidden(v)).ToList(); if (hh.Count > 0) v.HideElements(hh); jobs.Add(new[] { v.Name, fb + "Λ_3D_" + (sg > 0 ? "1" : "2") });
            }
            continue;
        }
        // 3D екі қарама-қарсы жақтан
        XYZ f1, f2; if (row == "D") { f1 = new XYZ(1, 0.45, -0.5); f2 = new XYZ(-1, -0.45, -0.5); } else { f1 = new XYZ(0.6, s, -0.55); f2 = new XYZ(-0.6, -s, -0.55); }
        var v1 = mk3(nmBase + "3D 1", f1, P(cx, cy, cz), box); jobs.Add(new[] { v1.Name, fb + "3D_1" });
        var v2 = mk3(nmBase + "3D 2", f2, P(cx, cy, cz), box); jobs.Add(new[] { v2.Name, fb + "3D_2" });
        // разрез рама жазықтығында (x = рама): −X-тен +X-ке қарау: BasisX = −Y, BasisY = Z, BasisZ = −X
        {
            double hw = (g[4] - g[1]) / 2 + MYm, hh = (g[5] - g[2]) / 2 + MZm; var tr = Transform.Identity; tr.Origin = P(fx, cy, cz); tr.BasisX = -XYZ.BasisY; tr.BasisY = XYZ.BasisZ; tr.BasisZ = -XYZ.BasisX;
            var bxs = new BoundingBoxXYZ(); bxs.Transform = tr; bxs.Min = new XYZ(-hw * MM, -hh * MM, -250 * MM); bxs.Max = new XYZ(hw * MM, hh * MM, 0);
            var sec = ViewSection.CreateSection(d, vftS.Id, bxs); sec.Name = nmBase + "разрез в плоскости рамы"; sec.Scale = 10; style(sec); jobs.Add(new[] { sec.Name, fb + "разрез_плоскость_рамы" });
        }
        // көлденең разрездер (план)
        int ci = 0;
        foreach (double zc in CUTZ[node])
        {
            ci++;   // горизонталь разрез = 3D көрініс (ортогонал, жоғарыдан төмен), section box z-ті [zc − 450, zc] кеседі — zc-тен жоғарыны жасырады
            var vh = mk3(nmBase + "разрез горизонтальный z" + F(zc), new XYZ(0, 0.02, -1), P(cx, cy, zc - 200), new[] { box[0], box[1], zc - 450, box[3], box[4], zc }); jobs.Add(new[] { vh.Name, fb + "разрез_горизонтальный_z" + F(zc) });
        }
    }
    t.Commit();
}
var ids = new FilteredElementCollector(d).OfClass(typeof(View)).Cast<View>().Where(v => !v.IsTemplate).ToDictionary(v => v.Name, v => v.Id, StringComparer.Ordinal);
foreach (var j in jobs)
{
    var opt = new ImageExportOptions(); opt.ExportRange = ExportRange.SetOfViews; opt.SetViewsAndSheets(new List<ElementId> { ids[j[0]] }); opt.FilePath = outDir + j[1]; opt.FitDirection = FitDirectionType.Horizontal;
    opt.HLRandWFViewsFileType = ImageFileType.PNG; opt.ShadowViewsFileType = ImageFileType.PNG; opt.ImageResolution = ImageResolution.DPI_300; opt.PixelSize = 2800; opt.ZoomType = ZoomFitType.FitToPage;
    try { d.ExportImage(opt); foreach (var ff in System.IO.Directory.GetFiles(outDir, j[1] + " - *.png")) { string tgt = outDir + j[1] + ".png"; if (System.IO.File.Exists(tgt)) System.IO.File.Delete(tgt); System.IO.File.Move(ff, tgt); } sb.AppendLine("exported " + j[0]); } catch (Exception ex) { sb.AppendLine("EXPORT FAIL " + j[0] + ": " + ex.Message); }
}
d.Save();
foreach (var j in jobs) { string f = outDir + j[1] + ".png"; if (!System.IO.File.Exists(f)) { sb.AppendLine("  ЖОҚ: " + f); continue; } var h = new byte[24]; using (var fs = System.IO.File.OpenRead(f)) fs.Read(h, 0, 24); int w = (h[16] << 24) | (h[17] << 16) | (h[18] << 8) | h[19], hh = (h[20] << 24) | (h[21] << 16) | (h[22] << 8) | h[23]; sb.AppendLine("  " + System.IO.Path.GetFileName(f) + " " + w + "x" + hh + " px, " + new System.IO.FileInfo(f).Length + " bytes"); }
return sb.ToString();
}
