var d = document; var sb = new System.Text.StringBuilder();
Func<Element, string> Cm = f => f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "";
var cols = new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(f => f.Location is LocationPoint && Cm(f) == "К1" && Math.Abs((f.Location as LocationPoint).Point.Y / MM - 18000) < 5).OrderBy(f => (f.Location as LocationPoint).Point.X).ToList();
sb.AppendLine("col\tcx\tz(web,y18000)\tz(fl,y+265.9)\tz(fl,y-265.9)\tz(fl,y+200)\tz(fl,y-200)\texp200\tvoidcuts");
double mn = 1e9, mx = -1e9;
foreach (var c in cols) {
  double cx = (c.Location as LocationPoint).Point.X / MM; var fr = new List<Sx>(); foreach (var s in SolidsOf(c)) fr.Add(new Sx { S = s, B = BBox(s) });
  Func<double, double, double> z = (x, y) => ProbeZ(fr, x, y, 8000, 9600, false);
  double a = z(cx, 18000), b = z(cx + 100, 18265.9), cc = z(cx + 100, 17734.1), e1 = z(cx + 100, 18200), e2 = z(cx + 100, 17800);
  var cuts = InstanceVoidCutUtils.GetCuttingVoidInstances(c).Count;
  sb.AppendLine(c.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString() + "\t" + F(cx) + "\t" + F(a) + "\t" + F(b) + "\t" + F(cc) + "\t" + F(e1) + "\t" + F(e2) + "\t" + F(9293 - 175.0 / 5500 * 200) + "\t" + cuts);
}
return sb.ToString();
}
