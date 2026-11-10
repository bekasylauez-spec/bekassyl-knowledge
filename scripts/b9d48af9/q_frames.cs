double M = 1 / 304.8; var sb = new System.Text.StringBuilder(); var d = document;
var fr = new FilteredElementCollector(d).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().ToElements();
foreach (var g in fr.GroupBy(x => x.Name.Split(' ')[0]).OrderBy(g => g.Key)) {
  var zs = g.Select(x => { var b = x.get_BoundingBox(null); return new[] { b.Min.Z / M, b.Max.Z / M, b.Min.X / M, b.Max.X / M }; }).ToList();
  sb.AppendLine(g.Key + " x" + g.Count() + " z " + Math.Round(zs.Min(q => q[0])) + ".." + Math.Round(zs.Max(q => q[1])) + " x " + Math.Round(zs.Min(q => q[2])) + ".." + Math.Round(zs.Max(q => q[3])) + " zmins " + string.Join(",", zs.Select(q => Math.Round(q[0] / 100) * 100).Distinct().OrderBy(q => q).Take(8)) + " | struct usage " + (g.First() as FamilyInstance)?.StructuralUsage);
}
var cols = new FilteredElementCollector(d).OfCategory(BuiltInCategory.OST_StructuralColumns).WhereElementIsNotElementType().ToElements();
foreach (var g in cols.GroupBy(x => x.Name)) { var b = g.Select(x => x.get_BoundingBox(null)); sb.AppendLine("COL " + g.Key + " x" + g.Count() + " top " + string.Join(",", b.Select(q => Math.Round(q.Max.Z / M)).Distinct().Take(5))); }
var tg = new FilteredElementCollector(d).OfCategory(BuiltInCategory.OST_StructuralFramingTags).WhereElementIsElementType().Cast<FamilySymbol>().First();
sb.AppendLine("tag fam " + tg.FamilyName);
return sb.ToString();
