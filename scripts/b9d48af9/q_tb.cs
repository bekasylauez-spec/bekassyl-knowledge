var sb = new System.Text.StringBuilder(); var d = document;
foreach (var tb in new FilteredElementCollector(d).OfCategory(BuiltInCategory.OST_TitleBlocks).WhereElementIsElementType().Cast<FamilySymbol>()) {
  sb.AppendLine("== " + tb.Name);
  foreach (Parameter p in tb.Parameters) sb.AppendLine("  " + p.Definition.Name + " = " + (p.StorageType == StorageType.Double ? Math.Round(p.AsDouble()*304.8,1).ToString() : p.AsValueString() ?? p.AsString()));
}
foreach (var tb in new FilteredElementCollector(d).OfCategory(BuiltInCategory.OST_TitleBlocks).WhereElementIsNotElementType().Take(1)) foreach (Parameter p in tb.Parameters) sb.AppendLine(" I " + p.Definition.Name + " = " + (p.AsValueString() ?? p.AsString()));
return sb.ToString();
