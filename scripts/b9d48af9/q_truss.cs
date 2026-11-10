double M = 1 / 304.8; var sb = new System.Text.StringBuilder();
var ol = new Outline(new XYZ(5800, -400, 9000) * M, new XYZ(6200, 9000, 16000) * M);
foreach (var e in new FilteredElementCollector(document).WherePasses(new BoundingBoxIntersectsFilter(ol)).WhereElementIsNotElementType().ToElements())
{ var b = e.get_BoundingBox(null); if (b == null || e.Category == null) continue; var cn = e.Category.Name; if (!(cn == "Каркас несущий")) continue;
  string geo = ""; if (e.Location is LocationCurve lc) { var c = lc.Curve; geo = " L " + Math.Round(c.GetEndPoint(0).Y/M) + "," + Math.Round(c.GetEndPoint(0).Z/M) + " -> " + Math.Round(c.GetEndPoint(1).Y/M) + "," + Math.Round(c.GetEndPoint(1).Z/M); }
  sb.AppendLine(e.Id + "\t" + e.Name + "\t" + document.GetElement(e.GetTypeId())?.Name + "\t" + Math.Round(b.Min.X/M) + "," + Math.Round(b.Min.Y/M) + "," + Math.Round(b.Min.Z/M) + " .. " + Math.Round(b.Max.X/M) + "," + Math.Round(b.Max.Y/M) + "," + Math.Round(b.Max.Z/M) + geo); }
return sb.ToString();
