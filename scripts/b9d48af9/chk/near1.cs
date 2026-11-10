var nd = document.Application.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt"));
var sb = new System.Text.StringBuilder(); double M = 1 / 304.8;
sb.AppendLine("docs: " + string.Join(" | ", document.Application.Documents.Cast<Document>().Select(d => d.Title)) + " ; active=" + document.Title);
var ol = new Outline(new XYZ(8000, -500, 4400) * M, new XYZ(10000, 500, 5700) * M);
foreach (var e in new FilteredElementCollector(nd).WherePasses(new BoundingBoxIntersectsFilter(ol)).WhereElementIsNotElementType())
{ var bb = e.get_BoundingBox(null); if (bb == null) continue; var mk = e.LookupParameter("Марка");
  sb.AppendLine(e.Id + " | " + e.GetType().Name + " | " + e.Category?.Name + " | " + e.Name + " | " + (mk == null ? "" : mk.AsString()) + " | " + string.Format("{0:F0},{1:F0},{2:F0} - {3:F0},{4:F0},{5:F0}", bb.Min.X/M, bb.Min.Y/M, bb.Min.Z/M, bb.Max.X/M, bb.Max.Y/M, bb.Max.Z/M)); }
return sb.ToString();
