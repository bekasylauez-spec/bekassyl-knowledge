var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\_probe4.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder();
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt"));
    sb.AppendLine("docs: " + string.Join(" | ", app.Documents.Cast<Document>().Select(d=>d.PathName)));
    const double M=304.8; var ds = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел" && x.ApplicationDataId=="база" && x.Name.StartsWith("База Б2")).ToList();
    foreach (var d in ds.Take(3)) { var b=d.get_BoundingBox(null); sb.AppendLine(d.Name.Substring(0,8)+" "+Math.Round(b.Min.X*M)+","+Math.Round(b.Min.Y*M)+","+Math.Round(b.Min.Z*M)+" -> "+Math.Round(b.Max.X*M)+","+Math.Round(b.Max.Y*M)+","+Math.Round(b.Max.Z*M)); }
    var v = new FilteredElementCollector(nd).OfClass(typeof(View3D)).Cast<View3D>().Where(x=>!x.IsTemplate).Select(x=>x.Name); sb.AppendLine("3D views: "+string.Join("; ",v));  } catch (Exception ex) { sb.AppendLine("ERR " + ex); }
  System.IO.File.WriteAllText(log, sb.ToString(), System.Text.Encoding.UTF8); };
uiapp.Idling += hnd;
return "queued";
}
static void _end() {
