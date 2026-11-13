// read-only: current framing/column instances vs model_dump.tsv (as-built after the v2 rebuild) -> moved elements; IsModified; counts
var d = document; var sb = new System.Text.StringBuilder();
sb.AppendLine("path " + d.PathName + " IsModified=" + d.IsModified);
var dump = System.IO.File.ReadAllLines(@"D:\Бекасыл КЖ КМ\РМЦ_КМ\_авто\model_dump.tsv", System.Text.Encoding.UTF8).Select(l => l.Split('\t')).ToList();
var byIm = new Dictionary<string, string[]>(); foreach (var r in dump) byIm[r[2]] = r;
var all = new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => (x.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "") != "" && x.Category != null && (x.Category.Id.Value == (long)BuiltInCategory.OST_StructuralFraming || x.Category.Id.Value == (long)BuiltInCategory.OST_StructuralColumns)).ToList();
Func<string, double> N = s => double.Parse(s.Replace(',', '.'), System.Globalization.CultureInfo.InvariantCulture);
int moved = 0, missing = 0, ok = 0; var seen = new HashSet<string>();
foreach (var fi in all)
{
    string im = fi.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)?.AsString() ?? ""; seen.Add(im);
    if (!byIm.ContainsKey(im)) { missing++; sb.AppendLine("NOT IN DUMP: " + im); continue; }
    var r = byIm[im]; XYZ pa = null, pb = null;
    if (fi.Location is LocationCurve lc) { pa = lc.Curve.GetEndPoint(0); pb = lc.Curve.GetEndPoint(1); } else if (fi.Location is LocationPoint lp) { pa = lp.Point; pb = pa; }
    var bb = fi.get_BoundingBox(null);
    double dd = Math.Abs(pa.X * 304.8 - N(r[5])) + Math.Abs(pa.Y * 304.8 - N(r[6])) + Math.Abs(pa.Z * 304.8 - N(r[7])) + Math.Abs(pb.X * 304.8 - N(r[8])) + Math.Abs(pb.Y * 304.8 - N(r[9])) + Math.Abs(pb.Z * 304.8 - N(r[10]));
    if (dd > 0.05) { moved++; sb.AppendLine("MOVED " + im + " Δ=" + Math.Round(dd, 3)); } else ok++;
}
foreach (var k in byIm.Keys) if (!seen.Contains(k)) sb.AppendLine("IN DUMP BUT NOT IN MODEL: " + k);
sb.AppendLine("instances " + all.Count + ", dump rows " + dump.Count + ", unchanged " + ok + ", moved " + moved + ", not in dump " + missing);
var ds = new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>().ToList();
sb.AppendLine("DirectShape " + ds.Count + ": " + string.Join(", ", ds.GroupBy(x => x.ApplicationId + ":" + (x.ApplicationDataId ?? "").Split('|')[0].Trim()).Select(g => g.Key + "=" + g.Count())));
var ui = new FilteredElementCollector(d).OfClass(typeof(View)).Cast<View>().Where(v => !v.IsTemplate).Select(v => v.Name).ToList(); sb.AppendLine("views " + ui.Count);
return sb.ToString();
