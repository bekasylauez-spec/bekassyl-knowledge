// Алатау: close-up 3D PNGs. Boxes come from _авто\revit\_audit_shots.txt, one per line: name x0 y0 z0 x1 y1 z1 fx fy fz (mm; f = view direction).
// A 3D view «КМ проверка» is reused (section box + orientation), scale 1:10, shaded with thin black edges; PNGs go to _тексеру\.
var app = document.Application; var uiapp = new UIApplication(app);
string root = @"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder();
  try {
    var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt"));
    var ci = System.Globalization.CultureInfo.InvariantCulture;
    foreach (var line in System.IO.File.ReadAllLines(root + @"shots.txt").Where(l => l.Trim().Length > 0 && !l.StartsWith("#")))
    {
        var f = line.Split(new[] { ' ' }, StringSplitOptions.RemoveEmptyEntries); var v = f.Skip(1).Select(x => double.Parse(x, ci)).ToArray();
        View3D v3;
        using (var t = new Transaction(nd, "проверка"))
        {
            t.Start();
            v3 = new FilteredElementCollector(nd).OfClass(typeof(View3D)).Cast<View3D>().FirstOrDefault(x => !x.IsTemplate && x.Name == "КМ проверка audit")
              ?? View3D.CreateIsometric(nd, new FilteredElementCollector(nd).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().First(x => x.ViewFamily == ViewFamily.ThreeDimensional).Id);
            v3.Name = "КМ проверка audit"; v3.DetailLevel = ViewDetailLevel.Fine; v3.DisplayStyle = DisplayStyle.ShadingWithEdges; v3.Scale = 10; v3.CropBoxActive = false;
            foreach (var bic in new[] { BuiltInCategory.OST_Levels, BuiltInCategory.OST_Grids, BuiltInCategory.OST_CLines, BuiltInCategory.OST_SectionBox })
            { var c = Category.GetCategory(nd, bic); if (c != null && v3.CanCategoryBeHidden(c.Id)) v3.SetCategoryHidden(c.Id, true); }
            var black = new Color(0, 0, 0);
            foreach (var bic in new[] { BuiltInCategory.OST_StructuralFraming, BuiltInCategory.OST_StructuralColumns, BuiltInCategory.OST_StructConnections, BuiltInCategory.OST_StructConnectionBolts, BuiltInCategory.OST_StructConnectionWelds })
            { var o = new OverrideGraphicSettings(); o.SetProjectionLineColor(black); o.SetProjectionLineWeight(1); try { v3.SetCategoryOverrides(new ElementId(bic), o); } catch { } }
            v3.SetSectionBox(new BoundingBoxXYZ { Min = new XYZ(v[0], v[1], v[2]) * MM, Max = new XYZ(v[3], v[4], v[5]) * MM });
            var fw = new XYZ(v[6], v[7], v[8]).Normalize(); var right = fw.CrossProduct(XYZ.BasisZ).Normalize(); var up = right.CrossProduct(fw).Normalize();
            var ctr = new XYZ((v[0] + v[3]) / 2, (v[1] + v[4]) / 2, (v[2] + v[5]) / 2) * MM;
            v3.SetOrientation(new ViewOrientation3D(ctr - fw * 100, up, fw));
            t.Commit();
        }
        var opt = new ImageExportOptions { FilePath = root + @"png\" + f[0], ExportRange = ExportRange.SetOfViews, ZoomType = ZoomFitType.FitToPage, PixelSize = 1600,
            ImageResolution = ImageResolution.DPI_150, HLRandWFViewsFileType = ImageFileType.PNG, ShadowViewsFileType = ImageFileType.PNG, FitDirection = FitDirectionType.Horizontal };
        opt.SetViewsAndSheets(new List<ElementId> { v3.Id }); nd.ExportImage(opt); sb.AppendLine("shot " + f[0]);
    }
  } catch (Exception ex) { sb.AppendLine("ERR " + ex); }
  System.IO.File.WriteAllText(root + @"shot_log.txt", sb.ToString()); };
uiapp.Idling += hnd;
return "queued";
}
