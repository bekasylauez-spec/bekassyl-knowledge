var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\fix_gridA.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder();
  try { var d = app.Documents.Cast<Document>().First(x => x.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt"));
    var g = new FilteredElementCollector(d).OfClass(typeof(Grid)).Cast<Grid>().First(q => q.Name == "A");
    var c = g.Curve; var p0 = c.GetEndPoint(0);
    using (var t = new Transaction(d, "ось A на место")) { t.Start();
      ElementTransformUtils.MoveElement(d, g.Id, new XYZ(-12000 * MM - p0.X, 0 - p0.Y, 0));
      t.Commit(); }
    var c2 = g.Curve; sb.AppendLine("A " + c2.GetEndPoint(0) / MM + " " + c2.GetEndPoint(1) / MM);
    var col = d.GetElement(new ElementId(2974449L)); sb.AppendLine("К1 " + ((LocationPoint)col.Location).Point / MM);
    d.Save(); sb.AppendLine("saved");
  } catch (Exception ex) { sb.AppendLine("ERR " + ex); }
  System.IO.File.WriteAllText(log, sb.ToString()); };
uiapp.Idling += hnd;
return "queued";
}
