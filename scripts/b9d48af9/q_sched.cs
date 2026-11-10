var uiapp = new UIApplication(document.Application);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\sched.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder(); var d = uiapp.ActiveUIDocument.Document;
  try { using (var t = new Transaction(d, "probe")) { t.Start();
      foreach (var cid in new[] { ElementId.InvalidElementId, new ElementId(BuiltInCategory.OST_StructuralFraming) }) {
        var vs = ViewSchedule.CreateSchedule(d, cid); sb.AppendLine("== " + (cid == ElementId.InvalidElementId ? "multi" : "framing"));
        foreach (var f in vs.Definition.GetSchedulableFields()) sb.AppendLine("  " + f.GetName(d) + " | " + f.FieldType + " | " + f.ParameterId); }
      foreach (var sc in new FilteredElementCollector(d).OfClass(typeof(ViewSchedule)).Cast<ViewSchedule>().Where(x => !x.IsTitleblockRevisionSchedule && !x.IsTemplate).Take(30)) sb.AppendLine("EXIST " + sc.Name);
      t.RollBack(); }
  } catch (Exception ex) { sb.AppendLine("ERR " + ex.Message); }
  System.IO.File.WriteAllText(log, sb.ToString()); };
uiapp.Idling += hnd; return "queued";
