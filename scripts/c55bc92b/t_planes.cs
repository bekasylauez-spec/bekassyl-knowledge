var app = document.Application; var sb = new System.Text.StringBuilder();
string tpl = @"C:\ProgramData\Autodesk\RVT 2025\Family Templates\Russian\Метрическая система, несущий каркас - Балки и раскосы.rft";
foreach (Document dd in app.Documents.Cast<Document>().ToList()) if (dd.IsFamilyDocument) dd.Close(false);
var fd = app.NewFamilyDocument(tpl);
try {
  Action<string> dump = tag => { sb.AppendLine("== " + tag);
    foreach (var rp in new FilteredElementCollector(fd).OfClass(typeof(ReferencePlane)).Cast<ReferencePlane>().OrderBy(r => r.BubbleEnd.X)) sb.AppendLine("  RP '" + rp.Name + "' x=" + Math.Round(rp.BubbleEnd.X * 304.8, 1) + " bubble=" + Math.Round(rp.BubbleEnd.Y * 304.8) + "," + Math.Round(rp.BubbleEnd.Z * 304.8) + " free=" + Math.Round(rp.FreeEnd.Y * 304.8) + "," + Math.Round(rp.FreeEnd.Z * 304.8));
    foreach (var dm in new FilteredElementCollector(fd).OfClass(typeof(Dimension)).Cast<Dimension>()) { string lab = ""; try { lab = dm.FamilyLabel == null ? "" : dm.FamilyLabel.Definition.Name; } catch { }
      string refs = ""; try { foreach (Reference r in dm.References) { var e = fd.GetElement(r); refs += (e is ReferencePlane rp2 ? rp2.Name : e == null ? "?" : e.GetType().Name) + ";"; } } catch { }
      sb.AppendLine("  DIM id=" + dm.Id + " val=" + (dm.Value.HasValue ? Math.Round(dm.Value.Value * 304.8, 1).ToString() : "-") + " segs=" + dm.NumberOfSegments + " label=" + lab + " refs=" + refs); }
    foreach (var fp in fd.FamilyManager.Parameters.Cast<FamilyParameter>().Where(p => p.Definition.Name.ToLower().Contains("длин") || p.Definition.Name.ToLower().Contains("отрез") || p.Definition.Name.ToLower().Contains("срез"))) sb.AppendLine("  FP " + fp.Definition.Name + " readonly=" + fp.IsReadOnly + " inst=" + fp.IsInstance); };
  dump("template");
  using (var t = new Transaction(fd, "planes")) { t.Start();
    foreach (var nm in new[] { "Слева", "Элемент слева", "Стикер слева", "Справа", "Элемент справа", "Стикер справа" }) { var rp = new FilteredElementCollector(fd).OfClass(typeof(ReferencePlane)).Cast<ReferencePlane>().First(r => r.Name == nm); ElementTransformUtils.MoveElement(fd, rp.Id, new XYZ((nm.Contains("лева") ? -2054.12 : 2054.12) / 304.8, 0, 0)); }
    t.Commit(); }
  dump("after move d0=2054.12");
} finally { fd.Close(false); }
return sb.ToString();
