var sb = new System.Text.StringBuilder(); double M = 1 / 304.8; var c = new XYZ(6000, 0, 14300);
foreach (var x in new FilteredElementCollector(document).WhereElementIsNotElementType().ToElements()) {
  if (x.Category == null || x.Category.CategoryType != CategoryType.Model || x.Category.Name == "Сварные швы") continue; var b = x.get_BoundingBox(null); if (b == null) continue;
  var mn = b.Min / M; var mx = b.Max / M; if (mx.X < c.X - 900 || mn.X > c.X + 900 || mx.Y < c.Y - 900 || mn.Y > c.Y + 900 || mx.Z < c.Z - 900 || mn.Z > c.Z + 900) continue;
  sb.AppendLine(x.Category.Name + " | " + x.Name + " | " + Math.Round(mn.X) + ".." + Math.Round(mx.X) + " y " + Math.Round(mn.Y) + ".." + Math.Round(mx.Y) + " z " + Math.Round(mn.Z) + ".." + Math.Round(mx.Z)); }
System.IO.File.WriteAllText(@"C:\Users\beka\AppData\Local\Temp\claude\83f5638966f051b1\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\n1.txt", sb.ToString());
return "ok";
