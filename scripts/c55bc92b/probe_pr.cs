// read-only: Пр1 геометриясы (қима, бағдар) және ригель беті
var d = document; var sb = new StringBuilder(); double MM = 1 / 304.8;
Func<double, string> F = v => Math.Round(v, 2).ToString(System.Globalization.CultureInfo.InvariantCulture);
var prs = new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(f => f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() == "Пр1").ToList();
sb.AppendLine("Пр1 саны " + prs.Count);
var ys = prs.Select(f => Math.Round(((f.Location as LocationCurve).Curve.GetEndPoint(0).Y / MM))).Distinct().OrderBy(v => v).ToList();
sb.AppendLine("y (A..G): " + string.Join(", ", ys));
foreach (var f in prs.Take(0)) { }
double[][] targ = { new[] { 266.0, 30000 }, new[] { 266.0, 150 }, new[] { 7316.0, 30000 }, new[] { 17800.0, 30000 }, new[] { 18200.0, 30000 }, new[] { 35734.0, 30000 } };
foreach (var tg in targ)
{
    foreach (var f in prs)
    {
        var lc = f.Location as LocationCurve; var p0 = lc.Curve.GetEndPoint(0) / MM; var p1 = lc.Curve.GetEndPoint(1) / MM;
        if (Math.Abs(p0.Y - tg[0]) > 1.5) continue; double xa = Math.Min(p0.X, p1.X), xb = Math.Max(p0.X, p1.X); if (!(xa < tg[1] + 1 && xb > tg[1] - 1 && xb - xa > 0)) continue;
        if (tg[1] == 150 && xa > 0) continue; if (tg[1] == 30000 && !(xa < 30000 && xb > 30000)) { }
        var bb = f.get_BoundingBox(null);
        sb.AppendLine("== Пр1 y=" + F(p0.Y) + " x " + F(p0.X) + "→" + F(p1.X) + " z " + F(p0.Z) + "→" + F(p1.Z) + " Mark " + f.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString() + " type " + f.Symbol.Name + " fam " + f.Symbol.FamilyName);
        sb.AppendLine("  bbox x " + F(bb.Min.X / MM) + "…" + F(bb.Max.X / MM) + " y " + F(bb.Min.Y / MM) + "…" + F(bb.Max.Y / MM) + " z " + F(bb.Min.Z / MM) + "…" + F(bb.Max.Z / MM));
        var tr = f.GetTransform(); sb.AppendLine("  transform X " + tr.BasisX + " Y " + tr.BasisY + " Z " + tr.BasisZ);
        var ge = f.get_Geometry(new Options { DetailLevel = ViewDetailLevel.Fine }); int sn = 0;
        foreach (var go in ge) { IEnumerable<GeometryObject> objs = go is GeometryInstance ? ((GeometryInstance)go).GetInstanceGeometry().Cast<GeometryObject>() : new[] { go };
            foreach (var s in objs.OfType<Solid>().Where(x => x.Volume > 1e-9)) { sn++; sb.AppendLine("  solid vol " + F(s.Volume / MM / MM / MM) + " faces " + s.Faces.Size);
                foreach (Face fc in s.Faces) { var pf = fc as PlanarFace; if (pf == null) continue; if (Math.Abs(pf.FaceNormal.X) < 0.99) continue; if (pf.FaceNormal.X < 0 != (true)) { }
                    var lo = pf.GetEdgesAsCurveLoops(); foreach (var cl in lo) { sb.Append("  endface n.x=" + F(pf.FaceNormal.X) + " xpos " + F(pf.Origin.X / MM) + " loop(y,z): "); foreach (Curve c in cl) { var q = c.GetEndPoint(0) / MM; sb.Append("(" + F(q.Y) + "," + F(q.Z) + ") "); } sb.AppendLine(); } } } }
        break;
    }
}
// ригель беті: Б1 үстіңгі полка ү. беті 6-A (x 30000), y 266 және 7316 бойынша probe
var cats = new List<BuiltInCategory> { BuiltInCategory.OST_StructuralFraming };
var flt = new LogicalAndFilter(new ElementMulticategoryFilter(cats), new BoundingBoxIntersectsFilter(new Outline(new XYZ(29500 * MM, -100 * MM, 8000 * MM), new XYZ(30500 * MM, 7000 * MM, 9500 * MM))));
var fr = new FilteredElementCollector(d).WherePasses(flt).WhereElementIsNotElementType().ToList();
foreach (var e in fr) sb.AppendLine("framing " + e.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString() + " " + e.Name + " bb y " + F(e.get_BoundingBox(null).Min.Y / MM) + "…" + F(e.get_BoundingBox(null).Max.Y / MM));
foreach (double y in new[] { 25.0, 266, 1326, 4321, 7316 })
{
    foreach (double dx in new[] { 0.0, 100, 125 })
    {
        double best = double.NaN;
        foreach (var e in fr) { var ge = e.get_Geometry(new Options { DetailLevel = ViewDetailLevel.Fine }); foreach (var go in ge) { IEnumerable<GeometryObject> objs = go is GeometryInstance ? ((GeometryInstance)go).GetInstanceGeometry().Cast<GeometryObject>() : new[] { go };
            foreach (var s in objs.OfType<Solid>().Where(x => x.Volume > 1e-9)) { try { var r = s.IntersectWithCurve(Line.CreateBound(new XYZ((30000 + dx) * MM, y * MM, 8000 * MM), new XYZ((30000 + dx) * MM, y * MM, 9600 * MM)), new SolidCurveIntersectionOptions()); for (int i = 0; i < r.SegmentCount; i++) { var c = r.GetCurveSegment(i); double z = Math.Max(c.GetEndPoint(0).Z, c.GetEndPoint(1).Z) / MM; if (double.IsNaN(best) || z > best) best = z; } } catch { } } } }
        sb.AppendLine("  Б1 top z at y " + y + " x+" + dx + " = " + F(best) + " (8968+0.05y=" + F(8968 + 0.05 * y) + ")");
    }
}
return sb.ToString();
