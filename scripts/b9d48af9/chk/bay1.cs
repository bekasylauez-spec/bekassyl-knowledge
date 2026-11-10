var nd = document.Application.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt"));
var sb = new System.Text.StringBuilder(); double M = 1 / 304.8;
var ol = new Outline(new XYZ(5800, -400, -400) * M, new XYZ(12200, 400, 15500) * M);
var rows = new List<string>();
foreach (var e in new FilteredElementCollector(nd).WherePasses(new BoundingBoxIntersectsFilter(ol)).WhereElementIsNotElementType())
{ var bb = e.get_BoundingBox(null); if (bb == null) continue; 
  if (e.Category == null || e.Category.Name == "Оси" || e.Category.Name == "Уровни") continue;
  string nm = e.Name; if (nm.StartsWith("Болт") || nm.StartsWith("шов")) continue;
  rows.Add(string.Format("{0}|{1}|{2}|{3:F0},{4:F0},{5:F0}-{6:F0},{7:F0},{8:F0}", ((int)(bb.Min.Z/M)+100000).ToString(), e.Id, nm, bb.Min.X/M, bb.Min.Y/M, bb.Min.Z/M, bb.Max.X/M, bb.Max.Y/M, bb.Max.Z/M)); }
rows.Sort(); foreach (var r in rows) sb.AppendLine(r.Substring(r.IndexOf('|')+1));
return sb.ToString();

