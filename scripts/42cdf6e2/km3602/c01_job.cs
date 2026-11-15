// 3602 (user 15.11.2026 «обектерді жеке жеке айыр, сосын артықтардың барлығын өшір»): the 4 per-block files in Каркастар.
// Блок 1 is only checked (image + q20). Блок 2 / Портики Блок 3 / Карниз: the 30.10 «ус тест» undone in Блок 2 (2 members back to the
// archive values, test view deleted), BI КЖ template clutter removed (view templates, non-КМ filters, unrelated families, purge
// unused), saved compact; then an isometric image and the q20 audit of every file.
var dir = @"D:\Бекасыл КЖ КМ\3602_Порталы_КМ\Каркастар";
var S = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\42cdf6e2-99f0-49e0-887d-f2503b7aa50f\scratchpad\km3602";
var outLog = S + @"\_clean.txt";
var blocks = new[] { "Портал Блок 1", "Портал Блок 2", "Портики Блок 3", "Карниз" };
var uiapp = new UIApplication(document.Application);
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> h = null;
h = (s, e) => {
  uiapp.Idling -= h; var L = new System.Text.StringBuilder();
  Action flush = () => { try { System.IO.File.WriteAllText(outLog + ".part", L.ToString(), System.Text.Encoding.UTF8); } catch { } };
  var restore = new Dictionary<string, double[]>();
  try {
    var arc = @"D:\Бекасыл КЖ КМ\3602_Порталы_КМ\Архив\3602-КМ_Портал Блок 2_до_БК_30.10.2026.rvt";
    var tmp = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "km_arc_" + Guid.NewGuid().ToString("N") + ".rvt"); System.IO.File.Copy(arc, tmp, true);
    var da = uiapp.Application.OpenDocumentFile(tmp);
    foreach (var id in new long[] { 2730172, 2730173 }) {
      var fi = da.GetElement(new ElementId(id)) as FamilyInstance; if (fi == null) continue;
      restore[fi.UniqueId] = new[] { fi.get_Parameter(BuiltInParameter.START_EXTENSION).AsDouble(), fi.get_Parameter(BuiltInParameter.END_EXTENSION).AsDouble(),
        Autodesk.Revit.DB.Structure.StructuralFramingUtils.IsJoinAllowedAtEnd(fi, 0) ? 1.0 : 0.0, Autodesk.Revit.DB.Structure.StructuralFramingUtils.IsJoinAllowedAtEnd(fi, 1) ? 1.0 : 0.0 };
    }
    da.Close(false); try { System.IO.File.Delete(tmp); } catch { }
    L.AppendLine("archive values read: " + restore.Count);
  } catch (Exception ex) { L.AppendLine("archive ERR " + ex.Message); }
  foreach (var blk in blocks)
  {
    var path = System.IO.Path.Combine(dir, "3602-КМ_" + blk + ".rvt"); Document d = null; bool opened = false;
    L.AppendLine("##### " + blk); flush();
    try {
      foreach (Document od in uiapp.Application.Documents) if (string.Equals(od.PathName, path, StringComparison.OrdinalIgnoreCase)) d = od;
      if (d == null) { d = uiapp.Application.OpenDocumentFile(path); opened = true; }
      bool clean = blk != "Портал Блок 1";
      L.AppendLine(Cln.Counts(d, blk, blocks, "before"));
      if (clean) {
        using (var t = new Transaction(d, "Артықтарды өшіру")) {
          t.Start(); var fo = t.GetFailureHandlingOptions(); fo.SetFailuresPreprocessor(new Quiet2()); t.SetFailureHandlingOptions(fo);
          if (blk == "Портал Блок 2") L.AppendLine(Cln.Restore(d, restore));
          L.AppendLine(Cln.Views(d));
          L.AppendLine(Cln.Filters(d));
          L.AppendLine(Cln.Unrelated(d));
          L.AppendLine("commit " + t.Commit());
        }
        L.AppendLine(Cln.Purge(d));
      } else L.AppendLine("Блок 1 kept as is; unused elements (not purged): " + d.GetUnusedElements(new HashSet<ElementId>()).Count);
      L.AppendLine(Cln.Counts(d, blk, blocks, "after"));
      L.AppendLine(Cln.ProjInfo(d));
      L.AppendLine(Cln.Image(d, blk, S));
      if (clean) { d.Save(new SaveOptions { Compact = true }); L.AppendLine("saved (compact)"); }
      flush();
      try { Audit(d); L.AppendLine("q20: " + System.IO.File.ReadAllText(@"D:\Бекасыл КЖ КМ\3602_Порталы_КМ\_авто\_audit.txt", System.Text.Encoding.UTF8)); }
      catch (Exception ex) { L.AppendLine("q20 ERR " + ex.Message); }
    } catch (Exception ex) { L.AppendLine("ERR " + ex); }
    finally { try { if (opened && d != null) d.Close(false); } catch (Exception ex2) { L.AppendLine("close ERR " + ex2.Message); } }
    flush();
  }
  System.IO.File.WriteAllText(outLog, L.ToString(), System.Text.Encoding.UTF8);
};
uiapp.Idling += h; return "queued";
}
public class Quiet2 : IFailuresPreprocessor { public FailureProcessingResult PreprocessFailures(FailuresAccessor a) {
    foreach (var f in a.GetFailureMessages()) { if (f.GetSeverity() == FailureSeverity.Warning) a.DeleteWarning(f); else if (f.HasResolutions()) { try { a.ResolveFailure(f); } catch { } } }
    return FailureProcessingResult.Continue; } }
