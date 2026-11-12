// READ-ONLY inventory of the В113 КМ model: sheets, views, annotations, members, DirectShapes, schedules, warnings.
var sb = new StringBuilder(); var d = document; double M = 304.8;
string outp = @"C:\Users\Admin\AppData\Local\Temp\claude\f4c3a78720b97f45\677e944d-f832-4f85-987d-aa96db42c8c8\scratchpad\inv.txt";
try {
sb.AppendLine("DOC " + d.PathName + " modified=" + d.IsModified + " title=" + d.Title);
var pi = d.ProjectInformation;
sb.AppendLine("== PROJECT INFO");
foreach (Parameter p in pi.Parameters) { string v = p.StorageType == StorageType.String ? p.AsString() : p.AsValueString(); if (!string.IsNullOrEmpty(v)) sb.AppendLine("  " + p.Definition.Name + " = " + v); }
sb.AppendLine("== LEVELS");
foreach (var l in new FilteredElementCollector(d).OfClass(typeof(Level)).Cast<Level>().OrderBy(x => x.Elevation)) sb.AppendLine("  " + l.Name + " " + (l.Elevation * M).ToString("0.#"));
sb.AppendLine("== GRIDS");
foreach (var g in new FilteredElementCollector(d).OfClass(typeof(Grid)).Cast<Grid>().OrderBy(x => x.Name)) { var c = g.Curve; var a = c.GetEndPoint(0) * M; var b = c.GetEndPoint(1) * M; sb.AppendLine("  " + g.Name + " " + a.X.ToString("0") + "," + a.Y.ToString("0") + " -> " + b.X.ToString("0") + "," + b.Y.ToString("0")); }
sb.AppendLine("== WARNINGS");
foreach (var w in d.GetWarnings().GroupBy(x => x.GetDescriptionText())) sb.AppendLine("  x" + w.Count() + " " + w.Key + " e.g. " + string.Join(",", w.First().GetFailingElements().Take(4).Select(i => i.Value)));

// ---- members
sb.AppendLine("== MEMBERS (mark | family | type | material | count | sumL m | Lmin..Lmax | z min..max)");
var fis = new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Category != null && (x.Category.Id.Value == (long)BuiltInCategory.OST_StructuralFraming || x.Category.Id.Value == (long)BuiltInCategory.OST_StructuralColumns)).ToList();
var rows = new List<Tuple<string, double, double, double, string>>();
var tsv = new StringBuilder(); tsv.AppendLine("id\tmark\tcat\tfamily\ttype\tmat\tax\tay\taz\tbx\tby\tbz\tlen\tcut\tbbmin\tbbmax");
foreach (var f in fis) {
  string mk = f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? ""; string mark2 = f.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)?.AsString() ?? "";
  string mat = d.GetElement(f.StructuralMaterialId)?.Name ?? "-"; var bb = f.get_BoundingBox(null); XYZ a, b;
  if (f.Location is LocationCurve lc) { a = lc.Curve.GetEndPoint(0); b = lc.Curve.GetEndPoint(1); } else { var lp = ((LocationPoint)f.Location).Point; a = new XYZ(lp.X, lp.Y, bb.Min.Z); b = new XYZ(lp.X, lp.Y, bb.Max.Z); }
  double len = a.DistanceTo(b) * M; double cut = (f.get_Parameter(BuiltInParameter.STRUCTURAL_FRAME_CUT_LENGTH)?.AsDouble() ?? 0) * M;
  string key = mk + " | " + f.Symbol.Family.Name + " | " + f.Symbol.Name + " | " + mat + " | " + f.Category.Name + (mark2 != "" ? " | Марка=" + mark2 : "");
  rows.Add(Tuple.Create(key, len, bb.Min.Z * M, bb.Max.Z * M, mk));
  tsv.AppendLine(f.Id.Value + "\t" + mk + "\t" + f.Category.Name + "\t" + f.Symbol.Family.Name + "\t" + f.Symbol.Name + "\t" + mat + "\t" + (a.X*M).ToString("0.#") + "\t" + (a.Y*M).ToString("0.#") + "\t" + (a.Z*M).ToString("0.#") + "\t" + (b.X*M).ToString("0.#") + "\t" + (b.Y*M).ToString("0.#") + "\t" + (b.Z*M).ToString("0.#") + "\t" + len.ToString("0.#") + "\t" + cut.ToString("0.#") + "\t" + (bb.Min.X*M).ToString("0") + "," + (bb.Min.Y*M).ToString("0") + "," + (bb.Min.Z*M).ToString("0") + "\t" + (bb.Max.X*M).ToString("0") + "," + (bb.Max.Y*M).ToString("0") + "," + (bb.Max.Z*M).ToString("0"));
}
System.IO.File.WriteAllText(outp.Replace("inv.txt", "members_rvt.tsv"), tsv.ToString(), Encoding.UTF8);
foreach (var g in rows.GroupBy(x => x.Item1).OrderBy(x => x.Key)) sb.AppendLine("  " + g.Key + " | " + g.Count() + " | " + (g.Sum(x => x.Item2) / 1000).ToString("0.00") + " | " + g.Min(x => x.Item2).ToString("0") + ".." + g.Max(x => x.Item2).ToString("0") + " | " + g.Min(x => x.Item3).ToString("0") + ".." + g.Max(x => x.Item4).ToString("0"));
sb.AppendLine("  TOTAL members " + fis.Count);
sb.AppendLine("== OTHER FAMILY INSTANCES (model categories)");
foreach (var g in new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Category != null && x.Category.CategoryType == CategoryType.Model && !fis.Contains(x)).GroupBy(x => x.Category.Name + " | " + x.Symbol.Family.Name + " | " + x.Symbol.Name)) sb.AppendLine("  " + g.Key + " x" + g.Count());
sb.AppendLine("== DIRECTSHAPES (appId | dataId | category | name | count | volume dm3)");
var dss = new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>().ToList();
var dst = new StringBuilder(); dst.AppendLine("id\tapp\tdata\tcat\tname\tmat\tvol_cm3\tmin\tmax\tcomments");
var gopt = new Options { DetailLevel = ViewDetailLevel.Fine };
var dsr = new List<Tuple<string, double>>();
foreach (var ds in dss) { double vol = 0; string mat = "-"; try { foreach (var g in ds.get_Geometry(gopt)) { var s = g as Solid; if (s != null && s.Volume > 1e-9) { vol += s.Volume; if (mat == "-" && s.Faces.Size > 0) mat = d.GetElement(s.Faces.get_Item(0).MaterialElementId)?.Name ?? "-"; } } } catch { }
  var bb = ds.get_BoundingBox(null); string cm = ds.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "";
  dsr.Add(Tuple.Create(ds.ApplicationId + " | " + ds.ApplicationDataId + " | " + (ds.Category?.Name ?? "-") + " | " + ds.Name + " | " + mat, vol * 28.316846592));
  dst.AppendLine(ds.Id.Value + "\t" + ds.ApplicationId + "\t" + ds.ApplicationDataId + "\t" + (ds.Category?.Name ?? "-") + "\t" + ds.Name + "\t" + mat + "\t" + (vol * 28316.846592).ToString("0") + "\t" + (bb == null ? "" : (bb.Min.X*M).ToString("0") + "," + (bb.Min.Y*M).ToString("0") + "," + (bb.Min.Z*M).ToString("0")) + "\t" + (bb == null ? "" : (bb.Max.X*M).ToString("0") + "," + (bb.Max.Y*M).ToString("0") + "," + (bb.Max.Z*M).ToString("0")) + "\t" + cm); }
