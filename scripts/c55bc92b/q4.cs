var d = document; var sb = new System.Text.StringBuilder(); double M = 304.8; var ci = System.Globalization.CultureInfo.InvariantCulture;
var rows = System.IO.File.ReadAllLines(@"D:\Бекасыл КЖ КМ\РМЦ_КМ\_авто\members.tsv", System.Text.Encoding.UTF8).Where(l => l.Trim().Length > 0).Select(l => l.Split('\t')).ToList();
var byMark = new Dictionary<string, FamilyInstance>();
foreach (var fi in new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>()) { var im = fi.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)?.AsString(); if (im != null) byMark[im] = fi; }
int bad = 0, n = 0;
for (int i = 0; i < rows.Count; i++)
{
    var r = rows[i]; string key = r[1] + "-" + r[0]; if (!byMark.ContainsKey(key)) { sb.AppendLine("missing " + key); bad++; continue; } n++;
    var fi = byMark[key]; var bb = fi.get_BoundingBox(null);
    if (r[2] == "C") { var lp = (fi.Location as LocationPoint).Point; double x = double.Parse(r[4], ci), y = double.Parse(r[5], ci);
        if (Math.Abs(lp.X * M - x) > 1 || Math.Abs(lp.Y * M - y) > 1 || Math.Abs(bb.Min.Z * M - 900) > 1) { bad++; sb.AppendLine("COL moved " + key + " now " + Math.Round(lp.X * M, 1).ToString(ci) + "," + Math.Round(lp.Y * M, 1).ToString(ci) + " want " + x + "," + y); } }
    else { var lc = fi.Location as LocationCurve; var a = lc.Curve.GetEndPoint(0); var b = lc.Curve.GetEndPoint(1);
        double[] A = { double.Parse(r[4], ci), double.Parse(r[5], ci), double.Parse(r[6], ci) }, B = { double.Parse(r[7], ci), double.Parse(r[8], ci), double.Parse(r[9], ci) };
        double e = Math.Max(Math.Abs(a.X * M - A[0]) + Math.Abs(a.Y * M - A[1]) + Math.Abs(a.Z * M - A[2]), Math.Abs(b.X * M - B[0]) + Math.Abs(b.Y * M - B[1]) + Math.Abs(b.Z * M - B[2]));
        if (e > 2 && r[3] != "purlin") { bad++; sb.AppendLine("BEAM moved " + key + " err " + Math.Round(e, 1).ToString(ci)); } }
}
sb.AppendLine("checked " + n + " of " + rows.Count + " bad " + bad);
return sb.ToString();
