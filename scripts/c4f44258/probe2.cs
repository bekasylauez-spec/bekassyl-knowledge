// read-only probe 2 (no Transaction)
const double MM = 1 / 304.8;
var nd = document.Application.Documents.Cast<Document>().First(q => q.PathName.EndsWith("БК-КМ_Узел_20К1-25Б1.rvt"));
var sb = new System.Text.StringBuilder(); try {
sb.AppendLine("doc " + nd.Title + " active=" + nd.Equals(document) + " modified=" + nd.IsModified);
Func<Element, List<Solid>> Sol = el => { var r = new List<Solid>();
    foreach (var go in el.get_Geometry(new Options { DetailLevel = ViewDetailLevel.Fine }))
    { IEnumerable<GeometryObject> objs = go is GeometryInstance gi ? gi.GetInstanceGeometry().Cast<GeometryObject>() : new[] { go };
      r.AddRange(objs.OfType<Solid>().Where(x => x.Volume > 1e-9)); } return r; };
Func<Element, string> Nm = el => (el is FamilyInstance fi ? fi.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString() + " " + fi.Symbol.Name : el.Name) + "#" + el.Id;
var mem = new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Symbol.Family.Name.StartsWith("(КМ)")).Cast<Element>().ToList();
var dss = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел").ToList();
var welds = dss.Where(x => x.Name.StartsWith("шов")).ToList(); var bolts = dss.Where(x => x.Name.StartsWith("болт")).ToList();
var sol = mem.Concat(dss).ToDictionary(e => e.Id, e => Sol(e));
Func<Solid, Solid, double> Inter = (a, b) => { try { var x = BooleanOperationsUtils.ExecuteBooleanOperation(a, b, BooleanOperationsType.Intersect); return x == null ? 0 : x.Volume / (MM * MM * MM); } catch { return -1; } };
// A. all bolt intersections
sb.AppendLine("A. bolt intersections (>0.01 mm3):");
foreach (var b in bolts) { var bb = b.get_BoundingBox(null); var parts = new List<string>();
  foreach (var e in mem.Concat(welds)) { double v = 0; foreach (var s1 in sol[b.Id]) foreach (var s2 in sol[e.Id]) v += Inter(s1, s2); if (Math.Abs(v) > 0.01) parts.Add(Nm(e) + "=" + Math.Round(v, 1)); }
  sb.AppendLine(string.Format("  bolt x {0:0} z {1:0}: {2}", (bb.Min.X + bb.Max.X) / 2 / MM, (bb.Min.Z + bb.Max.Z) / 2 / MM, string.Join(", ", parts))); }
// B. weld vertices: must lie on a member surface
var memFaces = mem.SelectMany(e => sol[e.Id].SelectMany(s => s.Faces.Cast<Face>())).ToList();
var memEdges = mem.SelectMany(e => sol[e.Id].SelectMany(s => s.Edges.Cast<Edge>())).ToList();
Func<XYZ, double> Dist = p => { double m = 1e9; foreach (var f in memFaces) { var r = f.Project(p); if (r != null && r.Distance < m) m = r.Distance; }
    foreach (var ed in memEdges) { var c = ed.AsCurve(); var r = c.Project(p); if (r != null && r.Distance < m) m = r.Distance; } return m / MM; };
sb.AppendLine("B. weld vertices off any member surface (>0.05 mm):");
foreach (var w in welds) { int nv = 0; var bad = new List<string>();
  foreach (var s in sol[w.Id]) { var vs = new List<XYZ>(); foreach (Edge ed in s.Edges) foreach (var p in ed.Tessellate()) if (!vs.Any(q => q.IsAlmostEqualTo(p, 1e-6))) vs.Add(p);
    foreach (var p in vs) { nv++; double dd = Dist(p); if (dd > 0.05) bad.Add(string.Format("({0:0.#},{1:0.#},{2:0.#}) d={3:0.##}", p.X / MM, p.Y / MM, p.Z / MM, dd)); } }
  sb.AppendLine("  " + w.Name + ": vertices " + nv + ", off " + bad.Count + (bad.Count > 0 ? ": " + string.Join(" ", bad.Take(24)) : "")); }
