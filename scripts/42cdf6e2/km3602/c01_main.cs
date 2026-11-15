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
