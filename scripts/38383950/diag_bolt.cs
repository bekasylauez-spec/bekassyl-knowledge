var nd = document.Application.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt"));
var sb = new System.Text.StringBuilder(); double M = 304.8;
foreach (var ds in new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => (x.Name ?? "").StartsWith("Болт")))
{
    var bb = ds.get_BoundingBox(null); if (bb == null) continue;
    if (bb.Max.X * M < 5800 || bb.Min.X * M > 7000 || bb.Min.Z * M > 5600 || bb.Max.Z * M < 4400 || Math.Abs((bb.Min.Y + bb.Max.Y) / 2 * M) > 400) continue;
    var ge = ds.get_Geometry(new Options()); int ns = 0; foreach (var go in ge) { var so = go as Solid; if (so != null && so.Volume > 0) { var c = so.ComputeCentroid(); if (c.X * M > 5800 && c.X * M < 7000 && c.Z * M > 4400 && c.Z * M < 5600) { ns++; if (ns % 5 == 3) sb.AppendLine("  shank " + Math.Round(c.X * M) + "," + Math.Round(c.Y * M) + "," + Math.Round(c.Z * M)); } } }
    sb.AppendLine(ds.Id.Value + " " + ds.Name + " x " + Math.Round(bb.Min.X * M) + ".." + Math.Round(bb.Max.X * M) + " y " + Math.Round(bb.Min.Y * M) + ".." + Math.Round(bb.Max.Y * M) + " z " + Math.Round(bb.Min.Z * M) + ".." + Math.Round(bb.Max.Z * M));
}
return sb.ToString();
