var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\_del.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; string r;
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt"));
    var v = new FilteredElementCollector(nd).OfClass(typeof(View3D)).Cast<View3D>().Where(x => x.Name == "КМ проверка audit C").ToList(); int n = 0;
    using (var t = new Transaction(nd, "del")) { t.Start(); foreach (var x in v) { nd.Delete(x.Id); n++; } t.Commit(); }
    r = "deleted " + n + "; remaining 3D: " + string.Join("; ", new FilteredElementCollector(nd).OfClass(typeof(View3D)).Cast<View3D>().Select(x => x.Name)); }
  catch (Exception ex) { r = "ERR " + ex; }
  System.IO.File.WriteAllText(log, r, System.Text.Encoding.UTF8); };
uiapp.Idling += hnd;
return "queued";
}
static void _end() {
