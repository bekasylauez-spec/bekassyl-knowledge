var uiapp = new UIApplication(document.Application);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\dims6b.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder(); var d = uiapp.ActiveUIDocument.Document; double M = 1 / 304.8;
  try {
    var v = new FilteredElementCollector(d).OfClass(typeof(ViewPlan)).Cast<ViewPlan>().First(x => x.Name == "КМ Схема расположения колонн и вертикальных связей");
    var dm = new FilteredElementCollector(d).OfClass(typeof(Dimension)).Cast<Dimension>().Where(x => x.OwnerViewId == v.Id).Skip(10).First();
    sb.AppendLine("hidden? " + dm.IsHidden(v) + " cat hidden " + v.GetCategoryHidden(dm.Category.Id));
    foreach (Reference r in dm.References) { var el = d.GetElement(r); sb.AppendLine("  ref " + el?.GetType().Name + " " + el?.Name + " hidden " + el?.IsHidden(v) + " cat " + el?.Category?.Name + " owner " + el?.OwnerViewId); }
    using (var t = new Transaction(d, "probe")) { t.Start();
      foreach (var cn in new[] { "Соединения несущих конструкций", "Перекрытия", "Стены", "Болты", "Обобщенные модели", "Сварные швы" }) { var c = d.Settings.Categories.Cast<Category>().FirstOrDefault(x => x.Name == cn); if (c != null && v.GetCategoryHidden(c.Id)) { v.SetCategoryHidden(c.Id, false); d.Regenerate(); sb.AppendLine("unhide " + cn + " -> visible dims " + new FilteredElementCollector(d, v.Id).OfClass(typeof(Dimension)).GetElementCount()); } }
      t.RollBack(); }
  } catch (Exception ex) { sb.AppendLine("ERR " + ex.Message); }
  System.IO.File.WriteAllText(log, sb.ToString()); };
uiapp.Idling += hnd; return "queued";
