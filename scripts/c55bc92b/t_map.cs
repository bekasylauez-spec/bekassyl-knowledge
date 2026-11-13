// MAPPING experiment: markers at nominal X, planes moved by d0 (or not), instance length Linst
var app = document.Application; var sb = new System.Text.StringBuilder();
string outDir = @"C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\";
string tpl = @"C:\ProgramData\Autodesk\RVT 2025\Family Templates\Russian\Метрическая система, несущий каркас - Балки и раскосы.rft";
foreach (Document dd in app.Documents.Cast<Document>().ToList()) if (dd.IsFamilyDocument) dd.Close(false);
double[] markers = { -3000, -2500, -2000, -1500, -1000, -500, 0, 500, 1000, 1500, 2000, 2500, 3000 };
foreach (var cfg in new[] { new[] { 0.0, 6608.24 }, new[] { 2054.12, 6608.24 }, new[] { 2054.12, 5000.0 } })
{
  double d0 = cfg[0], Linst = cfg[1]; string fpath = outDir + "t_map_" + (int)d0 + ".rfa"; var fd = app.NewFamilyDocument(tpl);
  try {
    using (var t = new Transaction(fd, "reset")) { t.Start(); var ex0 = new FilteredElementCollector(fd).OfClass(typeof(Extrusion)).ToElementIds(); if (ex0.Count > 0) fd.Delete(ex0); t.Commit(); }
    if (d0 > 0) using (var t = new Transaction(fd, "planes")) { t.Start();
      foreach (var nm in new[] { "Слева", "Элемент слева", "Стикер слева", "Справа", "Элемент справа", "Стикер справа" }) { var rp = new FilteredElementCollector(fd).OfClass(typeof(ReferencePlane)).Cast<ReferencePlane>().First(r => r.Name == nm); ElementTransformUtils.MoveElement(fd, rp.Id, new XYZ((nm.Contains("лева") ? -d0 : d0) / 304.8, 0, 0)); } t.Commit(); }
    using (var t = new Transaction(fd, "body")) { t.Start(); var plane = SketchPlane.Create(fd, Plane.CreateByNormalAndOrigin(XYZ.BasisY, XYZ.Zero));
      foreach (var m in markers) { var ca = new CurveArray(); double[] pts = { m - 10, 0, m + 10, 0, m + 10, -50, m - 10, -50 };
        for (int i = 0; i < 4; i++) ca.Append(Line.CreateBound(new XYZ(pts[2 * i] / 304.8, 0, pts[2 * i + 1] / 304.8), new XYZ(pts[(2 * i + 2) % 8] / 304.8, 0, pts[(2 * i + 3) % 8] / 304.8)));
        var aa = new CurveArrArray(); aa.Append(ca); var ex = fd.FamilyCreate.NewExtrusion(true, aa, plane, 1); ex.StartOffset = -50 / 304.8; ex.EndOffset = 50 / 304.8; }
      t.Commit(); }
    var fm = fd.FamilyManager; using (var t = new Transaction(fd, "t")) { t.Start(); if (fm.CurrentType == null) fm.NewType("T"); t.Commit(); }
    fd.SaveAs(fpath, new SaveAsOptions { OverwriteExistingFile = true });
  } finally { fd.Close(false); }
  var pd = app.NewProjectDocument(UnitSystem.Metric);
  try { Family fam; using (var t = new Transaction(pd, "load")) { t.Start(); pd.LoadFamily(fpath, out fam); t.Commit(); }
    var sym = pd.GetElement(fam.GetFamilySymbolIds().First()) as FamilySymbol; var lv = new FilteredElementCollector(pd).OfClass(typeof(Level)).Cast<Level>().First();
    using (var t = new Transaction(pd, "place")) { t.Start(); if (!sym.IsActive) sym.Activate(); pd.Regenerate();
      var fi = pd.Create.NewFamilyInstance(Line.CreateBound(new XYZ(0, 0, 0), new XYZ(Linst / 304.8, 0, 0)), sym, lv, Autodesk.Revit.DB.Structure.StructuralType.Beam); pd.Regenerate();
      var xs = new SortedSet<double>(); foreach (var go in fi.get_Geometry(new Options { DetailLevel = ViewDetailLevel.Fine })) { var gi = go as GeometryInstance; var objs = gi != null ? gi.GetInstanceGeometry().Cast<GeometryObject>() : new[] { go };
        foreach (var so in objs.OfType<Solid>()) foreach (Edge ed in so.Edges) foreach (var p in new[] { ed.AsCurve().GetEndPoint(0), ed.AsCurve().GetEndPoint(1) }) xs.Add(Math.Round(p.X * 304.8 - Linst / 2, 1)); }
      sb.AppendLine("d0=" + d0 + " Linst=" + Linst + "  actual X (rel. mid) of vertices: " + string.Join(" ", xs)); t.RollBack(); }
  } finally { pd.Close(false); }
}
return sb.ToString();
