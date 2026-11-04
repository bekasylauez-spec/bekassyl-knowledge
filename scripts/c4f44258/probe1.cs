// read-only probe of the node file, no Transaction
const double MM = 1 / 304.8;
var nd = document.Application.Documents.Cast<Document>().First(d => d.PathName.EndsWith("БК-КМ_Узел_20К1-25Б1.rvt"));
var sb = new System.Text.StringBuilder(); try {
sb.AppendLine("doc " + nd.Title + " active=" + (nd.Equals(document)));
Func<Element, List<Solid>> Sol = el => { var r = new List<Solid>();
    foreach (var go in el.get_Geometry(new Options { DetailLevel = ViewDetailLevel.Fine }))
    { IEnumerable<GeometryObject> objs = go is GeometryInstance gi ? gi.GetInstanceGeometry().Cast<GeometryObject>() : new[] { go };
      r.AddRange(objs.OfType<Solid>().Where(x => x.Volume > 1e-9)); } return r; };
var els = new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Symbol.Family.Name.StartsWith("(КМ)")).Cast<Element>()
    .Concat(new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел")).ToList();
// all model elements in the file (anything else?)
var allModel = new FilteredElementCollector(nd).WhereElementIsNotElementType().Where(e => e.Category != null && e.Category.CategoryType == CategoryType.Model && e.get_BoundingBox(null) != null).ToList();
sb.AppendLine("model elements total " + allModel.Count + ", node elements " + els.Count);
foreach (var g in allModel.GroupBy(e => e.Category.Name + " | " + e.GetType().Name)) sb.AppendLine("  " + g.Key + " ×" + g.Count());
var sol = els.ToDictionary(e => e.Id, e => Sol(e));
foreach (var e in els)
{
    var b = e.get_BoundingBox(null); string nm = e is FamilyInstance fi ? fi.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString() + " " + fi.Symbol.Name + " [" + fi.Symbol.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_MARK).AsString() + "]" : e.Name;
    var fmats = sol[e.Id].SelectMany(s => s.Faces.Cast<Face>()).Select(f => nd.GetElement(f.MaterialElementId)?.Name ?? "<none>").Distinct();
    sb.AppendLine(string.Format("{0} #{1} cat={2} solids={3} vol={4:0} mm3 bb x {5:0.##}..{6:0.##} y {7:0.##}..{8:0.##} z {9:0.##}..{10:0.##} faceMats={11}", nm, e.Id, e.Category.Name, sol[e.Id].Count,
        sol[e.Id].Sum(s => s.Volume) / (MM * MM * MM), b.Min.X / MM, b.Max.X / MM, b.Min.Y / MM, b.Max.Y / MM, b.Min.Z / MM, b.Max.Z / MM, string.Join(",", fmats)));
}
// C1 rerun with boolean exception count
int exc = 0, pairs = 0;
for (int i = 0; i < els.Count; i++) for (int j = i + 1; j < els.Count; j++)
    foreach (var a in sol[els[i].Id]) foreach (var b in sol[els[j].Id])
    { pairs++; if (pairs > 0) continue; try { BooleanOperationsUtils.ExecuteBooleanOperation(a, b, BooleanOperationsType.Intersect); } catch (Exception ex) { exc++; if (exc < 6) sb.AppendLine("  bool EXC " + els[i].Name + " / " + els[j].Name + ": " + ex.Message); } }
sb.AppendLine("C1x solid pairs " + pairs + ", boolean exceptions " + exc);
// point-in-weld tests
var welds = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.Name.StartsWith("шов")).SelectMany(x => sol[x.Id]).ToList();
var allSolids = els.SelectMany(e => sol[e.Id].Select(s => Tuple.Create(e, s))).ToList();
Func<double, double, double, string> In = (x, y, z) => {
    double h = 0.7; var loop = new CurveLoop(); var c = new XYZ(x * MM, y * MM, (z - h) * MM);
    var p1 = c + new XYZ(-h * MM, -h * MM, 0); var p2 = c + new XYZ(h * MM, -h * MM, 0); var p3 = c + new XYZ(h * MM, h * MM, 0); var p4 = c + new XYZ(-h * MM, h * MM, 0);
    loop.Append(Line.CreateBound(p1, p2)); loop.Append(Line.CreateBound(p2, p3)); loop.Append(Line.CreateBound(p3, p4)); loop.Append(Line.CreateBound(p4, p1));
    var cube = GeometryCreationUtilities.CreateExtrusionGeometry(new List<CurveLoop> { loop }, XYZ.BasisZ, 2 * h * MM);
    var hits = new List<string>();
    foreach (var t in allSolids) { try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(t.Item2, cube, BooleanOperationsType.Intersect); if (r != null && r.Volume > cube.Volume * 0.5) hits.Add(t.Item1.Name.Split(' ')[0] == "" ? t.Item1.Id.ToString() : (t.Item1 is FamilyInstance f2 ? f2.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString() : t.Item1.Name)); } catch { hits.Add("EXC"); } }
    return hits.Count == 0 ? "EMPTY" : string.Join("+", hits.Distinct()); };
