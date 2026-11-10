var uiapp = new UIApplication(document.Application);
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder(); var d = uiapp.ActiveUIDocument.Document;
  try { using (var t = new Transaction(d, "БК стиль КМ")) { t.Start(); BKStyle.Setup(d, @"D:\РАБОЧКА\Узлы_КМ\Семейства", sb); t.Commit(); }
    foreach (var f in new[] { "БК_узел_круг", "БК_обрыв", "БК_шов_заводской", "БК_шов_монтажный", "БК_шов_угол", "БК_типовая_аннотация_текст_с_выноской" }) { var fam = new FilteredElementCollector(d).OfClass(typeof(Family)).Cast<Family>().FirstOrDefault(x => x.Name == f); if (fam == null) { sb.AppendLine(f + " none"); continue; }
      var sy = (FamilySymbol)d.GetElement(fam.GetFamilySymbolIds().First()); var inst = new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().FirstOrDefault(x => x.Symbol.Family.Id == fam.Id);
      sb.AppendLine(f + " types: " + string.Join(",", fam.GetFamilySymbolIds().Select(i => d.GetElement(i).Name)) + " | inst params: " + (inst == null ? "-" : string.Join(",", inst.Parameters.Cast<Parameter>().Where(p => !p.IsReadOnly && p.Definition != null).Select(p => p.Definition.Name).Distinct().Take(12)))); }
  } catch (Exception ex) { sb.AppendLine("ERR " + ex); }
  System.IO.File.WriteAllText(@"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\bk\bk.txt", sb.ToString()); };
uiapp.Idling += hnd; return "queued";
