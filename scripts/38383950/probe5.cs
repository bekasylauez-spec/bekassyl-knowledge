var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\_probe5.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder();
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt"));
    sb.AppendLine("docs: " + string.Join(" | ", app.Documents.Cast<Document>().Select(d=>d.PathName)));
    var all = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().ToList();
    sb.AppendLine("шов решётки: " + all.Count(x => x.Name.StartsWith("шов решётки")) + "; Заглушка НП: " + all.Count(x => x.Name.StartsWith("Заглушка НП")));
    sb.AppendLine("DS name groups: " + string.Join("; ", all.GroupBy(x => System.Text.RegularExpressions.Regex.Replace(x.Name, @"[\d×x.,−-]+.*$", "").Trim()).OrderByDescending(g => g.Count()).Take(25).Select(g => g.Key + " " + g.Count())));  } catch (Exception ex) { sb.AppendLine("ERR " + ex); }
  System.IO.File.WriteAllText(log, sb.ToString(), System.Text.Encoding.UTF8); };
uiapp.Idling += hnd;
return "queued";
}
static void _end() {