public static class Cln {
  const double MM = 304.8;
  public static string Counts(Document d, string blk, string[] blocks, string tag) {
    Func<Type, int> n = ty => new FilteredElementCollector(d).OfClass(ty).GetElementCount();
    var vv = new FilteredElementCollector(d).OfClass(typeof(View)).Cast<View>().ToList();
    int foreign = new FilteredElementCollector(d).WhereElementIsNotElementType().Count(x => { var c = x.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString(); return !string.IsNullOrEmpty(c) && !c.Contains(blk) && blocks.Any(b => c.Contains(b)); });
    return tag + ": families " + n(typeof(Family)) + ", element types " + new FilteredElementCollector(d).WhereElementIsElementType().GetElementCount() + ", materials " + n(typeof(Material))
      + ", filters " + n(typeof(ParameterFilterElement)) + ", views " + vv.Count(v => !v.IsTemplate) + " [" + string.Join("; ", vv.Where(v => !v.IsTemplate && v.ViewType != ViewType.ProjectBrowser && v.ViewType != ViewType.SystemBrowser).Select(v => v.Name)) + "]"
      + ", templates " + vv.Count(v => v.IsTemplate) + ", framing " + new FilteredElementCollector(d).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().GetElementCount()
      + ", directshapes " + n(typeof(DirectShape)) + ", grids " + n(typeof(Grid)) + ", levels " + n(typeof(Level)) + ", FOREIGN-block elements " + foreign;
  }
  public static string Restore(Document d, Dictionary<string, double[]> r) {
    var sb = new System.Text.StringBuilder("restore Блок 2 «ус тест»: ");
    foreach (var kv in r) {
      var fi = d.GetElement(kv.Key) as FamilyInstance; if (fi == null) { sb.Append(kv.Key + " missing; "); continue; }
      for (int end = 0; end < 2; end++) {
        bool want = kv.Value[2 + end] > 0.5, now = Autodesk.Revit.DB.Structure.StructuralFramingUtils.IsJoinAllowedAtEnd(fi, end);
        if (want != now) { if (want) Autodesk.Revit.DB.Structure.StructuralFramingUtils.AllowJoinAtEnd(fi, end); else Autodesk.Revit.DB.Structure.StructuralFramingUtils.DisallowJoinAtEnd(fi, end); }
      }
      d.Regenerate();
      fi.get_Parameter(BuiltInParameter.START_EXTENSION).Set(kv.Value[0]); fi.get_Parameter(BuiltInParameter.END_EXTENSION).Set(kv.Value[1]);
      d.Regenerate();
      sb.AppendFormat("{0}: ext {1:F2}/{2:F2} join {3}/{4}; ", fi.Id, fi.get_Parameter(BuiltInParameter.START_EXTENSION).AsDouble() * MM, fi.get_Parameter(BuiltInParameter.END_EXTENSION).AsDouble() * MM,
        Autodesk.Revit.DB.Structure.StructuralFramingUtils.IsJoinAllowedAtEnd(fi, 0), Autodesk.Revit.DB.Structure.StructuralFramingUtils.IsJoinAllowedAtEnd(fi, 1));
    }
    return sb.ToString();
  }
  public static string Views(Document d) {
    int nv = 0, nt = 0;
    var test = new FilteredElementCollector(d).OfClass(typeof(View)).Cast<View>().Where(v => !v.IsTemplate && v.Name.Contains("тест")).Select(v => v.Id).ToList();
    foreach (var id in test) { try { if (d.GetElement(id) != null) { d.Delete(id); nv++; } } catch { } }
    foreach (var v in new FilteredElementCollector(d).OfClass(typeof(View)).Cast<View>().Where(v => !v.IsTemplate).ToList())
      { try { if (v.IsValidObject && v.ViewTemplateId != ElementId.InvalidElementId) v.ViewTemplateId = ElementId.InvalidElementId; } catch { } }
    var tpl = new FilteredElementCollector(d).OfClass(typeof(View)).Cast<View>().Where(v => v.IsTemplate).Select(v => v.Id).ToList();
    foreach (var id in tpl) { try { if (d.GetElement(id) != null) { d.Delete(id); nt++; } } catch { } }
    return "test views deleted " + nv + ", view templates deleted " + nt + "/" + tpl.Count;
  }
  public static string Filters(Document d) {
    var ids = new FilteredElementCollector(d).OfClass(typeof(ParameterFilterElement)).Cast<Element>().Where(f => !f.Name.StartsWith("КМ_")).Select(f => f.Id)
      .Concat(new FilteredElementCollector(d).OfClass(typeof(SelectionFilterElement)).ToElementIds()).ToList();
    int n = 0; foreach (var id in ids) { try { if (d.GetElement(id) != null) { d.Delete(id); n++; } } catch { } }
    return "filters deleted " + n + "/" + ids.Count + "; left: " + string.Join(", ", new FilteredElementCollector(d).OfClass(typeof(ParameterFilterElement)).Cast<Element>().Select(f => f.Name));
  }
  public static string Unrelated(Document d) {
    var cats = new[] { BuiltInCategory.OST_StructuralFramingSystem, BuiltInCategory.OST_CurtaSystem, BuiltInCategory.OST_DuctCurves, BuiltInCategory.OST_FlexDuctCurves,
      BuiltInCategory.OST_FlexPipeCurves, BuiltInCategory.OST_CurtainWallMullions, BuiltInCategory.OST_CableTray, BuiltInCategory.OST_Conduit, BuiltInCategory.OST_Roofs,
      BuiltInCategory.OST_Stairs, BuiltInCategory.OST_StairsRailing, BuiltInCategory.OST_Ramps, BuiltInCategory.OST_CurtainWallPanels, BuiltInCategory.OST_Ceilings,
      BuiltInCategory.OST_DuctSystem, BuiltInCategory.OST_Toposolid, BuiltInCategory.OST_PipingSystem, BuiltInCategory.OST_PipeCurves, BuiltInCategory.OST_FabricReinforcement,
      BuiltInCategory.OST_FabricAreas, BuiltInCategory.OST_AreaRein, BuiltInCategory.OST_PathRein, BuiltInCategory.OST_Rebar, BuiltInCategory.OST_RebarTags, BuiltInCategory.OST_Columns,
      BuiltInCategory.OST_StructuralColumns, BuiltInCategory.OST_Site, BuiltInCategory.OST_Topography, BuiltInCategory.OST_CableTrayRun, BuiltInCategory.OST_ConduitRun,
      BuiltInCategory.OST_MechanicalEquipment, BuiltInCategory.OST_PlumbingFixtures, BuiltInCategory.OST_Doors, BuiltInCategory.OST_Windows, BuiltInCategory.OST_Furniture,
      BuiltInCategory.OST_MedicalEquipment };
    var catIds = new HashSet<long>(cats.Select(c => (long)c));
    var used = new HashSet<long>(new FilteredElementCollector(d).WhereElementIsNotElementType().Select(x => x.GetTypeId().Value));
    int nF = 0, nT = 0; var refused = new List<string>();
    foreach (var f in new FilteredElementCollector(d).OfClass(typeof(Family)).Cast<Family>().ToList()) {
      if (!f.IsValidObject) continue;
      bool unrelated = (f.FamilyCategory != null && catIds.Contains(f.FamilyCategory.Id.Value)) || f.Name == "(марка)арматурный_стержень" || f.Name == "Системная панель" || f.Name.Contains("импост");
      if (!unrelated) continue;
      if (f.GetFamilySymbolIds().Any(id => used.Contains(id.Value))) { refused.Add(f.Name + " (используется)"); continue; }
      var nm = f.Name; try { d.Delete(f.Id); nF++; } catch (Exception ex) { refused.Add(nm + ": " + ex.Message.Split('\n')[0]); }
    }
    foreach (var t in new FilteredElementCollector(d).WhereElementIsElementType().Cast<ElementType>().ToList()) {
      if (!t.IsValidObject || t.Category == null || !catIds.Contains(t.Category.Id.Value) || used.Contains(t.Id.Value)) continue;
      var nm = t.Category.Name + ": " + t.Name; try { d.Delete(t.Id); nT++; } catch (Exception ex) { refused.Add(nm + " — " + ex.Message.Split('\n')[0]); }
    }
    return "unrelated families deleted " + nF + ", system types " + nT + "; refused " + refused.Count + (refused.Count > 0 ? ": " + string.Join("; ", refused.Take(12)) : "");
  }
  public static string Purge(Document d) {
    var log = new System.Text.StringBuilder("purge: "); int total = 0;
    using (var t = new Transaction(d, "Удалить неиспользуемое")) {
      t.Start(); var fo = t.GetFailureHandlingOptions(); fo.SetFailuresPreprocessor(new Quiet2()); t.SetFailureHandlingOptions(fo);
      for (int pass = 0; pass < 10; pass++) {
        var ids = d.GetUnusedElements(new HashSet<ElementId>()).Where(id => d.GetElement(id) != null).ToList();
        if (ids.Count == 0) break;
        int n = 0;
        try { n = d.Delete(ids).Count; }
        catch { foreach (var id in ids) try { if (d.GetElement(id) != null) { d.Delete(id); n++; } } catch { } }
        total += n; log.Append("pass " + (pass + 1) + ": " + ids.Count + "→" + n + "; ");
        d.Regenerate();
      }
      log.Append("commit " + t.Commit());
    }
    return log.ToString() + "; total " + total + "; families left: " + string.Join(", ", new FilteredElementCollector(d).OfClass(typeof(Family)).Cast<Family>().Select(f => f.Name).OrderBy(q => q));
  }
  public static string ProjInfo(Document d) {
    var pi = d.ProjectInformation; if (pi == null) return "projinfo: none";
    return "projinfo: " + string.Join(" | ", pi.Parameters.Cast<Parameter>().Where(p => p.StorageType == StorageType.String && !string.IsNullOrWhiteSpace(p.AsString())).Select(p => p.Definition.Name + "=" + p.AsString()).OrderBy(q => q));
  }
  public static string Image(Document d, string blk, string S) {
    try {
      var vft = new FilteredElementCollector(d).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().First(x => x.ViewFamily == ViewFamily.ThreeDimensional);
      var bbs = new FilteredElementCollector(d).WhereElementIsNotElementType().Where(x => x.Category != null && x.Category.CategoryType == CategoryType.Model
          && (x is FamilyInstance || x is DirectShape || x is Floor || x is Wall)).Select(x => x.get_BoundingBox(null)).Where(b => b != null).ToList();
      var lo = new XYZ(bbs.Min(b => b.Min.X), bbs.Min(b => b.Min.Y), bbs.Min(b => b.Min.Z)); var hi = new XYZ(bbs.Max(b => b.Max.X), bbs.Max(b => b.Max.Y), bbs.Max(b => b.Max.Z));
      var c = (lo + hi) / 2; var fwd = new XYZ(0.55, 1, -0.45).Normalize(); var up = (XYZ.BasisZ - fwd * XYZ.BasisZ.DotProduct(fwd)).Normalize();
      var eye = c - fwd * (150000 / MM);
      ElementId vid;
      using (var t = new Transaction(d, "tmp image view")) {
        t.Start(); var v = View3D.CreateIsometric(d, vft.Id); v.SetOrientation(new ViewOrientation3D(eye, up, fwd));
        try { v.DisplayStyle = DisplayStyle.ShadingWithEdges; } catch { } try { v.DetailLevel = ViewDetailLevel.Fine; } catch { }
        foreach (var bic in new[] { BuiltInCategory.OST_Levels, BuiltInCategory.OST_Grids, BuiltInCategory.OST_SectionBox }) { try { v.SetCategoryHidden(new ElementId(bic), true); } catch { } }
        vid = v.Id; t.Commit();
      }
      var fn = System.IO.Path.Combine(S, "img_" + blk.Replace(" ", "_"));
      var o = new ImageExportOptions { ExportRange = ExportRange.SetOfViews, FilePath = fn, ZoomType = ZoomFitType.FitToPage, PixelSize = 1400, FitDirection = FitDirectionType.Horizontal,
        ImageResolution = ImageResolution.DPI_150, HLRandWFViewsFileType = ImageFileType.PNG, ShadowViewsFileType = ImageFileType.PNG };
      o.SetViewsAndSheets(new List<ElementId> { vid });
      d.ExportImage(o);
      using (var t = new Transaction(d, "tmp image view del")) { t.Start(); d.Delete(vid); t.Commit(); }
      return "image → " + fn + string.Format("  (model bbox mm X {0:F0}..{1:F0} Y {2:F0}..{3:F0} Z {4:F0}..{5:F0})", lo.X * MM, hi.X * MM, lo.Y * MM, hi.Y * MM, lo.Z * MM, hi.Z * MM);
    } catch (Exception ex) { return "image ERR " + ex.Message; }
  }
}
static object Audit(Document document) {

// КМ model audit (user 29.10.2026: «мен айтқан қателерді алдағы уақытта жасамау үшін тексеретін агент жаса»). Read-only.
// Every check is a defect the user has pointed out once; each must be 0 before the model is shown:
//  C1 tube inside tube (any two members overlapping > 0.5 cm³: duplicates, collinear overrun, uncut crossing)   «мөлдір көрінеді»
//  C2 member stopped under a lower-rank one (cut back although only lower ranks meet there; a post under a top belt Б1 is meant to)                     «жасыл жоғарыға шығуы керек»
//  C3 higher-rank end not run over the lower members ending on it (post top below the belt top)                 ✗ corner, Блок 1
//  C4 open tube end without a cap ПЛ3, and caps not sitting on a free tube end                                     «реалды түрде»
//  C5 cut end without a weld bead / plate without a weld / joined crossing without a collar weld                  «сварка жоқ»
//  C6 end face lying exactly on the face it meets (z-fighting stripes)                                              «мынау не» (diagonal line)
//  C7 seam line across a straight column: collinear same-mark segments not joined                                 «мынау не» (horizontal line)
//  C8 bracket Кр1 end that is neither on a plate (RC) nor on a member                                              «кронштейн тек жб-ға»
//  C9 member material ≠ «КМ_<марка> (С245)» (colour per mark in every view)                                         «металдарға неге цвет бермедің»
//  C11 two support plates on top of each other (one shared plate ПЛ4)                                             3 nuts on 2 plates
//  C12 a top belt Б1 ending on a post top stops short of the post's far face                                     «соңына дейін жеткіз»
//  C10 needless splice: collinear pieces of one mark joined where no higher-rank member touches and no storey level   «әр қиылыста кесе берме»
// Writes _audit.txt (PASS/FAIL per check, samples with coordinates) and _boxes_audit.txt (close-up boxes of the first failures,
// format of q10_joints_img.cs). Rank: К1 > Ст1 > А1 > Б1 > Пр1 > Кн1 > Р1 > Кр1.
const double MM = 304.8;
var LOG = new System.Text.StringBuilder(); var BOX = new System.Text.StringBuilder();
try {
var rank = new Dictionary<string, int> { { "К1", 8 }, { "Ст1", 7 }, { "А1", 6 }, { "Б1", 5 }, { "Пр1", 4 }, { "Кн1", 3 }, { "Р1", 2 }, { "Кр1", 1 }, { "Кр2", 1 } };   // Кр2 — brackets of the AR cornices ДП-2 / ДП-3 (30.10.2026)
double tol = 2 / MM;
var opt = new Options { DetailLevel = ViewDetailLevel.Fine };
var fr = new FilteredElementCollector(document).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().Cast<FamilyInstance>().ToList();
var A = new List<Mb>();
foreach (var f in fr)
{
    var c = ((LocationCurve)f.Location).Curve; var a = c.GetEndPoint(0); var u = (c.GetEndPoint(1) - a).Normalize();
    XYZ ex = null;
    foreach (var go in f.get_Geometry(opt)) { IEnumerable<GeometryObject> objs = go is GeometryInstance gi ? gi.GetInstanceGeometry().Cast<GeometryObject>() : new[] { go };
        foreach (var o in objs) { var s = o as Solid; if (s == null || s.Volume <= 0) continue;
            foreach (Face fc in s.Faces) { var pf = fc as PlanarFace; if (pf != null && Math.Abs(pf.FaceNormal.DotProduct(u)) < 1e-3) { ex = pf.FaceNormal; break; } }
            if (ex != null) break; } if (ex != null) break; }
    if (ex == null) ex = Math.Abs(u.Z) > 0.9 ? XYZ.BasisX : u.CrossProduct(XYZ.BasisZ).Normalize();
    var t = document.GetElement(f.GetTypeId()); var mk = f.Symbol.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_MARK)?.AsString() ?? ""; if (mk == "") mk = f.LookupParameter("БК_позиция")?.AsString() ?? f.LookupParameter("BI_позиция")?.AsString() ?? "";
    A.Add(new Mb { f = f, a = a, u = u, ex = ex, ey = u.CrossProduct(ex).Normalize(), len = c.Length,
        e0 = f.get_Parameter(BuiltInParameter.START_EXTENSION).AsDouble(), e1 = f.get_Parameter(BuiltInParameter.END_EXTENSION).AsDouble(),
        hb = (t.LookupParameter("b")?.AsDouble() ?? 40 / MM) / 2, hh = (t.LookupParameter("h")?.AsDouble() ?? 40 / MM) / 2,
        mk = mk, r = rank.ContainsKey(mk) ? rank[mk] : 0, blk = f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString() ?? "" });
}
double cell = 500 / MM; var grid = new Dictionary<string, List<int>>();
Func<XYZ, int, int, int, string> key = (p, dx, dy, dz) => (Math.Floor(p.X / cell) + dx) + "|" + (Math.Floor(p.Y / cell) + dy) + "|" + (Math.Floor(p.Z / cell) + dz);
for (int i = 0; i < A.Count; i++) { int n = Math.Max(1, (int)Math.Ceiling(A[i].len / cell));
    for (int k = 0; k <= n; k++) { var kk = key(A[i].a + A[i].u * (A[i].len * k / n), 0, 0, 0); if (!grid.ContainsKey(kk)) grid[kk] = new List<int>(); if (!grid[kk].Contains(i)) grid[kk].Add(i); } }
Func<XYZ, List<int>> near = p => { var h = new HashSet<int>(); for (int dx = -1; dx <= 1; dx++) for (int dy = -1; dy <= 1; dy++) for (int dz = -1; dz <= 1; dz++) { var kk = key(p, dx, dy, dz); if (grid.ContainsKey(kk)) foreach (var j in grid[kk]) h.Add(j); } return h.ToList(); };
Func<Mb, XYZ, bool> onAxis = (o, p) => { double s = (p - o.a).DotProduct(o.u); return s > -tol && s < o.len + tol && (p - o.a - o.u * s).GetLength() < tol; };
Func<Mb, XYZ, bool> isEnd = (o, p) => o.a.DistanceTo(p) < tol || (o.a + o.u * o.len).DistanceTo(p) < tol;
Func<Mb, Mb, bool> par = (x, y) => x.u.CrossProduct(y.u).GetLength() < 1e-3;
// signed distance of q to the surface of o's full prism (negative = inside)
Func<Mb, XYZ, double> sdist = (o, q) => { var d = q - o.a; double s = d.DotProduct(o.u), x = Math.Abs(d.DotProduct(o.ex)), y = Math.Abs(d.DotProduct(o.ey));
    return Math.Max(Math.Max(x - o.hb, y - o.hh), Math.Max(-o.e0 - s, s - (o.len + o.e1))); };
Func<XYZ, string> P3 = p => Math.Round(p.X * MM) + "," + Math.Round(p.Y * MM) + "," + Math.Round(p.Z * MM);
var DS = new FilteredElementCollector(document).OfClass(typeof(DirectShape)).Cast<DirectShape>().Select(d => new { d, mk = d.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)?.AsString() ?? "", bb = d.get_BoundingBox(null) }).Where(x => x.bb != null).ToList();
var welds = DS.Where(x => x.mk.StartsWith("шов")).Select(x => new Outline(x.bb.Min, x.bb.Max)).ToList();
var caps = DS.Where(x => x.mk == "ПЛ3").Select(x => x.bb).ToList();
var plates = DS.Where(x => x.mk == "ПЛ1" || x.mk == "ПЛ2" || x.mk == "ПЛ4").ToList();
Func<XYZ, double, bool> weldAt = (p, r) => { var o = new Outline(p - new XYZ(r, r, r), p + new XYZ(r, r, r)); return welds.Any(w => w.Intersects(o, 0)); };
Func<XYZ, double, bool> plateAt = (p, r) => { var o = new Outline(p - new XYZ(r, r, r), p + new XYZ(r, r, r)); return plates.Any(w => new Outline(w.bb.Min, w.bb.Max).Intersects(o, 0)); };
var R = new Dictionary<string, List<string>>(); var firstBox = new Dictionary<string, XYZ>();
foreach (var c in new[] { "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10", "C11", "C12" }) R[c] = new List<string>();
var levelsZ = new FilteredElementCollector(document).OfClass(typeof(Level)).Cast<Level>().Select(l => l.Elevation).ToList();
Action<string, string, XYZ> fail = (c, s, p) => { R[c].Add(s + " @ " + P3(p)); if (!firstBox.ContainsKey(c)) firstBox[c] = p; };
var usedCaps = new HashSet<int>();
// C1 overlaps (solid booleans)
var sol = new Dictionary<ElementId, Solid>();
foreach (var f in fr) { Solid acc = null;
    foreach (var go in f.get_Geometry(opt)) { IEnumerable<GeometryObject> objs = go is GeometryInstance gi ? gi.GetInstanceGeometry().Cast<GeometryObject>() : new[] { go };
        foreach (var o in objs) { var s = o as Solid; if (s == null || s.Volume <= 1e-9) continue; try { acc = acc == null ? s : BooleanOperationsUtils.ExecuteBooleanOperation(acc, s, BooleanOperationsType.Union); } catch { if (acc == null) acc = s; } } }
    if (acc != null) sol[f.Id] = acc; }
