double M = 1 / 304.8; var sb = new System.Text.StringBuilder(); var d = document;
foreach (var c in new[] { new XYZ(6000, 0, 0), new XYZ(0, 12000, 0), new XYZ(6000, 24000, 0), new XYZ(-7000, 48000, 0), new XYZ(78000, 51000, 0) }) {
  sb.AppendLine("== around " + c);
  var ol = new Outline((c + new XYZ(-1200, -1200, -900)) * M, (c + new XYZ(1200, 1200, 400)) * M);
  foreach (var e in new FilteredElementCollector(d).WherePasses(new BoundingBoxIntersectsFilter(ol)).WhereElementIsNotElementType().ToElements()) {
    var b = e.get_BoundingBox(null); if (b == null || e.Category == null) continue;
    sb.AppendLine("  " + e.Id + " | " + e.Category.Name + " | " + e.Name + " | Марка=" + e.LookupParameter("Марка")?.AsString() + " | " + Math.Round(b.Min.X / M) + "," + Math.Round(b.Min.Y / M) + "," + Math.Round(b.Min.Z / M) + " .. " + Math.Round(b.Max.X / M) + "," + Math.Round(b.Max.Y / M) + "," + Math.Round(b.Max.Z / M)); } }
var names = new FilteredElementCollector(d).WhereElementIsNotElementType().ToElements().Where(x => x.Name.StartsWith("База") || x.Name.StartsWith("Б") && x.Name.Length <= 4).GroupBy(x => x.Name).Select(g => g.Key + " x" + g.Count());
sb.AppendLine("BASE NAMES " + string.Join("; ", names));
foreach (var v in new FilteredElementCollector(d).OfClass(typeof(ViewPlan)).Cast<ViewPlan>().Where(x => !x.IsTemplate)) sb.AppendLine("PLAN " + v.ViewType + " | " + v.Name + " | lvl " + v.GenLevel?.Name + " | 1:" + v.Scale);
foreach (var vft in new FilteredElementCollector(d).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().Where(x => x.ViewFamily == ViewFamily.FloorPlan || x.ViewFamily == ViewFamily.StructuralPlan)) sb.AppendLine("VFT " + vft.ViewFamily + " | " + vft.Name);
foreach (var gt in new FilteredElementCollector(d).OfClass(typeof(GridType)).Cast<GridType>()) sb.AppendLine("GRIDTYPE " + gt.Name);
foreach (var tg in new FilteredElementCollector(d).OfCategory(BuiltInCategory.OST_StructuralFramingTags).WhereElementIsElementType().Cast<FamilySymbol>()) sb.AppendLine("FRAMETAG " + tg.FamilyName + " | " + tg.Name);
foreach (var tg in new FilteredElementCollector(d).OfCategory(BuiltInCategory.OST_StructuralColumnTags).WhereElementIsElementType().Cast<FamilySymbol>()) sb.AppendLine("COLTAG " + tg.FamilyName + " | " + tg.Name);
foreach (var tg in new FilteredElementCollector(d).OfCategory(BuiltInCategory.OST_StructConnectionTags).WhereElementIsElementType().Cast<FamilySymbol>()) sb.AppendLine("CONNTAG " + tg.FamilyName + " | " + tg.Name);
return sb.ToString();
