var sb = new System.Text.StringBuilder();
sb.AppendLine(document.Title + " | " + document.PathName);
var all = new FilteredElementCollector(document).WhereElementIsNotElementType().ToElements();
var rx = new System.Text.RegularExpressions.Regex(@"Узел\s*\d+");
var g = all.Select(e => new { e, n = (e.Name ?? "") + " " + (e.LookupParameter("Комментарии")?.AsString() ?? "") }).Where(x => rx.IsMatch(x.n)).GroupBy(x => rx.Match(x.n).Value);
foreach (var gr in g.OrderBy(x => x.Key)) {
  var bbs = gr.Select(x => x.e.get_BoundingBox(null)).Where(b => b != null).ToList();
  sb.AppendLine(gr.Key + " count " + gr.Count() + " ex: " + string.Join(" / ", gr.Select(x => x.n.Trim()).Distinct().Take(4)));
  foreach (var b in bbs.Take(2)) sb.AppendLine("   bb " + Math.Round(b.Min.X*304.8) + "," + Math.Round(b.Min.Y*304.8) + "," + Math.Round(b.Min.Z*304.8) + " .. " + Math.Round(b.Max.X*304.8) + "," + Math.Round(b.Max.Y*304.8) + "," + Math.Round(b.Max.Z*304.8));
}
foreach (ViewSheet sh in new FilteredElementCollector(document).OfClass(typeof(ViewSheet))) sb.AppendLine("SHEET " + sh.SheetNumber + " " + sh.Name);
foreach (Family f in new FilteredElementCollector(document).OfClass(typeof(Family))) if (f.FamilyCategory != null && f.FamilyCategory.CategoryType == CategoryType.Annotation) sb.AppendLine("AFAM " + f.FamilyCategory.Name + " | " + f.Name);
foreach (Grid gd in new FilteredElementCollector(document).OfClass(typeof(Grid))) { var c = gd.Curve; sb.AppendLine("GRID " + gd.Name + " " + Math.Round(c.GetEndPoint(0).X*304.8) + "," + Math.Round(c.GetEndPoint(0).Y*304.8) + " " + Math.Round(c.GetEndPoint(1).X*304.8) + "," + Math.Round(c.GetEndPoint(1).Y*304.8)); }
foreach (Level l in new FilteredElementCollector(document).OfClass(typeof(Level))) sb.AppendLine("LEVEL " + l.Name + " " + Math.Round(l.Elevation*304.8));
return sb.ToString();
