var d = document; var sb = new System.Text.StringBuilder();
var ds = new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>().First(x => x.ApplicationDataId == "узел 1 | 6-A" && x.Name.Contains("оголовок"));
foreach (var s in SolidsOf(ds)) { int n = 0; foreach (Edge e in s.Edges) { var a = e.AsCurve() as Arc; if (a == null) continue; if (n++ < 40) sb.AppendLine("arc r=" + F(a.Radius / MM) + " c=" + F(a.Center.X / MM) + "," + F(a.Center.Y / MM) + "," + F(a.Center.Z / MM) + " n=" + F(a.Normal.X) + "," + F(a.Normal.Y) + "," + F(a.Normal.Z) + " len " + F(a.Length / MM)); }
  sb.AppendLine("arcs " + n + " faces " + s.Faces.Size + " edges " + s.Edges.Size + " vol " + F(s.Volume / MM / MM / MM)); }
return sb.ToString();
}
