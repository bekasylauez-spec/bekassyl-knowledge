var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\diag_grid.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder();
  try { var d = app.Documents.Cast<Document>().First(x => x.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt"));
    foreach (Grid g in new FilteredElementCollector(d).OfClass(typeof(Grid))) { var c = g.Curve; sb.AppendLine("grid " + g.Name + " " + (c.GetEndPoint(0)/MM) + " " + (c.GetEndPoint(1)/MM)); }
    var mem = System.IO.File.ReadAllLines(@"D:\Бекасыл КЖ КМ\Завод_В109_КМ\_авто\revit\members.tsv").Where(l => l.StartsWith("C\t")).Select(l => l.Split('\t')).ToList();
    int bad = 0;
    foreach (FamilyInstance fi in new FilteredElementCollector(d).OfCategory(BuiltInCategory.OST_StructuralColumns).WhereElementIsNotElementType().Cast<FamilyInstance>()) {
      var lp = fi.Location as LocationPoint; if (lp == null) continue; var p = lp.Point / MM;
      bool ok = mem.Any(m => Math.Abs(double.Parse(m[4], System.Globalization.CultureInfo.InvariantCulture) - p.X) < 1 && Math.Abs(double.Parse(m[5], System.Globalization.CultureInfo.InvariantCulture) - p.Y) < 1);
      if (!ok) { bad++; sb.AppendLine("MOVED " + fi.Id + " " + fi.Symbol.Name + " " + p); } }
    sb.AppendLine("moved columns " + bad);
  } catch (Exception ex) { sb.AppendLine("ERR " + ex); }
  System.IO.File.WriteAllText(log, sb.ToString()); };
uiapp.Idling += hnd;
return "queued";
}
