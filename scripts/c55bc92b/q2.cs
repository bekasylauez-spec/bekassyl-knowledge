var d = document; var sb = new System.Text.StringBuilder(); double M = 304.8; var ci = System.Globalization.CultureInfo.InvariantCulture;
foreach (var fi in new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>())
{
    string mk = fi.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? ""; var bb = fi.get_BoundingBox(null); if (bb == null) continue;
    double cx = (bb.Min.X + bb.Max.X) / 2 * M, cy = (bb.Min.Y + bb.Max.Y) / 2 * M;
    if (mk == "К1" && Math.Abs(cx - 48000) < 400 && cy > 15000 && cy < 21000 || (mk == "К1" && Math.Abs(cy - 18000) < 400))
    {
        var lp = fi.Location as LocationPoint; var tr = fi.GetTransform();
        sb.AppendLine(mk + " " + fi.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)?.AsString() + " loc " + Math.Round(lp.Point.X * M, 2).ToString(ci) + "," + Math.Round(lp.Point.Y * M, 2).ToString(ci) + "," + Math.Round(lp.Point.Z * M, 2).ToString(ci) + " rot " + lp.Rotation.ToString("0.000", ci) + " bb " + string.Join(",", new[] { bb.Min.X, bb.Min.Y, bb.Min.Z, bb.Max.X, bb.Max.Y, bb.Max.Z }.Select(q => Math.Round(q * M, 1).ToString(ci))));
    }
}
return sb.ToString();
