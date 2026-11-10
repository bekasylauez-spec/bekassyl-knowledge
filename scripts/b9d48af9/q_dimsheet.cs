var sb = new System.Text.StringBuilder(); var d = document;
var dims = new FilteredElementCollector(d).OfClass(typeof(Dimension)).Cast<Dimension>().ToList();
var byView = dims.GroupBy(x => x.OwnerViewId.Value).ToDictionary(g => g.Key, g => g.ToList());
foreach (var sh in new FilteredElementCollector(d).OfClass(typeof(ViewSheet)).Cast<ViewSheet>().OrderBy(x => { int n; return int.TryParse(x.SheetNumber, out n) ? n : 999; })) {
  var vals = new List<long>(); int sp = 0; var parts = new List<string>();
  foreach (var vid in sh.GetAllPlacedViews()) { var v = d.GetElement(vid) as View; List<Dimension> L; int c = 0;
    if (byView.TryGetValue(vid.Value, out L)) foreach (var dm in L) { if (dm is SpotDimension) { sp++; continue; }
      if (dm.Segments.Size > 0) foreach (DimensionSegment g in dm.Segments) { vals.Add((long)Math.Round((g.Value ?? 0) * 304.8)); c++; } else { vals.Add((long)Math.Round((dm.Value ?? 0) * 304.8)); c++; } }
    parts.Add(v.Name + ":" + c); }
  sb.AppendLine(sh.SheetNumber + " segs " + vals.Count + " spots " + sp + " | " + string.Join(", ", vals.GroupBy(x => x).OrderBy(g => g.Key).Select(g => g.Key + "x" + g.Count())) + " || " + string.Join("; ", parts)); }
return sb.ToString();
