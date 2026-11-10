var sb = new System.Text.StringBuilder(); Func<XYZ, string> f = p => Math.Round(p.X, 3) + "," + Math.Round(p.Y, 3) + "," + Math.Round(p.Z, 3);
foreach (var v in new FilteredElementCollector(document).OfClass(typeof(ViewSection)).Cast<View>().Where(x => x.Name.StartsWith("Узел 1"))) {
  var cb = v.CropBox; sb.AppendLine(v.Name + " right " + f(v.RightDirection) + " up " + f(v.UpDirection) + " vdir " + f(v.ViewDirection) + " origin " + f(v.Origin * 304.8) + " | cb X " + f(cb.Transform.BasisX) + " Z " + f(cb.Transform.BasisZ) + " O " + f(cb.Transform.Origin * 304.8) + " min " + f(cb.Min * 304.8) + " max " + f(cb.Max * 304.8)); }
return sb.ToString();
