var nd = document.Application.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt"));
var sb = new System.Text.StringBuilder(); double M = 304.8;
Func<XYZ,string> V = p => "(" + Math.Round(p.X*M) + "," + Math.Round(p.Y*M) + "," + Math.Round(p.Z*M) + ")";
foreach (long id in new long[] { 3612446, 3612447,3612448,3612449,3602170 })
{
  var el = nd.GetElement(new ElementId(id)); sb.AppendLine("#" + id + " " + el.Name);
  var ge = el.get_Geometry(new Options { DetailLevel = ViewDetailLevel.Fine });
  var solids = new List<Solid>();
  foreach (var go in ge) { if (go is GeometryInstance gi) foreach (var g2 in gi.GetInstanceGeometry()) { if (g2 is Solid s2 && s2.Volume > 1e-9) solids.Add(s2); } else if (go is Solid so && so.Volume > 1e-9) solids.Add(so); }
  foreach (var so in solids) {
    var bb = so.GetBoundingBox(); var a = bb.Transform.OfPoint(bb.Min); var b = bb.Transform.OfPoint(bb.Max);
    sb.AppendLine("  solid vol " + Math.Round(so.Volume*M*M*M) + " faces " + so.Faces.Size + " bb " + V(a) + ".." + V(b));
    if (so.Faces.Size <= 20) foreach (Face fc in so.Faces) { var pf = fc as PlanarFace; if (pf==null) continue; sb.AppendLine("     pf area " + Math.Round(pf.Area*M*M) + " n " + Math.Round(pf.FaceNormal.X,3)+","+Math.Round(pf.FaceNormal.Y,3)+","+Math.Round(pf.FaceNormal.Z,3) + " verts " + string.Join(" ", pf.GetEdgesAsCurveLoops().SelectMany(l=>l.Select(c=>V(c.GetEndPoint(0)))))); }
  }
}
return sb.ToString();
