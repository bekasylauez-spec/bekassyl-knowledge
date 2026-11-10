var sb = new System.Text.StringBuilder(); var d = document;
var cats = new[] { BuiltInCategory.OST_StructuralFraming, BuiltInCategory.OST_StructuralColumns };
foreach (var bc in cats) foreach (var g in new FilteredElementCollector(d).OfCategory(bc).WhereElementIsNotElementType().ToElements().GroupBy(x => x.GetTypeId()).Take(40)) {
  var ty = d.GetElement(g.Key) as ElementType; var e0 = g.First();
  sb.Append(ty?.FamilyName + " | " + ty?.Name + " x" + g.Count() + " ::");
  foreach (Parameter p in ty.Parameters) { if (p.StorageType == StorageType.String && !string.IsNullOrEmpty(p.AsString())) sb.Append(" [" + p.Definition.Name + "=" + p.AsString() + "]"); }
  var mat = e0.get_Parameter(BuiltInParameter.STRUCTURAL_MATERIAL_PARAM); sb.Append(" mat=" + (mat != null ? d.GetElement(mat.AsElementId())?.Name : "-"));
  foreach (Parameter p in e0.Parameters) { if (p.StorageType == StorageType.String && !string.IsNullOrEmpty(p.AsString()) && p.Definition.Name.Length < 25) sb.Append(" {" + p.Definition.Name + "=" + p.AsString() + "}"); }
  sb.AppendLine(); }
return sb.ToString();
