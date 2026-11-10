// Line annotation families with instance «Длина» (paper mm): БК_шов_заводской (ticks 1.5 мм, step 1), БК_шов_монтажный (crosses 0.9, step 1.2), БК_обрыв (zigzag centred, straight 1 мм pieces).
// Every mark is a set of real lines in subcategory «БК_шов_линия» (pen 1, 0.05 мм look), visible by formula «Длина > …».
var app = document.Application; var uiapp = new UIApplication(app);
string pd = @"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\uz_probe\";
string fdir = @"D:\Бекасыл КЖ КМ\_Стандарт_КЖ\семейства\";
string rft = @"C:\ProgramData\Autodesk\RVT 2025\Family Templates\English\Annotations\Metric Generic Annotation.rft";
double M = 1 / 304.8;
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder();
  foreach (var kind in new[] { "БК_шов_заводской", "БК_шов_монтажный", "БК_обрыв" }) {
  Document d = null;
  try {
    d = app.NewFamilyDocument(rft);
    View v = new FilteredElementCollector(d).OfClass(typeof(View)).Cast<View>().First(x => !x.IsTemplate && x.ViewType != ViewType.ProjectBrowser && x.ViewType != ViewType.SystemBrowser);
    using (var t = new Transaction(d, "f")) { t.Start();
      foreach (var id in new FilteredElementCollector(d).WhereElementIsNotElementType().ToElements().Where(x => x is TextNote || x is CurveElement).Select(x => x.Id).ToList()) { try { d.Delete(id); } catch { } }
      var cat = d.OwnerFamily.FamilyCategory;
      Category sc = null; foreach (Category c in cat.SubCategories) if (c.Name == "БК_шов_линия") sc = c;
      if (sc == null) sc = d.Settings.Categories.NewSubcategory(cat, "БК_шов_линия");
      sc.SetLineWeight(1, GraphicsStyleType.Projection); sc.LineColor = new Color(0, 0, 0);
      var gs = sc.GetGraphicsStyle(GraphicsStyleType.Projection);
      var fm = d.FamilyManager; if (fm.Types.Size == 0) fm.NewType(kind);
      var pL = fm.AddParameter("Длина", GroupTypeId.Geometry, SpecTypeId.Length, true);
      fm.Set(pL, 30 * M); var pE = fm.AddParameter("ед", GroupTypeId.Geometry, SpecTypeId.Length, false); fm.Set(pE, 0.05 * M);
      Func<XYZ, XYZ, DetailCurve> ln = (a, b) => { var c = d.FamilyCreate.NewDetailCurve(v, Line.CreateBound(a * M, b * M)); c.LineStyle = gs; return c; };
      int n = 0;
      Action<List<DetailCurve>, string> vis = (cs, formula) => {
        var p = fm.AddParameter("в" + (n++).ToString("000"), GroupTypeId.Graphics, SpecTypeId.Boolean.YesNo, true);
        fm.SetFormula(p, formula);
        foreach (var c in cs) fm.AssociateElementParameterToFamilyParameter(c.get_Parameter(BuiltInParameter.IS_VISIBLE_PARAM), p); };
      if (kind == "БК_шов_заводской") {
        for (int k = 0; k < 150; k++) { var x = 0.5 + k * 1.0; vis(new List<DetailCurve> { ln(new XYZ(x, 0, 0), new XYZ(x, 1.5, 0)) }, "Длина > ед * " + Math.Round((x + 0.4) / 0.05)); }
      } else if (kind == "БК_шов_монтажный") {
        for (int k = 0; k < 125; k++) { var x = 0.15 + k * 1.2; vis(new List<DetailCurve> { ln(new XYZ(x, 0.1, 0), new XYZ(x + 0.9, 1.0, 0)), ln(new XYZ(x, 1.0, 0), new XYZ(x + 0.9, 0.1, 0)) }, "Длина > ед * " + Math.Round((x + 1.0) / 0.05)); }
      } else {
        // zigzag centred at origin: width 3, height ±2.5 (paper mm)
        ln(new XYZ(-1.5, 0, 0), new XYZ(-0.75, 2.5, 0)); ln(new XYZ(-0.75, 2.5, 0), new XYZ(0.75, -2.5, 0)); ln(new XYZ(0.75, -2.5, 0), new XYZ(1.5, 0, 0));
        for (int k = 0; k < 150; k++) { double a = 1.5 + k, b = a + 1;
          vis(new List<DetailCurve> { ln(new XYZ(-b, 0, 0), new XYZ(-a, 0, 0)), ln(new XYZ(a, 0, 0), new XYZ(b, 0, 0)) }, "Длина > ед * " + Math.Round((2 * a + 0.5) / 0.05)); }
      }
      t.Commit(); sb.AppendLine(kind + " marks " + n); }
    d.SaveAs(fdir + kind + ".rfa", new SaveAsOptions { OverwriteExistingFile = true }); sb.AppendLine("saved " + fdir + kind + ".rfa");
  } catch (Exception ex) { sb.AppendLine(kind + " ERR " + ex); }
  try { if (d != null) d.Close(false); } catch { } }
  System.IO.File.WriteAllText(pd + "lines.txt", sb.ToString()); };
uiapp.Idling += hnd;
return "queued";