var seen = new HashSet<string>();
foreach (var f in fr)
{
    if (!sol.ContainsKey(f.Id)) continue; var bb = f.get_BoundingBox(null); if (bb == null) continue;
    foreach (var hid in new FilteredElementCollector(document).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType()
        .WherePasses(new BoundingBoxIntersectsFilter(new Outline(bb.Min, bb.Max))).WherePasses(new ElementIntersectsSolidFilter(sol[f.Id])).ToElementIds())
    {
        if (hid == f.Id || !sol.ContainsKey(hid)) continue;
        string kk = Math.Min(f.Id.Value, hid.Value) + "_" + Math.Max(f.Id.Value, hid.Value); if (!seen.Add(kk)) continue;
        Solid x; try { x = BooleanOperationsUtils.ExecuteBooleanOperation(sol[f.Id], sol[hid], BooleanOperationsType.Intersect); } catch { continue; }
        if (x != null && x.Volume * MM * MM * MM > 500) fail("C1", f.Id.Value + "×" + hid.Value + " " + Math.Round(x.Volume * MM * MM * MM / 1000, 1) + " см³", x.ComputeCentroid());
    }
}
// per member end
for (int i = 0; i < A.Count; i++)
{
    var m = A[i];
    for (int e = 0; e < 2; e++)
    {
        double ext = e == 0 ? m.e0 : m.e1; var P = e == 0 ? m.a : m.a + m.u * m.len; var outw = e == 0 ? -m.u : m.u; var E = P + outw * ext;
        var nb = near(P).Where(j => j != i).Select(j => A[j]).ToList();
        var atNode = nb.Where(o => onAxis(o, P) && !par(o, m)).ToList();
        bool cont = nb.Any(o => par(o, m) && isEnd(o, P));
        bool onPlate = ext < -7.5 / MM && ext > -9 / MM && plateAt(E + outw * (4 / MM), 6 / MM);
        string id = m.f.Id.Value + " " + m.mk + (e == 0 ? " нач" : " кон") + " ext " + Math.Round(ext * MM, 1) + " " + m.blk;
        // C2: cut back but nothing of higher / same-through rank here
        if (ext < -0.5 / MM && !onPlate && atNode.Count > 0 && atNode.All(o => o.r < m.r) && !(Math.Abs(m.u.Z) > 0.99 && atNode.Any(o => o.r == 5 && Math.Abs(o.u.Z) < 0.05))) fail("C2", id + " под " + string.Join("+", atNode.Select(o => o.mk)), P);
        // C3: higher rank, only lower ranks meet here, no continuation → must reach over them
        var lows = atNode.Where(o => o.r < m.r).ToList();
        if (!cont && lows.Count > 0 && atNode.All(o => o.r < m.r) && ext >= -0.5 / MM)
        {
            double need = lows.Max(o => Math.Abs(o.ex.DotProduct(m.u)) * o.hb + Math.Abs(o.ey.DotProduct(m.u)) * o.hh);
            if (ext < need - 1 / MM) fail("C3", id + " нужно ≥ " + Math.Round(need * MM, 1) + " (над " + string.Join("+", lows.Select(o => o.mk)) + ")", P);
        }
        // C12: a top belt Б1 ending on a post top (nothing else there) reaches the post's far face (user 30.10.2026 «соңына дейін жеткіз»)
        if (m.r == 5 && Math.Abs(m.u.Z) < 0.05 && atNode.Count == 1 && Math.Abs(atNode[0].u.Z) > 0.99 && isEnd(atNode[0], P) && (atNode[0].a.DistanceTo(P) < tol ? atNode[0].a + atNode[0].u * atNode[0].len : atNode[0].a).Z < P.Z && !cont)
        { var ps = atNode[0]; double need = Math.Abs(outw.X) * ps.hb + Math.Abs(outw.Y) * ps.hh; need = Math.Max(need, Math.Abs(outw.Y) * ps.hb + Math.Abs(outw.X) * ps.hh);
          if (ext < need - 1 / MM) fail("C12", id + " не доходит до грани стойки " + ps.f.Id.Value + " (нужно " + Math.Round(need * MM) + ")", P); }
        // C4: free end → cap
        bool free = ext > -0.5 / MM && !cont;
        if (free)
        {
            var probes = new List<XYZ> { E + outw * tol };
            foreach (var sx in new[] { -1.0, 1 }) foreach (var sy in new[] { -1.0, 1 }) probes.Add(E + outw * tol + m.ex * (sx * (m.hb - tol)) + m.ey * (sy * (m.hh - tol)));
            free = !nb.Any(o => probes.Any(q => sdist(o, q) <= 0));
        }
        if (free)
        {
            int ci = caps.FindIndex(cb => { var cc = (cb.Min + cb.Max) / 2; return cc.DistanceTo(E + outw * (2 / MM)) < 4 / MM; });
            if (ci < 0) fail("C4", id + " открытый торец без заглушки", E); else usedCaps.Add(ci);
            if (m.mk == "Кр1") fail("C8", id + " кронштейн висит (нет ПЛ / элемента)", E);
        }
        // C5: cut end → weld
        if (ext < -0.5 / MM && !weldAt(E + outw * (0.5 / MM), Math.Max(m.hb, m.hh) + 4 / MM)) fail("C5", id + " торец без шва", E);
        // C6: end face exactly on a face of the member it meets
        if (ext < -0.5 / MM && !onPlate)
            foreach (var sx in new[] { -0.9, 0.9 }) foreach (var sy in new[] { -0.9, 0.9 })
            {
                var q = E + m.ex * (sx * m.hb) + m.ey * (sy * m.hh);
                var o = nb.FirstOrDefault(x => Math.Abs(sdist(x, q)) < 0.1 / MM);
                if (o != null) { fail("C6", id + " торец в плоскости грани " + o.f.Id.Value + " " + o.mk, q); goto nextEnd; }
            }
        nextEnd:;
        // C7: seam on a straight column
        foreach (var o in nb.Where(o => par(o, m) && isEnd(o, P) && o.mk == m.mk && o.f.Id.Value > m.f.Id.Value))
        {
            double oext = o.a.DistanceTo(P) < tol ? o.e0 : o.e1;   // pieces cut back to a member between them do not touch — no seam
            if (ext > -0.5 / MM && oext > -0.5 / MM && !JoinGeometryUtils.AreElementsJoined(document, m.f, o.f)) fail("C7", m.f.Id.Value + "|" + o.f.Id.Value + " " + m.mk + " шов-линия на стыке сегментов " + m.blk, P);
            // C10: a splice is allowed only where a higher-rank member touches the node, or (vertical) at a storey level
            // a top belt Б1 is not split where a post only ends under it (30.10.2026)
            bool hi = nb.Any(x => x.r > m.r && !par(x, m) && onAxis(x, P) && !(m.r == 5 && Math.Abs(m.u.Z) < 0.05 && Math.Abs(x.u.Z) > 0.99 && isEnd(x, P) && (x.a.DistanceTo(P) < tol ? x.a + x.u * x.len : x.a).Z < P.Z));
            bool storey = Math.Abs(m.u.Z) > 0.99 && levelsZ.Any(z => Math.Abs(P.Z - z) < 600 / MM);
            if (!hi && !storey && o.f.GetTypeId() == m.f.GetTypeId() && o.blk == m.blk) fail("C10", m.f.Id.Value + "|" + o.f.Id.Value + " " + m.mk + " лишний стык (нет старшего элемента, не уровень этажа) " + m.blk, P);
        }
    }
    // C9 material
    var mat = document.GetElement(m.f.StructuralMaterialId) as Material;
    if (mat == null || mat.Name != "КМ_" + m.mk + " (С245)") fail("C9", m.f.Id.Value + " " + m.mk + " материал «" + (mat?.Name ?? "—") + "»", m.a);
}
// C4b: caps not on a free end; C5b: plates without weld; C5c: joined crossings without a collar
for (int ci = 0; ci < caps.Count; ci++) if (!usedCaps.Contains(ci)) fail("C4", "заглушка ПЛ3 не на свободном торце", (caps[ci].Min + caps[ci].Max) / 2);
foreach (var p in plates) { var o = new Outline(p.bb.Min - new XYZ(0.02, 0.02, 0.02), p.bb.Max + new XYZ(0.02, 0.02, 0.02)); if (!welds.Any(w => w.Intersects(o, 0))) fail("C5", p.mk + " " + p.d.Id.Value + " пластина без шва", (p.bb.Min + p.bb.Max) / 2); }
// C11: two plates on top of each other (one shared plate ПЛ4 is wanted)
for (int i = 0; i < plates.Count; i++) for (int j = i + 1; j < plates.Count; j++)
{
    var b1 = plates[i].bb; var b2 = plates[j].bb;
    double ox = Math.Min(b1.Max.X, b2.Max.X) - Math.Max(b1.Min.X, b2.Min.X), oy = Math.Min(b1.Max.Y, b2.Max.Y) - Math.Max(b1.Min.Y, b2.Min.Y), oz = Math.Min(b1.Max.Z, b2.Max.Z) - Math.Max(b1.Min.Z, b2.Min.Z);
    if (ox > 1 / MM && oy > 1 / MM && oz > 1 / MM) fail("C11", plates[i].mk + " " + plates[i].d.Id.Value + " / " + plates[j].mk + " " + plates[j].d.Id.Value + " пластины друг на друге", (b1.Min + b1.Max) / 2);
}
var jseen = new HashSet<string>();
foreach (var f in fr) foreach (var gid in JoinGeometryUtils.GetJoinedElements(document, f))
{
    var g = document.GetElement(gid) as FamilyInstance; if (g == null || g.Category.Id.Value != (long)BuiltInCategory.OST_StructuralFraming) continue;
    string kk = Math.Min(f.Id.Value, gid.Value) + "_" + Math.Max(f.Id.Value, gid.Value); if (!jseen.Add(kk)) continue;
    var cf = (Line)((LocationCurve)f.Location).Curve; var cg = (Line)((LocationCurve)g.Location).Curve; if (cf.Direction.CrossProduct(cg.Direction).GetLength() < 1e-3) continue;
    var b1 = f.get_BoundingBox(null); var b2 = g.get_BoundingBox(null);
    var lo = new XYZ(Math.Max(b1.Min.X, b2.Min.X), Math.Max(b1.Min.Y, b2.Min.Y), Math.Max(b1.Min.Z, b2.Min.Z)) - new XYZ(0.02, 0.02, 0.02);
    var hi = new XYZ(Math.Min(b1.Max.X, b2.Max.X), Math.Min(b1.Max.Y, b2.Max.Y), Math.Min(b1.Max.Z, b2.Max.Z)) + new XYZ(0.02, 0.02, 0.02);
    if (lo.X > hi.X || lo.Y > hi.Y || lo.Z > hi.Z) continue;
    var zone = new Outline(lo, hi); if (!welds.Any(w => w.Intersects(zone, 0))) fail("C5", kk + " соединение без шва", (lo + hi) / 2);
}
var names = new Dictionary<string, string> { { "C1", "труба в трубе" }, { "C2", "элемент обрезан под младшим" }, { "C3", "старший не перекрывает младших" }, { "C4", "заглушки ПЛ3" },
    { "C5", "швы" }, { "C6", "торец в плоскости грани (мерцание)" }, { "C7", "линия стыка на прямой колонне" }, { "C8", "кронштейн не на ж/б" }, { "C9", "материал/цвет марки" }, { "C10", "лишние стыки (труба = заводская деталь)" }, { "C11", "пластины друг на друге" }, { "C12", "торец пояса не перекрывает стойку" } };
