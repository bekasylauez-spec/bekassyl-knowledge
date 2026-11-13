// РМЦ КМ каркасы (v2): ригель Б1/Б2/Б3 және Б5 қимасын МОДЕЛЬ ГЕОМЕТРИЯСЫНАН өлшеу: тік сызық (x, y) бойымен денені кескенде z-кесінділері. Тек оқиды -> measure.tsv
var d = document; var sb = new System.Text.StringBuilder(); string auto = @"D:\Бекасыл КЖ КМ\РМЦ_КМ\_авто\";
var all = new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => (x.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "") != "").ToList();
Func<string, FamilyInstance> by = m => all.First(x => x.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString() == m);
var lines = new List<string>(); var opt = new SolidCurveIntersectionOptions(); opt.ResultType = SolidCurveIntersectionMode.CurveSegmentsInside;
Action<string, double, double[]> vert = (name, x, ys) => { var sl = SolidsOf(by(name));
    foreach (var y in ys) { var segs = new List<double[]>();
        foreach (var so in sl) { var line = Line.CreateBound(new XYZ(x / 304.8, y / 304.8, 2000 / 304.8), new XYZ(x / 304.8, y / 304.8, 12000 / 304.8)); var r = so.IntersectWithCurve(line, opt);
            for (int i = 0; i < r.SegmentCount; i++) { var c = r.GetCurveSegment(i); segs.Add(new[] { Math.Min(c.GetEndPoint(0).Z, c.GetEndPoint(1).Z) * 304.8, Math.Max(c.GetEndPoint(0).Z, c.GetEndPoint(1).Z) * 304.8 }); } }
        segs = segs.OrderBy(s => s[0]).ToList();
        lines.Add(name + "\t" + x + "\t" + y + "\t" + (segs.Count == 0 ? "-" : string.Join(" | ", segs.Select(s => Math.Round(s[0], 2) + ".." + Math.Round(s[1], 2))))); } };
vert("Б1-54", 150, new double[] { 0.5, 100, 300, 600, 3000, 6000, 6599.5 });
vert("Б1-57", 150, new double[] { 35999.5, 35700, 35400, 33000, 30000, 29400.5 });
vert("Б2-55", 150, new double[] { 6600.5, 9000, 12499.5 });
vert("Б3-56", 150, new double[] { 12500.5, 15000, 17989.5 });
vert("Б3-59", 150, new double[] { 18010.5, 21000, 23499.5 });
// Б5 ойығы: x бойымен ( y = 4000 және 4090 ), тік кесінділер
foreach (var dx in new double[] { 5, 100, 200, 2900 }) vert("Б5-243", 54023 + dx, new double[] { 4000, 4090 });
System.IO.File.WriteAllLines(auto + "measure.tsv", lines, new System.Text.UTF8Encoding(false));
return "measured " + lines.Count + " rows\n" + string.Join("\n", lines);
}
static List<Solid> SolidsOf(Element e) { var r = new List<Solid>(); foreach (var go in e.get_Geometry(new Options { DetailLevel = ViewDetailLevel.Fine })) { IEnumerable<GeometryObject> objs = go is GeometryInstance gi ? gi.GetInstanceGeometry().Cast<GeometryObject>() : new[] { go };
    r.AddRange(objs.OfType<Solid>().Where(x => x.Volume > 1e-9)); } return r;
