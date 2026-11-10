var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\_purge.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder();
  try {
    var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt"));
    var used = new HashSet<long>();
    foreach (var el in new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance))) { var fi = el as FamilyInstance; if (fi != null && fi.Symbol != null) used.Add(fi.Symbol.Family.Id.Value); }
    using (var t = new Transaction(nd, "purge БК_паз")) { t.Start();
      foreach (var f in new FilteredElementCollector(nd).OfClass(typeof(Family)).Cast<Family>().Where(x => x.Name.StartsWith("БК_паз")).ToList())
      { if (used.Contains(f.Id.Value)) { sb.AppendLine("keep " + f.Name); continue; } var nm = f.Name; try { nd.Delete(f.Id); sb.AppendLine("deleted " + nm); } catch (Exception ex) { sb.AppendLine("fail " + f.Name + " " + ex.Message); } }
      t.Commit(); }
    nd.Save(); sb.AppendLine("saved");
  } catch (Exception ex) { sb.AppendLine("ERR " + ex); }
  System.IO.File.WriteAllText(log, sb.ToString()); };
uiapp.Idling += hnd;
return "queued";

