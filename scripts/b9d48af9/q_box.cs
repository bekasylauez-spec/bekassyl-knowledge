double M = 1 / 304.8; var sb = new System.Text.StringBuilder();
var ol = new Outline(new XYZ(5000, -900, 13300) * M, new XYZ(7000, 1600, 15600) * M);
foreach (var e in new FilteredElementCollector(document).WherePasses(new BoundingBoxIntersectsFilter(ol)).WhereElementIsNotElementType().ToElements().OrderBy(x => x.Category?.Name))
{ var b = e.get_BoundingBox(null); if (b == null || e.Category == null) continue; if (e.Category.Name.Contains("Болт") || e.Category.Name.Contains("шв")) continue;
  sb.AppendLine(e.Id + "\t" + e.Category.Name + "\t" + e.Name + "\t" + (e.LookupParameter("Марка")?.AsString() ?? "") + "\t" + Math.Round(b.Min.X*304.8) + "," + Math.Round(b.Min.Y*304.8) + "," + Math.Round(b.Min.Z*304.8) + " .. " + Math.Round(b.Max.X*304.8) + "," + Math.Round(b.Max.Y*304.8) + "," + Math.Round(b.Max.Z*304.8)); }
return sb.ToString();
