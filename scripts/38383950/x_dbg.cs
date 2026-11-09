var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\x_dbg_out.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder();
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt"));
    var D = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел" && x.Name.Contains("6000 A 1") && x.Name.Contains("20Ш1")).ToList();
    foreach (var d in D) { sb.AppendLine(d.Name + " | cat " + d.Category?.Name);
      foreach (var go in d.get_Geometry(new Options { DetailLevel = ViewDetailLevel.Fine })) { sb.AppendLine("  " + go.GetType().Name);
        IEnumerable<GeometryObject> objs = go is GeometryInstance gi ? gi.GetInstanceGeometry().Cast<GeometryObject>() : new[] { go };
        foreach (var o in objs.OfType<Solid>().Take(6)) { var b = o.GetBoundingBox(); sb.AppendLine("   solid vol " + o.Volume + " bb " + Math.Round(b.Min.X*304.8,1)+","+Math.Round(b.Min.Y*304.8,1)+","+Math.Round(b.Min.Z*304.8,1)+" - "+Math.Round(b.Max.X*304.8,1)+","+Math.Round(b.Max.Y*304.8,1)+","+Math.Round(b.Max.Z*304.8,1)); } } }
  } catch (Exception ex) { sb.AppendLine("ERR " + ex); }
  System.IO.File.WriteAllText(log, sb.ToString()); };
uiapp.Idling += hnd;
return "queued";
}
static void _e() {