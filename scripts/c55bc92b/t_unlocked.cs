// TEST: unlocked geometry placement in a beam family (new project doc, nothing saved to the model)
var app = document.Application; var sb = new System.Text.StringBuilder();
string outDir = @"C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\"; 
string tpl = @"C:\ProgramData\Autodesk\RVT 2025\Family Templates\Russian\Метрическая система, несущий каркас - Балки и раскосы.rft";
foreach (Document dd in app.Documents.Cast<Document>().ToList()) if (dd.IsFamilyDocument || (dd.PathName == "" && !dd.IsFamilyDocument)) { try { dd.Close(false); } catch { } }
var fd = app.NewFamilyDocument(tpl);
string fpath = outDir + "t_unlocked.rfa";
try {
  var vLen = new FilteredElementCollector(fd).OfClass(typeof(View)).Cast<View>().First(v => v.ViewType == ViewType.FloorPlan && v.Name == "Опорный уровень");
  using (var t = new Transaction(fd, "reset")) { t.Start(); var ex0 = new FilteredElementCollector(fd).OfClass(typeof(Extrusion)).ToElementIds(); if (ex0.Count > 0) fd.Delete(ex0); t.Commit(); }
  using (var t = new Transaction(fd, "body")) { t.Start();
    var plane = SketchPlane.Create(fd, Plane.CreateByNormalAndOrigin(XYZ.BasisY, XYZ.Zero));
    // unlocked box: X 100..700 (nominal), Z -50..0, width 100
    var ca = new CurveArray(); double[] pts = { 100, 0, 700, 0, 700, -50, 100, -50 };
    for (int i = 0; i < 4; i++) ca.Append(Line.CreateBound(new XYZ(pts[2*i]/304.8, 0, pts[2*i+1]/304.8), new XYZ(pts[(2*i+2)%8]/304.8, 0, pts[(2*i+3)%8]/304.8)));
    var aa = new CurveArrArray(); aa.Append(ca); var ex = fd.FamilyCreate.NewExtrusion(true, aa, plane, 1); ex.StartOffset = -50 / 304.8; ex.EndOffset = 50 / 304.8;
    t.Commit(); }
  var fm = fd.FamilyManager; using (var t = new Transaction(fd, "t")) { t.Start(); if (fm.CurrentType == null) fm.NewType("T"); t.Commit(); }
  fd.SaveAs(fpath, new SaveAsOptions { OverwriteExistingFile = true });
} finally { fd.Close(false); }
var pd = app.NewProjectDocument(UnitSystem.Metric);
try {
  Family fam; using (var t = new Transaction(pd, "load")) { t.Start(); pd.LoadFamily(fpath, out fam); t.Commit(); }
  var sym = pd.GetElement(fam.GetFamilySymbolIds().First()) as FamilySymbol;
  var lv = new FilteredElementCollector(pd).OfClass(typeof(Level)).Cast<Level>().First();
  foreach (var len in new double[] { 6000, 3000 })
  using (var t = new Transaction(pd, "place")) { t.Start(); if (!sym.IsActive) sym.Activate(); pd.Regenerate();
    var fi = pd.Create.NewFamilyInstance(Line.CreateBound(new XYZ(1000 / 304.8, 500 / 304.8, 0), new XYZ((1000 + len) / 304.8, 500 / 304.8, 0)), sym, lv, Autodesk.Revit.DB.Structure.StructuralType.Beam);
    fi.get_Parameter(BuiltInParameter.Z_JUSTIFICATION).Set((int)Autodesk.Revit.DB.Structure.ZJustification.Top);
    pd.Regenerate(); var bb = fi.get_BoundingBox(null);
    sb.AppendLine("len " + len + " bbox X " + Math.Round(bb.Min.X * 304.8, 1) + ".." + Math.Round(bb.Max.X * 304.8, 1) + " Y " + Math.Round(bb.Min.Y * 304.8, 1) + ".." + Math.Round(bb.Max.Y * 304.8, 1) + " Z " + Math.Round(bb.Min.Z * 304.8, 1) + ".." + Math.Round(bb.Max.Z * 304.8, 1));
    t.RollBack(); }
} finally { pd.Close(false); }
return sb.ToString();
