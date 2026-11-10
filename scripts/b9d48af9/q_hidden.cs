var sb = new System.Text.StringBuilder(); var d = document;
var fr = new FilteredElementCollector(d).WhereElementIsNotElementType().ToElements().Where(x => x.Category != null && (x.Category.Id.Value == (long)BuiltInCategory.OST_StructuralFraming || x.Category.Id.Value == (long)BuiltInCategory.OST_StructuralColumns)).ToList();
foreach (var sh in new FilteredElementCollector(d).OfClass(typeof(ViewSheet)).Cast<ViewSheet>().Where(x => { int n; return int.TryParse(x.SheetNumber, out n) && n >= 5 && n <= 13; }).OrderBy(x => int.Parse(x.SheetNumber)))
  foreach (var vid in sh.GetAllPlacedViews()) { var v = (View)d.GetElement(vid); if (v is ViewSchedule) continue;
    var vis = new HashSet<long>(new FilteredElementCollector(d, v.Id).WhereElementIsNotElementType().ToElementIds().Select(i => i.Value));
    var hid = fr.Where(x => x.IsHidden(v)).GroupBy(x => x.Name.Split(' ')[0]).Select(g => g.Key + "x" + g.Count());
    sb.AppendLine(sh.SheetNumber + " " + v.Name + " HIDDEN: " + string.Join(", ", hid)); }
System.IO.File.WriteAllText(@"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\hidden.txt", sb.ToString());
return "ok";
