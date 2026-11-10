var uiapp = new UIApplication(document.Application);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\g7b.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder(); var d = uiapp.ActiveUIDocument.Document; double M = 1 / 304.8;
  try {
    var v = new FilteredElementCollector(d).OfClass(typeof(ViewPlan)).Cast<ViewPlan>().First(x => x.Name == "КМ Схема распорок и вертикальных связей");
    var g1 = new FilteredElementCollector(d).OfClass(typeof(Grid)).Cast<Grid>().First();
    var ex = g1.GetExtents(); sb.AppendLine("grid extents z " + ex.MinimumPoint.Z / M + " .. " + ex.MaximumPoint.Z / M);
    using (var t = new Transaction(d, "probe")) { t.Start();
      foreach (var cut in new[] { 300.0, 5000, 9000, 10500, 14400 }) { var vr = v.GetViewRange(); vr.SetOffset(PlanViewPlane.TopClipPlane, (cut + 500) * M); vr.SetOffset(PlanViewPlane.CutPlane, cut * M); vr.SetOffset(PlanViewPlane.BottomClipPlane, (cut - 200) * M); vr.SetOffset(PlanViewPlane.ViewDepthPlane, (cut - 200) * M); v.SetViewRange(vr); d.Regenerate();
        sb.AppendLine("cut " + cut + " grids " + new FilteredElementCollector(d, v.Id).OfClass(typeof(Grid)).GetElementCount()); }
      t.RollBack(); }
  } catch (Exception ex) { sb.AppendLine("ERR " + ex.Message); }
  System.IO.File.WriteAllText(log, sb.ToString()); };
uiapp.Idling += hnd; return "queued";
