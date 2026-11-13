var d = document; var sb = new System.Text.StringBuilder();
var ds = new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>().ToList();
foreach (var g in ds.GroupBy(x => x.ApplicationId + ":" + (x.ApplicationDataId ?? "").Split('|')[0].Trim()))
{
    var locs = g.GroupBy(x => (x.ApplicationDataId ?? "").Contains("|") ? x.ApplicationDataId.Split('|')[1].Trim() : "?").OrderBy(k => k.Key).Select(k => k.Key + "x" + k.Count());
    sb.AppendLine(g.Key + " = " + g.Count() + " : " + string.Join(" ", locs));
}
return sb.ToString();
