var sb = new System.Text.StringBuilder();
foreach (var fi in new FilteredElementCollector(document).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Symbol.Family.Name == "БК_узел_круг").Take(3))
  foreach (Parameter p in fi.Parameters) if (p.Definition != null && (p.Definition.Name == "Номер" || p.Definition.Name == "Лист" || p.Definition.Name.Contains("узла") || p.Definition.Name.Contains("схемы"))) sb.AppendLine(fi.Id + " " + p.Definition.Name + " " + p.StorageType + " ro " + p.IsReadOnly + " = " + p.AsValueString() + "|" + p.AsString());
var fam = new FilteredElementCollector(document).OfClass(typeof(Family)).Cast<Family>().First(x => x.Name == "БК_узел_круг");
var sy = (FamilySymbol)document.GetElement(fam.GetFamilySymbolIds().First()); foreach (Parameter p in sy.Parameters) if (p.Definition != null && p.StorageType == StorageType.String) sb.AppendLine("type " + p.Definition.Name + " = " + p.AsString());
return sb.ToString();
