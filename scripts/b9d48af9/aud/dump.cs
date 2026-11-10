var sb = new System.Text.StringBuilder(); double F = 304.8; var ci = System.Globalization.CultureInfo.InvariantCulture;
Func<double, string> f = v => Math.Round(v, 1).ToString(ci);
var opt = new Options { DetailLevel = ViewDetailLevel.Fine };
foreach (var ds in new FilteredElementCollector(document).OfClass(typeof(DirectShape)).Cast<DirectShape>())
{
    string cm = ds.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? ds.Name;
    string cat = ds.Category == null ? "?" : ds.Category.Name;
    var bb = ds.get_BoundingBox(null);
    sb.Append("DS\t" + ds.Id.Value + "\t" + cat + "\t" + ds.ApplicationDataId + "\t" + cm.Replace("\t", " ") + "\t");
    if (bb != null) sb.Append(f(bb.Min.X * F) + "\t" + f(bb.Min.Y * F) + "\t" + f(bb.Min.Z * F) + "\t" + f(bb.Max.X * F) + "\t" + f(bb.Max.Y * F) + "\t" + f(bb.Max.Z * F));
    sb.AppendLine();
    var ge = ds.get_Geometry(opt); if (ge == null) continue;
    foreach (var go in ge)
    {
        var s = go as Solid; if (s == null || s.Volume < 1e-12) continue;
        var sbb = s.GetBoundingBox(); var tr = sbb.Transform;
        var a = tr.OfPoint(sbb.Min); var b = tr.OfPoint(sbb.Max);
        double amax = 0; XYZ nrm = XYZ.Zero; double rad = 0; int nf = 0;
        foreach (Face fc in s.Faces) { nf++; if (fc is PlanarFace pf) { if (pf.Area > amax) { amax = pf.Area; nrm = pf.FaceNormal; } } else if (fc is CylindricalFace cf) { rad = Math.Max(rad, cf.get_Radius(0).GetLength()); } }
        double vol = s.Volume * F * F * F; double t = amax > 0 ? vol / (amax * F * F) : 0;
        sb.AppendLine("S\t" + ds.Id.Value + "\t" + f(Math.Min(a.X, b.X) * F) + "\t" + f(Math.Min(a.Y, b.Y) * F) + "\t" + f(Math.Min(a.Z, b.Z) * F) + "\t" + f(Math.Max(a.X, b.X) * F) + "\t" + f(Math.Max(a.Y, b.Y) * F) + "\t" + f(Math.Max(a.Z, b.Z) * F)
            + "\t" + Math.Round(vol).ToString(ci) + "\t" + f(t) + "\t" + Math.Round(nrm.X, 3).ToString(ci) + "," + Math.Round(nrm.Y, 3).ToString(ci) + "," + Math.Round(nrm.Z, 3).ToString(ci) + "\t" + f(rad * F) + "\t" + nf + "\t" + f(amax * F * F));
    }
}
foreach (var fi in new FilteredElementCollector(document).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>())
{
    string cm = fi.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "";
    string loc = "";
    if (fi.Location is LocationCurve lc) { var p0 = lc.Curve.GetEndPoint(0); var p1 = lc.Curve.GetEndPoint(1); loc = "C\t" + f(p0.X * F) + "\t" + f(p0.Y * F) + "\t" + f(p0.Z * F) + "\t" + f(p1.X * F) + "\t" + f(p1.Y * F) + "\t" + f(p1.Z * F); }
    else if (fi.Location is LocationPoint lp) { var p = lp.Point; loc = "P\t" + f(p.X * F) + "\t" + f(p.Y * F) + "\t" + f(p.Z * F); }
    var bb = fi.get_BoundingBox(null); string bs = bb == null ? "" : f(bb.Min.X * F) + "\t" + f(bb.Min.Y * F) + "\t" + f(bb.Min.Z * F) + "\t" + f(bb.Max.X * F) + "\t" + f(bb.Max.Y * F) + "\t" + f(bb.Max.Z * F);
    sb.AppendLine("FI\t" + fi.Id.Value + "\t" + (fi.Category?.Name ?? "") + "\t" + fi.Symbol.Family.Name + "\t" + fi.Symbol.Name + "\t" + cm + "\t" + loc + "\tBB\t" + bs);
}
System.IO.File.WriteAllText(@"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\aud\dump.tsv", sb.ToString());
return "ok " + sb.Length + " " + document.Title;
