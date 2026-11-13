// TEST v2 families in a throw-away project doc
var app = document.Application; var sb = new System.Text.StringBuilder(); string fam = @"C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\";
var pd = app.NewProjectDocument(UnitSystem.Metric);
try {
  var lv = new FilteredElementCollector(pd).OfClass(typeof(Level)).Cast<Level>().First();
  Func<string, double[], double[], double, string> test = (file, a, b, wantX) => {
    Family f; using (var t = new Transaction(pd, "load")) { t.Start(); pd.LoadFamily(fam + file, out f); t.Commit(); }
    var sym = pd.GetElement(f.GetFamilySymbolIds().First()) as FamilySymbol; string res = "";
    using (var t = new Transaction(pd, "place")) { t.Start(); if (!sym.IsActive) sym.Activate(); pd.Regenerate();
      var fi = pd.Create.NewFamilyInstance(Line.CreateBound(new XYZ(a[0] / 304.8, a[1] / 304.8, a[2] / 304.8), new XYZ(b[0] / 304.8, b[1] / 304.8, b[2] / 304.8)), sym, lv, Autodesk.Revit.DB.Structure.StructuralType.Beam);
      fi.get_Parameter(BuiltInParameter.Z_JUSTIFICATION).Set((int)Autodesk.Revit.DB.Structure.ZJustification.Top); pd.Regenerate();
      var pts = new SortedSet<string>(); double vol = 0;
      foreach (var go in fi.get_Geometry(new Options { DetailLevel = ViewDetailLevel.Fine })) { var gi = go as GeometryInstance; var objs = gi != null ? gi.GetInstanceGeometry().Cast<GeometryObject>() : new[] { go };
        foreach (var so in objs.OfType<Solid>()) { vol += so.Volume; foreach (Edge ed in so.Edges) foreach (var p in new[] { ed.AsCurve().GetEndPoint(0), ed.AsCurve().GetEndPoint(1) }) if (Math.Abs(p.X * 304.8 - wantX) < 0.5) pts.Add(string.Format("{0,9:0.00} {1,9:0.00}", p.Y * 304.8, p.Z * 304.8)); } }
      res = file + " vol(mm3)=" + Math.Round(vol * Math.Pow(304.8, 3)) + "\n  (y z) at x=" + wantX + ":\n  " + string.Join("\n  ", pts); t.RollBack(); }
    return res; };
  sb.AppendLine(test("TEST_Б1_двутавр_сварной.rfa", new double[] { 150, 0, 8968 }, new double[] { 150, 6600, 9298 }, 275));
  sb.AppendLine(test("TEST_Б3_двутавр_сварной.rfa", new double[] { 150, 12500, 9593 }, new double[] { 150, 17990, 9867.5 }, 325));
  sb.AppendLine(test("TEST_Б5L5804_двутавр_сварной.rfa", new double[] { 275, 4000, 3900 }, new double[] { 6079, 4000, 3900 }, 275 + 100 - 100));
} finally { pd.Close(false); }
return sb.ToString();
