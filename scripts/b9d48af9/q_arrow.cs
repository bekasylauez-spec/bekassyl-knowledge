var sb = new System.Text.StringBuilder(); var d = document;
foreach (var a in new FilteredElementCollector(d).OfClass(typeof(ElementType)).Cast<ElementType>().Where(x => x.get_Parameter(BuiltInParameter.ARROW_TYPE) != null)) {
  sb.Append(a.Name + " | type " + a.get_Parameter(BuiltInParameter.ARROW_TYPE).AsInteger() + " (" + a.get_Parameter(BuiltInParameter.ARROW_TYPE).AsValueString() + ")");
  foreach (Parameter p in a.Parameters) if (p.Definition.Name != "Имя типа" && p.StorageType != StorageType.None) sb.Append(" ; " + p.Definition.Name + "=" + (p.AsValueString() ?? p.AsString()));
  sb.AppendLine(); }
var dt = new FilteredElementCollector(d).OfClass(typeof(DimensionType)).Cast<DimensionType>().First(x => x.StyleType == DimensionStyleType.Linear && x.Name == "БК_основной_2,5мм");
var fo = dt.GetUnitsFormatOptions(); sb.AppendLine("dim units default " + fo.UseDefault + " acc " + (fo.UseDefault ? d.GetUnits().GetFormatOptions(SpecTypeId.Length).Accuracy : fo.Accuracy));
var vs = new FilteredElementCollector(d).OfClass(typeof(ViewSection)).Cast<View>().First(x => x.Name == "Узел 3");
foreach (var el in new FilteredElementCollector(d, vs.Id).WhereElementIsNotElementType().ToElements().Where(x => x.Category != null && x.Category.CategoryType == CategoryType.Model)) sb.AppendLine("U3 " + el.Category.Name + " | " + el.Name + " | Марка=" + el.LookupParameter("Марка")?.AsString() + " ovr " + (vs.GetElementOverrides(el.Id).SurfaceForegroundPatternId.Value));
return sb.ToString();
