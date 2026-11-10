var sb = new System.Text.StringBuilder(); double M = 1 / 304.8;
foreach (var x in new FilteredElementCollector(document).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().ToElements()) {
  var b = x.get_BoundingBox(null); if (b == null) continue;
  if (b.Max.X / M > 4400 && b.Min.X / M < 6600 && b.Max.Y / M > 24500 && b.Min.Y / M < 35500 && b.Max.Z / M > 9000) sb.AppendLine(x.Name + " | " + Math.Round(b.Min.X / M) + ".." + Math.Round(b.Max.X / M) + " y " + Math.Round(b.Min.Y / M) + ".." + Math.Round(b.Max.Y / M) + " z " + Math.Round(b.Min.Z / M) + ".." + Math.Round(b.Max.Z / M)); }
return sb.ToString();
