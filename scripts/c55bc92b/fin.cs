var d = document; var sb = new System.Text.StringBuilder();
sb.AppendLine("IsModified=" + d.IsModified + " path=" + d.PathName);
var ds = new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>().ToList();
foreach (var g in ds.GroupBy(x => (x.ApplicationDataId ?? "").Split('|')[0].Trim()).OrderBy(g => g.Key)) sb.AppendLine("  " + g.Key + " = " + g.Count() + " DS, орын " + g.Select(x => (x.ApplicationDataId ?? "").Split('|').Last().Trim()).Distinct().Count());
int fi = new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Count(x => (x.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "") != "" && x.Category != null && (x.Category.Id.Value == (long)BuiltInCategory.OST_StructuralFraming || x.Category.Id.Value == (long)BuiltInCategory.OST_StructuralColumns));
int voids = new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Count(x => x.Symbol.FamilyName == "БК_срез_плоскостью" && (x.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "").StartsWith("РМЦ_Λ"));
sb.AppendLine("каркас " + fi + ", Λ void " + voids + ", views " + new FilteredElementCollector(d).OfClass(typeof(View)).Cast<View>().Count(v => !v.IsTemplate));
return sb.ToString();
}