var pts = new List<Tuple<string, double, double, double>> {
  Tuple.Create("beam top flange tip +x end face (weld across flange thickness?)", 62.8, 119.0, -4.0),
  Tuple.Create("beam top flange tip -x", -62.8, 119.0, -4.0),
  Tuple.Create("beam bottom flange tip +x", 62.8, 119.0, -244.0),
  Tuple.Create("top flange inside, root fillet zone +x (x 2.5..14.5)", 9.0, 119.0, -21.0),
  Tuple.Create("top flange inside, root fillet zone, near fillet surface", 6.0, 119.0, -14.0),
  Tuple.Create("bottom flange inside, root fillet zone +x", 9.0, 119.0, -227.0),
  Tuple.Create("web weld +x mid", 3.5, 119.0, -124.0),
  Tuple.Create("top flange outside weld centre", 0.0, 120.0, 2.0),
  Tuple.Create("top flange inside weld x=40", 40.0, 120.0, -10.0),
  Tuple.Create("top flange inside weld x=-40", -40.0, 120.0, -10.0),
  Tuple.Create("bottom flange inside weld x=40", 40.0, 120.0, -238.0),
  Tuple.Create("rib top +x: outer free edge at flange +y (x 98.25..99.5)", 98.9, 87.0, -4.0),
  Tuple.Create("rib +x top weld to +y flange, underside", 60.0, 87.0, -9.0),
  Tuple.Create("rib +x top weld to −y flange, top", 60.0, -87.0, 1.0),
  Tuple.Create("rib +x top ↔ web underside", 4.0, 0.0, -9.0),
  Tuple.Create("rib -x bottom ↔ web top", -4.0, 0.0, -239.0),
  Tuple.Create("rib chamfer corner +x +y (should be empty)", 10.0, 80.0, -4.0),
  Tuple.Create("bolt hole in plate (bolt shank)", 50.0, 108.0, 43.0),
  Tuple.Create("plate↔column flange gap at y=98", 80.0, 98.0, 60.0),
};
foreach (var p in pts) sb.AppendLine("  pt " + p.Item1 + " (" + p.Item2 + "," + p.Item3 + "," + p.Item4 + "): " + In(p.Item2, p.Item3, p.Item4));
// z-fighting: coplanar planar faces, same normal, different elements, overlapping area
int zf = 0; var faces = new List<Tuple<Element, PlanarFace>>();
foreach (var e in els) foreach (var s in sol[e.Id]) foreach (Face f in s.Faces) if (f is PlanarFace pf) faces.Add(Tuple.Create(e, pf));
var opp = 0;
for (int i = 0; i < faces.Count; i++) for (int j = i + 1; j < faces.Count; j++)
{
    if (faces[i].Item1.Id == faces[j].Item1.Id) continue;
    var A = faces[i].Item2; var B = faces[j].Item2; double dot = A.FaceNormal.DotProduct(B.FaceNormal);
    if (Math.Abs(dot) < 0.99999) continue;
    if (Math.Abs((B.Origin - A.Origin).DotProduct(A.FaceNormal)) > 0.01 * MM) continue;
    // overlap of in-plane bboxes using mesh vertices
    var n = A.FaceNormal; var u = Math.Abs(n.Z) < 0.9 ? XYZ.BasisZ.CrossProduct(n).Normalize() : XYZ.BasisX; var v = n.CrossProduct(u);
    Func<PlanarFace, double[]> R = f => { var vs = f.Triangulate().Vertices; return new[] { vs.Min(q => q.DotProduct(u)), vs.Max(q => q.DotProduct(u)), vs.Min(q => q.DotProduct(v)), vs.Max(q => q.DotProduct(v)) }; };
    var ra = R(A); var rb = R(B);
    double ou = Math.Min(ra[1], rb[1]) - Math.Max(ra[0], rb[0]), ov = Math.Min(ra[3], rb[3]) - Math.Max(ra[2], rb[2]);
    if (ou <= 0.05 * MM || ov <= 0.05 * MM) continue;
    // real overlap: test a point of the intersection rect centre on both faces
    var cpt = A.Origin + u * ((Math.Max(ra[0], rb[0]) + Math.Min(ra[1], rb[1])) / 2 - A.Origin.DotProduct(u)) + v * ((Math.Max(ra[2], rb[2]) + Math.Min(ra[3], rb[3])) / 2 - A.Origin.DotProduct(v));
    var pa = A.Project(cpt); var pb = B.Project(cpt);
    bool both = pa != null && pb != null && pa.Distance < 0.05 * MM && pb.Distance < 0.05 * MM;
    string tag = dot > 0 ? "SAME-DIR (z-fight)" : "opposite (contact)";
    if (dot > 0) zf++; else opp++;
    if (dot > 0 || opp <= 40)
        sb.AppendLine(string.Format("  coplanar {0} {1} / {2}  n=({3:0.##},{4:0.##},{5:0.##}) overlap {6:0.#}x{7:0.#} mm centreOnBoth={8}", tag,
            faces[i].Item1 is FamilyInstance fa ? fa.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString() + "#" + fa.Id : faces[i].Item1.Name,
            faces[j].Item1 is FamilyInstance fb ? fb.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString() + "#" + fb.Id : faces[j].Item1.Name, n.X, n.Y, n.Z, ou / MM, ov / MM, both));
}
sb.AppendLine("coplanar same-direction overlapping face pairs: " + zf + ", opposite (contact) pairs: " + opp);
// materials
foreach (var m in new FilteredElementCollector(nd).OfClass(typeof(Material)).Cast<Material>().Where(m => m.Name.StartsWith("КМ_")))
    sb.AppendLine(string.Format("  mat {0}: rgb {1},{2},{3} shin {4} smooth {5} transp {6} useRenderApp {7}", m.Name, m.Color.Red, m.Color.Green, m.Color.Blue, m.Shininess, m.Smoothness, m.Transparency, m.UseRenderAppearanceForShading));