int total = R.Sum(x => x.Value.Count);
LOG.AppendLine("КМ AUDIT " + DateTime.Now.ToString("dd.MM.yyyy HH:mm") + " — members " + A.Count + ", welds " + welds.Count + ", caps " + caps.Count + ", plates " + plates.Count + " → " + (total == 0 ? "ALL PASS" : "FAIL " + total));
foreach (var kv in R) LOG.AppendLine(kv.Key + " " + names[kv.Key] + ": " + (kv.Value.Count == 0 ? "PASS" : "FAIL " + kv.Value.Count));
foreach (var kv in R.Where(x => x.Value.Count > 0)) { LOG.AppendLine("— " + kv.Key); foreach (var s in kv.Value.Take(15)) LOG.AppendLine("   " + s); }
foreach (var kv in firstBox) { var c = kv.Value * MM;
    BOX.AppendLine("audit " + kv.Key + ";" + Math.Round(c.X - 220) + "," + Math.Round(c.Y - 220) + "," + Math.Round(c.Z - 180) + ";" + Math.Round(c.X + 220) + "," + Math.Round(c.Y + 220) + "," + Math.Round(c.Z + 180) + ";0.6,0.8,-0.5"); }
} catch (Exception ex) { LOG.AppendLine("ERR " + ex); }
System.IO.File.WriteAllText(@"D:\Бекасыл КЖ КМ\3602_Порталы_КМ\_авто\_audit.txt", LOG.ToString(), System.Text.Encoding.UTF8);
System.IO.File.WriteAllText(@"D:\Бекасыл КЖ КМ\3602_Порталы_КМ\_авто\_boxes_audit.txt", BOX.ToString(), System.Text.Encoding.UTF8);
var head = LOG.ToString(); return head.Length > 1500 ? head.Substring(0, 1500) : head;
}
public class Mb { public FamilyInstance f; public XYZ a, u, ex, ey; public double len, e0, e1, hb, hh; public string mk, blk; public int r; }
static void Pad() {
