// БК_узел_круг from a copy of БК_типовая_аннотация_текст_с_выноской: circle Ø13 + horizontal diameter line, number above, sheet below (3.5 мм).
var app = document.Application; var uiapp = new UIApplication(app);
string pd = @"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\uz_probe\";
string dst = @"D:\Бекасыл КЖ КМ\_Стандарт_КЖ\семейства\БК_узел_круг.rfa";
double M = 1 / 304.8;
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder(); Document d = null;
  try {
    d = app.OpenDocumentFile(pd + @"fam\БК_типовая_аннотация_текст_с_выноской.rfa");
    View v = new FilteredElementCollector(d).OfClass(typeof(View)).Cast<View>().First(x => !x.IsTemplate && x.ViewType != ViewType.ProjectBrowser && x.ViewType != ViewType.SystemBrowser);
    using (var t = new Transaction(d, "krug")) { t.Start();
      var fm = d.FamilyManager;
      var del = new FilteredElementCollector(d).WhereElementIsNotElementType().ToElements().Where(x => x is CurveElement || x is Dimension).Select(x => x.Id).ToList();
      foreach (var id in del) { try { d.Delete(id); } catch { } }
      var pw = fm.get_Parameter("Ширина полки"); if (pw != null) fm.RemoveParameter(pw);
      fm.RenameParameter(fm.get_Parameter("Текст верх"), "Номер узла");
      fm.RenameParameter(fm.get_Parameter("Текст низ"), "Лист схемы");
      double r = 6.5 * M;
      d.FamilyCreate.NewDetailCurve(v, Arc.Create(new XYZ(0, 0, 0), r, 0, Math.PI, XYZ.BasisX, XYZ.BasisY));
      d.FamilyCreate.NewDetailCurve(v, Arc.Create(new XYZ(0, 0, 0), r, Math.PI, 2 * Math.PI, XYZ.BasisX, XYZ.BasisY));
      d.FamilyCreate.NewDetailCurve(v, Line.CreateBound(new XYZ(-r, 0, 0), new XYZ(r, 0, 0)));
      // label type 3.5 mm
      var labs = new FilteredElementCollector(d).OfClass(typeof(TextElement)).Cast<TextElement>().ToList();
      var tt0 = (TextElementType)d.GetElement(labs[0].GetTypeId());
      var t35 = new FilteredElementCollector(d).OfClass(typeof(TextElementType)).Cast<TextElementType>().FirstOrDefault(x => x.Name == "3.5 мм") ?? (TextElementType)tt0.Duplicate("3.5 мм");
      t35.get_Parameter(BuiltInParameter.TEXT_SIZE).Set(3.5 * M);
      foreach (var lb in labs) { lb.ChangeTypeId(t35.Id);
        sb.AppendLine("label '" + lb.Text.Trim() + "' coord " + Math.Round(lb.Coord.X/M,2) + "," + Math.Round(lb.Coord.Y/M,2) + " halign " + lb.HorizontalAlignment + " valign " + lb.VerticalAlignment + " w " + Math.Round(lb.Width/M,2)); }
      t.Commit(); }
    using (var t = new Transaction(d, "pos")) { t.Start();
      foreach (var lb in new FilteredElementCollector(d).OfClass(typeof(TextElement)).Cast<TextElement>()) {
        bool top = lb.Text.Contains("верх") || lb.Text.Contains("Номер");
        lb.HorizontalAlignment = HorizontalTextAlignment.Center; lb.VerticalAlignment = top ? VerticalTextAlignment.Bottom : VerticalTextAlignment.Top;
        // Coord = the label's insertion point (centre of its box); text 3.5 -> box ~3.5 high: centre 2.9 above / below the diameter line
        var want = top ? new XYZ(0, 2.9 * M, 0) : new XYZ(0, -2.9 * M, 0);
        lb.HorizontalAlignment = HorizontalTextAlignment.Center; lb.VerticalAlignment = VerticalTextAlignment.Middle;
        ElementTransformUtils.MoveElement(d, lb.Id, want - lb.Coord);
        sb.AppendLine((top ? "top " : "bot ") + "coord " + Math.Round(lb.Coord.X / M, 2) + "," + Math.Round(lb.Coord.Y / M, 2) + " w " + Math.Round(lb.Width / M, 2));
        lb.Width = 10 * M;
      }
      t.Commit(); }
    d.SaveAs(dst, new SaveAsOptions { OverwriteExistingFile = true }); sb.AppendLine("saved " + dst);
  } catch (Exception ex) { sb.AppendLine("ERR " + ex); }
  try { if (d != null) d.Close(false); } catch { }
  System.IO.File.WriteAllText(pd + "krug.txt", sb.ToString()); };
uiapp.Idling += hnd;
return "queued";
