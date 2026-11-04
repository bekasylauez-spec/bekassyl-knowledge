// read-only probe 3: is the 0.3 mm rule-5 gap (beam end y 118.3, column top z 89.7) everywhere under a weld or another member?
const double MM = 1 / 304.8;
var nd = document.Application.Documents.Cast<Document>().First(q => q.PathName.EndsWith("БК-КМ_Узел_20К1-25Б1.rvt"));
var sb = new System.Text.StringBuilder(); try {
sb.AppendLine("doc active=" + nd.Equals(document) + " modified=" + nd.IsModified);
Func<Element, List<Solid>> Sol = el => { var r = new List<Solid>();
    foreach (var go in el.get_Geometry(new Options { DetailLevel = ViewDetailLevel.Fine }))
    { IEnumerable<GeometryObject> objs = go is GeometryInstance gi ? gi.GetInstanceGeometry().Cast<GeometryObject>() : new[] { go };
      r.AddRange(objs.OfType<Solid>().Where(x => x.Volume > 1e-9)); } return r; };
var mem = new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Symbol.Family.Name.StartsWith("(КМ)")).ToList();
var welds = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел" && x.Name.StartsWith("шов")).SelectMany(x => Sol(x)).ToList();
Func<FamilyInstance, string> Cm = fi => fi.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString();
var ray = new XYZ(0.613, 0.371, 0.697).Normalize();
var sopt = new SolidCurveIntersectionOptions { ResultType = SolidCurveIntersectionMode.CurveSegmentsInside };
Func<XYZ, List<Solid>, bool> Inside = (p, ss) => { double h = 0.5 * MM; var lp = new CurveLoop(); var cc = new[] { new XYZ(-h, -h, -h), new XYZ(h, -h, -h), new XYZ(h, h, -h), new XYZ(-h, h, -h) };
    for (int i = 0; i < 4; i++) lp.Append(Line.CreateBound(p + cc[i], p + cc[(i + 1) % 4]));
    var cube = GeometryCreationUtilities.CreateExtrusionGeometry(new List<CurveLoop> { lp }, XYZ.BasisZ, 2 * h);
    foreach (var s in ss) { try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(s, cube, BooleanOperationsType.Intersect); if (r != null && r.Volume > cube.Volume * 0.5) return true; } catch { } } return false; };
foreach (var job in new[] { Tuple.Create("Балка", new XYZ(0, -1, 0), 118.3, 119.5), Tuple.Create("Колонна", new XYZ(0, 0, 1), 89.7, 88.5) })
{
    var el = mem.First(x => Cm(x) == job.Item1); var n = job.Item2;
    var others = mem.Where(x => x.Id != el.Id).SelectMany(x => Sol(x)).ToList();
    var ends = Sol(el).SelectMany(s => s.Faces.Cast<Face>()).OfType<PlanarFace>().Where(f => f.FaceNormal.DotProduct(n) > 0.99999 && Math.Abs(f.Origin.DotProduct(n) / MM - (n.Y < 0 ? -job.Item3 : job.Item3)) < 0.01).ToList();
    sb.AppendLine(job.Item1 + ": end faces at " + job.Item3 + ": " + ends.Count);
    double tot = 0, bad = 0; var badPts = new List<string>();
    foreach (var f in ends) foreach (EdgeArray loop in f.EdgeLoops) foreach (Edge e in loop)
    {
        var c = e.AsCurve(); double L = c.Length / MM; int ns = Math.Max(2, (int)Math.Ceiling(L / 2));
        for (int k = 0; k < ns; k++)
        {
            double t = c.GetEndParameter(0) + (c.GetEndParameter(1) - c.GetEndParameter(0)) * (k + 0.5) / ns;
            var tr = c.ComputeDerivatives(t, false); var p = tr.Origin; var tg = tr.BasisX.Normalize(); var m = tg.CrossProduct(n).Normalize();
            XYZ outDir = null;
            foreach (var sg in new[] { 1.0, -1.0 }) { var pp = p + m * sg * 0.4 * MM; if (!ends.Any(g => { var r = g.Project(pp); return r != null && r.Distance < 1e-6; })) { outDir = m * sg; break; } }
            if (outDir == null) continue;   // internal edge between two end faces
            tot += L / ns;
            var q = p + outDir * 1.5 * MM - n * (job.Item3 - job.Item4) * MM * (n.Y < 0 ? -1 : 1) * (n.Y < 0 ? -1 : 1);
            q = new XYZ(q.X, n.Y != 0 ? job.Item4 * MM : q.Y, n.Z != 0 ? job.Item4 * MM : q.Z);
            if (Inside(q, welds) || Inside(q, others)) continue;
            bad += L / ns; badPts.Add(string.Format("({0:0.#},{1:0.#},{2:0.#})", p.X / MM, p.Y / MM, p.Z / MM));
        }
    }
    sb.AppendLine(string.Format("  gap perimeter {0:0} mm, NOT under a weld / member {1:0} mm{2}", tot, bad, badPts.Count > 0 ? ": " + string.Join(" ", badPts.Take(60)) : ""));
}
} catch (Exception ex) { sb.AppendLine("EXC " + ex.ToString().Substring(0, Math.Min(1500, ex.ToString().Length))); }
return sb.ToString();