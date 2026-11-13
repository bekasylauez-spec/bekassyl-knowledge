var d = document; var sb = new System.Text.StringBuilder(); double M = 304.8; var ci = System.Globalization.CultureInfo.InvariantCulture;
int n = 0;
foreach (var fi in new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>())
{
    var bb = fi.get_BoundingBox(null); if (bb == null) continue; n++;
    string im = fi.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)?.AsString() ?? ""; string mk = fi.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "";
    double cx = (bb.Min.X + bb.Max.X) / 2 * M, cy = (bb.Min.Y + bb.Max.Y) / 2 * M;
    if (im == "К1-26" || (Math.Abs(cx - 48000) < 200 && Math.Abs(cy - 18000) < 600 && (bb.Max.Z - bb.Min.Z) * M > 3000))
        sb.AppendLine(fi.Id + " " + fi.Symbol.Family.Name + " " + fi.Symbol.Name + " im=" + im + " c=" + mk + " bb " + string.Join(",", new[] { bb.Min.X, bb.Min.Y, bb.Min.Z, bb.Max.X, bb.Max.Y, bb.Max.Z }.Select(q => Math.Round(q * M, 1).ToString(ci))));
}
sb.AppendLine("total fi " + n);
return sb.ToString();
