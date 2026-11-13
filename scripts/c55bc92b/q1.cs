var d = document; var sb = new System.Text.StringBuilder(); double M = 304.8;
sb.AppendLine("doc " + d.PathName + " active=" + d.Title);
foreach (var fi in new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>())
{
    string mk = fi.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? ""; var bb = fi.get_BoundingBox(null); if (bb == null) continue;
    double cy = (bb.Min.Y + bb.Max.Y) / 2 * M;
    if ((mk == "К1" && Math.Abs(cy - 18000) < 400) || (mk.StartsWith("СВ") && bb.Min.Y * M < 18200 && bb.Max.Y * M > 17800 && bb.Min.Z * M < 2500))
        sb.AppendLine(mk + " " + fi.Symbol.Name + " " + fi.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)?.AsString() + " bb " + string.Join(",", new[] { bb.Min.X, bb.Min.Y, bb.Min.Z, bb.Max.X, bb.Max.Y, bb.Max.Z }.Select(q => Math.Round(q * M, 1))));
}
var ds = new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>().ToList();
sb.AppendLine("DirectShapes " + ds.Count + ": " + string.Join(";", ds.Select(x => x.ApplicationId + "/" + x.ApplicationDataId).Distinct().Take(20)));
sb.AppendLine("materials: " + string.Join(", ", new FilteredElementCollector(d).OfClass(typeof(Material)).Cast<Material>().Select(m => m.Name).Where(n => n.StartsWith("КМ_")).OrderBy(n => n)));
sb.AppendLine("views: " + string.Join(", ", new FilteredElementCollector(d).OfClass(typeof(View)).Cast<View>().Where(v => !v.IsTemplate).Select(v => v.Name + "[" + v.ViewType + "]")));
sb.AppendLine("phases/worksets n/a; units ok");
return sb.ToString();