System.IO.File.WriteAllText(outp.Replace("inv.txt", "ds_rvt.tsv"), dst.ToString(), Encoding.UTF8);
foreach (var g in dsr.GroupBy(x => x.Item1).OrderBy(x => x.Key)) sb.AppendLine("  " + g.Key + " | " + g.Count() + " | " + g.Sum(x => x.Item2).ToString("0.00"));
sb.AppendLine("  TOTAL DS " + dss.Count);
sb.AppendLine("== OTHER MODEL ELEMENTS (category counts, non-FI non-DS)");
foreach (var g in new FilteredElementCollector(d).WhereElementIsNotElementType().Where(x => x.Category != null && x.Category.CategoryType == CategoryType.Model && !(x is FamilyInstance) && !(x is DirectShape) && x.ViewSpecific == false).GroupBy(x => x.Category.Name)) sb.AppendLine("  " + g.Key + " x" + g.Count());

// ---- sheets
sb.AppendLine("== SHEETS");
var sheets = new FilteredElementCollector(d).OfClass(typeof(ViewSheet)).Cast<ViewSheet>().ToList();
var placed = new HashSet<long>();
Func<Element, string> annot = v => { var parts = new List<string>(); foreach (var g in new FilteredElementCollector(d, v.Id).WhereElementIsNotElementType().Where(x => x.Category != null && x.ViewSpecific).GroupBy(x => x.Category.Name)) parts.Add(g.Key + ":" + g.Count()); return string.Join("; ", parts); };
foreach (var sh in sheets.OrderBy(x => x.Id.Value)) {
  var tb = new FilteredElementCollector(d, sh.Id).OfCategory(BuiltInCategory.OST_TitleBlocks).Cast<FamilyInstance>().FirstOrDefault();
  string tbs = tb == null ? "NO TITLEBLOCK" : tb.Symbol.Family.Name + ":" + tb.Symbol.Name + " " + ((tb.get_Parameter(BuiltInParameter.SHEET_WIDTH)?.AsDouble() ?? 0) * M).ToString("0") + "x" + ((tb.get_Parameter(BuiltInParameter.SHEET_HEIGHT)?.AsDouble() ?? 0) * M).ToString("0");
  sb.AppendLine("SHEET [" + sh.SheetNumber + "] " + sh.Name + " | id " + sh.Id.Value + " | " + tbs + " | printable=" + sh.CanBePrinted);
  foreach (Parameter p in sh.Parameters) { if (p.StorageType != StorageType.String) continue; string v = p.AsString(); if (!string.IsNullOrEmpty(v) && p.Definition.Name != "Имя листа" && p.Definition.Name != "Номер листа") sb.AppendLine("    P " + p.Definition.Name + " = " + v); }
  if (tb != null) foreach (Parameter p in tb.Parameters) { if (p.IsReadOnly) continue; string v = p.StorageType == StorageType.String ? p.AsString() : (p.StorageType == StorageType.Integer ? p.AsInteger().ToString() : null); if (!string.IsNullOrEmpty(v)) sb.AppendLine("    TB " + p.Definition.Name + " = " + v); }
  sb.AppendLine("    on-sheet: " + annot(sh));
  foreach (var tn in new FilteredElementCollector(d, sh.Id).OfClass(typeof(TextNote)).Cast<TextNote>()) sb.AppendLine("    TXT[" + tn.TextNoteType.Name + "] " + tn.Text.Replace("\r", " / ").Replace("\n", ""));
  foreach (var si in new FilteredElementCollector(d, sh.Id).OfClass(typeof(ScheduleSheetInstance)).Cast<ScheduleSheetInstance>()) { if (si.IsTitleblockRevisionSchedule) continue; var bb = si.get_BoundingBox(sh); sb.AppendLine("    SCHED " + si.Name + " bbox " + (bb == null ? "?" : (bb.Min.X*M).ToString("0") + "," + (bb.Min.Y*M).ToString("0") + " .. " + (bb.Max.X*M).ToString("0") + "," + (bb.Max.Y*M).ToString("0"))); placed.Add(si.ScheduleId.Value); }
  foreach (var vid in sh.GetAllViewports()) { var vp = (Viewport)d.GetElement(vid); var v = (View)d.GetElement(vp.ViewId); placed.Add(v.Id.Value); var o = vp.GetBoxOutline();
    string tpl = v.ViewTemplateId == ElementId.InvalidElementId ? "-" : d.GetElement(v.ViewTemplateId).Name;
    sb.AppendLine("    VP " + v.Name + " [" + v.ViewType + "] 1:" + v.Scale + " detail=" + v.DetailLevel + " style=" + v.DisplayStyle + " tpl=" + tpl + " vptype=" + d.GetElement(vp.GetTypeId()).Name + " box " + (o.MinimumPoint.X*M).ToString("0") + "," + (o.MinimumPoint.Y*M).ToString("0") + " .. " + (o.MaximumPoint.X*M).ToString("0") + "," + (o.MaximumPoint.Y*M).ToString("0") + " title=" + (v.get_Parameter(BuiltInParameter.VIEW_DESCRIPTION)?.AsString() ?? ""));
    sb.AppendLine("       annot: " + annot(v));
    foreach (var tn in new FilteredElementCollector(d, v.Id).OfClass(typeof(TextNote)).Cast<TextNote>()) sb.AppendLine("       TXT[" + tn.TextNoteType.Name + "] " + tn.Text.Replace("\r", " / ").Replace("\n", ""));
    var tags = new FilteredElementCollector(d, v.Id).OfClass(typeof(IndependentTag)).Cast<IndependentTag>().Select(t => { try { return t.TagText; } catch { return "?"; } }).GroupBy(x => x).Select(g => g.Key + (g.Count() > 1 ? "×" + g.Count() : ""));
    sb.AppendLine("       TAGS: " + string.Join(" | ", tags));
    var dims = new FilteredElementCollector(d, v.Id).OfClass(typeof(Dimension)).Cast<Dimension>().ToList(); var dv = new List<string>();
    foreach (var dm in dims) { try { if (dm.NumberOfSegments > 1) dv.Add("[" + string.Join("+", dm.Segments.Cast<DimensionSegment>().Select(sg => (sg.ValueOverride != null && sg.ValueOverride != "" ? "OVR:" + sg.ValueOverride : sg.ValueString))) + "]"); else dv.Add((dm.ValueOverride != null && dm.ValueOverride != "" ? "OVR:" + dm.ValueOverride : dm.ValueString) ?? "?"); } catch { dv.Add("?"); } }
    sb.AppendLine("       DIMS(" + dims.Count + "): " + string.Join(" ", dv));
    var spots = new FilteredElementCollector(d, v.Id).OfClass(typeof(SpotDimension)).Cast<SpotDimension>().Select(x => { try { return x.ValueString ?? x.get_Parameter(BuiltInParameter.SPOT_ELEV_SINGLE_OR_UPPER_VALUE)?.AsValueString() ?? "?"; } catch { return "?"; } }).ToList();
    if (spots.Count > 0) sb.AppendLine("       SPOTS: " + string.Join(" ", spots));
  }
}
sb.AppendLine("== VIEWS NOT ON SHEETS");
foreach (var v in new FilteredElementCollector(d).OfClass(typeof(View)).Cast<View>().Where(x => !x.IsTemplate && !(x is ViewSheet) && !placed.Contains(x.Id.Value) && x.ViewType != ViewType.ProjectBrowser && x.ViewType != ViewType.SystemBrowser && x.ViewType != ViewType.Internal).OrderBy(x => x.ViewType.ToString() + x.Name)) sb.AppendLine("  " + v.ViewType + " | " + v.Name);
sb.AppendLine("== SCHEDULES (body)");
foreach (var vs in new FilteredElementCollector(d).OfClass(typeof(ViewSchedule)).Cast<ViewSchedule>().Where(x => !x.IsTemplate && !x.IsTitleblockRevisionSchedule)) {
  sb.AppendLine("SCHEDULE " + vs.Name + " placed=" + placed.Contains(vs.Id.Value));
  try { var td = vs.GetTableData(); foreach (var st in new[] { SectionType.Header, SectionType.Body }) { var sec = td.GetSectionData(st); if (sec == null) continue; for (int r = 0; r < sec.NumberOfRows && r < 120; r++) { var cells = new List<string>(); for (int c = 0; c < sec.NumberOfColumns; c++) { string t = ""; try { t = vs.GetCellText(st, r, c); } catch { } cells.Add(t); } sb.AppendLine("   " + (st == SectionType.Header ? "H " : "") + string.Join(" ¦ ", cells)); } } } catch (Exception ex) { sb.AppendLine("   ERR " + ex.Message); }
}
sb.AppendLine("== TEXT TYPES / DIM TYPES");
foreach (var t in new FilteredElementCollector(d).OfClass(typeof(TextNoteType)).Cast<TextNoteType>()) sb.AppendLine("  TXT " + t.Name + " font=" + t.get_Parameter(BuiltInParameter.TEXT_FONT)?.AsString() + " h=" + ((t.get_Parameter(BuiltInParameter.TEXT_SIZE)?.AsDouble() ?? 0) * M).ToString("0.##") + " w=" + (t.get_Parameter(BuiltInParameter.TEXT_WIDTH_SCALE)?.AsDouble() ?? 0).ToString("0.##") + " it=" + t.get_Parameter(BuiltInParameter.TEXT_STYLE_ITALIC)?.AsInteger() + " used=" + new FilteredElementCollector(d).OfClass(typeof(TextNote)).Cast<TextNote>().Count(x => x.GetTypeId() == t.Id));
foreach (var t in new FilteredElementCollector(d).OfClass(typeof(DimensionType)).Cast<DimensionType>()) { int used = new FilteredElementCollector(d).OfClass(typeof(Dimension)).Count(x => x.GetTypeId() == t.Id) + new FilteredElementCollector(d).OfClass(typeof(SpotDimension)).Count(x => x.GetTypeId() == t.Id); if (used > 0) sb.AppendLine("  DIM " + t.Name + " [" + t.StyleType + "] font=" + t.get_Parameter(BuiltInParameter.TEXT_FONT)?.AsString() + " h=" + ((t.get_Parameter(BuiltInParameter.TEXT_SIZE)?.AsDouble() ?? 0) * M).ToString("0.##") + " used=" + used); }
} catch (Exception ex) { sb.AppendLine("ERR " + ex); }
System.IO.File.WriteAllText(outp, sb.ToString(), Encoding.UTF8);
return "written " + sb.Length;