// C. coplanar faces (same direction = z-fight), near-coplanar same-direction < 0.5 mm
var faces = new List<Tuple<Element, PlanarFace>>();
foreach (var e in mem.Concat(dss)) foreach (var s in sol[e.Id]) foreach (Face f in s.Faces) if (f is PlanarFace pf) faces.Add(Tuple.Create((Element)e, pf));
int zf = 0, near = 0;
for (int i = 0; i < faces.Count; i++) for (int j = i + 1; j < faces.Count; j++)
{
    if (faces[i].Item1.Id == faces[j].Item1.Id) continue;
    var A = faces[i].Item2; var B = faces[j].Item2; double dot = A.FaceNormal.DotProduct(B.FaceNormal);
    if (dot < 0.99999) continue;
    double off = Math.Abs((B.Origin - A.Origin).DotProduct(A.FaceNormal)) / MM; if (off > 0.5) continue;
    var ma = A.Triangulate(); int hit = 0, tot = 0;
    for (int k = 0; k < ma.NumTriangles; k++) { var t = ma.get_Triangle(k); var c = (t.get_Vertex(0) + t.get_Vertex(1) + t.get_Vertex(2)) / 3;
      foreach (var p in new[] { c, c + (t.get_Vertex(0) - c) * 0.5, c + (t.get_Vertex(1) - c) * 0.5, c + (t.get_Vertex(2) - c) * 0.5 }) { tot++; var r = B.Project(p); if (r != null && r.Distance / MM < off + 0.01) hit++; } }
    if (hit == 0) continue;
    if (off < 0.05) zf++; else near++;
    sb.AppendLine(string.Format("  {0} {1} / {2} n=({3:0.###},{4:0.###},{5:0.###}) off {6:0.##} mm, samples on both {7}/{8}", off < 0.05 ? "SAME-DIR COPLANAR" : "near-coplanar", Nm(faces[i].Item1), Nm(faces[j].Item1), A.FaceNormal.X, A.FaceNormal.Y, A.FaceNormal.Z, off, hit, tot));
}
sb.AppendLine("C. same-direction coplanar overlapping: " + zf + ", near-coplanar (<0.5 mm): " + near);
// D. weld coverage along the contact lines (1 mm cube 1.5 mm inside the corner)
var wsol = welds.SelectMany(x => sol[x.Id]).ToList();
Func<XYZ, bool> Has = p => { double h = 0.5 * MM; var lp = new CurveLoop(); var c = new[] { new XYZ(-h, -h, -h), new XYZ(h, -h, -h), new XYZ(h, h, -h), new XYZ(-h, h, -h) };
    for (int i = 0; i < 4; i++) lp.Append(Line.CreateBound(p + c[i], p + c[(i + 1) % 4]));
    var cube = GeometryCreationUtilities.CreateExtrusionGeometry(new List<CurveLoop> { lp }, XYZ.BasisZ, 2 * h); return wsol.Any(w => Inter(w, cube) > 0.5); };
double TA = 0.15, CA = 1 / Math.Sqrt(1 + TA * TA), SA = TA * CA; var Dv = new XYZ(0, CA, -SA); var X = XYZ.BasisX; var Y = XYZ.BasisY; var Z = XYZ.BasisZ;
Func<double, double, double> ZW = (y, w) => -TA * (y - 118) + w / CA;
Func<double, double, double, XYZ, XYZ, XYZ> Pt = (x, y, z, a, b) => new XYZ(x * MM, y * MM, z * MM) + (a + b) * 1.5 * MM;
var miss = new List<string>(); int nprobe = 0;
Action<string, XYZ> T = (k, p) => { nprobe++; if (!Has(p)) miss.Add(k); };
foreach (var x in new[] { -60.0, -30, 30, 60 }) { T("top out x" + x, Pt(x, 118, ZW(118, 0), Z, Dv)); T("bot out x" + x, Pt(x, 118, ZW(118, -248), -Z, Dv)); }
foreach (var x in new[] { -60.0, -16, 16, 60 }) { T("top in x" + x, Pt(x, 118, ZW(118, -8), -Z, Dv)); T("bot in x" + x, Pt(x, 118, ZW(118, -240), Z, Dv)); }
foreach (var z in new[] { -40.0, -124, -210 }) foreach (var sx in new[] { 1.0, -1.0 }) T("web z" + z + " x" + sx, Pt(sx * 2.5, 118, ZW(118, 0) + z, sx * X, Y));
foreach (var zb in new[] { -8.0, -250.75 }) foreach (var sx in new[] { 1.0, -1.0 }) {
  foreach (var y in new[] { -66.0, 0, 66 }) { T("rib web top " + zb + " " + sx + " y" + y, Pt(sx * 3.25, y, zb + 8, sx * X, Z)); T("rib web bot " + zb + " " + sx + " y" + y, Pt(sx * 3.25, y, zb, sx * X, -Z)); }
  foreach (var sy in new[] { 1.0, -1.0 }) foreach (var xa in new[] { 25.0, 96 }) { T("rib fl top " + zb + " " + sx + " " + sy + " x" + xa, Pt(sx * xa, sy * 88, zb + 8, -sy * Y, Z)); T("rib fl bot " + zb + " " + sx + " " + sy + " x" + xa, Pt(sx * xa, sy * 88, zb, -sy * Y, -Z)); } }
