{ var expDoc = System.IO.File.ReadAllText(@"D:\Бекасыл КЖ КМ\3602_Порталы_КМ\_авто\_expect_doc.txt", System.Text.Encoding.UTF8).Trim(); if (document.Title != expDoc) return "WRONG DOC: «" + document.Title + "»"; }
const double MM = 304.8;
var L = new System.Text.StringBuilder();
try {
var opt = new Options { DetailLevel = ViewDetailLevel.Fine };
Func<Element, List<Solid>> sols = e => { var r = new List<Solid>(); var g = e.get_Geometry(opt); if (g == null) return r;
    foreach (var go in g) { IEnumerable<GeometryObject> objs = go is GeometryInstance gi ? gi.GetInstanceGeometry().Cast<GeometryObject>() : new[] { go };
        foreach (var x in objs) { var s = x as Solid; if (s != null && s.Volume > 1e-9) r.Add(s); } } return r; };
var fr = new FilteredElementCollector(document).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().Cast<FamilyInstance>().ToList();
var members = fr.Where(f => f.Symbol.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_MARK)?.AsString() != "шов").ToList();
L.AppendLine("framing instances " + fr.Count + ", members " + members.Count + " (non-members: " + (fr.Count - members.Count) + ")");
// --- materials per mark
var byMark = members.GroupBy(f => f.Symbol.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_MARK)?.AsString() ?? "").OrderBy(g => g.Key);
var cols = new Dictionary<string, string>();
int faceNoMat = 0, faceWrong = 0; var wrongS = new List<string>();
foreach (var g in byMark)
{
    var mats = g.Select(f => (document.GetElement(f.StructuralMaterialId) as Material)).Where(m => m != null).GroupBy(m => m.Id).ToList();
    var mm = mats.FirstOrDefault()?.First();
    string info = mm == null ? "NO MAT" : mm.Name + " rgb(" + mm.Color.Red + "," + mm.Color.Green + "," + mm.Color.Blue + ") transp " + mm.Transparency + " shin " + mm.Shininess + " smooth " + mm.Smoothness + " renderShade " + mm.UseRenderAppearanceForShading;
    double gloss = -1; try { var ae = document.GetElement(mm.AppearanceAssetId) as AppearanceAssetElement; if (ae != null) { var asset = ae.GetRenderingAsset(); var pr = asset.FindByName("generic_glossiness") as Autodesk.Revit.DB.Visual.AssetPropertyDouble; if (pr != null) gloss = pr.Value; } } catch { }
    cols[g.Key] = mm == null ? "" : mm.Color.Red + "," + mm.Color.Green + "," + mm.Color.Blue;
    L.AppendLine("  марка " + g.Key + " ×" + g.Count() + ": " + info + " gloss " + gloss + " (материалдар саны " + mats.Count + ")");
    foreach (var f in g) { foreach (var s in sols(f)) foreach (Face fc in s.Faces) { var mid = fc.MaterialElementId; if (mid == ElementId.InvalidElementId) { faceNoMat++; if (wrongS.Count < 8) wrongS.Add("#" + f.Id + " " + g.Key + " face no mat"); } else { var fm = document.GetElement(mid) as Material; if (fm == null || fm.Name != "КМ_" + g.Key + " (С245)") { faceWrong++; if (wrongS.Count < 8) wrongS.Add("#" + f.Id + " " + g.Key + " face mat " + fm?.Name); } } } }
}
var dupCol = cols.Where(kv => kv.Value != "").GroupBy(kv => kv.Value).Where(g => g.Count() > 1).ToList();
L.AppendLine("МАТЕРИАЛ: беттері материалсыз " + faceNoMat + ", беттері басқа материалда " + faceWrong + (wrongS.Count > 0 ? " → " + string.Join("; ", wrongS) : "") + "; бірдей түсті марка жұптары " + dupCol.Count + (dupCol.Count > 0 ? " (" + string.Join(" | ", dupCol.Select(g => string.Join("=", g.Select(x => x.Key)))) + ")" : ""));
// --- DirectShape materials (grey faces)
var ds = new FilteredElementCollector(document).OfClass(typeof(DirectShape)).Cast<DirectShape>().ToList();
var dsStat = new Dictionary<string, int[]>(); var dsMatNames = new Dictionary<string, HashSet<string>>(); var noMatIds = new List<string>();
foreach (var d in ds) { string key = (d.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)?.AsString() ?? "") + "|" + d.Name.Split(' ')[0]; if (!dsStat.ContainsKey(key)) { dsStat[key] = new int[3]; dsMatNames[key] = new HashSet<string>(); }
    dsStat[key][0]++; foreach (var s in sols(d)) foreach (Face fc in s.Faces) { var mid = fc.MaterialElementId; if (mid == ElementId.InvalidElementId) { dsStat[key][1]++; if (noMatIds.Count < 6 && !noMatIds.Contains(d.Id.ToString())) noMatIds.Add(d.Id.ToString()); } else { dsStat[key][2]++; dsMatNames[key].Add((document.GetElement(mid) as Material)?.Name ?? "?"); } } }
