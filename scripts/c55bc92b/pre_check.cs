// read-only: IsModified + current positions of all framing/column instances -> scratchpad cur_dump_now.tsv
var d = document; var sb = new System.Text.StringBuilder();
string outp = @"C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\cur_dump_now.tsv";
sb.AppendLine("path " + d.PathName + " IsModified=" + d.IsModified + " activeview=" + (d == null ? "" : "ok"));
var all = new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => (x.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "") != "" && x.Category != null && (x.Category.Id.Value == (long)BuiltInCategory.OST_StructuralFraming || x.Category.Id.Value == (long)BuiltInCategory.OST_StructuralColumns)).ToList();
var lines = new List<string>();
Func<XYZ, string> f3 = p => p == null ? "\t\t" : Math.Round(p.X * 304.8, 2) + "\t" + Math.Round(p.Y * 304.8, 2) + "\t" + Math.Round(p.Z * 304.8, 2);
foreach (var fi in all)
{
    XYZ pa = null, pb = null; if (fi.Location is LocationCurve lc) { pa = lc.Curve.GetEndPoint(0); pb = lc.Curve.GetEndPoint(1); } else if (fi.Location is LocationPoint lp) { pa = lp.Point; }
    var bb = fi.get_BoundingBox(null); string bs = bb == null ? "\t\t\t\t\t" : string.Join("\t", new[] { bb.Min.X, bb.Min.Y, bb.Min.Z, bb.Max.X, bb.Max.Y, bb.Max.Z }.Select(q => Math.Round(q * 304.8, 2).ToString(System.Globalization.CultureInfo.InvariantCulture)));
    lines.Add(string.Join("\t", new[] { fi.Id.Value.ToString(), fi.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString(), fi.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)?.AsString() ?? "", f3(pa), f3(pb), bs }));
}
System.IO.File.WriteAllLines(outp, lines, new System.Text.UTF8Encoding(false));
sb.AppendLine("dumped " + lines.Count);
var cats = new FilteredElementCollector(d).WhereElementIsNotElementType().Where(e => e.Category != null).GroupBy(e => e.Category.Name).Select(g => g.Key + "=" + g.Count());
sb.AppendLine("categories: " + string.Join("; ", cats));
return sb.ToString();
}
static int Dummy() { return 0;
