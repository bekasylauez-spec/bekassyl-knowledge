// 3602: read-only inspection of the 4 per-block files in Каркастар — what belongs to the block, what is foreign or extra.
// Opens each file in the background (or uses it if already open), writes a report, closes without saving.
var blocks = new[] { "Портал Блок 1", "Портал Блок 2", "Портики Блок 3", "Карниз" };
var dir = @"D:\Бекасыл КЖ КМ\3602_Порталы_КМ\Каркастар";
var outLog = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\42cdf6e2-99f0-49e0-887d-f2503b7aa50f\scratchpad\km3602\_inspect.txt";
var uiapp = new UIApplication(document.Application);
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> h = null;
h = (s, e) => {
  uiapp.Idling -= h; var log = new System.Text.StringBuilder();
  foreach (var blk in blocks)
  {
    var path = System.IO.Path.Combine(dir, "3602-КМ_" + blk + ".rvt"); Document d = null; bool opened = false;
    try {
      foreach (Document od in uiapp.Application.Documents) if (string.Equals(od.PathName, path, StringComparison.OrdinalIgnoreCase)) d = od;
      if (d == null) { d = uiapp.Application.OpenDocumentFile(path); opened = true; }
      Insp.Run(d, blk, blocks, log);
    } catch (Exception ex) { log.AppendLine("##### " + blk + ": ERR " + ex.Message); }
    finally { try { if (opened && d != null) d.Close(false); } catch (Exception ex2) { log.AppendLine("close ERR " + ex2.Message); } }
  }
  System.IO.File.WriteAllText(outLog, log.ToString(), System.Text.Encoding.UTF8);
};
uiapp.Idling += h; return "queued";
}
public static class Insp {
  const double MM = 304.8;
  static string Cm(Element e) { var p = e.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS); return p == null ? null : p.AsString(); }
  static string Tag(string c, string blk, string[] blocks) {
    if (string.IsNullOrEmpty(c)) return "none";
    if (c.Contains(blk)) return "own";
    foreach (var b in blocks) if (c.Contains(b)) return "FOREIGN:" + b;
    return "other";
  }
  public static void Run(Document d, string blk, string[] blocks, System.Text.StringBuilder L) {
    L.AppendLine("##### " + blk + " :: " + d.Title + " :: " + d.PathName + " :: workshared=" + d.IsWorkshared);
    var all = new FilteredElementCollector(d).WhereElementIsNotElementType().Where(x => x.Category != null).ToList();
    L.AppendLine("elements with category: " + all.Count);
    // tags by category
    foreach (var g in all.GroupBy(x => Tag(Cm(x), blk, blocks) + " | " + x.Category.Name).OrderBy(g => g.Key))
      if (!g.Key.StartsWith("none") || g.First().Category.CategoryType == CategoryType.Model) L.AppendLine("  " + g.Key + ": " + g.Count());
    // distinct comment values (non-own)
    L.AppendLine("-- comment values that are not own (top 40):");
    foreach (var g in all.Select(x => Cm(x)).Where(c => !string.IsNullOrEmpty(c) && !c.Contains(blk)).GroupBy(c => c).OrderByDescending(g => g.Count()).Take(40)) L.AppendLine("  [" + g.Key + "] x" + g.Count());
    L.AppendLine("-- own comment values (top 15):");
    foreach (var g in all.Select(x => Cm(x)).Where(c => !string.IsNullOrEmpty(c) && c.Contains(blk)).GroupBy(c => c).OrderByDescending(g => g.Count()).Take(15)) L.AppendLine("  [" + g.Key + "] x" + g.Count());
    // footprint from own model elements with bbox
    var own = all.Where(x => x.Category.CategoryType == CategoryType.Model && Tag(Cm(x), blk, blocks) == "own").Select(x => x.get_BoundingBox(null)).Where(b => b != null).ToList();
    if (own.Count == 0) { L.AppendLine("NO OWN MODEL ELEMENTS"); return; }
    double x0 = own.Min(b => b.Min.X), x1 = own.Max(b => b.Max.X), y0 = own.Min(b => b.Min.Y), y1 = own.Max(b => b.Max.Y), z0 = own.Min(b => b.Min.Z), z1 = own.Max(b => b.Max.Z);
    L.AppendLine(string.Format("own footprint mm: X {0:F0}..{1:F0}  Y {2:F0}..{3:F0}  Z {4:F0}..{5:F0}", x0 * MM, x1 * MM, y0 * MM, y1 * MM, z0 * MM, z1 * MM));
    double m = 3000 / MM;
    Func<BoundingBoxXYZ, bool> inside = b => { var c = (b.Min + b.Max) / 2; return c.X > x0 - m && c.X < x1 + m && c.Y > y0 - m && c.Y < y1 + m; };
    // untagged model elements: inside / outside footprint
    var none = all.Where(x => x.Category.CategoryType == CategoryType.Model && Tag(Cm(x), blk, blocks) != "own").ToList();
    L.AppendLine("-- non-own model elements by category (in/out of footprint ±3 m, nobbox):");
    foreach (var g in none.GroupBy(x => x.Category.Name).OrderBy(g => g.Key)) {
      int ins = 0, outs = 0, nob = 0; foreach (var x in g) { var b = x.get_BoundingBox(null); if (b == null) nob++; else if (inside(b)) ins++; else outs++; }
      L.AppendLine("  " + g.Key + ": in " + ins + ", OUT " + outs + ", nobbox " + nob);
    }
    int k = 0;
    foreach (var x in none) { var b = x.get_BoundingBox(null); if (b == null || inside(b)) continue; if (k++ >= 40) break;
      var c = (b.Min + b.Max) / 2; var ty = d.GetElement(x.GetTypeId());
      L.AppendLine(string.Format("    OUT id {0} {1} [{2}] {3} @ {4:F0},{5:F0},{6:F0} cm=[{7}]", x.Id, x.Category.Name, ty == null ? "" : ty.Name, x.Name, c.X * MM, c.Y * MM, c.Z * MM, Cm(x))); }
    // grids
    L.AppendLine("-- grids:");
    foreach (var g in new FilteredElementCollector(d).OfClass(typeof(Grid)).Cast<Grid>()) {
      var a = g.Curve.GetEndPoint(0); var b = g.Curve.GetEndPoint(1);
      bool far = Math.Max(a.X, b.X) < x0 - m || Math.Min(a.X, b.X) > x1 + m || Math.Max(a.Y, b.Y) < y0 - m || Math.Min(a.Y, b.Y) > y1 + m;
      L.AppendLine(string.Format("  {0} ({1:F0},{2:F0})→({3:F0},{4:F0}) {5}", g.Name.Replace("\u200B", "~"), a.X * MM, a.Y * MM, b.X * MM, b.Y * MM, far ? "FAR" : "ok"));
    }
    // levels
    L.AppendLine("-- levels (elev mm, elements on level, plan views):");
    var lvUse = all.GroupBy(x => x.LevelId).ToDictionary(g => g.Key, g => g.Count());
    var plans = new FilteredElementCollector(d).OfClass(typeof(ViewPlan)).Cast<ViewPlan>().Where(v => !v.IsTemplate && v.GenLevel != null).ToList();
    foreach (var lv in new FilteredElementCollector(d).OfClass(typeof(Level)).Cast<Level>().OrderBy(q => q.Elevation)) {
      int n; lvUse.TryGetValue(lv.Id, out n);
      L.AppendLine(string.Format("  {0} {1:F0} el={2} plans={3}", lv.Name, lv.Elevation * MM, n, plans.Count(v => v.GenLevel.Id == lv.Id)));
    }
    // views / sheets
    var views = new FilteredElementCollector(d).OfClass(typeof(View)).Cast<View>().Where(v => !v.IsTemplate).ToList();
    L.AppendLine("-- views: " + views.Count + " (templates " + new FilteredElementCollector(d).OfClass(typeof(View)).Cast<View>().Count(v => v.IsTemplate) + ")");
    foreach (var v in views.OrderBy(v => v.ViewType.ToString()).ThenBy(v => v.Name)) {
      string f = blocks.Where(b => b != blk && v.Name.Contains(b)).FirstOrDefault();
      string extra = "";
      if (v is ViewSheet) { var sh = (ViewSheet)v; extra = " #" + sh.SheetNumber + " vps=" + sh.GetAllPlacedViews().Count; }
      L.AppendLine("  " + v.ViewType + ": " + v.Name + extra + (f != null ? "   <<< FOREIGN " + f : ""));
    }
    // filters, materials, families, links, groups
    var filt = new FilteredElementCollector(d).OfClass(typeof(ParameterFilterElement)).Cast<Element>().Select(x => x.Name).ToList();
    L.AppendLine("-- filters " + filt.Count + ": " + string.Join("; ", filt));
    var mats = new FilteredElementCollector(d).OfClass(typeof(Material)).Cast<Material>().Select(x => x.Name).Where(n => n.StartsWith("КМ_")).ToList();
    L.AppendLine("-- КМ_ materials " + mats.Count + ": " + string.Join("; ", mats));
    var fams = new FilteredElementCollector(d).OfClass(typeof(Family)).Cast<Family>().ToList();
    L.AppendLine("-- families " + fams.Count + ": " + string.Join("; ", fams.Select(f => f.Name).OrderBy(n => n)));
    L.AppendLine("-- imports " + new FilteredElementCollector(d).OfClass(typeof(ImportInstance)).GetElementCount() + ", CAD types " + new FilteredElementCollector(d).OfClass(typeof(CADLinkType)).GetElementCount()
      + ", rvt links " + new FilteredElementCollector(d).OfClass(typeof(RevitLinkInstance)).GetElementCount() + ", groups " + new FilteredElementCollector(d).OfClass(typeof(Group)).GetElementCount()
      + ", group types " + new FilteredElementCollector(d).OfClass(typeof(GroupType)).GetElementCount() + ", directshapes " + new FilteredElementCollector(d).OfClass(typeof(DirectShape)).GetElementCount());
    // schedules content hint
    foreach (var vs in new FilteredElementCollector(d).OfClass(typeof(ViewSchedule)).Cast<ViewSchedule>().Where(v => !v.IsTemplate && !v.IsTitleblockRevisionSchedule)) {
      try { var td = vs.GetTableData().GetSectionData(SectionType.Body); L.AppendLine("  schedule " + vs.Name + ": rows " + td.NumberOfRows); } catch { }
    }
    L.AppendLine();
  }
}
static void Pad() {
