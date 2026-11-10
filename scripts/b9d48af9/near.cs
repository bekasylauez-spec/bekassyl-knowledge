var sb = new System.Text.StringBuilder(); double M = 1 / 304.8;
var ol = new Outline(new XYZ(3200, 3400, 14200) * M, new XYZ(4000, 4100, 14900) * M);
foreach (var e in new FilteredElementCollector(document).WherePasses(new BoundingBoxIntersectsFilter(ol)).WhereElementIsNotElementType())
{ var bb = e.get_BoundingBox(null); if (bb == null) continue; var mk = e.LookupParameter("Марка"); 
  sb.AppendLine(e.Id + " | " + e.Category?.Name + " | " + e.Name + " | " + (mk == null ? "" : mk.AsString()) + " | " + string.Format("{0:F0},{1:F0},{2:F0} - {3:F0},{4:F0},{5:F0}", bb.Min.X/M, bb.Min.Y/M, bb.Min.Z/M, bb.Max.X/M, bb.Max.Y/M, bb.Max.Z/M)); }
return sb.ToString();
