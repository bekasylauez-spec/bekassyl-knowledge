var d = document; var sb = new System.Text.StringBuilder();
var ds = new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>().ToList();
foreach (var x in ds.Where(x => { var a = x.ApplicationDataId ?? ""; return a.EndsWith("| 4-D") || a.EndsWith("| 4-A") || a.EndsWith("| 6-D"); }).OrderBy(x => x.ApplicationDataId).ThenBy(x => x.Name))
{ var cm = x.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS); sb.AppendLine(x.Id.Value + " | " + x.ApplicationDataId + " | " + x.Name + " | cat " + x.Category.Name + " | " + (cm == null ? "" : cm.AsString())); }
return sb.ToString();