// categories line weight / colour
foreach (var bic in new[] { BuiltInCategory.OST_StructuralColumns, BuiltInCategory.OST_StructuralFraming, BuiltInCategory.OST_GenericModel, BuiltInCategory.OST_StructConnectionBolts, BuiltInCategory.OST_StructConnectionWelds, BuiltInCategory.OST_StructConnectionPlates, BuiltInCategory.OST_StructConnections })
{ var c = Category.GetCategory(nd, bic); if (c == null) { sb.AppendLine("  cat " + bic + " null"); continue; }
  sb.AppendLine("  cat " + c.Name + ": proj lw " + c.GetLineWeight(GraphicsStyleType.Projection) + " cut lw " + c.GetLineWeight(GraphicsStyleType.Cut) + " color " + (c.LineColor.IsValid ? c.LineColor.Red + "," + c.LineColor.Green + "," + c.LineColor.Blue : "-")); }
// rib/plate/column/beam family categories
foreach (var fi in els.OfType<FamilyInstance>()) { }
sb.AppendLine("  family cats: " + string.Join(", ", els.OfType<FamilyInstance>().Select(x => x.Symbol.Family.Name + "=" + x.Category.Name).Distinct()));
// 3D view
var v3 = new FilteredElementCollector(nd).OfClass(typeof(View3D)).Cast<View3D>().FirstOrDefault(v => !v.IsTemplate && v.Name == "КМ 3D Узел 1");
if (v3 != null) { sb.AppendLine("  view КМ 3D Узел 1: style " + v3.DisplayStyle + " detail " + v3.DetailLevel + " filters " + v3.GetFilters().Count + " template " + v3.ViewTemplateId);
  foreach (var e in els.Take(1)) { }
  foreach (var bic in new[] { BuiltInCategory.OST_StructuralColumns, BuiltInCategory.OST_StructuralFraming, BuiltInCategory.OST_GenericModel, BuiltInCategory.OST_StructConnectionBolts, BuiltInCategory.OST_StructConnectionWelds })
  { var c = Category.GetCategory(nd, bic); if (c == null) continue; var o = v3.GetCategoryOverrides(c.Id); sb.AppendLine("    ovr " + c.Name + ": projLw " + o.ProjectionLineWeight + " projColor " + (o.ProjectionLineColor.IsValid ? o.ProjectionLineColor.Red + "," + o.ProjectionLineColor.Green + "," + o.ProjectionLineColor.Blue : "-") + " surfPat " + o.SurfaceForegroundPatternId + " transp " + o.Transparency + " hidden " + v3.GetCategoryHidden(c.Id)); } }
// template traces
var traces = new List<string>();
var it = nd.ParameterBindings.ForwardIterator(); while (it.MoveNext()) { var nm = it.Key.Name; if (nm.StartsWith("BI_") || nm.StartsWith("KNP_") || nm.StartsWith("RAS_")) traces.Add("param " + nm); }
foreach (var e in new FilteredElementCollector(nd).WhereElementIsElementType()) { var nm = e.Name ?? ""; if (nm.StartsWith("BI_") || nm.StartsWith("KNP_") || nm.StartsWith("RAS_")) traces.Add("type " + nm); }
foreach (var v in new FilteredElementCollector(nd).OfClass(typeof(View)).Cast<View>()) { if (v.Name.StartsWith("BI_") || v.Name.StartsWith("KNP_") || v.Name.StartsWith("RAS_")) traces.Add("view " + v.Name); }
sb.AppendLine("template traces BI_/KNP_/RAS_: " + traces.Count + (traces.Count > 0 ? " e.g. " + string.Join("; ", traces.Take(10)) : ""));
sb.AppendLine("views: " + string.Join("; ", new FilteredElementCollector(nd).OfClass(typeof(View)).Cast<View>().Where(v => !v.IsTemplate).Select(v => v.ViewType + ":" + v.Name).Take(40)));
} catch (Exception ex) { sb.AppendLine("EXC " + ex.ToString().Substring(0, Math.Min(1500, ex.ToString().Length))); }
return sb.ToString();