foreach (var kv in dsStat.OrderBy(k => k.Key)) L.AppendLine("  DS " + kv.Key + " ×" + kv.Value[0] + " беттер без материала " + kv.Value[1] + ", с материалом " + kv.Value[2] + " мат: " + string.Join(",", dsMatNames[kv.Key]));
L.AppendLine("DS материалсыз беттері бар элементтер: " + noMatIds.Count + " " + string.Join(",", noMatIds));
// --- category line weights / colours
foreach (var bc in new[] { BuiltInCategory.OST_StructuralFraming, BuiltInCategory.OST_StructConnections, BuiltInCategory.OST_GenericModel })
{ try { var cat = Category.GetCategory(document, bc); var c = cat.LineColor; L.AppendLine("  category " + cat.Name + ": proj weight " + cat.GetLineWeight(GraphicsStyleType.Projection) + " cut " + cat.GetLineWeight(GraphicsStyleType.Cut) + " colour rgb(" + c.Red + "," + c.Green + "," + c.Blue + ")"); } catch (Exception e2) { L.AppendLine("  cat err " + e2.Message); } }
// --- 3D views overrides on framing/connection categories (graphic override weights)
foreach (var v in new FilteredElementCollector(document).OfClass(typeof(View3D)).Cast<View3D>().Where(v => !v.IsTemplate))
{ try { var o = v.GetCategoryOverrides(new ElementId(BuiltInCategory.OST_StructuralFraming)); L.AppendLine("  view3D «" + v.Name + "» framing: proj line weight " + o.ProjectionLineWeight + ", halftone " + o.Halftone + ", transp " + o.Transparency + ", detail " + v.DetailLevel + ", style " + v.DisplayStyle); } catch { } }
// --- low-threshold overlaps (> 20 mm3) between members
var sol = new Dictionary<ElementId, Solid>();
foreach (var f in members) { Solid acc = null; foreach (var s in sols(f)) { try { acc = acc == null ? s : BooleanOperationsUtils.ExecuteBooleanOperation(acc, s, BooleanOperationsType.Union); } catch { if (acc == null) acc = s; } } if (acc != null) sol[f.Id] = acc; }
var seen = new HashSet<string>(); var big = new List<string>(); int small = 0; var smallS = new List<string>();
foreach (var f in members) { if (!sol.ContainsKey(f.Id)) continue; var bb = f.get_BoundingBox(null); if (bb == null) continue;
    foreach (var hid in new FilteredElementCollector(document).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().WherePasses(new BoundingBoxIntersectsFilter(new Outline(bb.Min, bb.Max))).WherePasses(new ElementIntersectsSolidFilter(sol[f.Id])).ToElementIds())
    { if (hid == f.Id || !sol.ContainsKey(hid)) continue; string kk = Math.Min(f.Id.Value, hid.Value) + "_" + Math.Max(f.Id.Value, hid.Value); if (!seen.Add(kk)) continue;
        Solid x; try { x = BooleanOperationsUtils.ExecuteBooleanOperation(sol[f.Id], sol[hid], BooleanOperationsType.Intersect); } catch { continue; }
        if (x == null) continue; double v = x.Volume * MM * MM * MM; if (v > 500) big.Add(f.Id + "×" + hid + " " + Math.Round(v)); else if (v > 5) { small++; if (smallS.Count < 10) smallS.Add(f.Id + "×" + hid + " " + Math.Round(v, 1) + "мм³ @" + Math.Round(x.ComputeCentroid().X * MM) + "," + Math.Round(x.ComputeCentroid().Y * MM) + "," + Math.Round(x.ComputeCentroid().Z * MM)); } } }