foreach (var x in new[] { -88.0, 0, 88 }) T("cap plate outer x" + x, Pt(x, 118, 90, -Z, Y));
foreach (var x in new[] { -97.0, 0, 97 }) T("cap flange -y outer x" + x, Pt(x, -98, 90, -Z, -Y));
foreach (var sx in new[] { 1.0, -1.0 }) {
  T("cap ↔ plate side x" + sx, Pt(sx * 90, 108, 90, sx * X, -Z)); T("cap ↔ column flange edge +y x" + sx, Pt(sx * 99.5, 93, 90, sx * X, -Z)); T("cap ↔ column flange edge -y x" + sx, Pt(sx * 99.5, -93, 90, sx * X, -Z));
  T("beam top flange edge return x" + sx, Pt(sx * 62, 118, -4, sx * X, Y)); T("beam bot flange edge return x" + sx, Pt(sx * 62, 118, ZW(118, -244), sx * X, Y)); }
sb.AppendLine("D. weld coverage probes " + nprobe + ", missing " + miss.Count + ": " + string.Join("; ", miss));
// E. weld protruding outside the cap: weld points beyond cap edge
// F. beam far end, void cut
var beam = mem.OfType<FamilyInstance>().First(x => x.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString() == "Балка");
var bfaces = sol[beam.Id].SelectMany(s => s.Faces.Cast<Face>()).OfType<PlanarFace>().ToList();
var far = bfaces.OrderByDescending(f => f.Origin.Y).First();
sb.AppendLine(string.Format("F. beam far-end face normal ({0:0.###},{1:0.###},{2:0.###}), bbox y max {3:0.#}; length param {4:0.#}; void cuts {5}", far.FaceNormal.X, far.FaceNormal.Y, far.FaceNormal.Z, beam.get_BoundingBox(null).Max.Y / MM,
   (beam.get_Parameter(BuiltInParameter.INSTANCE_LENGTH_PARAM)?.AsDouble() ?? 0) / MM, string.Join(",", InstanceVoidCutUtils.GetCuttingVoidInstances(beam).Select(i => Nm(nd.GetElement(i))))));
var nearEnd = bfaces.Where(f => Math.Abs(f.FaceNormal.Y + 1) < 1e-6).Select(f => string.Format("y {0:0.###}", f.Origin.Y / MM));
sb.AppendLine("  beam faces with normal -Y: " + string.Join(", ", nearEnd));
var v3 = new FilteredElementCollector(nd).OfClass(typeof(View3D)).Cast<View3D>().First(v => !v.IsTemplate && v.Name == "КМ 3D Узел 1");
var cutInst = new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Symbol.Family.Name == "БК_срез_плоскостью").ToList();
foreach (var ci in cutInst) { var g = ci.get_Geometry(new Options { View = v3 }); int n = g == null ? 0 : g.Cast<GeometryObject>().Count(); sb.AppendLine("  cut instance " + Nm(ci) + " cat " + ci.Category.Name + ", geometry objects in 3D view " + n); }
// G. other model elements
foreach (var g in new FilteredElementCollector(nd).WhereElementIsNotElementType().Where(e => e.Category != null && e.Category.CategoryType == CategoryType.Model && e.get_BoundingBox(null) != null).GroupBy(e => e.Category.Name)) sb.AppendLine("  G " + g.Key + " ×" + g.Count());
// H. face materials, materials, view
foreach (var e in mem) sb.AppendLine("  H " + Nm(e) + " faceMats " + string.Join(",", sol[e.Id].SelectMany(s => s.Faces.Cast<Face>()).Select(f => nd.GetElement(f.MaterialElementId)?.Name ?? "<none>").Distinct()));
foreach (var m in new FilteredElementCollector(nd).OfClass(typeof(Material)).Cast<Material>().Where(m => m.Name.StartsWith("КМ_")))
    sb.AppendLine(string.Format("  mat {0}: rgb {1},{2},{3} shin {4} smooth {5} transp {6} useRender {7}", m.Name, m.Color.Red, m.Color.Green, m.Color.Blue, m.Shininess, m.Smoothness, m.Transparency, m.UseRenderAppearanceForShading));
sb.AppendLine("  view: style " + v3.DisplayStyle + " detail " + v3.DetailLevel + " filters " + v3.GetFilters().Count);
foreach (var bic in new[] { BuiltInCategory.OST_StructuralColumns, BuiltInCategory.OST_StructuralFraming, BuiltInCategory.OST_GenericModel, BuiltInCategory.OST_StructConnectionBolts, BuiltInCategory.OST_StructConnectionWelds })
{ var c = Category.GetCategory(nd, bic); if (c == null) continue; var o = v3.GetCategoryOverrides(c.Id);
  sb.AppendLine("  cat " + c.Name + ": lw " + c.GetLineWeight(GraphicsStyleType.Projection) + " color " + (c.LineColor.IsValid ? c.LineColor.Red + "," + c.LineColor.Green + "," + c.LineColor.Blue : "-") + " | view ovr lw " + o.ProjectionLineWeight + " color " + (o.ProjectionLineColor.IsValid ? o.ProjectionLineColor.Red + "," + o.ProjectionLineColor.Green + "," + o.ProjectionLineColor.Blue : "-")); }
} catch (Exception ex) { sb.AppendLine("EXC " + ex.ToString().Substring(0, Math.Min(1500, ex.ToString().Length))); }
return sb.ToString();