L.AppendLine("ТРУБА ІШІНДЕ ТРУБА: >500 мм³: " + big.Count + "; 5…500 мм³: " + small + " " + string.Join("; ", smallS));
// --- orphan / duplicate welds and plates
var dsb = ds.Select(d => new { d, m = d.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)?.AsString() ?? "", b = d.get_BoundingBox(null) }).Where(x => x.b != null).ToList();
var sigs = new Dictionary<string, int>(); int dup = 0; var dupS = new List<string>();
foreach (var x in dsb) { string sg = x.m + "|" + Math.Round(x.b.Min.X * MM, 1) + "," + Math.Round(x.b.Min.Y * MM, 1) + "," + Math.Round(x.b.Min.Z * MM, 1) + "," + Math.Round(x.b.Max.X * MM, 1) + "," + Math.Round(x.b.Max.Y * MM, 1) + "," + Math.Round(x.b.Max.Z * MM, 1); if (sigs.ContainsKey(sg)) { dup++; if (dupS.Count < 6) dupS.Add("#" + x.d.Id + " " + sg); } else sigs[sg] = 1; }
L.AppendLine("ДУБЛЬ DirectShape (бірдей марка+габарит): " + dup + " " + string.Join("; ", dupS));
var mbb = members.Select(f => f.get_BoundingBox(null)).Where(b => b != null).ToList();
int orphan = 0; var orS = new List<string>(); double e1 = 1.5 / MM;
foreach (var x in dsb.Where(x => x.m.StartsWith("шов") || x.m == "ПЛ3" || x.m == "ПЛ5"))
{ var o = new Outline(x.b.Min - new XYZ(e1, e1, e1), x.b.Max + new XYZ(e1, e1, e1));
  bool hit = mbb.Any(b => new Outline(b.Min, b.Max).Intersects(o, 0)); if (!hit) hit = dsb.Any(y => y.d.Id != x.d.Id && (y.m == "ПЛ1" || y.m == "ПЛ2" || y.m == "ПЛ4" || y.m == "ПЛ3") && new Outline(y.b.Min, y.b.Max).Intersects(o, 0));
  if (!hit) { orphan++; if (orS.Count < 8) orS.Add(x.m + " #" + x.d.Id + " " + x.d.Name + " @" + Math.Round(x.b.Min.X * MM) + "," + Math.Round(x.b.Min.Y * MM) + "," + Math.Round(x.b.Min.Z * MM)); } }
L.AppendLine("ЖЕТІМСІЗ шов/заглушка/ПЛ5 (ештеңеге тимейді): " + orphan + " " + string.Join("; ", orS));
// Shop-piece counts per mark: vertical vs total
L.AppendLine("DS by mark: " + string.Join(", ", dsb.GroupBy(x => x.m).Select(g => g.Key + "=" + g.Count())));
} catch (Exception ex) { L.AppendLine("ERR " + ex); }
System.IO.File.WriteAllText(@"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\42cdf6e2-99f0-49e0-887d-f2503b7aa50f\scratchpad\_chk2.txt", L.ToString(), System.Text.Encoding.UTF8);
return "ok";